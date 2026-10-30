from pathlib import Path

from langchain_community.document_loaders import TextLoader

repo_root = Path(__file__).resolve().parent.parent

loader = TextLoader(
    file_path=repo_root / "asset/load/text.txt",
    encoding="utf-8"
)

docs = loader.load()

print(type(docs[0]))
print(docs[0].metadata)
print(docs[0].page_content)
