"""
Phase 4：RAG 端到端测试 —— 最重要的里程碑！
==============================================
把检索 + LLM 推理串起来，输入文本 → 输出「是否广告 + 风险等级 + 依据」。

运行前先构建知识库：
    python knowledge_base/build_kb.py

然后运行本脚本：
    python phase4/test_rag_e2e.py
"""
import os
import sys

# 把 code/ 目录加入 sys.path，以便 import core 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.rag_pipeline import RAGPipeline

# 测试文本集（覆盖：明显广告、法规原文、普通分享、边界情况）
test_texts = [
    "姐妹们！最近发现一款神仙面霜，用了一周皮肤真的变好了！链接在评论区，现在还有限时优惠，赶紧冲！",
    "根据《消费者权益保护法》，经营者应当保证其提供的商品或者服务符合保障人身、财产安全的要求。",
    "今天天气真好，出去公园走了走，拍了几张照片。",
    "作为一个数码爱好者，我自费购买了最新的三款手机，给大家做一个横评对比。左边这款性价比最高，右边这款拍照最强。",
]

# 初始化 Pipeline
print("初始化 RAG Pipeline...\n")
pipeline = RAGPipeline()

# 逐条测试
for i, text in enumerate(test_texts, 1):
    print("=" * 60)
    print(f"测试 {i}/{len(test_texts)}：")
    print(f"输入文本：{text[:60]}...")

    result = pipeline.detect(text, prompt_mode="full")

    print(f"\n判定结果：")
    print(f"  是否广告：{result.get('is_ad', '无法判定')}")
    print(f"  风险等级：{result.get('risk_level', '未知')}")
    print(f"  广告类型：{result.get('ad_type', '未知')}")
    print(f"  置信度：{result.get('confidence', '未知')}")
    print(f"  推理摘要：{result.get('reasoning', '无')[:80]}...")

    meta = result.get("_meta", {})
    print(f"\nToken 用量：输入 {meta.get('prompt_tokens', '?')} + 输出 {meta.get('completion_tokens', '?')}")
    print(f"匹配法规数：{len(meta.get('retrieved_laws', []))}")
    print(f"匹配案例数：{len(meta.get('retrieved_cases', []))}")
    print()
