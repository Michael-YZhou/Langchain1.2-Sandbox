from langchain_community.document_loaders import PyPDFLoader

# Fill in the PDF's path, e.g. Path(__file__).resolve().parent.parent / "asset/load/sample.pdf"
loader = PyPDFLoader(
    file_path="",
    extraction_mode="plain"
)

docs = loader.load()

print(len(docs))
for doc in docs:
    print(doc.metadata)
    print(doc.page_content)
    print()
