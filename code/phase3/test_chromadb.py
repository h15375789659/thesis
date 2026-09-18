"""
Phase 3-B：ChromaDB 增删改查 + 语义检索
========================================
目标：
1. 把 3 条法规存入 ChromaDB
2. 用一句「关键词完全不重叠」的话去查询
3. 亲眼看到它命中语义相关的法规（而不是关键词匹配）
"""
import os

# 离线模式：模型已下载到本地，禁止联网检查
os.environ["HF_HUB_OFFLINE"] = "1"

import chromadb
from chromadb.utils import embedding_functions

print("加载 BGE-M3 模型...\n")
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-m3"
)

# 1. 创建 ChromaDB 客户端（持久化到本地目录）
client = chromadb.PersistentClient(path="./phase3_test_db")

# 2. 创建一个 Collection（类似 MySQL 的 Table）
# 注意：ChromaDB 1.x 要求名字以字母开头，3-512 字符
collection = client.get_or_create_collection(
    name="ad_laws_test",
    embedding_function=embed_fn
)

# 3. 插入数据（相当于 SQL INSERT）
# 只在 collection 为空时插入，避免重复运行时报错
if collection.count() == 0:
    print("插入测试数据...")
    collection.add(
        documents=[
            "广告应当具有可识别性，能够使消费者辨明其为广告。",
            "大众传播媒介不得以新闻报道形式变相发布广告。",
            "通过大众传播媒介发布的广告应当显著标明'广告'。"
        ],
        metadatas=[
            {"source": "广告法第十四条", "type": "regulation"},
            {"source": "广告法第十四条", "type": "regulation"},
            {"source": "广告法第十四条", "type": "regulation"}
        ],
        ids=["law_001", "law_002", "law_003"]
    )
    print(f"[OK] 插入完成，共 {collection.count()} 条\n")
else:
    print(f"数据已存在，共 {collection.count()} 条，跳过插入\n")

# 4. 语义检索（相当于 SQL SELECT ... WHERE 语义相似 ORDER BY 相似度 LIMIT 2）
query_text = "新闻里能不能偷偷插广告？"

print(f"查询文本：「{query_text}」")
print("检索最相似的 2 条结果：\n")

results = collection.query(
    query_texts=[query_text],
    n_results=2
)

# 打印检索结果
for i in range(len(results['ids'][0])):
    doc_id = results['ids'][0][i]
    doc = results['documents'][0][i]
    meta = results['metadatas'][0][i]
    distance = results['distances'][0][i]
    print(f"第 {i+1} 名 | 距离: {distance:.4f} | 来源: {meta['source']}")
    print(f"       | {doc}")
    print()

print("=" * 55)
print("关键观察：查询「新闻里能不能偷偷插广告？」")
print("命中的是「不得以新闻报道形式变相发布广告」")
print("两句话没有一个词重合，但语义高度相关 → 这就是向量检索的价值！")
