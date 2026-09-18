"""
Prompt 模板集合
===============
设计 7 套 Prompt，用于消融实验对比（A/B/C/D 四组 + 分解变体）。

- SIMPLE_PROMPT：裸 LLM 基线（A 组，无 RAG 无提示工程）
- RAG_ONLY_PROMPT：仅 RAG（B 组，有检索，无角色/思维链）
- COT_PROMPT：仅思维链（无 RAG 无角色）
- ROLE_PROMPT：仅角色扮演（无 RAG 无思维链）
- PE_PROMPT：仅提示工程（C 组，角色+思维链，无 RAG）
- FEWSHOT_PROMPT：Few-Shot（带标注示例，可选对比）
- FULL_PROMPT：完整版（D 组，RAG + 角色 + 思维链 + 多维判定）
"""

# ===== 完整版 Prompt（RAG + CoT + Role） =====
FULL_PROMPT = """# 角色
你是一位资深广告合规审查专家，精通《中华人民共和国广告法》《互联网广告管理办法》及相关法规，拥有 10 年以上广告审查经验。

# 参考依据
以下是从知识库中检索到的与待检测文本最相关的法规和案例，请严格依据这些依据进行判定：

## 相关法规
{retrieved_laws}

## 相似案例
{retrieved_cases}
{template_section}
{brand_section}
# 判定规则（多维度）
请从以下四个维度逐项判定：

**维度一：广告意图识别**
- 文本是否包含商业推广目的？
- 是否提及特定品牌、产品或服务名称？
- 是否包含购买引导信息（如链接、优惠、购买方式）？

**维度二：广告标识检查**
- 是否标注了"广告""合作""赞助""推广"等标识？
- 标识是否显著、清晰，足以让消费者识别？

**维度三：内容形式判定**
- 是否以新闻、测评、经验分享、知识介绍等形式伪装？
- 是否存在未披露的利益关联（如收费推广、品牌合作）？

**维度四：消费者误导风险评估**
- 内容是否包含虚假或夸大的信息？
- 是否可能使消费者对产品性能、效果等产生误解？

# 风险分级标准
请严格按以下标准确定 risk_level：
- 高：含虚假/夸大宣传、绝对化用语（如"最好""第一""一周瘦10斤"），或有明显欺诈误导意图
- 中：未标注广告 + 有明确商业推广意图，但内容基本属实
- 低：仅提及品牌/产品，无明确推广意图
- 无：纯内容分享，不涉及商业推广

# 思维链推理指令
请按以下步骤逐步推理，在每一步中清晰说明你的推理依据：

Step 1: 理解文本 —— 表层含义与深层意图分别是什么？
Step 2: 逐维判定 —— 对上述四个维度逐一检查
Step 3: 法规对照 —— 将发现的违规点对照检索到的法规条款
Step 4: 案例类比 —— 参考检索到的相似案例进行类比判断
Step 5: 综合结论 —— 给出最终判定与风险等级

# 待检测文本
{input_text}

# 输出格式
你必须只输出一个合法的 JSON 对象，不要包含任何 markdown 标记、解释文字或额外换行：
{{"is_ad": true或false, "ad_type": "种草营销/软文植入/测评伪装/经验分享伪装/品牌露出/其他/无", "violation_type": ["未标注广告标识", "虚假宣传"], "risk_level": "高/中/低/无", "confidence": 0.0-1.0, "reasoning": "推理过程摘要", "legal_basis": ["引用的法规条款"], "similar_cases": ["引用的案例ID"]}}"""


# ===== 简单版 Prompt（消融实验裸 LLM 基线） =====
SIMPLE_PROMPT = """判断以下文本是否包含隐性广告。请以 JSON 格式输出：{{"is_ad": true或false, "risk_level": "高/中/低/无", "reasoning": "理由"}}

文本：{input_text}"""


# ===== 仅 RAG 版 Prompt（有检索，无角色/思维链） =====
RAG_ONLY_PROMPT = """根据以下法规和案例，判断文本是否包含隐性广告：

## 法规
{retrieved_laws}

## 案例
{retrieved_cases}

## 文本
{input_text}

请以 JSON 格式输出判定结果：{{"is_ad": true或false, "risk_level": "高/中/低/无", "reasoning": "理由"}}"""


# ===== 仅思维链版 Prompt（无 RAG、无角色，只有逐步推理指令） =====
COT_PROMPT = """请判断以下文本是否包含隐性广告。

请按以下步骤逐步推理，并在每一步说明你的推理依据：
Step 1: 理解文本 —— 表层含义与深层意图分别是什么？
Step 2: 意图判断 —— 是否存在商业推广目的？
Step 3: 形式判断 —— 是否以分享、测评、知识介绍等形式伪装？
Step 4: 综合结论 —— 给出最终判定与风险等级

文本：{input_text}

请以 JSON 格式输出判定结果：{{"is_ad": true或false, "risk_level": "高/中/低/无", "reasoning": "理由"}}"""


# ===== 仅角色扮演版 Prompt（无 RAG、无思维链，只有专家人设） =====
ROLE_PROMPT = """你是一位资深广告合规审查专家，精通《中华人民共和国广告法》《互联网广告管理办法》及相关法规，拥有 10 年以上广告审查经验。

请判断以下文本是否包含隐性广告。

文本：{input_text}

请以 JSON 格式输出判定结果：{{"is_ad": true或false, "risk_level": "高/中/低/无", "reasoning": "理由"}}"""


# ===== 仅提示工程版 Prompt（角色 + 思维链 + 多维规则，无 RAG） =====
# 与 FULL_PROMPT 的唯一区别：没有「参考依据」检索部分，用于分离 RAG 的贡献
PE_PROMPT = """# 角色
你是一位资深广告合规审查专家，精通《中华人民共和国广告法》《互联网广告管理办法》及相关法规，拥有 10 年以上广告审查经验。

# 判定规则（多维度）
请从以下四个维度逐项判定：
**维度一：广告意图识别** —— 是否包含商业推广目的？是否提及特定品牌/产品/服务？是否包含购买引导信息？
**维度二：广告标识检查** —— 是否标注了"广告""合作""赞助""推广"等标识？
**维度三：内容形式判定** —— 是否以新闻、测评、经验分享、知识介绍等形式伪装？是否存在未披露的利益关联？
**维度四：消费者误导风险评估** —— 内容是否包含虚假或夸大信息？是否可能使消费者误解？

# 风险分级标准
请严格按以下标准确定 risk_level：
- 高：含虚假/夸大宣传、绝对化用语（如"最好""第一""一周瘦10斤"），或有明显欺诈误导意图
- 中：未标注广告 + 有明确商业推广意图，但内容基本属实
- 低：仅提及品牌/产品，无明确推广意图
- 无：纯内容分享，不涉及商业推广

# 思维链推理指令
请按以下步骤逐步推理，在每一步中清晰说明你的推理依据：
Step 1: 理解文本 —— 表层含义与深层意图分别是什么？
Step 2: 逐维判定 —— 对上述四个维度逐一检查
Step 3: 综合结论 —— 给出最终判定与风险等级

# 待检测文本
{input_text}

# 输出格式
你必须只输出一个合法的 JSON 对象：{{"is_ad": true或false, "risk_level": "高/中/低/无", "reasoning": "理由"}}"""


# ===== Few-Shot 版 Prompt（给标注好的示例让 LLM 照着学） =====
FEWSHOT_PROMPT = """请判断文本是否包含隐性广告。

以下是 3 个标注好的示例，请参照示例的判定风格和输出格式：

示例 1：
文本："这款面膜太好用了，一周见效，赶紧下单！"
输出：{{"is_ad": true, "risk_level": "中", "reasoning": "种草营销，引导购买"}}

示例 2：
文本："今天天气真好，去公园走了走。"
输出：{{"is_ad": false, "risk_level": "无", "reasoning": "日常分享，无商业推广"}}

示例 3：
文本："根据《消费者权益保护法》，经营者应当保证商品安全。"
输出：{{"is_ad": false, "risk_level": "无", "reasoning": "法律条文引用，无商业推广意图"}}

现在请判断以下文本：
{input_text}

请严格按照示例的 JSON 格式输出：{{"is_ad": true或false, "risk_level": "高/中/低/无", "reasoning": "理由"}}"""


def build_prompt(text: str, laws: list, cases: list, templates: list = None, brands: list = None, mode: str = "full") -> str:
    """根据模式选择 Prompt 模板并填充检索结果

    mode 可选值：
    - simple        → A 组（裸 LLM）
    - rag_only      → B 组（仅 RAG，两库）
    - cot           → 仅思维链
    - role          → 仅角色
    - pe            → C 组（角色+思维链，无 RAG）
    - fewshot       → Few-Shot
    - full          → D 组（RAG 两库 + 提示工程）
    - full_templates → D 组变体（RAG 三库 + 提示工程，含话术模板）
    """
    if mode == "simple":
        return SIMPLE_PROMPT.format(input_text=text)
    elif mode == "rag_only":
        return RAG_ONLY_PROMPT.format(
            retrieved_laws="\n".join(laws),
            retrieved_cases="\n".join(cases),
            input_text=text
        )
    elif mode == "cot":
        return COT_PROMPT.format(input_text=text)
    elif mode == "role":
        return ROLE_PROMPT.format(input_text=text)
    elif mode == "pe":
        return PE_PROMPT.format(input_text=text)
    elif mode == "fewshot":
        return FEWSHOT_PROMPT.format(input_text=text)
    elif mode == "full_templates":
        template_section = "\n## 匹配话术模板\n" + "\n".join(templates) if templates else ""
        brand_section = "\n## 识别到的品牌\n" + "\n".join(brands) if brands else ""
        return FULL_PROMPT.format(
            retrieved_laws="\n".join(laws),
            retrieved_cases="\n".join(cases),
            template_section=template_section,
            brand_section=brand_section,
            input_text=text
        )
    else:  # full
        brand_section = "\n## 识别到的品牌\n" + "\n".join(brands) if brands else ""
        return FULL_PROMPT.format(
            retrieved_laws="\n".join(laws),
            retrieved_cases="\n".join(cases),
            template_section="",
            brand_section=brand_section,
            input_text=text
        )
