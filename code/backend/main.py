"""
FastAPI 后端 —— 把 RAG Pipeline 封装成 RESTful API
====================================================
类比 JavaWeb 的 Controller 层。

启动：
    cd code/backend
    uvicorn main:app --reload --port 8000

启动后访问 http://localhost:8000/docs 查看 Swagger 自动生成的接口文档。
"""
import os
import sys

# 把 code/ 目录加入 sys.path，以便 import core 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import AdRequest, AdResponse
from core.rag_pipeline import RAGPipeline

app = FastAPI(title="隐性广告识别 API", version="1.0.0")

# CORS（允许 Streamlit 前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局单例：启动时加载一次模型，后续请求复用（避免每次请求都加载）
print("正在初始化 RAG Pipeline（加载模型，约 8 秒）...")
pipeline = RAGPipeline()


@app.get("/")
def root():
    """健康检查"""
    return {"message": "隐性广告识别 API 运行中", "docs": "/docs"}


@app.post("/detect", response_model=AdResponse)
def detect_advertisement(request: AdRequest):
    """检测文本是否包含隐性广告"""
    result = pipeline.detect(request.text, prompt_mode=request.mode)
    meta = result.pop("_meta", {})

    return AdResponse(
        # 核心判定结果
        is_ad=result.get("is_ad"),
        ad_type=result.get("ad_type"),
        risk_level=result.get("risk_level", "unknown"),
        violation_type=result.get("violation_type", []),
        confidence=result.get("confidence"),
        reasoning=result.get("reasoning", ""),
        legal_basis=result.get("legal_basis", []),
        similar_cases=result.get("similar_cases", []),
        # 附加信息
        retrieved_laws=[law[:100] for law in meta.get("retrieved_laws", [])],
        retrieved_cases=[case[:100] for case in meta.get("retrieved_cases", [])],
        matched_brands=meta.get("matched_brands", []),
        tokens_used=meta.get("prompt_tokens", 0) + meta.get("completion_tokens", 0),
    )
