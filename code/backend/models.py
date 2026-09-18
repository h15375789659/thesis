"""
Pydantic 数据模型 —— 定义 API 的请求和响应格式
================================================
类比 Java 的 Bean / DTO。
"""
from typing import Optional
from pydantic import BaseModel


class AdRequest(BaseModel):
    """检测请求"""
    text: str                      # 待检测文本
    mode: str = "full"             # 推理模式：simple/rag_only/cot/role/pe/fewshot/full/full_templates


class AdResponse(BaseModel):
    """检测响应"""
    # === 核心判定结果 ===
    is_ad: Optional[bool] = None          # 是否隐性广告
    ad_type: Optional[str] = None         # 广告伪装类型
    risk_level: str = "unknown"           # 风险等级（高/中/低/无）
    violation_type: list = []             # 违规类型
    confidence: Optional[float] = None    # 置信度
    reasoning: str = ""                   # 推理摘要
    legal_basis: list = []                # 法律依据
    similar_cases: list = []              # 相似案例 ID

    # === 附加信息（供调试和分析） ===
    retrieved_laws: list = []             # 检索到的法规
    retrieved_cases: list = []            # 检索到的案例
    matched_brands: list = []             # 识别到的品牌
    tokens_used: int = 0                  # token 用量
