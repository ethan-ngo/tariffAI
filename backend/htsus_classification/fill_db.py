from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb

# setting the environment
DATA_PATH = r"data/htsus_flattened.csv"
CHROMA_PATH = r"chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="htsus_codes")

print("Finish env setup.")

# loading the document 
loader = CSVLoader(file_path=DATA_PATH, encoding="utf-8-sig")
raw_documents = loader.load()

# splitting the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

chunks = text_splitter.split_documents(raw_documents)

print("Successfully split documents into chunks.")

# preparing to be added in chromadb
documents = []
metadata = []
ids = []
i = 0

print("Starting to prepare documents...")

for i, chunk in enumerate(chunks):
    # Optional: parse structured fields (if raw_documents[i] has metadata)
    content = chunk.page_content
    documents.append(content)
    ids.append(f"HTSUS_{i}")
    metadata.append({
        "source": chunk.metadata.get("source", ""),
        "row": i
    })

print(f"Total chunks created: {len(documents)}")
print("Adding to chromadb now...")

# adding to chromadb
BATCH_SIZE = 5000  # Safe value below ChromaDB's limit (5461)

for i in range(0, len(documents), BATCH_SIZE):
    batch_docs = documents[i:i + BATCH_SIZE]
    batch_ids = ids[i:i + BATCH_SIZE]
    batch_metadata = metadata[i:i + BATCH_SIZE]

    print(f"Upserting batch {i // BATCH_SIZE + 1}...")

    collection.upsert(
        documents=batch_docs,
        metadatas=batch_metadata,
        ids=batch_ids
    )
