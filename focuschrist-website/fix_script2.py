import re

# Read the file
with open(r'C:\Users\carib\.openclaw\workspace\focuschrist-website\ask.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Also need to fix text: '...' patterns in sources
# Pattern for text: '...' in sources
def fix_sources_text(match):
    original = match.group(1)
    fixed = original.replace("'", "\\'")
    return "text: '" + fixed + "'"

# Apply the fix for text: '...' pattern
new_content = re.sub(r"text:\s*'([^']*)'", fix_sources_text, content)

# Write back
with open(r'C:\Users\carib\.openclaw\workspace\focuschrist-website\ask.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed apostrophes in sources text strings")
