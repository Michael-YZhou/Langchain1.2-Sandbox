from pymilvus import MilvusClient
from common.llm import get_embedding_model

client = MilvusClient("http://localhost:19530")

# 查看数据库
existed_db = client.list_databases()

for db in existed_db:
    print(db)

# 新建数据库
dbname = "rag_demo"

if dbname not in existed_db:
    client.create_database(dbname)

# 切换数据库
client.use_database(dbname)

# 查看collections
collections = client.list_collections()

for collection in collections:
    print(collection)

# 创建collection
coll_name = "docs"
if coll_name not in collections:
    client.create_collection(
        collection_name=coll_name,
        dimension=1024,
        metric_type="COSINE"
    )

# 准备向量化demo数据
texts = [
    "Milvus 是一个开源的向量数据库，用于存储和检索嵌入向量。",
    "LangChain 是一个用于构建大语言模型应用的开发框架。",
    "熊猫是中国的国宝，主要以竹子为食。"
]

# 数据向量化
embeddings_model = get_embedding_model()

vectors = embeddings_model.embed_documents(texts)

print(len(vectors))
print(len(vectors[0]))

# 保存向量数据
# 封装可保存的数据格式
data = [{
    "id": i,
    "vector": vectors[i],
    "text": texts[i],
    "source": "rag_demo"
} for i in range(len(vectors))]

# 插入数据
insert_result = client.upsert(collection_name=coll_name, data=data)

print(insert_result)

# 手动落盘
client.flush(collection_name=coll_name)

# 查看collection统计信息
stats = client.get_collection_stats(collection_name=coll_name)

print(stats)

# 检索向量相似度
query = "什么是向量数据库"

# 查询文本也要用同一个嵌入模型向量化（查询用 embed_query）
query_vector = embeddings_model.embed_query(query)

# data 是查询向量列表，可一次查多个；limit 是返回的 top-k
search_results = client.search(
    collection_name=coll_name,
    data=[query_vector],
    limit=3,
    output_fields=["text", "source"],
)

# search_results[0] 是第一个查询向量的结果，按相似度从高到低排列
# COSINE 下 distance 是余弦相似度，越大越相似
print(f"\n查询：{query}")
for rank, hit in enumerate(search_results[0], start=1):
    print(f"{rank}. id={hit['id']} 相似度={hit['distance']:.4f} 文本={hit['entity']['text']}")
