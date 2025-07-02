from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb

# setting the environment

DATA_PATH = r"data/htsus_flattened.csv"
CHROMA_PATH = r"chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="htsus_codes")

# loading the document

# loader = CSVLoader(file_path=DATA_PATH)  
loader = CSVLoader(file_path=DATA_PATH, encoding="utf-8-sig")
raw_documents = loader.load()

# splitting the document

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

chunks = text_splitter.split_documents(raw_documents)

# preparing to be added in chromadb

documents = []
metadata = []
ids = []

i = 0

# for chunk in chunks:
#     documents.append(chunk.page_content)
#     ids.append("ID"+str(i))
#     metadata.append(chunk.metadata)

#     i += 1

for i, chunk in enumerate(chunks):
    # Optional: parse structured fields (if raw_documents[i] has metadata)
    content = chunk.page_content
    documents.append(content)
    ids.append(f"HTSUS_{i}")
    metadata.append({
        "source": chunk.metadata.get("source", ""),
        "row": i
    })


# adding to chromadb


collection.upsert(
    documents=documents,
    metadatas=metadata,
    ids=ids
)