"""
Phase 3 前置：下载 BGE-M3 模型
================================
BGE-M3 模型约 2GB，从 HuggingFace 下载。

默认走国内镜像 hf-mirror.com（无需梯子，速度快）。
如果想用官方源（需要梯子），把 USE_MIRROR 改成 False。

下载完成后，模型会缓存在本地，后续离线可用。
"""
import os
from huggingface_hub import snapshot_download

# ===== 配置 =====
MODEL_NAME = "BAAI/bge-m3"
USE_MIRROR = True  # True=用国内镜像（推荐），False=用官方源（需梯子）

# 镜像地址
if USE_MIRROR:
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    print("使用镜像：https://hf-mirror.com（国内直连）")
else:
    os.environ.pop("HF_ENDPOINT", None)
    print("使用官方源：https://huggingface.co（需要梯子）")

print(f"开始下载模型：{MODEL_NAME}")
print("模型约 2GB，请耐心等待（首次下载 5-15 分钟）...\n")

# snapshot_download 会自动下载模型的所有必要文件
local_path = snapshot_download(
    repo_id=MODEL_NAME,
    local_dir=None,  # None = 下载到 HuggingFace 默认缓存目录
)

print("\n" + "=" * 50)
print("下载完成！")
print(f"模型本地路径：{local_path}")
print("=" * 50)
print("\n后续 ChromaDB 加载时直接用 model_name='BAAI/bge-m3' 即可。")
