import os
import re

def fix_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace HTML entity quotes with actual quotes
    content = content.replace('&quot;', '"')
    
    # Fix missing angle brackets in HTML tags
    content = re.sub(r'([^<])(link|script)\s+', r'\1<\2 ', content)
    content = re.sub(r'(</?\w+)([^>]*)\s*$', r'\1\2>', content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                print(f"Fixing {file_path}")
                fix_html_file(file_path)

if __name__ == "__main__":
    process_directory('templates')
    print("HTML files fixed successfully!")
