# Add answers for new Q&A topics

with open(r'C:\Users\carib\.openclaw\workspace\focuschrist-website\pioneers.html', 'r', encoding='utf-8') as f:
    content = f.read()

# New answers to add
new_answers = '''

 // NEW: Daily Life & Food Answers
 "Pioneer bread was made from flour, water, and salt, baked in Dutch ovens over open fires. Hardtack was a popular durable biscuit that could be stored for months. Pioneers also made Johnny cakes (cornmeal pancakes) and biscuits when ingredients allowed.",

 "Pioneers made coffee by roasting green coffee beans in a pan over the fire, then grinding them by hand. The grounds were boiled in water to create a strong, dark brew. Coffee was a prized luxury that helped pioneers wake up and stay alert during long days on the trail.",

 "Pioneer children sang hymns and folk songs during the journey. 'Come, Come, Ye Saints' was a beloved hymn. Children also sang simple songs their parents taught them, and some companies had evening sings where the whole group participated in music.",

 "Birthdays on the trail were simple but meaningful. Families would do their best to mark the occasion with a special meal or song. For children, it was a chance to feel special during the difficult journey. Some parents saved special treats for birthday celebrations.",

 "Pioneer children played simple games like tag, hide-and-seek, and jump rope. They also made their own toys from wood and cloth. Playing helped children cope with the hardships of the journey and provided normal childhood moments amid the challenges.",

 "The worst pioneer meals often came at the end of supplies when food was low and monotonous. Salt pork and hardtack could become tiresome, and when supplies ran low, pioneers sometimes went hungry. A typical dinner was bacon, beans, and bread.",

 "Pioneers preserved meat by salting (salting pork and beef), smoking, and drying (making jerky). They also packed salted meat in salt barrels for the journey. Meat was precious and carefully rationed throughout the trip.",

 "Pioneers carried herbs like sage, mint, and chamomile for medicinal purposes. They also brought along castor oil, Epsom salts, and other remedies. Many relied on folk medicine and herbal treatments passed down through generations.",

 "Mosquitoes and insects were a major annoyance on the trail. Pioneers used smoke from campfires, homemade repellents, and netting to protect themselves. Despite the irritation, bugs were just another challenge pioneers endured.",

 "Pioneer weddings on the trail were simple ceremonies conducted by company leaders or elders. Couples exchanged vows, often with the whole company as witnesses. The ceremony was followed by a simple celebration with food and music from the company.",'''

# Find where to insert answers - after the last answer entry
insert_marker = '// Answers for new 20 research topics'
insert_point = content.find(insert_marker)

if insert_point > 0:
    content = content[:insert_point] + new_answers + content[insert_point:]
    with open(r'C:\Users\carib\.openclaw\workspace\focuschrist-website\pioneers.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added new answers!')
else:
    print('Insert point not found')
