# htsus_classifier_openai.py
import os
from dotenv import load_dotenv
import requests
import chromadb
import re

# Load environment variables from .env file
load_dotenv()

# Set up the chromadb environment
CHROMA_PATH = r"chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="htsus_codes") # My HTSUS collection

# Get the openai url and key
url = os.getenv("OPENAI_URL")
api_key = os.getenv("OPENAI_API_KEY")

with open("prompt_openai.txt", "r", encoding="utf-8") as f:
    prompt_txt = f.read()

with open("few_shot.txt", "r", encoding="utf-8") as f:
    few_shot_txt = f.read()

# Uses Gemini Flash to get the HTSUS code and duty tax for a given product description
def get_top_n_codes(product_description, product_chapter, query, n, irrelevant):
    # Get or create the collection for that chapter
    collection_name = f"htsus_chapter_{product_chapter}"
    chapter_collection = chroma_client.get_or_create_collection(name=collection_name)

    results = chapter_collection.query(
        query_texts=[product_description],
        n_results=n
    )

    documents = results.get('documents', [[]])[0]

    if not documents:
        print("No relevant HTSUS codes found.")
        return
    
    print(f"Retrieved {len(documents)} HTSUS codes.")

    with open("chapter_test.txt", "w", encoding="utf-8") as f:
        for i, doc in enumerate(documents, 1):
            f.write(f"{doc}\n\n")

    return documents

def process_top_n_codes(output_text, product_description):
    prompt_filter = "prompt_filter_irrelevant_htsus.txt"
    with open(prompt_filter, "r", encoding="utf-8") as f:
        prompt_filter_txt = f.read()

    # This function can be used to process the top 50 HTSUS codes if needed
    full_prompt = (
        f"HTSUS codes retrieved:\n{output_text}\n\n"
        f"Product Description:\n{product_description}\n\n"
        f"Instructions:\n{prompt_filter_txt}\n\n"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",  # Replace with your actual API key
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "text": full_prompt
    }

    print("Sent request to OpenAI to process top n codes...")
    response = requests.post(url, headers=headers, json=data)
    
    # Handle response
    if response.status_code == 200:
        response_json = response.json()  # Parse the JSON response
        chatbot_output = response_json.get("text", "")  # Get the "text" field safely
        chatbot_output = chatbot_output.strip()  # Clean up any leading/trailing whitespace

        # print("Chatbot Response in process top n:", chatbot_output, " and its length is ", len(chatbot_output))
        if not chatbot_output:
            print("No output from the chatbot. Exiting classification.")    
            return [], [], ""

        # Split into sections
        relevant_split = chatbot_output.split("Relevant Documents:")[1]
        
        if "Irrelevant Documents:" in relevant_split:
            relevant_text, rest = relevant_split.split("Irrelevant Documents:")
        else:
            relevant_text = relevant_split
            rest = ""

        if "Prompt Suggestion:" in rest:
            irrelevant_text, prompt_text = rest.split("Prompt Suggestion:")
        else:
            irrelevant_text = rest
            prompt_text = ""

        # Clean and split into entries
        relevant_entries = [line.strip() for line in relevant_text.strip().split("\n") if line.strip()]
        irrelevant_entries = [line.strip() for line in irrelevant_text.strip().split("\n") if line.strip()]
        prompt_suggestion = prompt_text.strip()

        return relevant_entries, irrelevant_entries, prompt_suggestion
    else:
        print("Error:", response.status_code, response.text)

def semantically_process_product_description(product_description):
    with open("prompt_semantics.txt", "r", encoding="utf-8") as f:
        prompt_semantics_txt = f.read()

    full_prompt = (
        f"Product description:\n{product_description}\n\n"
        f"Instruction:\n{prompt_semantics_txt}\n\n"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",  # Replace with your actual API key
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "text": full_prompt
    }

    response = requests.post(url, headers=headers, json=data)

    # Handle response
    if response.status_code == 200:
        response_json = response.json()  # Parse the JSON response
        chatbot_output = response_json.get("text", "")  # Get the "text" field safely
        # print("Simplified result:", chatbot_output)
        # print("Response result:", response_json)

        with open("semantics.txt", "w", encoding="utf-8") as f:          
            f.write(str(chatbot_output))

        return chatbot_output
    else:
        print("Error:", response.status_code, response.text)
        return ""
    
def get_chapter_number(product_description):
    prompt_chapter_file = "prompt_get_chapter.txt"
    with open(prompt_chapter_file, "r", encoding="utf-8") as f:
        prompt_chapter_txt = f.read()

    full_prompt = (
        f"Product description:\n{product_description}\n\n"
        f"Instruction:\n{prompt_chapter_txt}\n\n"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",  # Replace with your actual API key
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "text": full_prompt
    }

    response = requests.post(url, headers=headers, json=data)

    # Handle response
    if response.status_code == 200:
        response_json = response.json()  # Parse the JSON response
        chatbot_output = response_json.get("text", "")  # Get the "text" field safely

        with open("chapter.txt", "w", encoding="utf-8") as f:          
            f.write(str(chatbot_output))

        return chatbot_output
    else:
        print("Error:", response.status_code, response.text)
        return ""
    

def extract_chapter_number(text):
    match = re.search(r'\b(\d{1,2})\b', text)
    return match.group(1) if match else None
    
def classify_htsus(product_description):
    # Step -1: Get the HTSUS chapter number based on the product description
    # Step 0: Process product_description:
    product_context = semantically_process_product_description(product_description)

    if not product_context: 
        print("Failed to process product description semantics. Exiting classification.")
        return
    
    product_chapter = get_chapter_number(product_context)
    if not product_chapter:
        print("Failed to retrieve HTSUS chapter number. Exiting classification.")
        return
    
    product_chapter = extract_chapter_number(product_chapter)
    
    print(f"HTSUS Chapter Number: {product_chapter}")

    output_text_1 = get_top_n_codes(product_context, product_chapter, "", 75, "")

    if not output_text_1:
        print("No HTSUS codes retrieved. Exiting classification.")
        return

    # Output the top 100 HTSUS codes to a file
    with open("outputtext1.txt", "w", encoding="utf-8") as f:
        f.write(str(output_text_1))
    print("Successfully retrieved HTSUS codes based on the product description.")

    # Step 2: Process the top 100 HTSUS codes to filter out irrelevant ones
    # and suggest a prompt for future queries
    relevant, irrelevant, added_prompt = process_top_n_codes(output_text_1, product_description)

    if not relevant and not irrelevant and not added_prompt:
        print("No relevant or irrelevant HTSUS codes found. Exiting classification.")
        return 
    
    # Step 3: Get the top 100 HTSUS codes based on product description + prompt suggestion
    added_prompt_str = added_prompt.strip()
    added_query = f" as well as additional instructions for a more accurate search: {added_prompt_str}",
    output_text_2 = get_top_n_codes(product_description, product_chapter, added_query, 75, irrelevant)

    # Output the top 100 HTSUS codes based on the combined query to a file
    if not output_text_2:
        print("No additional HTSUS codes retrieved based on the prompt suggestion. Exiting classification.")
        return
    with open("outputtext2.txt", "w", encoding="utf-8") as f:
        f.write(str(output_text_2))
    print("Successfully retrieved additional HTSUS codes based on the prompt suggestion.")

    relevant2, irrelevant2, added_prompt2 = process_top_n_codes(output_text_2, product_description)
    

    all_relevant = relevant + relevant2  # Combine the two lists of relevant HTSUS codes
    with open("relevant.txt", "w", encoding="utf-8") as f:
        for code in all_relevant:
            f.write(code + "\n")

    full_prompt = (
        f"Product description:\n{product_description}\n\n"
        f"Few-shot examples:\n{few_shot_txt}\n\n"
        f"Instructions:\n{prompt_txt}\n\n"
        "HTSUS data to choose from:\n"
        + "\n".join(all_relevant) 
    )

    # Step 4: Generate response using OpenAI 
    headers = {
        "Authorization": f"Bearer {api_key}",  # Replace with your actual API key
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "text": full_prompt
    }

    print("Sent request to OpenAI to retrieve final codes and duty tax...")
    response = requests.post(url, headers=headers, json=data)

    # Handle response
    if response.status_code == 200:
        response_json = response.json()  # Parse the JSON response
        chatbot_output = response_json.get("text", "")  # Get the "text" field safely
        print("Simplified result:", chatbot_output)
        # print("Response result:", response_json)

        with open("final_output.txt", "w", encoding="utf-8") as f:          
            f.write(str(chatbot_output))
    else:
        print("Error:", response.status_code, response.text)

    # Step 5: Post-process the response to cross check if the HTSUS code exists in htsus_flattened.csv?

def get_all_chapter_collections():
    collections = chroma_client.list_collections()
    htsus_collections = [col for col in collections if col.name.startswith("htsus_chapter_")]
    all_documents = []

    for col_meta in htsus_collections:
        chapter_name = col_meta.name
        collection = chroma_client.get_or_create_collection(name=chapter_name)
        all_data = collection.get()

        # Flatten document list
        docs = all_data.get("documents", [])
        flat_docs = [doc for sublist in docs for doc in sublist]
        all_documents.extend(flat_docs)

    with open("all_htsus_documents.txt", "w", encoding="utf-8") as f:
        for doc in enumerate(all_documents, 1):
            f.write(f"{doc}")

# Example usage
if __name__ == "__main__":
    # classify_htsus("Men 100 cotton denim jeans") # WRONG! it outputted 6203.42.4011 & 16.6%; WRONG SHUD BE 6203.42.07.11
    # classify_htsus("Leather handbag") # works! it outputted the 3 possibilities shown in few_shot.txt
    
    # classify_htsus("Porcelain plate") # WORKS it out putted 6911.10.80.00 w/ correct duty tax 20.80% and rate 2 of 75%
    # classify_htsus("Smartphone with 128GB storage, OLED screen, and 5G support") # WORKS! it outputted 8517.13.0000 & 0%
    # classify_htsus("Cordless drill") # WRONG outputted 8467.21.00.30 and 4.70% (shud be 1.7)
    # classify_htsus("cotton plushie") # not working yet, but shud output 9503.00.0073 & 0%
    # classify_htsus("Polyester camping tent, 4-person capacity, waterproof")
    

    # get_top_n_codes("cotton plushie", "95", "", 75, "")
    # get_all_chapter_collections

    classify_htsus("cotton plushie") # good enof but shud output 9503.00.0073 or 9503.00.00.71 & 0% but 6% bc my db has 6%
    # classify_htsus("Frozen Alaskan Salmon fillets, 1kg pack") # good enof 
    # classify_htsus("Polyester camping tent, 4-person capacity, waterproof") # good 
    # classify_htsus("grand piano") # good 
    # classify_htsus("Electric bicycle with 500W motor and 48V battery") # good enof
    # classify_htsus("LED TV") # good enof