/* focusChrist Art -> scripture / official media / video study router.
 * Preserves artwork unchanged. Study connections appear only in the open modal.
 */
(function () {
    'use strict';

    const CHURCH_SEARCH = 'https://www.churchofjesuschrist.org/search?lang=eng&query=';
    const BIBLE_VIDEOS = 'https://www.churchofjesuschrist.org/study/videos-and-images/bible-videos?lang=eng';
    const BOM_VIDEOS = 'https://www.churchofjesuschrist.org/study/videos-and-images/book-of-mormon-videos?lang=eng';
    const GOSPEL_MEDIA = 'https://www.churchofjesuschrist.org/study/videos-and-images?lang=eng';
    const JESUS_VIDEOS = 'https://www.churchofjesuschrist.org/comeuntochrist/believe/jesus/videos';
    const CHANNEL = 'https://www.youtube.com/@theRisen636';

    const FEATURED = {
        'The Living Christ': { focus: 'art-study/the-living-christ.html', official: JESUS_VIDEOS, officialLabel: 'Official Jesus Christ videos', query: 'The Living Christ Jesus Christ' },
        'The Good Shepherd': { focus: 'art-study/the-good-shepherd.html', official: BIBLE_VIDEOS, officialLabel: 'Official Bible Videos', query: 'Good Shepherd Jesus Christ' },
        'Suffer the Little Children': { focus: 'art-study/suffer-the-little-children.html', official: BIBLE_VIDEOS, officialLabel: 'Official Bible Videos', query: 'Jesus children suffer little children' },
        'Be Still': { focus: 'art-study/be-still.html', official: CHURCH_SEARCH + encodeURIComponent('Be still Psalm 46 Jesus Christ'), officialLabel: 'Search official Church study', query: 'Be Still' }
    };

    const SCENE_HINTS = [
        { match: ['Jesus Baptized'], query: 'baptism of Jesus Christ', official: BIBLE_VIDEOS, label: 'Official Bible Videos' },
        { match: ['Jesus Boat'], query: 'Jesus Christ calms the storm', official: BIBLE_VIDEOS, label: 'Official Bible Videos' },
        { match: ['Jesus Feeding People','Jesus Feeding the Fish'], query: 'Jesus Christ feeding the five thousand', official: BIBLE_VIDEOS, label: 'Official Bible Videos' },
        { match: ['Jesus Leper','Now I See'], query: 'Jesus Christ healing miracles', official: BIBLE_VIDEOS, label: 'Official Bible Videos' },
        { match: ['Jesus Seven Times Seven','Let It Go'], query: 'Jesus Christ forgiveness seventy times seven', official: BIBLE_VIDEOS, label: 'Official Bible Videos' },
        { match: ['Palms','Jesus Walking Jerusalem'], query: 'Palm Sunday Jesus Christ Jerusalem', official: BIBLE_VIDEOS, label: 'Official Bible Videos' },
        { match: ['Widows Mite'], query: "widow's mite Jesus Christ", official: BIBLE_VIDEOS, label: 'Official Bible Videos' },
        { match: ['The Garden','There Is a Green Hill Far Away'], query: 'Jesus Christ Gethsemane Crucifixion Resurrection', official: BIBLE_VIDEOS, label: 'Official Bible Videos' },
        { match: ['Jesus with Apostles Sunflowers'], query: 'Jesus Christ Apostles teachings', official: BIBLE_VIDEOS, label: 'Official Bible Videos' },
        { match: ['Rest in the Lord, Trust in the Lord'], query: 'rest in the Lord trust in the Lord Psalms', official: CHURCH_SEARCH + encodeURIComponent('rest in the Lord trust in the Lord Psalms'), label: 'Search official Church study' },
        { match: ['See That Ye Be Not Troubled'], query: 'see that ye be not troubled Matthew 24', official: CHURCH_SEARCH + encodeURIComponent('see that ye be not troubled Matthew 24'), label: 'Search official Church study' },
        { match: ['Joy Cometh in the Morning'], query: 'joy cometh in the morning Psalms', official: CHURCH_SEARCH + encodeURIComponent('joy cometh in the morning Psalms'), label: 'Search official Church study' },
        { match: ['Blessed Be the Name of the Lord'], query: 'blessed be the name of the Lord Job', official: CHURCH_SEARCH + encodeURIComponent('blessed be the name of the Lord Job'), label: 'Search official Church study' },
        { match: ['Make a Joyful Noise Unto God'], query: 'make a joyful noise unto God Psalms', official: CHURCH_SEARCH + encodeURIComponent('make a joyful noise unto God Psalms'), label: 'Search official Church study' }
    ];

    function captionForItem(item) {
        const caption = item ? item.querySelector('.caption') : null;
        return caption ? caption.textContent.trim() : '';
    }

    function routeForCaption(caption) {
        if (FEATURED[caption]) return Object.assign({ caption: caption }, FEATURED[caption]);
        const hint = SCENE_HINTS.find(function (entry) { return entry.match.includes(caption); });
        if (hint) {
            return { caption: caption, focus: '', official: hint.official, officialLabel: hint.label, query: hint.query };
        }
        const query = caption || 'Jesus Christ';
        return { caption: caption || 'This artwork', focus: '', official: CHURCH_SEARCH + encodeURIComponent(query), officialLabel: 'Search official Church study', query: query };
    }

    function channelSearch(query) {
        return CHANNEL + '/search?query=' + encodeURIComponent(query || 'Jesus Christ');
    }

    function ensureStyles() {
        if (document.getElementById('focuschrist-art-study-router-styles')) return;
        const style = document.createElement('style');
        style.id = 'focuschrist-art-study-router-styles';
        style.textContent = `
            .fc-art-study-button{position:absolute;left:22px;bottom:18px;z-index:1002;min-height:42px;padding:8px 15px;border:1px solid rgba(240,204,130,.72);border-radius:999px;background:rgba(17,11,7,.90);color:#f0cc82;font:inherit;font-size:.82rem;font-weight:700;cursor:pointer;backdrop-filter:blur(8px)}
            .fc-art-study-button:hover,.fc-art-study-button:focus-visible{background:rgba(48,31,18,.96);color:#f8ead7;outline:none}
            .fc-art-study-drawer{position:absolute;left:18px;right:18px;bottom:72px;z-index:1003;display:none;max-width:760px;margin:0 auto;padding:16px;border:1px solid rgba(211,170,98,.40);border-radius:14px;background:rgba(16,10,6,.96);box-shadow:0 18px 50px rgba(0,0,0,.48);cursor:default}
            .fc-art-study-drawer.open{display:block}
            .fc-art-study-title{margin:0 0 10px;color:#f0cc82;font-family:Georgia,'Times New Roman',serif;font-size:1.15rem}
            .fc-art-study-copy{margin:0 0 12px;color:#baa18a;font-size:.84rem;line-height:1.55}
            .fc-art-study-links{display:flex;flex-wrap:wrap;gap:8px}
            .fc-art-study-links a{display:inline-flex;align-items:center;min-height:38px;padding:7px 12px;border:1px solid rgba(211,170,98,.32);border-radius:999px;background:rgba(211,170,98,.06);color:#f0cc82!important;text-decoration:none!important;font-size:.76rem;font-weight:700}
            .fc-art-study-links a:hover,.fc-art-study-links a:focus-visible{background:rgba(181,91,45,.14);border-color:#f0cc82;outline:none}
            .fc-art-study-hint{max-width:760px;margin:0 auto 6px;padding:0 18px;color:#a9937e;font-size:.82rem;text-align:center}
            @media(max-width:700px){.fc-art-study-button{left:12px;bottom:12px}.fc-art-study-drawer{left:10px;right:10px;bottom:62px;padding:13px}.fc-art-study-links{display:grid}.fc-art-study-links a{justify-content:center}}
        `;
        document.head.appendChild(style);
    }

    function ensureHint() {
        const gallery = document.querySelector('.gallery');
        if (!gallery || document.querySelector('[data-focuschrist-art-study-hint]')) return;
        const hint = document.createElement('p');
        hint.className = 'fc-art-study-hint';
        hint.setAttribute('data-focuschrist-art-study-hint', 'true');
        hint.textContent = 'Open an artwork to view it full-size and explore related scripture, official Church media, and video study paths.';
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

    function buildDrawer(drawer, route) {
        drawer.replaceChildren();
        const title = document.createElement('h3');
        title.className = 'fc-art-study-title';
        title.textContent = route.caption;
        drawer.appendChild(title);

        const copy = document.createElement('p');
        copy.className = 'fc-art-study-copy';
        copy.textContent = 'Continue from the image into scripture, verified Church resources, or related video study.';
        drawer.appendChild(copy);

        const links = document.createElement('div');
        links.className = 'fc-art-study-links';

        if (route.focus) {
            const focus = document.createElement('a');
            focus.href = route.focus;
            focus.textContent = 'focusChrist Art & Study';
            links.appendChild(focus);
        }

        const official = document.createElement('a');
        official.href = route.official || GOSPEL_MEDIA;
        official.target = '_blank';
        official.rel = 'noopener noreferrer';
        official.textContent = route.officialLabel || 'Official Church study';
        links.appendChild(official);

        const channel = document.createElement('a');
        channel.href = channelSearch(route.query);
        channel.target = '_blank';
        channel.rel = 'noopener noreferrer';
        channel.textContent = 'Related @theRisen636 videos';
        links.appendChild(channel);
        drawer.appendChild(links);
    }

    function refreshModalRoute(drawer) {
        const item = currentGalleryItem();
        const caption = captionForItem(item) || 'This artwork';
        buildDrawer(drawer, routeForCaption(caption));
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

    function init() {
        ensureStyles();
        ensureHint();
        initModalStudy();
        document.documentElement.setAttribute('data-focuschrist-art-study-router', 'ready');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }
})();