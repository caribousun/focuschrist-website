import re

# Read the file
with open(r'C:\Users\carib\.openclaw\workspace\focuschrist-website\ask.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all answer: "..." patterns and escape any single quotes inside them
# Pattern matches 'answer: "..."' where the content can contain any characters except unescaped quotes

def fix_apostrophes(match):
    original = match.group(1)
    # Escape any unescaped single quotes
    fixed = original.replace("'", "\\'")
    return 'answer: "' + fixed + '"'

# Apply the fix
new_content = re.sub(r'answer:\s*"([^"]*)"', fix_apostrophes, content)

# Write back
with open(r'C:\Users\carib\.openclaw\workspace\focuschrist-website\ask.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed apostrophes in answer strings")
