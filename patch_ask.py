import re

path = r"C:\Users\carib\.openclaw\workspace\focuschrist-website\ask.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("'personal revelation': { answer:")
if idx < 0:
    print("Not found")
    exit(1)

end = content.find("},", idx)
if end < 0:
    print("End marker not found")
    exit(1)

old_text = content[idx:end+2]
print("Found, length:", len(old_text))
print("First 100:", repr(old_text[:100]))
print("Last 100:", repr(old_text[-100:]))

print("\n--- Now doing replacements ---")

# Replace the personal revelation entry with an expanded version
# The answer text uses \" for internal quotes
new_entry = """        'personal revelation': { answer: "President Russell M. Nelson taught that every Latter-day Saint may merit personal revelation. He shared his own experience: while preparing a conference talk, he was awakened from sleep with an impression on his mind. He wrote rapidly - only to find his handwriting illegible in the morning! Revelation from God is always compatible with His eternal law - it never contradicts His revealed doctrine. It is facilitated by reverence and obedience. Nelson taught: \\"To them will I reveal all mysteries... concerning my kingdom.\\" Revelation may be incremental - \\"line upon line, precept upon precept\\" - and \\"unto him that receiveth, I will give more.\\" The key difference between a secondhand testimony and personal revelation? Moroni 10:5: ask with REAL intent, and you WILL know. D and C 8:2-3: \\"I will tell you in your MIND and HEART by the Holy Ghost.\\" This is personal, direct, and available to every faithful child of God.", sources: [{text:'\\u0001\\ufe0f President Nelson - Ask, Seek, Knock',url:'https://www.churchofjesuschrist.org/study/general-conference/2009/10/ask-seek-knock'},{text:'\\u0001\\ufe0f D&C 98:12',url:'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/98.12'},{text:'\\u0001\\ufe0f Moroni 10:5',url:'https://www.churchofjesuschrist.org/study/scriptures/bofm/moro/10.5'},{text:'\\u0001\\ufe0f D&C 8:2-3',url:'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/8.2'}] },"""

content = content.replace(old_text, new_entry, 1)
print("Replaced personal revelation")

# Now add the three new entries before 'spiritual discernment'
new_entries = """
        'recognizing the spirit': { answer: "**How do I recognize the Spirit's whisperings in the noise of daily life?** - The Holy Ghost speaks in a \\"still small voice\\" (1 Kings 19:12). In a world of constant noise, recognizing that voice is a skill developed through practice, patience, and proximity to the Lord. The key is **stillness** - we cannot hear the whisper when we are shouting. **The Spirit speaks through:** **Peace** - a calm assurance despite confusion (D&C 19:23). **Promptings** - \\"Do this\\" or \\"Do not go there.\\" **Impressions** - thoughts that feel different from your own. **Confirmations** - \\"That is right\\" or \\"That is not from Me.\\" D&C 8:2-3: \\"I will tell you in your mind and heart by the Holy Ghost.\\" The more we seek, the more we are given - \\"Light cleaves unto light\\" (D&C 88:11). Nephi was \\"led by the Spirit\\" (1 Nephi 2:16, 4:6). Alma's conversion happened when the Spirit \\"wrought a mighty change\\" (Alma 17:2-3). The question is: are you still enough to hear Him?", sources: [{text:'\\u0001\\ufe0f 1 Kings 19:11-13',url:'https://www.churchofjesuschrist.org/study/scriptures/ot/1-kgs/19.11'},{text:'\\u0001\\ufe0f D&C 8:2-3',url:'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/8.2'},{text:'\\u0001\\ufe0f D&C 88:11',url:'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/88.11'},{text:'\\u0001\\ufe0f John 10:27',url:'https://www.churchofjesuschrist.org/study/scriptures/nt/john/10.27'},{text:'\\u0001\\ufe0f Romans 8:14',url:'https://www.churchofjesuschrist.org/study/scriptures/nt/rom/8.14'},{text:'\\u0001\\ufe0f Alma 17:2-3',url:'https://www.churchofjesuschrist.org/study/scriptures/bofm/alma/17.2'}] },
        'personal revelation vs secondhand': { answer: "**How does personal revelation differ from secondhand testimony?** - There is a difference between knowing what others testify (secondhand) and knowing for yourself through revelation (firsthand). The adversary is content when we rely on others' testimonies. True conversion comes when we receive our own witness from the Holy Ghost. **Moroni 10:5** - \\"Ask with REAL intent, and you SHALL know by the Holy Ghost.\\" **The personal witness standard:** \\"I know the Book of Mormon is true because my bishop or parent said so\\" -> \\"I KNOW it is true because the Holy Ghost told ME.\\" **The pattern in scripture:** Nephi - \\"I saw the things my father saw\\" (1 Nephi 2:1) then received his own vision (1 Nephi 11). Joseph Smith - read James, asked God, received the First Vision. Alma the Younger - saw a vision, but his conversion was HIS, not his father's. D&C 8:2-3: \\"You shall have a voice... by the Holy Ghost... which shall be in THY HEART.\\" This is PERSONAL. The testimony of others is valuable - but it must become YOUR testimony. Ask. Seek. Knock. Then you will know.", sources: [{text:'\\u0001\\ufe0f Moroni 10:5',url:'https://www.churchofjesuschrist.org/study/scriptures/bofm/moro/10.5'},{text:'\\u0001\\ufe0f D&C 8:2-3',url:'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/8.2'},{text:'\\u0001\\ufe0f James 1:5-6',url:'https://www.churchofjesuschrist.org/study/scriptures/nt/james/1.5'},{text:'\\u0001\\ufe0f Acts 2:38',url:'https://www.churchofjesuschrist.org/study/scriptures/nt/acts/2.38'},{text:'\\u0001\\ufe0f John 14:26',url:'https://www.churchofjesuschrist.org/study/scriptures/nt/john/14.26'},{text:'\\u0001\\ufe0f John 7:37-39',url:'https://www.churchofjesuschrist.org/study/scriptures/nt/john/7.37'}] },
        'obedience revelation': { answer: "**How does obedience unlock the door to revelation?** - God does not force revelation on the unwilling. He waits to be asked. D&C 58:26-28: \\"Why command when you can invite? Revelation requires seeking.\\" **The danger of pushing ahead without asking:** Moses and the golden calf - the people acted without asking. King Noah's priests acted in haste (Mosiah 11:26) - without seeking divine guidance. Joseph Smith Sr. was warned: do not run faster than you have strength, and do not act on things not commanded (D&C 3:6). **The reward of asking first:** Nephi asked about the things his father saw (1 Nephi 2:16) - received his own vision. Enos prayed all day and night (Enos 1:1-4) - received a personal remission of sins. Joseph Smith studied James 1:5 first, then asked God - received the First Vision. **Obedience creates the capacity to receive:** D&C 88:67-68 - \\"Draw near unto me and I will draw near unto you... let your soul be at rest.\\" Alma 32:27-28 - exercise faith even a particle, and the word will begin to enlarge your soul. Obedience purifies the vessel so light can enter (D&C 50:24). Disobedience creates static - \\"Your sins have hid His face\\" (Isaiah 59:2). Ask FIRST. Then obey.", sources: [{text:'\\u0001\\ufe0f D&C 8:2-3',url:'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/8.2'},{text:'\\u0001\\ufe0f D&C 9:7-9',url:'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/9.7'},{text:'\\u0001\\ufe0f D&C 58:26-28',url:'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/58.26'},{text:'\\u0001\\ufe0f Alma 37:37',url:'https://www.churchofjesuschrist.org/study/scriptures/bofm/alma/37.37'},{text:'\\u0001\\ufe0f James 1:5-6',url:'https://www.churchofjesuschrist.org/study/scriptures/nt/james/1.5'},{text:'\\u0001\\ufe0f 1 Samuel 3:7',url:'https://www.churchofjesuschrist.org/study/scriptures/ot/1-sm/3.7'},{text:'\\u0001\\ufe0f D&C 1:19',url:'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/1.19'}] },"""

# Insert before 'spiritual discernment' 
marker = "        'spiritual discernment':"
if marker in content:
    content = content.replace(marker, new_entries + marker, 1)
    print("Inserted 3 new entries before 'spiritual discernment'")
else:
    print("ERROR: 'spiritual discernment' marker not found")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done!")