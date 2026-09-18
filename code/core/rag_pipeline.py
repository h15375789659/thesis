"""
RAG 核心链路：检索 → 拼装 Prompt → LLM 推理 → 解析
====================================================
这是整个项目的核心，把 Phase 2 的 LLM 和 Phase 3 的检索串起来。
"""
import json
import os
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI

from core.config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL,
    CHROMA_DB_PATH, EMBEDDING_MODEL, TOP_K, BASE_DIR
)
from core.prompt_templates import build_prompt
from core.parser import safe_parse_json


class RAGPipeline:
    """RAG 推理管线"""

    def __init__(self):
        # 1. 加载 Embedding 模型
        print("加载 BGE-M3 Embedding 模型...")
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )

        # 2. 连接 ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

        # 3. 获取知识库 Collections（法规库 + 案例库 + 话术库）
        self.laws_col = self._get_collection("ad_laws")
        self.cases_col = self._get_collection("ad_cases")
        self.templates_col = self._get_collection("ad_templates")

        # 4. 加载品牌特征表（关键词精确匹配，不进 ChromaDB）
        brands_path = os.path.join(BASE_DIR, "knowledge_base", "data", "brands.json")
        with open(brands_path, "r", encoding="utf-8") as f:
            self.brands = json.load(f)

        # 5. 初始化 LLM 客户端
        self.llm = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

        print("[OK] RAG Pipeline 初始化完成\n")

    def _get_collection(self, name: str):
        """获取或创建 Collection（用余弦相似度做语义检索）"""
        return self.chroma_client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},  # 余弦相似度，文本语义检索标准做法
            embedding_function=self.embed_fn
        )

    def match_brands(self, text: str) -> list:
        """品牌识别：关键词精确匹配品牌名/别称（区别于向量检索）"""
        matched = []
        for b in self.brands:
            candidates = [b["brand"]] + b["aliases"]
            for c in candidates:
                if c.lower() in text.lower():
                    matched.append(f"{b['brand']}（别称：{c}，{b['category']}）")
                    break  # 命中一个别名即可，避免重复
        return matched

    def retrieve(self, query: str, include_templates: bool = False) -> dict:
        """多路召回：从法规库、案例库（及可选话术库）分别检索 Top-K"""
        laws_result = self.laws_col.query(
            query_texts=[query],
            n_results=TOP_K
        )
        cases_result = self.cases_col.query(
            query_texts=[query],
            n_results=TOP_K
        )

        result = {
            "laws": laws_result['documents'][0] if laws_result['documents'] else [],
            "cases": cases_result['documents'][0] if cases_result['documents'] else []
        }

        # 话术库为可选增强（用于两库 vs 三库对比实验）
        if include_templates:
            templates_result = self.templates_col.query(
                query_texts=[query],
                n_results=TOP_K
            )
            result["templates"] = templates_result['documents'][0] if templates_result['documents'] else []
        else:
            result["templates"] = []

        return result

    def detect(self, text: str, prompt_mode: str = "full") -> dict:
        """完整检测流程：检索 → 拼 Prompt → LLM 推理 → 解析"""
        # Step 1: 检索（full_templates 模式额外检索话术库）+ 品牌识别
        include_templates = (prompt_mode == "full_templates")
        knowledge = self.retrieve(text, include_templates=include_templates)
        knowledge["brands"] = self.match_brands(text)

        # Step 2: 拼装 Prompt
        prompt = build_prompt(
            text=text,
            laws=knowledge["laws"],
            cases=knowledge["cases"],
            templates=knowledge.get("templates", []),
            brands=knowledge.get("brands", []),
            mode=prompt_mode
        )

        # Step 3: LLM 推理
        response = self.llm.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1  # 低温度确保输出稳定
        )

        raw_output = response.choices[0].message.content

        # Step 4: 解析结果
        result = safe_parse_json(raw_output)

        # 附加元信息（供调试和实验分析）
        result["_meta"] = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "retrieved_laws": knowledge["laws"],
            "retrieved_cases": knowledge["cases"],
            "retrieved_templates": knowledge.get("templates", []),
            "matched_brands": knowledge.get("brands", []),
            "raw_output": raw_output
        }

        return result
