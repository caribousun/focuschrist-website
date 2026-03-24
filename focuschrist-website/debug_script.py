import re

# Read the file
with open(r'C:\Users\carib\.openclaw\workspace\focuschrist-website\ask.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Look for problematic apostrophe patterns in the entire script
# Find "answer: " strings that contain unescaped apostrophes
pattern = r"answer:\s*\"([^\"]*)\""
matches = re.findall(pattern, content)

# Check each answer for problematic characters
issues = []
for i, m in enumerate(matches):
    # Check if there's a pattern like "Something's" inside the quotes
    if "'s" in m and m.count("'") > 1:
        issues.append((i, m[:100]))

print(f"Found {len(issues)} potential issues")
for idx, txt in issues[:10]:
    print(f"Match {idx}: ...{txt}...")
