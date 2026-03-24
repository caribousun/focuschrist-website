import re

# Files to update
files = ['index.html', 'ask.html', 'art.html', 'pioneers.html', 'about.html']

youtube_section = '''
                <hr style="border: 0; border-top: 1px solid rgba(201,169,97,0.3); margin: 8px 0;">
                <div style="color: #c9a961; font-size: 0.8em; padding: 8px 15px 4px;">YouTube</div>
                <a href="https://www.youtube.com/@theRisen636" target="_blank">@theRisen636</a>
'''

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Add YouTube section before closing hamburger-menu div
    # Find the last </a> in hamburger menu and add after it
    pattern = r'(<a href="https://www\.churchofjesuschrist\.org/tools\?lang=eng&activeTab=all" target="_blank">All Resources</a>)'
    content = re.sub(pattern, r'\1' + youtube_section, content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print('Updated ' + f)
