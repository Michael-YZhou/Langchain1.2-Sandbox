from pathlib import Path

from langchain_community.document_loaders import JSONLoader

repo_root = Path(__file__).resolve().parent.parent


# Copy the fields that aren't the page content into each Document's metadata
def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["sender"] = record.get("sender")
    metadata["title"] = record.get("title")
    metadata["timestamp"] = record.get("timestamp")
    return metadata


loader = JSONLoader(
    file_path=repo_root / "asset/load/messages.json",
    jq_schema=".messages[]",
    text_content=True,
    content_key="content",
    metadata_func=metadata_func
)

docs = loader.load()

print(len(docs))
for doc in docs:
    print(doc.metadata)
    print(doc.page_content)
    print()
