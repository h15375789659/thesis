"""
Phase 3-A：验证 BGE-M3 Embedding 模型能加载，理解「向量是什么」
================================================================
目标：
1. 加载 BGE-M3 模型（首次加载会较慢，约 30 秒 - 2 分钟）
2. 把文字转成向量，直观看到「向量是什么」
3. 理解「语义相近 → 向量距离近」这个核心原理
"""
import os
import time

# 离线模式：模型已下载到本地，禁止联网检查
# （否则 sentence-transformers 会连 huggingface.co 官网，被墙导致 SSL 错误）
os.environ["HF_HUB_OFFLINE"] = "1"

from chromadb.utils import embedding_functions

print("正在加载 BGE-M3 模型...")
print("（首次加载需要把约 1GB 权重读入内存，请耐心等待 30 秒 - 2 分钟）\n")

start = time.time()

# 加载模型
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-m3"
)

elapsed = time.time() - start
print(f"[OK] 模型加载成功！耗时 {elapsed:.1f} 秒\n")

# 测试三句话（text1 和 text3 都是法规，语义相近；text2 是广告，语义不同）
text1 = "广告应当具有可识别性，能够使消费者辨明其为广告。"
text2 = "这款面膜超级好用，一周见效，赶紧下单！"
text3 = "大众传播媒介不得以新闻报道形式变相发布广告。"

# 生成向量
vectors = embed_fn([text1, text2, text3])

print("=== 向量长什么样 ===\n")
print(f"text1 向量维度：{len(vectors[0])} 维（BGE-M3 是 1024 维）")
print(f"text1 前 8 个数字：{[round(v, 4) for v in vectors[0][:8]]}")
print(f"text2 前 8 个数字：{[round(v, 4) for v in vectors[1][:8]]}")
print(f"text3 前 8 个数字：{[round(v, 4) for v in vectors[2][:8]]}")
print("\n（注意看：text1 和 text3 的开头几个数字更接近，因为语义都是法规）")

# 计算向量之间的余弦相似度，直观验证「语义相近 → 距离近」
import numpy as np

def cosine_similarity(a, b):
    """计算两个向量的余弦相似度（越接近 1 越相似）"""
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

print("\n=== 相似度对比 ===\n")
sim_1_3 = cosine_similarity(vectors[0], vectors[2])   # 法规 vs 法规
sim_1_2 = cosine_similarity(vectors[0], vectors[1])   # 法规 vs 广告
sim_2_3 = cosine_similarity(vectors[1], vectors[2])   # 广告 vs 法规

print(f"text1(法规) 与 text3(法规) 相似度：{sim_1_3:.4f}  ← 应该最高")
print(f"text1(法规) 与 text2(广告) 相似度：{sim_1_2:.4f}")
print(f"text2(广告) 与 text3(法规) 相似度：{sim_2_3:.4f}")

print("\n结论：语义相近的句子，向量相似度更高。")
print("这就是 ChromaDB 语义检索的底层原理。")
