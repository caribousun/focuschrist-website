# Add more Q&A topics to pioneer page

with open(r'C:\Users\carib\.openclaw\workspace\focuschrist-website\pioneers.html', 'r', encoding='utf-8') as f:
    content = f.read()

# New Q&A topics to add
new_topics = '''
 // NEW: Daily Life & Food
 "What was pioneer bread made of?",
 "How did pioneers make coffee on the trail?",
 "What songs did pioneer children sing?",
 "How did pioneers celebrate birthdays on the trail?",
 "What games did pioneer children play?",
 "What was the worst pioneer meal?",
 "How did pioneers preserve meat?",
 "What herbs did pioneers carry for medicine?",
 "How did pioneers handle mosquitoes and insects?",
 "What was a pioneer wedding like on the trail?",'''

# Find the location in the JavaScript to insert
insert_marker = '// NEW: Trail History'
insert_point = content.find(insert_marker)

if insert_point > 0:
    content = content[:insert_point] + new_topics + '\n' + content[insert_point:]
    with open(r'C:\Users\carib\.openclaw\workspace\focuschrist-website\pioneers.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added new Q&A topics!')
else:
    print('Insert point not found - looking for alternatives')
    # Try to find the historianQuestions array
    if 'historianQuestions' in content:
        print('historianQuestions found')
