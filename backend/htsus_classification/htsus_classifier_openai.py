# htsus_classifier_openai.py
import os
import os
from dotenv import load_dotenv
import requests
import chromadb

# Load environment variables from .env file
load_dotenv()

# Set up the chromadb environment
CHROMA_PATH = r"chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="htsus_codes") # My HTSUS collection

# Get the openai url and key
url = os.getenv("OPENAI_URL")
api_key = os.getenv("OPENAI_API_KEY")

# Few-shot prompt template for HTSUS classification along with the CSV file path
prompt_file = "prompt_openai.txt"
few_shot_file = "few_shot.txt"

# Uses Gemini Flash to get the HTSUS code and duty tax for a given product description
def classify_htsus(product_description):
    # Step 1: Load prompt template
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_txt = f.read()
    print("Successfully loaded prompt.")

    # Step 2: Load few-shot examples
    with open(few_shot_file, "r", encoding="utf-8") as f:
        few_shot_txt = f.read()
    print("Successfully loaded few shot examples.")

    # Step 3: Retrieve relevant HTSUS codes from ChromaDB
    results = collection.query(
        query_texts=[product_description],
        n_results=10  # get top 10 most relevant chunks
    )
    retrieved_docs = results['documents']

    # Flatten the list of lists into a single list of strings
    flat_retrieved_docs = [doc for sublist in retrieved_docs for doc in sublist]

    if not flat_retrieved_docs:
        print("No relevant HTSUS codes found.")
        return
    
    print("Successfully retrieved relevant HTSUS codes.")
    print("First 3 retrieved HTSUS code entries:")
    for i, doc in enumerate(flat_retrieved_docs[:3]):
        print(f"{i+1}: {doc}\n")

    
    full_prompt = (
        f"Product description:\n{product_description}\n\n"
        f"Few-shot examples:\n{few_shot_txt}\n\n"
        f"Instructions:\n{prompt_txt}\n\n"
        "HTSUS data to choose from:\n"
        + "\n---\n".join(flat_retrieved_docs)
    )

    print("Full prompt constructed. Setting up request to OpenAI...")
    # Step 4: Generate response using OpenAI 
    headers = {
        "Authorization": f"Bearer {api_key}",  # Replace with your actual API key
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "text": full_prompt
    }

    print("Sent request to OpenAI...")
    response = requests.post(url, headers=headers, json=data)

    # Handle response
    if response.status_code == 200:
        response_json = response.json()  # Parse the JSON response
        chatbot_output = response_json.get("text", "")  # Get the "text" field safely
        print("Simplified result:", chatbot_output)
        print("Response result:", response_json)
    else:
        print("Error:", response.status_code, response.text)

    # Step 5: Post-process the response to cross check if the HTSUS code exists in htsus_flattened.csv?

# Example usage
if __name__ == "__main__":
    classify_htsus("Men 100 cotton denim jeans") # WRONG! it outputted 6203.42.4011 & 16.6%; WRONG SHUD BE 6203.42.07.11
    # classify_htsus("cotton plushie") # works! it outputted 9503.00.0073 & 0%
    # classify_htsus("Smartphone with 128GB storage, OLED screen, and 5G support") # works! it outputted 8517.13.0000 & 0%
    # classify_htsus("Leather handbag") # works! it outputted the 3 possibilities shown in few_shot.txt
    # classify_htsus("Porcelain plate") # WRONG! it outputted 6911.10.0000 and 2.9% instead of 6911.10.5200 and 25%
    # classify_htsus("Cordless drill") # WRONG! it outputted 8467.21.00.10 but 3.7% instead of 1.7%
    