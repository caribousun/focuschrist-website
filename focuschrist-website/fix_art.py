import re

# Read art.html
with open('art.html', 'r', encoding='utf-8') as f:
    content = f.read()

# New gallery - exactly 12 items from desktop
new_gallery = '''        <div class="art-gallery">
            <div class="art-item" onclick="openLightbox(0)">
                <img src="Jesus.png" alt="The Good Shepherd">
                <div class="art-caption">The Good Shepherd</div>
            </div>
            <div class="art-item" onclick="openLightbox(1)">
                <img src="jesus3.jpg" alt="The Living Christ">
                <div class="art-caption">The Living Christ</div>
            </div>
            <div class="art-item" onclick="openLightbox(2)">
                <img src="Suffer the Little Children.jpg" alt="Suffer the Little Children">
                <div class="art-caption">Suffer the Little Children</div>
            </div>
            <div class="art-item" onclick="openLightbox(3)">
                <img src="Jesus boat.png" alt="Peace Be Still">
                <div class="art-caption">Peace, Be Still</div>
            </div>
            <div class="art-item" onclick="openLightbox(4)">
                <img src="Jesus fun.png" alt="Fishers of Men">
                <div class="art-caption">Fishers of Men</div>
            </div>
            <div class="art-item" onclick="openLightbox(5)">
                <img src="Jesus and Mary his mom.jpg" alt="Jesus and Mary">
                <div class="art-caption">Jesus and Mary</div>
            </div>
            <div class="art-item" onclick="openLightbox(6)">
                <img src="Jesus baptized.png" alt="Jesus Baptism">
                <div class="art-caption">Jesus Baptism</div>
            </div>
            <div class="art-item" onclick="openLightbox(7)">
                <img src="Jesus feeding people.png" alt="Feeding the Multitude">
                <div class="art-caption">Feeding the Multitude</div>
            </div>
            <div class="art-item" onclick="openLightbox(8)">
                <img src="Jesus feeding people 2.png" alt="Feeding the 5000">
                <div class="art-caption">Feeding the 5000</div>
            </div>
            <div class="art-item" onclick="openLightbox(9)">
                <img src="Jesus feeding the fish.png" alt="Miraculous Catch">
                <div class="art-caption">Miraculous Catch</div>
            </div>
            <div class="art-item" onclick="openLightbox(10)">
                <img src="Jesus leper.jpg" alt="Healing the Leper">
                <div class="art-caption">Healing the Leper</div>
            </div>
            <div class="art-item" onclick="openLightbox(11)">
                <img src="Jesus with the children.jpg" alt="Let the Children Come">
                <div class="art-caption">Let the Children Come</div>
            </div>
        </div>'''

# Replace gallery section
pattern = r'<div class="art-gallery">.*?</div>\s*</main>'
content = re.sub(pattern, new_gallery + '</main>', content, flags=re.DOTALL)

# Update artImages array
new_artimages = '''var artImages = [
    { src: 'Jesus.png', caption: 'The Good Shepherd' },
    { src: 'jesus3.jpg', caption: 'The Living Christ' },
    { src: 'Suffer the Little Children.jpg', caption: 'Suffer the Little Children' },
    { src: 'Jesus boat.png', caption: 'Peace, Be Still' },
    { src: 'Jesus fun.png', caption: 'Fishers of Men' },
    { src: 'Jesus and Mary his mom.jpg', caption: 'Jesus and Mary' },
    { src: 'Jesus baptized.png', caption: 'Jesus Baptism' },
    { src: 'Jesus feeding people.png', caption: 'Feeding the Multitude' },
    { src: 'Jesus feeding people 2.png', caption: 'Feeding the 5000' },
    { src: 'Jesus feeding the fish.png', caption: 'Miraculous Catch' },
    { src: 'Jesus leper.jpg', caption: 'Healing the Leper' },
    { src: 'Jesus with the children.jpg', caption: 'Let the Children Come' }
];'''

content = re.sub(r'var artImages = \[.*?\];', new_artimages, content, flags=re.DOTALL)

with open('art.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - 12 art images from desktop')
