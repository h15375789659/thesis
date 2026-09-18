"""
Phase 2-B：测试 DeepSeek 输出 JSON 的稳定性
============================================
目标：直观感受「LLM 输出不稳定」这个核心风险。

实验：让 LLM 只输出 JSON，多跑几次，观察有没有多出
      ```json 包裹、解释文字、markdown 标记等情况。
"""
from openai import OpenAI
import json
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# 一条明显的隐性广告测试文本
test_text = "姐妹们！这款防晒霜真的绝绝子！我用了一个月，皮肤白了一个度！限时优惠中，赶紧冲！"

# Prompt：要求只输出 JSON
prompt = f"""判断以下文本是否包含隐性广告。

文本：{test_text}

你必须只输出 JSON，不要包含任何其他文字或 markdown 标记：
{{"is_ad": true或false, "reason": "一句话理由", "risk_level": "高/中/低/无"}}"""

# 连续跑 5 次，观察输出是否每次都干净
print("连续调用 5 次，观察输出稳定性：\n")

for i in range(5):
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1  # 低温度，输出更稳定
    )

    raw_output = response.choices[0].message.content
    print(f"--- 第 {i+1} 次 ---")
    print(f"原始输出：{repr(raw_output)}")  # repr 能看出有没有换行符\n

    # 尝试直接解析
    try:
        result = json.loads(raw_output)
        print(f"✅ 直接解析成功 → 判定：{'是广告' if result['is_ad'] else '不是广告'}")
    except json.JSONDecodeError:
        print("❌ 直接解析失败！需要容错处理")
    print()
