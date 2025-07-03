import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Get the openai url and key
url = os.getenv("OPENAI_URL")
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Upload the file for RAG
with open("data/htsus_flattened.csv", "rb") as f:
    file = client.files.create(
        file=f,
        purpose="assistants"  # For Assistants API and RAG
    )

print("Uploaded file ID:", file.id)
