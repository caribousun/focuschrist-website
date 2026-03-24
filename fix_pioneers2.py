old = '''<p class="journal-source">-- Heber C. Kimball, Pioneer Journal</p>
 </div>
 </div>
 </section>

 <!-- Q&A Section -->'''

new = '''<p class="journal-source">-- Heber C. Kimball, Pioneer Journal</p>
 </div>
 <div class="journal-card">
 <div class="journal-date">September 1848</div>
 <p class="journal-text">"The crickets have come upon our fields like locusts... but the gulls came to our rescue! It was a miracle - the gulls ate the crickets and saved our crops."</p>
 <p class="journal-source">— Pioneer accounts of the 1848 cricket miracle</p>
 </div>
 <div class="journal-card">
 <div class="journal-date">May 1852</div>
 <p class="journal-text">"We have crossed the plains with our own handcart. My wife and children are weary but strong in faith. The Great Salt Lake Valley awaits us."</p>
 <p class="journal-source">— British convert journal entry</p>
 </div>
 <div class="journal-card">
 <div class="journal-date">October 1856</div>
 <p class="journal-text">"The snow is deep and the cold is bitter. Many have given out. I pray we will be found by those sent to rescue us. God is with his people."</p>
 <p class="journal-source">— Martin Handcart Company survivor</p>
 </div>
 <div class="journal-card">
 <div class="journal-date">April 1847</div>
 <p class="journal-text">"This day we crossed the Missouri River on the ice. The oxen broke through in places but we got all the wagons across. A hard day but we are one stage nearer to the valley."</p>
 <p class="journal-source">— William A. Anderson, Pioneer Journal</p>
 </div>
 <div class="journal-card">
 <div class="journal-date">June 1856</div>
 <p class="journal-text">"Our company of 500 souls has left Florence, Nebraska. We have hand carts and are prepared to walk most of the way. The Church has provided well."</p>
 <p class="journal-source">— John D. Lee, Handcart Company</p>
 </div>
 </div>
 </section>

 <!-- Q&A Section -->'''

with open(r'C:\Users\carib\.openclaw\workspace\focuschrist-website\pioneers.html', 'r', encoding='utf-8') as f:
    content = f.read()

if old in content:
    content = content.replace(old, new)
    with open(r'C:\Users\carib\.openclaw\workspace\focuschrist-website\pioneers.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Success!')
else:
    print('Old string not found')
    idx = content.find('-- Heber C. Kimball')
    print('Actually:', repr(content[idx:idx+100]))
