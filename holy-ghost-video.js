(function () {
    'use strict';
    const root = document.getElementById('holy-ghost-video');
    if (!root) return;
    const preview = root.querySelector('[data-video-preview]');
    const stage = root.querySelector('[data-video-stage]');
    const close = root.querySelector('[data-video-close]');
    const status = root.querySelector('[data-video-status]');
    let player = null;
    let timer = null;
    let generation = 0;
    let apiPromise;
    let apiScript;
    function loadAPI() {
        if (window.YT && window.YT.Player) return Promise.resolve(window.YT);
        if (apiPromise) return apiPromise;
        apiPromise = new Promise((resolve, reject) => {
            const previous = window.onYouTubeIframeAPIReady;
            window.onYouTubeIframeAPIReady = function () {
                if (typeof previous === 'function') previous();
                resolve(window.YT);
            };
            const script = document.createElement('script');
            apiScript = script;
            script.src = 'https://www.youtube.com/iframe_api';
            script.async = true;
            script.onerror = () => { apiPromise = null; script.remove(); reject(new Error('Player unavailable')); };
            document.head.appendChild(script);
        });
        return apiPromise;
    }
    function dispose() {
        clearTimeout(timer);
        if (player && typeof player.destroy === 'function') player.destroy();
        player = null;
        stage.replaceChildren();
        stage.hidden = true;
    }
    function fail(message, token) {
        if (token !== generation) return;
        generation++;
        if (!window.YT || !window.YT.Player) {
            apiPromise = null;
            if (apiScript) apiScript.remove();
        }
        dispose();
        preview.hidden = false;
        close.hidden = true;
        status.textContent = message;
        preview.focus({ preventScroll: true });
    }
    close.addEventListener('click', () => {
        generation++;
        dispose();
        preview.hidden = false;
        close.hidden = true;
        status.textContent = '';
        preview.focus({ preventScroll: true });
    });
    preview.addEventListener('click', () => {
        const token = ++generation;
        preview.hidden = true;
        stage.hidden = false;
        close.hidden = false;
        close.focus({ preventScroll: true });
        status.textContent = 'Loading the video…';
        const mount = document.createElement('div');
        stage.appendChild(mount);
        timer = setTimeout(() => fail('The video player did not become ready. Try again, or watch on YouTube below.', token), 15000);
        loadAPI().then(YT => {
            if (token !== generation) return;
            player = new YT.Player(mount, {
                width: '100%', height: '100%', videoId: 'AGS45Fd9nmE',
                playerVars: { autoplay: 0, playsinline: 1, rel: 0, origin: window.location.origin },
                events: {
                    onReady(event) {
                        if (token !== generation) return;
                        clearTimeout(timer);
                        status.textContent = 'The player is ready. Use its play button to begin.';
                        const frame = event.target.getIframe();
                        if (frame) frame.title = 'David A. Bednar: Is it the Holy Ghost or Me?';
                    },
                    onStateChange(event) {
                        if (token === generation && event.data === 1) status.textContent = '';
                    },
                    onError() { fail('This video could not play here. Watch it on YouTube below.', token); }
                }
            });
        }).catch(() => fail('The video player could not load. Watch it on YouTube below.', token));
    });
}());
