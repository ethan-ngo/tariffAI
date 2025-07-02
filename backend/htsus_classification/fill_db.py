from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import csv

# setting the environment
DATA_PATH = r"data/htsus_flattened_shortened.csv"
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

print("Starting to prepare documents...")

# Read CSV rows and prepare documents
with open(DATA_PATH, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for i, row in enumerate(reader):
        # Combine all fields into a single string for the document content
        doc_text = " | ".join([f"{k}: {v}" for k, v in row.items()])
        documents.append(doc_text)
        
        # Store the entire row as metadata (optional, but useful)
        metadata.append(row)
        
        # Create unique ID per row
        ids.append(f"HTSUS_{i}")

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
