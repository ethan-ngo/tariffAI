from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import csv
import os

# setting the environment

# Get the folder this script lives in (process/)
BASE_DIR = os.path.dirname(__file__)

# Go up one level (to project/) and into data/
DATA_PATH = os.path.abspath(os.path.join(BASE_DIR, os.pardir, "data", "htsus_flattened_with_chapters.csv"))

# initialize ChromaDB client
CHROMA_PATH = os.path.abspath(os.path.join(BASE_DIR, os.pardir, "chroma_db"))
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# db is stored as a dict with the keys being the chapter numbers
# and values being the codes under the respective chapter
collections_by_chapter = {} # Dictionary to track chapter collections

print("Finish env setup.")

BATCH_SIZE = 5000
batches = {}

# read in the CSV file in the data directory
# upload the CSV file to the directory in batches of BATCH_SIZE and by chapter
with open(DATA_PATH, newline='', encoding="utf-8-sig") as csvfile:
    reader = csv.DictReader(csvfile)

    for i, row in enumerate(reader):
        chapter = row.get('HTS_Chapter', 'unknown').zfill(2)

        if chapter not in collections_by_chapter:
            collections_by_chapter[chapter] = chroma_client.get_or_create_collection(name=f"htsus_chapter_{chapter}")

        if chapter not in batches:
            batches[chapter] = {'docs': [], 'ids': []}

        # Combine all fields into a single string for the document content
        doc_text = " | ".join([f"{k}: {v}" for k, v in row.items()])
        
        # Create unique ID per row
        doc_id = row.get('HTS_Number', f"HTSUS_{i}")  # fallback if missing
        
        batches[chapter]['docs'].append(doc_text)
        batches[chapter]['ids'].append(doc_id)

        if len(batches[chapter]['docs']) == BATCH_SIZE:
            print(f"Upserting batch {i // BATCH_SIZE + 1}...")

            collections_by_chapter[chapter].upsert(
                documents=batches[chapter]['docs'],
                ids=batches[chapter]['ids']
            )

            batches[chapter]['docs'] = []
            batches[chapter]['ids'] = []

    # After loop, flush remaining docs per chapter
    for chapter, batch in batches.items():
        if batch['docs']:
            collections_by_chapter[chapter].upsert(
                documents=batch['docs'],
                ids=batch['ids']
            )
