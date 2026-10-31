from pathlib import Path

from langchain_community.document_loaders import CSVLoader

from common.llm import init_embedding_model

repo_root = Path(__file__).resolve().parent.parent

embedding_model = init_embedding_model()

print("############ Embed text ###############\n\n")

text = "你好，很高兴认识你！"

embedded_text = embedding_model.embed_query(text)

print(len(embedded_text))
print(embedded_text[:5])

print("############ Embedding documents ###############\n\n")

loader = CSVLoader(
    file_path=repo_root / "asset/load/users.csv",
    encoding="utf-8",
)

documents = loader.load_and_split()

texts = [doc.page_content for doc in documents]

embedded_docs = embedding_model.embed_documents(texts)

for i in range(len(embedded_docs)):
    print(f"{texts[i], embedded_docs[i][:3]}", end="\n\n")
