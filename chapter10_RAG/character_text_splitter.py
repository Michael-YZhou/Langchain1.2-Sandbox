from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

repo_root = Path(__file__).resolve().parent.parent

loader = TextLoader(
    file_path=repo_root / "asset/load/text.txt",
    encoding="utf-8"
)

docs = loader.load()

# split the text on one separator only
splitter = CharacterTextSplitter(
    separator="\n\n",       # split on paragraphs, never anything smaller
    chunk_size=300,
    chunk_overlap=0,
    add_start_index=True,   # metadata gets start_index
)

chunks = splitter.split_documents(docs)

print(f"{len(docs)} document -> {len(chunks)} chunks")
for i, chunk in enumerate(chunks):
    print(f"[{i}] start={chunk.metadata['start_index']} ({len(chunk.page_content)} chars) {chunk.page_content!r}")
