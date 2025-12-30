#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# Try to find the CSV file in common locations
possible_paths = [
    'sample_students.csv',
    os.path.join(os.path.dirname(__file__), 'sample_students.csv'),
    os.path.join(os.getcwd(), 'sample_students.csv'),
]

csv_path = None
for path in possible_paths:
    if os.path.exists(path):
        csv_path = path
        break

if not csv_path:
    print("Error: Could not find sample_students.csv")
    sys.exit(1)

# Read the file
encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'windows-1252']
content = None

for encoding in encodings:
    try:
        with open(csv_path, 'r', encoding=encoding) as f:
            content = f.read()
            print(f"Read file with encoding: {encoding}")
            break
    except:
        continue

if not content:
    print("Error: Could not read file")
    sys.exit(1)

# Write with UTF-8 BOM
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    f.write(content)

print("SUCCESS: File converted to UTF-8 with BOM")
print("Azerbaijani characters should now display correctly!")
