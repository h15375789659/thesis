"""
知识库构建脚本 —— 将 JSON 数据向量化存入 ChromaDB（一次性运行）
==============================================================
把 data/laws.json 和 data/cases.json 里的法规/案例，
用 BGE-M3 向量化后存入 ChromaDB，供 RAG 检索使用。

运行：python knowledge_base/build_kb.py
"""
import json
import os
import sys

# 把 code/ 目录加入 sys.path，以便 import core 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.utils import embedding_functions
from core.config import CHROMA_DB_PATH, EMBEDDING_MODEL

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def build_knowledge_base():
    print("=" * 50)
    print("开始构建知识库...")
    print("=" * 50)

    # 1. 加载 Embedding 模型
    print("\n[1/4] 加载 BGE-M3 Embedding 模型...")
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    # 2. 连接/创建 ChromaDB
    print("[2/4] 连接 ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # 3. 读取 JSON 数据并入库
    print("[3/4] 读取数据并向量化入库...")

    # --- 法规库 ---
    with open(os.path.join(DATA_DIR, "laws.json"), "r", encoding="utf-8") as f:
        laws = json.load(f)

    laws_col = client.get_or_create_collection(
        name="ad_laws",
        metadata={"hnsw:space": "cosine"},
        embedding_function=embed_fn
    )

    # 清空旧数据，避免重复入库
    if laws_col.count() > 0:
        laws_col.delete(ids=laws_col.get()['ids'])

    laws_col.add(
        documents=[law["content"] for law in laws],
        metadatas=[{"source": law["source"], "type": law["type"]} for law in laws],
        ids=[law["id"] for law in laws]
    )
    print(f"  [OK] 法规库：{len(laws)} 条")

    # --- 案例库 ---
    with open(os.path.join(DATA_DIR, "cases.json"), "r", encoding="utf-8") as f:
        cases = json.load(f)

    cases_col = client.get_or_create_collection(
        name="ad_cases",
        metadata={"hnsw:space": "cosine"},
        embedding_function=embed_fn
    )

    if cases_col.count() > 0:
        cases_col.delete(ids=cases_col.get()['ids'])

    cases_col.add(
        documents=[case["content"] for case in cases],
        metadatas=[{"source": case["source"], "type": case["type"],
                     "violation_type": case["violation_type"]} for case in cases],
        ids=[case["id"] for case in cases]
    )
    print(f"  [OK] 案例库：{len(cases)} 条")

    # --- 话术模板库 ---
    with open(os.path.join(DATA_DIR, "templates.json"), "r", encoding="utf-8") as f:
        templates = json.load(f)

    templates_col = client.get_or_create_collection(
        name="ad_templates",
        metadata={"hnsw:space": "cosine"},
        embedding_function=embed_fn
    )

    if templates_col.count() > 0:
        templates_col.delete(ids=templates_col.get()['ids'])

    templates_col.add(
        documents=[tpl["content"] for tpl in templates],
        metadatas=[{"category": tpl["category"], "type": tpl["type"]} for tpl in templates],
        ids=[tpl["id"] for tpl in templates]
    )
    print(f"  [OK] 话术库：{len(templates)} 条")

    # 4. 验证
    print(f"\n[4/4] 验证：")
    print(f"  ad_laws 共 {laws_col.count()} 条")
    print(f"  ad_cases 共 {cases_col.count()} 条")
    print(f"  ad_templates 共 {templates_col.count()} 条")

    print("\n" + "=" * 50)
    print("[OK] 知识库构建完成！")
    print("=" * 50)


if __name__ == "__main__":
    build_knowledge_base()
