import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# setting the environment

DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="growing_vegetables")


user_query = input("What product are you looking for a HTSUS code?\n\n")

results = collection.query(
    query_texts=[user_query],
    n_results=4
)

print(results['documents'])
#print(results['metadatas'])

client = OpenAI()

system_prompt = """
You are an intelligent customs assistant designed to accurately classify products under the Harmonized Tariff Schedule of the United States (HTSUS). You must rely strictly on retrieved HTSUS documentation, legal notes, rulings, and classification guidelines to identify the correct code.

Instructions:
- Use only the retrieved context documents to form your response.
- Do not make assumptions or guesses beyond the retrieved text.
- If no relevant HTSUS classification is found in the retrieved context, clearly state: "No applicable HTSUS code found based on the available information."
- Follow General Rules of Interpretation (GRIs) if relevant content is retrieved.
- Include the HTSUS heading/subheading and full description when available.
- Cite the HTSUS chapter or note that justifies your classification.

Retrieved Context:
{retrieved_docs}

Output Format:
HTSUS Code: [####.##.####]
Description: [Official HTSUS item description]
Justification:
- Reasoning based strictly on the retrieved HTSUS notes or rulings.
- Any applicable legal notes, chapter/section references.

If you cannot determine a code confidently from the retrieved data, say: "Insufficient information to assign a specific HTSUS code."
"""

#print(system_prompt)

response = client.chat.completions.create(
    model="gpt-4o",
    messages = [
        {"role":"system","content":system_prompt},
        {"role":"user","content":user_query}    
    ]
)

print("\n\n---------------------\n\n")

print(response.choices[0].message.content)