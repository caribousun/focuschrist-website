/* focusChrist Art -> topic study / official Church search / contextual Ask router.
 * Preserves artwork unchanged. Study connections appear only in the open modal.
 * Production hardening: no generic YouTube study exit; Ask carries artwork context and an exact return path.
 */
(function () {
    'use strict';

    const CHURCH_SEARCH = 'https://www.churchofjesuschrist.org/search?lang=eng&query=';

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
        { match: ['Jesus Feeding People', 'Jesus Feeding the Fish'], query: 'Jesus Christ feeding five thousand John 6' },
        { match: ['Jesus Fun', 'Little Friends'], query: 'Jesus Christ joy children discipleship' },
        { match: ['Jesus in Africa'], query: 'Jesus Christ all nations children of God' },
        { match: ['Jesus Leper', 'Now I See'], query: 'Jesus Christ healing miracles faith New Testament' },
        { match: ['Jesus Seven Times Seven', 'Let It Go'], query: 'Jesus Christ forgiveness seventy times seven Matthew 18' },
        { match: ['Palms', 'Jesus Walking Jerusalem'], query: 'Palm Sunday Jesus Christ Jerusalem triumphal entry' },
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
        if (FEATURED[caption]) return Object.assign({ caption: caption }, FEATURED[caption]);
        const hint = SCENE_HINTS.find(function (entry) { return entry.match.includes(caption); });
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
            .fc-art-study-button{position:absolute;left:22px;bottom:18px;z-index:1002;min-height:42px;padding:8px 15px;border:1px solid rgba(240,204,130,.72);border-radius:999px;background:rgba(17,11,7,.90);color:#f0cc82;font:inherit;font-size:.82rem;font-weight:700;cursor:pointer;backdrop-filter:blur(8px)}
            .fc-art-study-button:hover,.fc-art-study-button:focus-visible{background:rgba(48,31,18,.96);color:#f8ead7;outline:none}
            .fc-art-study-drawer{position:absolute;left:18px;right:18px;bottom:72px;z-index:1003;display:none;max-width:780px;margin:0 auto;padding:16px;border:1px solid rgba(211,170,98,.40);border-radius:14px;background:rgba(16,10,6,.97);box-shadow:0 18px 50px rgba(0,0,0,.48);cursor:default}
            .fc-art-study-drawer.open{display:block}
            .fc-art-study-title{margin:0 0 8px;color:#f0cc82;font-family:Georgia,'Times New Roman',serif;font-size:1.15rem}
            .fc-art-study-copy{margin:0 0 12px;color:#c8b4a0;font-size:.84rem;line-height:1.55}
            .fc-art-study-links{display:flex;flex-wrap:wrap;gap:8px}
            .fc-art-study-links a{display:inline-flex;align-items:center;justify-content:center;min-height:40px;padding:8px 13px;border:1px solid rgba(211,170,98,.34);border-radius:999px;background:rgba(211,170,98,.06);color:#f0cc82!important;text-decoration:none!important;font-size:.77rem;font-weight:700}
            .fc-art-study-links a[data-art-ask]{background:#f0cc82;color:#1c130c!important;border-color:#f0cc82}
            .fc-art-study-links a:hover,.fc-art-study-links a:focus-visible{background:rgba(181,91,45,.18);border-color:#f0cc82;outline:none}
            .fc-art-study-links a[data-art-ask]:hover,.fc-art-study-links a[data-art-ask]:focus-visible{background:#f7dfaa;color:#1c130c!important}
            .fc-art-study-hint{max-width:760px;margin:0 auto 6px;padding:0 18px;color:#a9937e;font-size:.82rem;text-align:center}
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
        copy.textContent = 'Continue with this exact subject. Search official Church study resources or open a contextual Ask conversation; when you return, focusChrist will reopen this artwork.';
        drawer.appendChild(copy);

        const links = document.createElement('div');
        links.className = 'fc-art-study-links';

        const official = document.createElement('a');
        official.href = officialSearch(route.query);
        official.target = '_blank';
        official.rel = 'noopener noreferrer';
        official.textContent = 'Study this topic on ChurchofJesusChrist.org';
        official.setAttribute('data-art-official-study', 'true');
        links.appendChild(official);

        const ask = document.createElement('a');
        ask.href = askUrl(route);
        ask.textContent = 'Ask about this artwork';
        ask.setAttribute('data-art-ask', 'true');
        links.appendChild(ask);

        if (route.focus) {
            const focus = document.createElement('a');
            focus.href = route.focus;
            focus.textContent = 'Open focusChrist Art & Study';
            focus.setAttribute('data-art-focus-study', 'true');
            links.appendChild(focus);
        }

        drawer.appendChild(links);
    }

    function refreshModalRoute(drawer) {
        const item = currentGalleryItem();
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
        button.textContent = 'Study this artwork';

        const drawer = document.createElement('aside');
        drawer.className = 'fc-art-study-drawer';
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
        modal.appendChild(button);
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
        const item = Array.from(document.querySelectorAll('.gallery-item')).find(function (candidate) {
            return captionForItem(candidate).toLowerCase() === requested.trim().toLowerCase();
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
