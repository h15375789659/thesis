"""
Phase 1：Python 最小必要知识
============================
对照 Java 经验，只学项目用得到的 8 个知识点。
每个点都有「Java 对比」帮你快速建立映射。
"""

# ============================================================
# 1. 变量与数据类型
# ============================================================
# Java:  String name = "张三";  int age = 20;  boolean flag = true;
# Python: 不用声明类型，解释器自动推断

name = "隐性广告识别系统"       # str  — 类比 Java String
version = 1.0                  # float — 类比 Java double
max_tokens = 4096              # int   — 类比 Java int
is_ad = False                  # bool  — 类比 Java boolean，注意大写 True/False
risk_level = None              # None  — 类比 Java null

# 打印用 print()，不用 System.out.println()
print(f"系统名称：{name}，版本：{version}")

# Python 的核心数据结构：list 和 dict（项目中最常用）
# ─────────────────────────────────────────────

# list — 类比 Java 的 ArrayList / 数组
test_texts = ["这款面膜太好用了", "今天天气真好", "这个课程改变了我的人生"]
print(f"测试文本数量：{len(test_texts)}")          # len() 类比 .size() / .length
print(f"第一条：{test_texts[0]}")                   # 索引从 0 开始，和 Java 一样
test_texts.append("限时优惠，赶紧下单")              # append() 类比 .add()

# dict — 类比 Java 的 HashMap<String, Object>
# 这是项目中最重要的数据结构，API 返回的 JSON 解析出来就是 dict
result = {
    "is_ad": True,
    "risk_level": "中",
    "reason": "未标注广告标识，含产品推荐"
}
print(f"风险等级：{result['risk_level']}")          # 用 [] 取值，不是 .get()
print(f"所有 key：{list(result.keys())}")           # 查看有哪些字段

# dict 支持嵌套（项目中很常见）
api_response = {
    "code": 200,
    "data": {
        "is_ad": True,
        "confidence": 0.95,
        "legal_basis": ["广告法第十四条", "互联网广告管理办法第九条"]
    }
}
# 取嵌套值
confidence = api_response["data"]["confidence"]
print(f"置信度：{confidence}")


# ============================================================
# 2. 字符串操作
# ============================================================
# Java:  "Hello " + name  或  String.format("Hello %s", name)
# Python: f-string 是最常用的写法，比 Java 方便很多

text = "这款面霜太好用了"

# f-string — 变量直接嵌入字符串
print(f"待检测文本：「{text}」，长度：{len(text)} 字")

# 常用方法
print(text.upper())              # 全大写（相当于 Java .toUpperCase()）
print("广告" in text)             # 子串判断（相当于 Java .contains()），返回 bool
print(text.replace("面霜", "**")) # 替换（相当于 Java .replace()）
words = text.split("，")         # 分割（相当于 Java .split()）
print(words)

# 拼接 — join() 比 Java 更直观
tags = ["种草", "软文", "隐性广告"]
print(" | ".join(tags))          # "种草 | 软文 | 隐性广告"

# 多行字符串 — 项目里 Prompt 模板用它
prompt = f"""你是一个广告审查专家。

待检测文本：{text}

请判断是否包含隐性广告。"""
print("\n--- Prompt 预览 ---")
print(prompt)


# ============================================================
# 3. 列表与字典操作
# ============================================================
# Java:  for (String s : list) { ... }
# Python: for s in list: ...

texts = [
    {"content": "这款面膜太好用了", "platform": "小红书"},
    {"content": "今天天气真好", "platform": "微博"},
    {"content": "限时优惠，赶紧下单", "platform": "抖音"},
]

# 遍历列表
for item in texts:
    # 直接拿到元素，不需要 texts[i]
    print(f"平台：{item['platform']}，内容：{item['content']}")

# 带索引的遍历
for i, item in enumerate(texts):
    print(f"第 {i+1} 条：{item['content']}")

# 列表推导式 — Python 特色语法，一行搞定过滤/转换
# 比 Java 的 stream().filter().collect() 更简洁
ad_texts = [t for t in texts if "广告" in t["content"] or "优惠" in t["content"]]
print(f"\n筛选出含广告关键词的：{len(ad_texts)} 条")


# ============================================================
# 4. 函数定义
# ============================================================
# Java:
#   public boolean checkIsAd(String text) {
#       return text.contains("推荐");
#   }
# Python:

def check_is_ad(text: str) -> bool:
    """
    简单的关键词检测（后面会被 LLM 取代）。
    text: str 是类型提示（可选的，不强制校验）
    -> bool 表示返回布尔值
    """
    ad_keywords = ["推荐", "好用", "购买", "限时", "优惠", "链接"]
    for kw in ad_keywords:
        if kw in text:
            return True
    return False

# 调用
for t in test_texts:
    print(f"「{t}」→ {'广告' if check_is_ad(t) else '非广告'}")

# 带默认参数的函数
def detect_ad(text: str, prompt_mode: str = "full") -> dict:
    """
    prompt_mode 有默认值 "full"，不传就用默认值。
    类比 Java 的方法重载。
    """
    return {"text": text, "mode": prompt_mode, "result": "待实现"}

r1 = detect_ad("测试文本")              # 不传 mode，用默认 "full"
r2 = detect_ad("测试文本", "simple")    # 传 mode
print(r1, r2)


# ============================================================
# 5. 文件读写
# ============================================================
import json
import os

# 写 JSON — 项目里用于保存知识库、测试结果
output_data = {
    "results": [
        {"text": "面霜推荐", "is_ad": True},
        {"text": "天气真好", "is_ad": False},
    ],
    "total": 2
}

# with 语句自动关闭文件（类比 Java 的 try-with-resources）
with open("test_output.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)
    # ensure_ascii=False → 中文正常显示，不转义成 \uXXXX
    # indent=2 → 格式化缩进，可读性好

print("[OK] 已写入 test_output.json")

# 读 JSON
with open("test_output.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)         # json.load() 从文件读
print(f"读回数据：共 {loaded['total']} 条结果")

# 检查文件是否存在（避免 FileNotFoundException）
if os.path.exists("test_output.json"):
    print("文件存在")
else:
    print("文件不存在")


# ============================================================
# 6. 导入模块
# ============================================================
# Java:  import java.util.List;
# Python 三种导入方式：

# 方式 1：导入整个模块
import json
data = json.loads('{"key": "value"}')     # 需要写 json. 前缀

# 方式 2：从模块导入特定函数（项目中最常用）
from json import loads, dumps
data = loads('{"key": "value"}')          # 不需要写 json. 前缀

# 方式 3：导入并取别名
import numpy as np
# arr = np.array([1, 2, 3])               # 用 np 代替 numpy


# ============================================================
# 7. 错误处理
# ============================================================
# Java:  try { ... } catch (Exception e) { ... }
# Python: try / except / finally，结构和 Java 几乎一样

# 场景：LLM 输出的 JSON 可能不合法（项目核心风险）
raw_llm_output = '{"is_ad": true, "risk_level": "中"'  # 故意少了结尾 }

try:
    result = json.loads(raw_llm_output)
    print("解析成功")
except json.JSONDecodeError as e:     # as e 类比 catch (Exception e)
    print(f"JSON 解析失败：{e}")
    print("触发容错策略...")
    result = {"is_ad": None, "parse_error": True}
finally:
    print(f"最终结果：{result}")       # finally 和 Java 一样，无论如何都执行


# ============================================================
# 8. 看懂报错
# ============================================================
# Python 的报错信息从下往上读：最后一行是错误类型，往上是调用链。

# 常见错误速查：
# ┌──────────────────────┬────────────────────────────────┐
# │ 错误类型              │ 原因                           │
# ├──────────────────────┼────────────────────────────────┤
# │ NameError            │ 变量/函数名写错了               │
# │ TypeError            │ 类型不对（如把 int 当 str 用）   │
# │ KeyError             │ dict 里 key 不存在              │
# │ IndexError           │ list 索引越界                  │
# │ IndentationError     │ 缩进不对（Python 用缩进代替 {}） │
# │ ModuleNotFoundError  │ 没装包 / import 路径错了        │
# │ JSONDecodeError      │ JSON 格式不合法                 │
# │ AttributeError       │ 对象没有这个属性/方法            │
# └──────────────────────┴────────────────────────────────┘

# 示例：故意写错，看看报什么错
# print(undefined_var)    # NameError
# result["not_exist"]     # KeyError

print("\n" + "=" * 50)
print("[OK] Phase 1 基础语法全部覆盖完毕！")
print("=" * 50)
