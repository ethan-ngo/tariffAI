import pandas as pd

df = pd.read_csv("htsus_flattened_filtered.csv")

def extract_chapter(hts_number):
    try:
        return hts_number[:2].zfill(2)
    except Exception:
        return None
    
# Apply function to each row
df["HTS_Chapter"] = df["HTS_Number"].astype(str).apply(extract_chapter)

# Reorder cols 
cols = ["HTS_Chapter"] + [col for col in df.columns if col != "HTS_Chapter"]
df = df[cols]

# Save to new CSV
df.to_csv("htsus_flattened_with_chapters.csv", index=False)