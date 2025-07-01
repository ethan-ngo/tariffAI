import csv

def normalize_hts_number(hts_number):
    # Remove dots and pad with zeros to get 10 digits
    digits_only = hts_number.replace('.', '')
    digits_only = digits_only.ljust(10, '0')[:10]
    # Format as 4-2-2-2 segments
    parts = [digits_only[:4], digits_only[4:6], digits_only[6:8], digits_only[8:10]]
    return '.'.join(parts)

def flatten_hts_csv(input_file, output_file):
    # Step 1: Read input and fill missing duty rates by indent level
    last_rates_by_indent = {}
    rows_filled = []

    with open(input_file, newline='', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            indent = int(row['Indent'].strip()) if row['Indent'].strip() else 0

            for field in ['General Rate of Duty', 'Special Rate of Duty', 'Column 2 Rate of Duty', 'Additional Duties']:
                current_value = row.get(field, '').strip()

                if current_value:
                    last_rates_by_indent[indent] = last_rates_by_indent.get(indent, {})
                    last_rates_by_indent[indent][field] = current_value
                else:
                    for parent_indent in reversed(range(indent)):
                        parent_rates = last_rates_by_indent.get(parent_indent)
                        if parent_rates and field in parent_rates:
                            row[field] = parent_rates[field]
                            break

            rows_filled.append(row)

    # Step 2: Flatten rows
    flattened_rows = []
    indent_stack = {}

    fieldnames = [
        'HTS_Number',
        'Full_Description',
        'General_Rate_of_Duty',
        'Special_Rate_of_Duty',
        'Column_2_Rate_of_Duty',
        'Additional_Duties'
    ]

    for row in rows_filled:
        try:
            indent_level = int(row['Indent'].strip()) if row['Indent'].strip() else 0
        except:
            indent_level = 0

        description = (row.get('Description') or "").strip()
        if description:
            indent_stack[indent_level] = description

        # Remove deeper levels
        for key in list(indent_stack.keys()):
            if key > indent_level:
                del indent_stack[key]

        full_description = " - ".join(indent_stack[i] for i in sorted(indent_stack) if indent_stack[i])

        raw_hts = (row.get('HTS_Number') or "").strip()
        if raw_hts:
            normalized_hts = normalize_hts_number(raw_hts)
            flattened_rows.append({
                'HTS_Number': normalized_hts,
                'Full_Description': full_description,
                'General_Rate_of_Duty': (row.get('General Rate of Duty') or "").strip(),
                'Special_Rate_of_Duty': (row.get('Special Rate of Duty') or "").strip(),
                'Column_2_Rate_of_Duty': (row.get('Column 2 Rate of Duty') or "").strip(),
                'Additional_Duties': (row.get('Additional Duties') or "").strip()
            })

    # Write output CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened_rows)

# Example usage
with open('htsus.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    print("Field names (column headers) in htsus.csv:")
    for i, field in enumerate(reader.fieldnames):
        print(f"{i+1}. {repr(field)}")

        
flatten_hts_csv('htsus.csv', 'output2.csv')
