"""
Phase 2-A：验证 DeepSeek API 能调通
====================================
目标：用 Python 调用 DeepSeek，让大模型回复一句话。

学到的概念：
1. OpenAI Python SDK —— DeepSeek 兼容 OpenAI 的接口格式
2. client.chat.completions.create() —— 发一次对话请求
3. system vs user 的 role 区别
4. temperature 参数（高=随机，低=稳定）
"""
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL

# 创建客户端（类比：new 一个数据库连接）
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# 最简单的调用
response = client.chat.completions.create(
    model=LLM_MODEL,
    messages=[
        # system：设定角色（对整个对话生效的"人设"）
        {"role": "system", "content": "你是一个助手，用中文回答。"},
        # user：具体任务（用户问的问题）
        {"role": "user", "content": "你好，请用一句话介绍什么是隐性广告。"}
    ],
    temperature=0.7  # 0.7 比较自然，适合普通对话
)

# 打印回复
print("=== LLM 回复 ===")
print(response.choices[0].message.content)

# 打印 token 用量（计费依据：输入 + 输出）
print("\n=== Token 用量 ===")
print(f"输入: {response.usage.prompt_tokens} tokens")
print(f"输出: {response.usage.completion_tokens} tokens")
print(f"合计: {response.usage.total_tokens} tokens")
