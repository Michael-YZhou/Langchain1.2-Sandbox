from pathlib import Path

from langchain_community.document_loaders import CSVLoader

repo_root = Path(__file__).resolve().parent.parent

loader = CSVLoader(
    file_path=repo_root / "asset/load/users.csv",
    encoding="utf-8"
)

docs = loader.load()

print(len(docs))
for doc in docs:
    print(doc.metadata)
    print(doc.page_content)
    print()
