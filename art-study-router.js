/* focusChrist Art -> topic study / official Church search / contextual Ask router.
 * Preserves artwork unchanged. Study connections appear only in the open modal.
 * Production hardening: no generic YouTube study exit; Ask carries artwork context and an exact return path.
 */
(function () {
    'use strict';

    const CHURCH_SEARCH = 'https://www.churchofjesuschrist.org/search?lang=eng&query=';

    const TITLE_ALIASES = {
    "Jesus Boat": "Jesus with His Disciples at Sea",
    "Jesus Fun": "Joy Beside the Lake",
    "Jesus Leper": "The Healing Touch of Jesus",
    "Jesus Seven Times Seven": "Learning to Forgive",
    "Jesus with Apostles Sunflowers": "Walking with the Apostles",
    "Jesus and Mary His Mom": "Jesus and His Mother Mary",
    "Widows Mite": "The Widow's Mite"
};

    const PICTURE_REFLECTIONS = {
    "Divine Push": "Jesus helps a woman move a handcart while two children rest inside. Consider the burdens someone near you is carrying, and one way you could help.",
    "Forever Friends": "Jesus walks beside a smiling man along a sunlit forest path. A quiet walk with someone can be a simple gift of friendship.",
    "Forever": "Jesus kneels beside a man and woman in a cemetery, drawing them close. In a time of loss, a loving presence can matter more than finding the right words.",
    "Jesus and His Mother Mary": "Jesus and Mary embrace beneath olive trees in the evening light. Their closeness invites a moment of gratitude for the people who have cared for us.",
    "Jesus Baptized": "John baptizes Jesus as people watch from the riverbank. Consider what it means to follow His example.",
    "Jesus with His Disciples at Sea": "Jesus stands among His disciples in a boat while waves rise around them. The scene invites reflection on turning toward Him when life feels unsettled.",
    "Jesus Feeding People": "Bread and fish fill a basket as Jesus offers food to a waiting crowd. Notice how care for people's daily needs can become part of following Him.",
    "Jesus Feeding the Fish": "Jesus scatters food toward fish in the shallow water. This quiet scene invites us to notice and care for the living things around us.",
    "Joy Beside the Lake": "Jesus smiles beside a lakeside village filled with boats, people, and daily work. There can be room for gratitude and joy in an ordinary day.",
    "Jesus in Africa": "Adults and children gather around Jesus beneath a broad tree near thatched homes. Consider the Savior's invitation to welcome and love people across nations and cultures.",
    "The Healing Touch of Jesus": "Jesus reaches toward a man and rests a hand gently on his head. Compassion often begins with drawing near and giving someone our attention.",
    "Learning to Forgive": "Jesus rests His arm around a man as they talk together. Forgiveness can begin with a willingness to listen and take another step together.",
    "Jesus Walking Jerusalem": "Jesus walks with a group of men along a stone street in Jerusalem. Imagine how paying attention to Him might change the way you walk through your own day.",
    "Walking with the Apostles": "Jesus and His apostles walk together through sunflowers in the evening light. Think of the people whose companionship helps you keep following Him.",
    "Little Friends": "Two young children lean close as Jesus holds them in His arms. Their embrace invites us to consider how we help children feel welcomed and loved.",
    "Never Alone": "Jesus rests a hand on a woman's shoulder beside her hospital bed. A visit, a listening ear, or a quiet prayer can offer comfort during illness.",
    "Now I See": "Jesus touches an older man's closed eyes while others watch nearby. Pause with the scene and consider what it means to seek His help with hope.",
    "Palms": "Jesus raises His hands before a crowd carrying palm branches. The words from Isaiah offer the reassurance that we are remembered and loved.",
    "Posterity": "An older man and woman stand close to Jesus beneath golden clouds. Consider the love shared across generations and the hope you bring to your family relationships.",
    "Suffer the Little Children": "Children gather around Jesus beside olive trees, some holding small flowers. Their welcome invites us to give children patient attention and a place beside us.",
    "The Garden": "Jesus kneels in prayer against an olive tree while others rest nearby. In a difficult hour, prayer can begin with simply turning to the Father.",
    "The Good Shepherd": "Jesus smiles on a busy market street as daily life continues around Him. His care reaches into the ordinary needs of our lives.",
    "The Living Christ": "A warm smile fills this portrait of Jesus against a golden sky. Take a quiet moment to consider what it means to draw closer to the living Christ.",
    "Tranquil Morning": "Jesus and a young girl sit beside a pond, feeding ducks and ducklings at sunrise. A small, peaceful moment can remind us to slow down and notice what is good.",
    "The Widow's Mite": "An older woman places a coin into an offering box while Jesus stands nearby. Her small offering invites reflection on giving with a willing heart.",
    "Let It Go": "Jesus walks beside a troubled man with a hand resting on his shoulder. Consider a burden you might bring to Him in prayer today.",
    "Be Still": "Jesus walks beside a man through a crowded city street. Even in a busy day, a brief pause can help us turn our attention toward Him.",
    "The Savior's Invitation": "Jesus extends an open hand beside the water in the evening light. Consider one small step you could take toward Him today.",
    "Rest in the Lord, Trust in the Lord": "Jesus reaches out among sunflowers as children run behind Him. The words on the picture invite us to rest in the Lord and practice trusting Him.",
    "See That Ye Be Not Troubled": "Jesus holds out His hand in a landscape of storm clouds, lightning, and distant fires. The picture's words invite us to seek steadiness in Him when the world feels troubled.",
    "Joy Cometh in the Morning": "A woman embraces a smiling child among flowers while Jesus stands nearby. The words about morning joy offer hope to hold beside seasons of sorrow.",
    "Blessed Be the Name of the Lord": "Jesus sits beside a man among sunflowers. Job's words give us much to ponder about faith through both receiving and losing.",
    "There Is a Green Hill Far Away": "A walled city and three crosses on a distant hill appear behind Jesus. The hymn's words invite a quiet moment to remember His sacrifice.",
    "Make a Joyful Noise Unto God": "Children and adults laugh beside a stream where Jesus sits with them. Gratitude for shared joy is one way to begin praising God.",
    "In the Name of the Lord of Hosts": "Jesus rests His hands on a boy holding a sling while an armored warrior stands behind them. The words from David's story invite reflection on courage and trust in the Lord.",
    "There Is a Greater Victory Ahead": "Jesus extends His hand toward an armored warrior. The invitation to turn and follow Him asks us to consider what kind of victory we are seeking.",
    "His Strength and Redeeming Power": "Jesus extends His hands above a woman in golden light and a bowed figure in shadow. The words on the picture invite reflection on His strength and redeeming power.",
    "God Will Feel After You": "Jesus walks beside a stream toward a sunlit tree. The words about God's care invite us to keep seeking Him through the trials we face.",
    "Jesus Christ": "This portrait shows Jesus in the warm light of sunset. Let the quiet image be an invitation to remember Him and the way He taught us to live."
};

    const FEATURED = {
        'The Living Christ': { focus: 'art-study/the-living-christ.html', query: 'The Living Christ Jesus Christ Atonement Resurrection' },
        'The Good Shepherd': { focus: 'art-study/the-good-shepherd.html', query: 'Good Shepherd Jesus Christ John 10' },
        'Suffer the Little Children': { focus: 'art-study/suffer-the-little-children.html', query: 'Jesus Christ children suffer little children' },
        'Be Still': { focus: 'art-study/be-still.html', query: 'Be still Psalm 46 trust God Jesus Christ' }
    };

    const SCENE_HINTS = [
        { match: ['Divine Push'], query: 'Jesus Christ guidance discipleship trust God' },
        { match: ['Forever Friends', 'Forever', 'Posterity'], query: 'eternal families Jesus Christ resurrection family relationships' },
        { match: ['Jesus and Mary His Mom'], query: 'Mary mother of Jesus Christ New Testament' },
        { match: ['Jesus Baptized'], query: 'baptism of Jesus Christ Matthew 3' },
        { match: ['Jesus Boat'], query: 'Jesus Christ calms the storm Mark 4 faith' },
        { match: ['Jesus Feeding People'], query: 'Jesus Christ feeding five thousand John 6' },
        { match: ['Jesus Feeding the Fish'], query: "Jesus Christ kindness caring for God's creations" },
        { match: ['Jesus Fun', 'Little Friends'], query: 'Jesus Christ joy children discipleship' },
        { match: ['Jesus in Africa'], query: 'Jesus Christ all nations children of God' },
        { match: ['Jesus Leper', 'Now I See'], query: 'Jesus Christ healing miracles faith New Testament' },
        { match: ['Jesus Seven Times Seven', 'Let It Go'], query: 'Jesus Christ forgiveness seventy times seven Matthew 18' },
        { match: ['Palms'], query: 'Jesus Christ Isaiah 49:16 remembered not forgotten' },
        { match: ['Jesus Walking Jerusalem'], query: 'Jesus Christ ministry Jerusalem disciples' },
        { match: ['Jesus with Apostles Sunflowers'], query: 'Jesus Christ Apostles disciples teachings' },
        { match: ['Never Alone'], query: 'Jesus Christ comfort never alone Holy Ghost' },
        { match: ['Widows Mite'], query: "widow's mite Jesus Christ Mark 12 sacrifice" },
        { match: ['The Garden', 'There Is a Green Hill Far Away'], query: 'Jesus Christ Gethsemane Crucifixion Atonement Resurrection' },
        { match: ["The Savior's Invitation"], query: 'Jesus Christ invitation come unto me discipleship' },
        { match: ['Rest in the Lord, Trust in the Lord'], query: 'rest in the Lord trust in the Lord Psalm 37' },
        { match: ['See That Ye Be Not Troubled'], query: 'see that ye be not troubled Matthew 24 Jesus Christ' },
        { match: ['Joy Cometh in the Morning'], query: 'joy cometh in the morning Psalm 30 Jesus Christ hope' },
        { match: ['Blessed Be the Name of the Lord'], query: 'blessed be the name of the Lord Job 1 faith adversity' },
        { match: ['Make a Joyful Noise Unto God'], query: 'make a joyful noise unto God Psalm 66 worship praise' },
        { match: ['In the Name of the Lord of Hosts'], query: 'David Goliath 1 Samuel 17 Lord of hosts faith' },
        { match: ['There Is a Greater Victory Ahead'], query: 'Jesus Christ victory hope adversity faith' },
        { match: ['His Strength and Redeeming Power'], query: 'Jesus Christ redeeming power strength Atonement' },
        { match: ['God Will Feel After You'], query: 'God feel after you Joseph Smith seek God revelation' },
        { match: ['Tranquil Morning'], query: 'Jesus Christ peace prayer stillness morning devotion' }
    ];

    function captionForItem(item) {
        const caption = item ? item.querySelector('.caption') : null;
        return caption ? caption.textContent.trim() : '';
    }

    function routeForCaption(caption) {
        const legacy = Object.keys(TITLE_ALIASES).find(function (key) { return TITLE_ALIASES[key] === caption; }) || caption;
        if (FEATURED[caption]) return Object.assign({ caption: caption }, FEATURED[caption]);
        const hint = SCENE_HINTS.find(function (entry) { return entry.match.includes(legacy); });
        const query = hint ? hint.query : (caption || 'Jesus Christ');
        return { caption: caption || 'This artwork', focus: '', query: query };
    }

    function officialSearch(query) {
        return CHURCH_SEARCH + encodeURIComponent(query || 'Jesus Christ');
    }

    function returnUrlForCaption(caption) {
        return 'art.html?art=' + encodeURIComponent(caption || 'This artwork');
    }

    function askUrl(route) {
        const params = new URLSearchParams();
        params.set('art', route.caption);
        params.set('topic', route.query || route.caption);
        params.set('return', returnUrlForCaption(route.caption));
        return 'ask.html?' + params.toString() + '#ask-question';
    }

    function ensureStyles() {
        if (document.getElementById('focuschrist-art-study-router-styles')) return;
        const style = document.createElement('style');
        style.id = 'focuschrist-art-study-router-styles';
        style.textContent = `
            .fc-art-study-button{position:absolute;left:22px;bottom:18px;z-index:1002;min-height:42px;padding:8px 15px;border:1px solid var(--fc-line-strong);border-radius:999px;background:var(--fc-bg-warm);color:var(--fc-gold-light);font:inherit;font-size:.82rem;font-weight:700;cursor:pointer;backdrop-filter:blur(8px)}
            .fc-art-study-button:hover,.fc-art-study-button:focus-visible{background:var(--fc-surface);color:var(--fc-cream);outline:none}
            .fc-art-study-drawer{position:absolute;left:18px;right:18px;bottom:72px;z-index:1003;display:none;max-width:780px;margin:0 auto;padding:16px;border:1px solid var(--fc-line);border-radius:14px;background:var(--fc-bg-deep);box-shadow:var(--fc-shadow);cursor:default}
            #imageModal .fc-art-viewer-actions{position:absolute;left:max(12px,env(safe-area-inset-left));right:max(12px,env(safe-area-inset-right));bottom:max(18px,env(safe-area-inset-bottom));display:grid;grid-template-columns:1.4fr 1fr .8fr;gap:8px;max-width:560px;margin:0 auto;z-index:1002;cursor:default}
            #imageModal .fc-art-viewer-actions>*{position:static;transform:none;box-sizing:border-box;display:flex;align-items:center;justify-content:center;min-width:0;width:100%;height:44px;min-height:44px;margin:0;padding:6px;border:1px solid var(--fc-line-strong);border-radius:999px;background:var(--fc-bg-warm);color:var(--fc-cream);font:inherit;font-size:.78rem;font-weight:700;line-height:1.2;text-align:center;text-decoration:none;white-space:nowrap;cursor:pointer;backdrop-filter:blur(8px)}
            #imageModal .fc-art-viewer-actions>*:hover,#imageModal .fc-art-viewer-actions>*:focus-visible{background:var(--fc-surface);color:var(--fc-cream);outline:3px solid var(--fc-line-strong);outline-offset:2px}
            #imageModal .image-counter{bottom:calc(max(18px,env(safe-area-inset-bottom)) + 52px);font-size:.8rem;line-height:1.2;pointer-events:none;width:fit-content;padding:4px 8px;border-radius:999px;background:var(--fc-bg-warm)}
            #imageModal .fc-art-study-drawer{bottom:calc(max(18px,env(safe-area-inset-bottom)) + 68px + .96rem);max-height:calc(100dvh - 120px);overflow-y:auto;box-sizing:border-box}
            .fc-art-study-drawer.open{display:block}
            .fc-art-study-title{margin:0 0 8px;color:var(--fc-gold-light);font-family:var(--fc-font-display);font-size:1.15rem}
            .fc-art-study-copy{margin:0 0 16px;color:var(--fc-text);font-size:.84rem;line-height:1.55}
            .fc-art-study-links{display:flex;flex-wrap:wrap;gap:8px}
            .fc-art-study-links a{box-sizing:border-box;min-width:0;white-space:normal;overflow-wrap:anywhere;display:inline-flex;align-items:center;justify-content:center;min-height:40px;padding:8px 13px;border:1px solid var(--fc-line);border-radius:999px;background:var(--fc-surface-soft);color:var(--fc-gold-light)!important;text-decoration:none!important;font-size:.77rem;font-weight:700}
            .fc-art-study-links a[data-art-ask]{background:var(--fc-action-fill);color:var(--fc-action-text)!important;border-color:var(--fc-gold-light)}
            .fc-art-study-links a:hover,.fc-art-study-links a:focus-visible{background:var(--fc-surface-hover);border-color:var(--fc-gold-light);outline:none}
            .fc-art-study-links a[data-art-ask]:hover,.fc-art-study-links a[data-art-ask]:focus-visible{background:var(--fc-action-hover);color:var(--fc-action-text)!important}
            .fc-art-study-hint{max-width:760px;margin:0 auto 6px;padding:0 18px;color:var(--fc-muted);font-size:.82rem;text-align:center}
            @media(max-width:700px){.fc-art-study-button{left:12px;bottom:12px}.fc-art-study-drawer{left:10px;right:10px;bottom:62px;padding:13px}.fc-art-study-links{display:grid}.fc-art-study-links a{width:100%}}
        `;
        document.head.appendChild(style);
    }

    function ensureHint() {
        const gallery = document.querySelector('.gallery');
        if (!gallery || document.querySelector('[data-focuschrist-art-study-hint]')) return;
        const hint = document.createElement('p');
        hint.className = 'fc-art-study-hint';
        hint.setAttribute('data-focuschrist-art-study-hint', 'true');
        hint.textContent = 'Open an artwork to view it full-size, study its gospel theme on the official Church website, or ask follow-up questions without losing your place in the gallery.';
        gallery.insertAdjacentElement('beforebegin', hint);
    }

    function currentGalleryItem() {
        const modalImage = document.getElementById('modalImage');
        if (!modalImage) return null;
        const currentSrc = modalImage.getAttribute('src') || '';
        const items = Array.from(document.querySelectorAll('.gallery-item'));
        return items.find(function (item) {
            const img = item.querySelector('img');
            if (!img) return false;
            const full = img.getAttribute('data-full-src') || img.getAttribute('src') || '';
            return full === currentSrc || img.getAttribute('src') === currentSrc;
        }) || null;
    }

    function syncArtworkUrl(caption) {
        if (!caption || !window.history || typeof window.history.replaceState !== 'function') return;
        const url = new URL(window.location.href);
        url.searchParams.set('art', caption);
        url.hash = '';
        window.history.replaceState(null, '', url.pathname + '?' + url.searchParams.toString());
    }

    function buildDrawer(drawer, route) {
        drawer.replaceChildren();
        const title = document.createElement('h3');
        title.className = 'fc-art-study-title';
        title.textContent = route.caption;
        drawer.appendChild(title);

        const copy = document.createElement('p');
        copy.className = 'fc-art-study-copy';
        copy.textContent = PICTURE_REFLECTIONS[route.caption] || document.getElementById('modalImage').alt;
        drawer.appendChild(copy);

        const links = document.createElement('div');
        links.className = 'fc-art-study-links';

        const official = document.createElement('a');
        official.href = officialSearch(route.query);
        official.target = '_blank';
        official.rel = 'noopener noreferrer';
        official.textContent = 'Church study resources';
        official.setAttribute('data-art-official-study', 'true');
        links.appendChild(official);

        const ask = document.createElement('a');
        ask.href = askUrl(route);
        ask.textContent = 'Ask about this picture';
        ask.setAttribute('data-art-ask', 'true');
        links.appendChild(ask);

        if (route.focus) {
            const focus = document.createElement('a');
            focus.href = route.focus;
            focus.textContent = 'Read the related study';
            focus.setAttribute('data-art-focus-study', 'true');
            links.appendChild(focus);
        }

        drawer.appendChild(links);
    }

    function refreshModalRoute(drawer) {
        const item = currentGalleryItem();
        const save = document.getElementById('artSaveImage');
        const image = document.getElementById('modalImage');
        if (save && image) {
            save.href = image.src;
            save.download = window.fcArtworkDownloadFilename(captionForItem(item) || image.alt || 'Artwork', image.src);
        }
        const caption = captionForItem(item) || 'This artwork';
        const route = routeForCaption(caption);
        buildDrawer(drawer, route);
        if (document.getElementById('imageModal')?.classList.contains('active')) syncArtworkUrl(caption);
    }

    function initModalStudy() {
        const modal = document.getElementById('imageModal');
        const modalImage = document.getElementById('modalImage');
        if (!modal || !modalImage || modal.querySelector('[data-focuschrist-art-study-button]')) return;

        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'fc-art-study-button';
        button.setAttribute('data-focuschrist-art-study-button', 'true');
        button.textContent = 'About this picture';

        const drawer = document.createElement('aside');
        drawer.className = 'fc-art-study-drawer';
        drawer.id = 'artPictureDetails';
        button.setAttribute('aria-controls', drawer.id);
        drawer.setAttribute('data-focuschrist-art-study-drawer', 'true');
        drawer.setAttribute('aria-live', 'polite');

        button.addEventListener('click', function (event) {
            event.stopPropagation();
            refreshModalRoute(drawer);
            drawer.classList.toggle('open');
            button.setAttribute('aria-expanded', drawer.classList.contains('open') ? 'true' : 'false');
        });
        button.setAttribute('aria-expanded', 'false');

        drawer.addEventListener('click', function (event) { event.stopPropagation(); });
        const actions = document.createElement('div');
        actions.className = 'fc-art-viewer-actions';
        const save = document.createElement('a');
        save.id = 'artSaveImage';
        save.textContent = 'Save image';
        save.setAttribute('download', '');
        actions.appendChild(button);
        actions.appendChild(save);
        const close = modal.querySelector('.close');
        if (close) actions.appendChild(close);
        modal.appendChild(actions);
        modal.appendChild(drawer);

        const observer = new MutationObserver(function () {
            if (modal.classList.contains('active')) refreshModalRoute(drawer);
            else {
                drawer.classList.remove('open');
                button.setAttribute('aria-expanded', 'false');
            }
        });
        observer.observe(modalImage, { attributes: true, attributeFilter: ['src'] });
        observer.observe(modal, { attributes: true, attributeFilter: ['class'] });
    }

    function restoreRequestedArtwork() {
        const params = new URLSearchParams(window.location.search);
        const requested = params.get('art');
        if (!requested || typeof window.openModal !== 'function') return;
        const oldTitle = Object.keys(TITLE_ALIASES).find(function (key) { return key.toLowerCase() === requested.trim().toLowerCase(); });
        const resolved = oldTitle ? TITLE_ALIASES[oldTitle] : requested.trim();
        const item = Array.from(document.querySelectorAll('.gallery-item')).find(function (candidate) {
            return captionForItem(candidate).toLowerCase() === resolved.toLowerCase();
        });
        if (!item) return;
        window.setTimeout(function () {
            try { item.scrollIntoView({ block: 'center', behavior: 'auto' }); } catch (_error) { item.scrollIntoView(); }
            window.openModal(item);
            document.documentElement.setAttribute('data-focuschrist-art-return-restored', 'true');
        }, 80);
    }

    function init() {
        ensureStyles();
        ensureHint();
        initModalStudy();
        restoreRequestedArtwork();
        document.documentElement.setAttribute('data-focuschrist-art-study-router', 'ready');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }
})();
