from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

repo_root = Path(__file__).resolve().parent.parent

loader = TextLoader(
    file_path=repo_root / "asset/load/text.txt",
    encoding="utf-8"
)

docs = loader.load()

# split the text
splitter = RecursiveCharacterTextSplitter(
    chunk_size=40,
    chunk_overlap=5,
    separators=["\n\n", "\n", ". ", " ", ""],  # try sentence ends before spaces
    keep_separator="end",                       # keep ". " on the end of the sentence
    add_start_index=True,                       # metadata gets start_index
    length_function=len,
)

chunks = splitter.split_documents(docs)

print(f"{len(docs)} document -> {len(chunks)} chunks")
for i, chunk in enumerate(chunks):
    print(f"[{i}] start={chunk.metadata['start_index']} ({len(chunk.page_content)} chars) {chunk.page_content!r}")
