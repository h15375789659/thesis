"""
LLM 输出多层容错解析器
======================
LLM 输出 JSON 不稳定（可能带 ```json 包裹、多余文字等）。
按优先级尝试 5 种策略，逐级降级，确保尽量解析出结构化结果。
"""
import json
import re


def safe_parse_json(llm_output: str) -> dict:
    """
    多层容错解析 LLM 输出的 JSON。

    策略优先级：
    1. 直接解析（理想情况，LLM 输出了纯 JSON）
    2. 提取 ```json ... ``` 代码块
    3. 提取 ``` ... ``` 任意代码块
    4. 正则匹配第一个 { ... } 对象
    5. 兜底：返回带 parse_error 标记的 dict
    """
    # 策略 1：直接解析
    try:
        return json.loads(llm_output)
    except (json.JSONDecodeError, TypeError):
        pass

    # 策略 2：提取 ```json ... ``` 代码块
    match = re.search(r'```json\s*(.*?)\s*```', llm_output, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except (json.JSONDecodeError, TypeError):
            pass

    # 策略 3：提取 ``` ... ``` 任意代码块
    match = re.search(r'```\s*(.*?)\s*```', llm_output, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except (json.JSONDecodeError, TypeError):
            pass

    # 策略 4：正则匹配第一个 { ... } 对象（支持嵌套）
    match = re.search(r'\{.*\}', llm_output, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except (json.JSONDecodeError, TypeError):
            pass

    # 策略 5：兜底 —— 解析失败，返回标记
    return {
        "is_ad": None,
        "risk_level": "unknown",
        "reasoning": llm_output,
        "parse_error": True
    }
