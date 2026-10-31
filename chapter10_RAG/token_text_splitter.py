from pathlib import Path

import tiktoken
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import TokenTextSplitter

repo_root = Path(__file__).resolve().parent.parent

loader = TextLoader(
    file_path=repo_root / "asset/load/text.txt",
    encoding="utf-8"
)

docs = loader.load()

# split the text by token count, using OpenAI's cl100k_base encoding
splitter = TokenTextSplitter(
    encoding_name="cl100k_base",
    chunk_size=100,         # tokens, not characters
    chunk_overlap=10,
    # no add_start_index: it treats chunk_overlap as characters, so with a
    # token overlap it can't find every other chunk and sets start_index=-1
)

chunks = splitter.split_documents(docs)

encoding = tiktoken.get_encoding("cl100k_base")
print(f"{len(docs)} document ({len(encoding.encode(docs[0].page_content))} tokens) -> {len(chunks)} chunks")
for i, chunk in enumerate(chunks):
    tokens = len(encoding.encode(chunk.page_content))
    print(f"[{i}] ({tokens} tokens, {len(chunk.page_content)} chars) {chunk.page_content!r}")
