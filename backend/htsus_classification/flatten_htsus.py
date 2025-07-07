import csv

def normalize_hts_number(hts_number):
    # Remove dots and pad with zeros to get 10 digits
    digits_only = hts_number.replace('.', '')
    digits_only = digits_only.ljust(10, '0')[:10]
    # Format as 4-2-2-2 segments
    parts = [digits_only[:4], digits_only[4:6], digits_only[6:8], digits_only[8:10]]
    return '.'.join(parts)

def flatten_hts_csv(input_file, output_file):
    with open(input_file, newline='', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        last_filled = {col: '' for col in fieldnames}
        rows_filled = []
        for row in reader:
            new_row = {}
            for col in fieldnames:
                value = row[col].strip() if row[col] is not None else ''
                if value == '':
                    value = last_filled[col]
                else:
                    last_filled[col] = value
                new_row[col] = value
            rows_filled.append(new_row)

    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_filled)

# Example usage
flatten_hts_csv('htsus.csv', 'htsus_flattened.csv')
