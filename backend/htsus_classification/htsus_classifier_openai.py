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

with open(prompt_file, "r", encoding="utf-8") as f:
    prompt_txt = f.read()

with open(few_shot_file, "r", encoding="utf-8") as f:
    few_shot_txt = f.read()

# Uses Gemini Flash to get the HTSUS code and duty tax for a given product description
def get_top_n_codes(product_description, query, n, irrelevant):
    # Step 3: Retrieve relevant HTSUS codes from ChromaDB
    query_string = "\n".join([
        f"This is the product description: {product_description}",
        " ".join(query) if isinstance(query, tuple) else str(query),
        f"Do not include irrelevant HTSUS codes as follows: {irrelevant}"
    ])
    
    with open("query_string.txt", "w", encoding="utf-8") as f:
        f.write(query_string)

    results = collection.query(
        query_texts=[query_string],  # query is a tuple of (product description, additional instructions)
        n_results=n  # get top 30 most relevant chunks
    )

    # results = collection.get()
    retrieved_docs = results['documents']

    # Flatten the list of lists into a single list of strings
    flat_retrieved_docs = [doc for sublist in retrieved_docs for doc in sublist]

    if not flat_retrieved_docs:
        print("No relevant HTSUS codes found.")
        return
    
    print(f"Retrieved {len(flat_retrieved_docs)} HTSUS codes.")

    with open("output_docs.txt", "w", encoding="utf-8") as f:
        for i, doc in enumerate(flat_retrieved_docs):
            f.write(f"{i+1}. {doc}\n\n")

    output_text = "\n---\n".join(flat_retrieved_docs)

    return output_text

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

        # print("Simplified result:", response_json)

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
    prompt_semantics_file = "prompt_semantics.txt"
    full_prompt = (
        f"Product description:\n{product_description}\n\n"
        f"Instruction:\n{prompt_semantics_file}\n\n"
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
        print("Simplified result:", chatbot_output)
        # print("Response result:", response_json)

        with open("semantics.txt", "w", encoding="utf-8") as f:          
            f.write(str(chatbot_output))
    else:
        print("Error:", response.status_code, response.text)


def classify_htsus(product_description):
    # Step 0: Process product_description:
    # semantically_process_product_description(product_description)

    # return

    # Step 1: Get the top 100 HTSUS codes based on the product description
    output_text_1 = get_top_n_codes(product_description, "", 100, "")

    # Output the top 100 HTSUS codes to a file
    with open("outputtext1.txt", "w", encoding="utf-8") as f:
        f.write(str(output_text_1))
    print("Successfully retrieved HTSUS codes based on the product description.")

    # Step 2: Process the top 100 HTSUS codes to filter out irrelevant ones
    # and suggest a prompt for future queries
    if not output_text_1:
        print("No HTSUS codes retrieved. Exiting classification.")
        return
    relevant, irrelevant, added_prompt = process_top_n_codes(output_text_1, product_description)
    # print("Relevant HTSUS codes after filtering:", relevant[0:5], " and its length is ", len(relevant))  # Print first 5 relevant codes for brevity
    # print("Irrelevant HTSUS codes after filtering:", irrelevant[0:5], " and its length is ", len(irrelevant))  # Print first 5 irrelevant codes for brevity
    # print("Prompt suggestion for future queries:", added_prompt)

    # Step 3: Get the top 100 HTSUS codes based on product description + prompt suggestion

    added_prompt_str = added_prompt.strip()
    added_query = f" as well as additional instructions for a more accurate search: {added_prompt_str}",
    output_text_2 = get_top_n_codes(product_description, added_query, 100, irrelevant)

    # Output the top 100 HTSUS codes based on the combined query to a file
    if not output_text_2:
        print("No additional HTSUS codes retrieved based on the prompt suggestion. Exiting classification.")
        return
    with open("outputtext2.txt", "w", encoding="utf-8") as f:
        f.write(str(output_text_2))
    print("Successfully retrieved additional HTSUS codes based on the prompt suggestion.")

    # relevant2, irrelevant2, added_prompt2 = process_top_50(output_text_2, product_description)
    # print("Relevant HTSUS codes after filtering:", relevant2[0:5], " and its length is ", len(relevant2))  # Print first 5 relevant codes for brevity
    # print("Irrelevant HTSUS codes after filtering:", irrelevant[0:5], " and its length is ", len(irrelevant))  # Print first 5 irrelevant codes for brevity
    # print("Prompt suggestion for future queries:", added_prompt)


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

# Example usage
if __name__ == "__main__":
    # classify_htsus("Men 100 cotton denim jeans") # WRONG! it outputted 6203.42.4011 & 16.6%; WRONG SHUD BE 6203.42.07.11
    # classify_htsus("cotton plushie") # works! it outputted 9503.00.0073 & 0%
    # classify_htsus("Leather handbag") # works! it outputted the 3 possibilities shown in few_shot.txt
    # classify_htsus("Cordless drill") # WRONG! it outputted 8467.21.00.10 but 3.7% instead of 1.7%
    
    classify_htsus("Porcelain plate") # WORKS it out putted 6911.10.80.00 w/ correct duty tax 20.80% and rate 2 of 75%
    # classify_htsus("Smartphone") # works! it outputted 8517.13.0000 & 0%
    
    