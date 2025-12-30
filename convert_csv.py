# -*- coding: utf-8 -*-
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(script_dir, 'sample_students.csv')

if not os.path.exists(csv_file):
    print(f"Error: {csv_file} not found")
    sys.exit(1)

# Read with various encodings
for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
    try:
        with open(csv_file, 'r', encoding=enc) as f:
            content = f.read()
        print(f"Read with {enc}")
        break
    except:
        continue
else:
    print("Could not read file")
    sys.exit(1)

# Write with UTF-8 BOM
with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
    f.write(content)

print("SUCCESS: Converted to UTF-8 with BOM")

