import csv
import re

def normalize_hts_number(hts_number):
    # Remove dots and pad with zeros to get 10 digits
    digits_only = hts_number.replace('.', '')
    digits_only = digits_only.ljust(10, '0')[:10]
    # Format as 4-2-2-2 segments
    parts = [digits_only[:4], digits_only[4:6], digits_only[6:8], digits_only[8:10]]
    return '.'.join(parts)

import csv

def flatten_hts_csv(input_file, output_file):
    with open(input_file, newline='', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        rows_filled = []
        last_filled = {col: '' for col in fieldnames}
        indent_stack = {}

        for row in reader:
            new_row = {}
            for col in fieldnames:
                value = row[col].strip() if row[col] is not None else ''
                if value == '':
                    value = last_filled[col]
                else:
                    last_filled[col] = value
                new_row[col] = value

            # Build hierarchical description
            try:
                indent = int(new_row['Indent'])
            except:
                indent = 0

            description = new_row.get('Description', '').strip()
            if description:
                indent_stack[indent] = description

                # Clear deeper levels
                for deeper_indent in list(indent_stack.keys()):
                    if deeper_indent > indent:
                        del indent_stack[deeper_indent]

            # Build full nested description
            full_description = ' - '.join(
                indent_stack[i] for i in sorted(indent_stack) if indent_stack[i]
            )
            new_row['Description'] = full_description

            rows_filled.append(new_row)

    # Write output
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_filled)

def filter_hts_by_digit_length(input_file, output_file):
    def is_valid_hts_number(hts):
        # Remove dots and check length
        digits_only = re.sub(r'\D', '', hts)
        return len(digits_only) in (8, 10)

    with open(input_file, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        filtered_rows = []

        for row in reader:
            hts_number = row.get('HTS_Number', '').strip()
            if hts_number and is_valid_hts_number(hts_number):
                filtered_rows.append(row)

    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_rows)

import csv

def remove_columns(input_file, output_file):
    # Columns to exclude
    columns_to_remove = {'Indent', 'Unit of Quantity'}

    with open(input_file, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        # New fieldnames: keep only the ones NOT in columns_to_remove
        new_fieldnames = [field for field in reader.fieldnames if field not in columns_to_remove]

        # Read and strip unwanted columns
        rows = []
        for row in reader:
            new_row = {key: row[key] for key in new_fieldnames}
            rows.append(new_row)

    # Write output with only the remaining fields
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# Example usage
flatten_hts_csv('htsus.csv', 'htsus_flattened.csv')
filter_hts_by_digit_length('htsus_flattened.csv', 'htsus_flattened_filtered.csv')
remove_columns('htsus_flattened_filtered.csv', 'htsus_flattened_filtered_cleaned.csv')
