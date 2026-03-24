import re

with open('art.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add lightbox HTML before </body>
lightbox_html = '''
    <!-- Lightbox -->
    <div id="lightbox" class="lightbox" onclick="closeLightbox(event)">
        <span class="lightbox-close" onclick="closeLightbox(event)">&times;</span>
        <span class="lightbox-arrow prev" onclick="changeImage(-1); event.stopPropagation()">&#10094;</span>
        <div class="lightbox-content" onclick="event.stopPropagation()">
            <img id="lightbox-img" src="" alt="">
            <div id="lightbox-caption" class="lightbox-caption"></div>
        </div>
        <span class="lightbox-arrow next" onclick="changeImage(1); event.stopPropagation()">&#10095;</span>
    </div>

    <script>
        var artImages = [
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
            { src: 'Jesus leper.jpg', caption: 'Healing the Leper' }
        ];
        var currentIndex = 0;
        
        function openLightbox(index) {
            currentIndex = index;
            updateLightbox();
            document.getElementById('lightbox').classList.add('active');
        }
        
        function updateLightbox() {
            var img = artImages[currentIndex];
            document.getElementById('lightbox-img').src = img.src;
            document.getElementById('lightbox-caption').textContent = img.caption;
        }
        
        function changeImage(delta) {
            currentIndex += delta;
            if (currentIndex < 0) currentIndex = artImages.length - 1;
            if (currentIndex >= artImages.length) currentIndex = 0;
            updateLightbox();
        }
        
        function closeLightbox(event) {
            if (event && event.target !== event.currentTarget && event.target.tagName !== 'SPAN') return;
            document.getElementById('lightbox').classList.remove('active');
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            var lightbox = document.getElementById('lightbox');
            if (!lightbox.classList.contains('active')) return;
            if (e.key === 'ArrowLeft') changeImage(-1);
            if (e.key === 'ArrowRight') changeImage(1);
            if (e.key === 'Escape') closeLightbox();
        });
    </script>
'''

# Add before </body>
content = content.replace('</body>', lightbox_html + '</body>')

with open('art.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Added lightbox back to art.html')
