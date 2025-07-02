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
    # results = collection.query(
    #     query_texts=[product_description],
    #     n_results=30  # get top 30 most relevant chunks
    # )
    results = collection.get()
    retrieved_docs = results['documents']
    retrieved_ids = results['ids']
    retrieved_metadatas = results['metadatas']

    # Flatten the list of lists into a single list of strings
    flat_retrieved_docs = [doc for sublist in retrieved_docs for doc in sublist]
    flat_retrieved_ids = [id for sublist in retrieved_ids for id in sublist]
    flat_retrieved_metadatas = [md for sublist in retrieved_metadatas for md in sublist]

    if not flat_retrieved_docs:
        print("No relevant HTSUS codes found.")
        return
    
    print("Successfully retrieved relevant HTSUS codes.")

    with open("combined_output.txt", "w", encoding="utf-8") as f:
        f.write("IDs:\n")
        for id_ in flat_retrieved_ids:
            f.write(f"{id_}")

        f.write("\nDocuments:\n")
        for doc in flat_retrieved_docs:
            f.write(f"{doc}")

        f.write("\nMetadata:\n")
        for meta in flat_retrieved_metadatas:
            f.write(f"{meta}")


    # combined_entries = []
    # for i in range(len(flat_retrieved_docs)):
    #     entry = (
    #         f"ID: {flat_retrieved_ids[i]}\n"
    #         f"Document: {flat_retrieved_docs[i]}\n"
    #         f"Metadata: {flat_retrieved_metadatas[i]}"
    #     )
    #     combined_entries.append(entry)

    # with open("combined_output.txt", "w", encoding="utf-8") as f:
    #     for entry in combined_entries:
    #         f.write(entry + "\n")  

    return 
    output_text = "\n---\n".join(combined_entries)

    full_prompt = (
        f"Product description:\n{product_description}\n\n"
        f"Few-shot examples:\n{few_shot_txt}\n\n"
        f"Instructions:\n{prompt_txt}\n\n"
        "HTSUS data to choose from:\n"
        + output_text
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
    # classify_htsus("Men 100 cotton denim jeans") # WRONG! it outputted 6203.42.4011 & 16.6%; WRONG SHUD BE 6203.42.07.11
    # classify_htsus("cotton plushie") # works! it outputted 9503.00.0073 & 0%
    # classify_htsus("Smartphone with 128GB storage, OLED screen, and 5G support") # works! it outputted 8517.13.0000 & 0%
    # classify_htsus("Leather handbag") # works! it outputted the 3 possibilities shown in few_shot.txt
    classify_htsus("Porcelain plate") # WRONG! it outputted 6911.10.0000 and 2.9% instead of 6911.10.5200 and 25%
    # classify_htsus("Cordless drill") # WRONG! it outputted 8467.21.00.10 but 3.7% instead of 1.7%
    