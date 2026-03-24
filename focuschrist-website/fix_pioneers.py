import re

with open('pioneers.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add banner HTML after </nav>
banner_html = '''
    <div class="banner">
        <div class="banner-bg"></div>
        <div class="banner-overlay"></div>
        <a href="https://caribousun.github.io/focuschrist-website/Gemini_Generated_Image_eui1q0eui1q0eui1.png" target="_blank" class="banner-link"></a>
        <div class="banner-content">
        </div>
    </div>
'''

# Find </nav> and add banner after it
content = content.replace('    </nav>', '    </nav>' + banner_html)

# Also need to add banner CSS
banner_css = '''
    /* Banner */
    .banner { position: relative; width: 100%; height: 280px; overflow: hidden; }
    .banner-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: url('Gemini_Generated_Image_eui1q0eui1q0eui1.png') center/cover; }
    .banner-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(180deg, rgba(26,21,16,0.6) 0%, rgba(26,21,16,0.4) 100%); }
    .banner-content { position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%); text-align: center; }
    .banner-link { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
'''

# Add banner CSS before </style>
content = content.replace(' </style>', banner_css + ' </style>')

with open('pioneers.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Added banner to pioneers page')
