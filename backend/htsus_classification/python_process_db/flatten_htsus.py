import csv
import re

# format hts codes as 10 digit numbers without periods
def normalize_hts_number(hts_number):
    # Remove dots and pad with zeros to get 10 digits
    digits_only = hts_number.replace('.', '')
    digits_only = digits_only.ljust(10, '0')[:10]
    # Format as 4-2-2-2 segments
    parts = [digits_only[:4], digits_only[4:6], digits_only[6:8], digits_only[8:10]]
    return '.'.join(parts)

# flatten the HTS CSV file and filter out invalid entries
# also remove indent and unit of quantity columns
def flatten_and_filter_hts_csv(input_file, output_file):
    def is_valid_hts_number(hts):
        digits_only = re.sub(r'\D', '', hts)
        return len(digits_only) in (8, 10)

    with open(input_file, newline='', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        # We'll drop 'Indent' and 'Unit of Quantity'
        output_fields = [f for f in fieldnames if f not in ('Indent', 'Unit of Quantity')]

        last_filled = {col: '' for col in fieldnames}
        indent_stack = {}
        seen_ids = set()
        output_rows = []

        for row in reader:
            # Fill missing cells
            new_row = {}
            for col in fieldnames:
                value = row[col].strip() if row[col] else ''
                if value == '':
                    value = last_filled[col]
                else:
                    last_filled[col] = value
                new_row[col] = value

            # Parse indent level
            try:
                indent = int(new_row.get('Indent', '0'))
            except ValueError:
                indent = 0

            description = new_row.get('Description', '').strip()
            if description:
                indent_stack[indent] = description
                # Remove deeper levels
                for deeper in list(indent_stack.keys()):
                    if deeper > indent:
                        del indent_stack[deeper]

            # Compose nested description
            full_description = ' - '.join(
                indent_stack[i] for i in sorted(indent_stack) if indent_stack[i]
            )
            new_row['Description'] = full_description

            # Only keep rows that are valid 8- or 10-digit HTS and not duplicates
            hts_number = new_row.get('HTS_Number', '').strip()
            if hts_number and is_valid_hts_number(hts_number) and hts_number not in seen_ids:
                seen_ids.add(hts_number)
                output_rows.append({k: new_row[k] for k in output_fields})

    # Write filtered output
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(output_rows)

# htsus.csv is the csv downloaded from the official htsus website
# htsus_flattened_filtered.csv is the output file with flattened and filtered data
    # htsus_flattened_filtered.csv is used as input to add_hts_chapter.py
flatten_and_filter_hts_csv('htsus.csv', 'htsus_flattened_filtered.csv')

