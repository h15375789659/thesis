"""
Phase 5：Prompt 变体对比测试
==============================
用同一批测试文本，跑不同的 Prompt 变体，对比判定效果。

运行：
    python phase5/compare_prompts.py

说明：
- 8 个 mode 会在每条文本上都跑一遍（共 10×8 = 80 次 LLM 调用，约 5-8 分钟）
- 最后输出每个 mode 的准确率（系统判定 vs 人工标注）
"""
import os
import sys
import json

# 把 code/ 目录加入 sys.path，以便 import core 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.rag_pipeline import RAGPipeline

# 要测试的 mode（可自行删减，减少调用次数）
MODES = ["simple", "rag_only", "cot", "role", "pe", "fewshot", "full", "full_templates"]

# 加载测试集
TEST_SET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_set.json")
with open(TEST_SET_PATH, "r", encoding="utf-8") as f:
    test_set = json.load(f)

print(f"加载测试集：{len(test_set)} 条\n")

# 初始化 Pipeline
pipeline = RAGPipeline()

# 结果统计：{mode: {"correct": 正确数, "total": 总数}}
stats = {mode: {"correct": 0, "total": 0} for mode in MODES}

# 逐条测试
for item in test_set:
    text = item["text"]
    label = item["label_is_ad"]
    label_name = "广告" if label else "非广告"

    print("=" * 70)
    print(f"{item['id']} | 标注：{label_name}")
    print(f"文本：{text[:60]}...")
    print("-" * 70)

    for mode in MODES:
        result = pipeline.detect(text, prompt_mode=mode)
        pred = result.get("is_ad")
        risk = result.get("risk_level", "未知")
        conf = result.get("confidence", None)

        # 判断对错（解析失败 pred=None 视为错误）
        correct = (pred is not None and pred == label)
        stats[mode]["total"] += 1
        if correct:
            stats[mode]["correct"] += 1

        mark = "[对]" if correct else "[错]"
        conf_str = f"{conf:.2f}" if conf is not None else " - "
        pred_str = str(pred) if pred is not None else "解析失败"
        print(f"  {mode:15s} → is_ad={pred_str:6s} risk={risk:4s} conf={conf_str} {mark}")

    print()

# 汇总准确率
print("\n" + "=" * 70)
print("准确率汇总（系统判定 vs 人工标注）")
print("=" * 70)
print(f"{'mode':16s} {'正确/总数':12s} {'准确率':8s}")
print("-" * 40)
for mode in MODES:
    correct = stats[mode]["correct"]
    total = stats[mode]["total"]
    acc = correct / total if total else 0
    print(f"{mode:16s} {correct}/{total:8d}   {acc:6.1%}")
