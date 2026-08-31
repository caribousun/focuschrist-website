(() => {
  'use strict';

  const root = document.querySelector('[data-watch-theme-explorer]');
  if (!root || root.dataset.watchReady === 'true') return;
  root.dataset.watchReady = 'true';

  const data = {
    christ: {
      watch: {
        kicker: 'Watch',
        title: 'Because of Him',
        copy: 'Continue with an official Church video centered on the Savior, His Resurrection, and the hope made possible because of Him.',
        href: 'https://www.churchofjesuschrist.org/media/video/2020-02-4100-because-of-him-easter-video?lang=eng',
        thumb: 'https://www.churchofjesuschrist.org/imgs/3a960a019d9f6bb9a0abc1d6dba875c8d0aa13bf/full/!768,/0/default',
        external: true
      },
      study: {
        kicker: 'Study',
        title: 'Jesus Christ',
        copy: 'Continue into a permanent focusChrist Answer about His divine Sonship, Atonement, Resurrection, mission, and promised return.',
        href: 'answers/jesus-christ-latter-day-saint-beliefs.html'
      },
      continue: {
        kicker: 'Art & Study',
        title: 'The Living Christ',
        copy: 'Continue through visual study centered on the risen and living Savior, then follow the related scripture and study paths.',
        href: 'art-study/the-living-christ.html'
      }
    },
    prayer: {
      watch: {
        kicker: 'Watch',
        title: 'Hear Him',
        copy: 'Listen to the words and teachings of Jesus Christ and consider what it means to hear Him in your own discipleship.',
        href: 'https://www.churchofjesuschrist.org/study/video/easter-videos/2020-02-4000-this-easter-hearhim-jesus-christs-words-are-for-you-1080p?lang=eng',
        thumb: 'https://www.churchofjesuschrist.org/imgs/46BE164CBF18B911A146DA4838DC630D7FEBDD47/full/!768,/0/default',
        external: true
      },
      study: {
        kicker: 'Study',
        title: 'Prayer & Personal Revelation',
        copy: 'Study prayer, guidance from God, recognizing spiritual impressions, and faithful waiting when an answer is not immediate.',
        href: 'answers/prayer-and-personal-revelation.html'
      },
      continue: {
        kicker: 'Art & Study',
        title: 'Be Still',
        copy: 'Continue with Psalm 46:10 and a visual study path about trusting God and becoming still amid uncertainty.',
        href: 'art-study/be-still.html'
      }
    },
    book: {
      watch: {
        kicker: 'Watch',
        title: 'Jesus Christ Appears in the Ancient Americas',
        copy: 'Watch the resurrected Savior appear to the people in the Book of Mormon, then continue into the scriptural witness of Jesus Christ.',
        href: 'https://www.churchofjesuschrist.org/media/video/2022-07-0100-jesus-christ-appears-in-the-ancient-americas-3-nephi-8-11?lang=eng',
        thumb: 'https://www.churchofjesuschrist.org/imgs/18da2703093511ed8ad5eeeeac1ea1e004d5c967/full/!768,/0/default',
        external: true
      },
      study: {
        kicker: 'Study',
        title: 'What Is the Book of Mormon?',
        copy: 'Continue into a permanent Answer about the Book of Mormon as another testament of Jesus Christ and its relationship to the Bible.',
        href: 'answers/what-is-the-book-of-mormon.html'
      },
      continue: {
        kicker: 'Continue',
        title: 'Bible & Book of Mormon Together',
        copy: 'Explore how Latter-day Saints study two distinct scriptural witnesses together and what each contributes.',
        href: 'answers/bible-and-book-of-mormon-together.html'
      }
    },
    temples: {
      watch: {
        kicker: 'Watch',
        title: 'Welcome to the House of the Lord',
        copy: 'Watch an official introduction to the Christ-centered purpose of temples and the covenants made in these sacred spaces.',
        href: 'https://www.churchofjesuschrist.org/media/video/2023-10-0060-welcome-to-the-temple-video-president-nelson-elder-and-sister-christofferson?lang=eng',
        thumb: 'https://www.churchofjesuschrist.org/imgs/fbeeffd36f5d11eea80aeeeeac1e2a5eec857672/full/!768,/0/default',
        external: true
      },
      study: {
        kicker: 'Study',
        title: 'Why Latter-day Saints Build Temples',
        copy: 'Study worship, covenants, ordinances, eternal families, and service for the dead in a permanent focusChrist Answer.',
        href: 'answers/why-latter-day-saints-build-temples.html'
      },
      continue: {
        kicker: 'Ask',
        title: 'Ask Your Temple Question',
        copy: 'Continue with the specific question you have now and explore the answer with the focusChrist Ask experience.',
        href: 'ask.html'
      }
    }
  };

  const cards = {
    watch: root.querySelector('[data-watch-path="watch"]'),
    study: root.querySelector('[data-watch-path="study"]'),
    continue: root.querySelector('[data-watch-path="continue"]')
  };

  function renderCard(card, value) {
    if (!card || !value) return;
    const kicker = card.querySelector('.watch-path-kicker');
    const title = card.querySelector('.watch-path-title');
    const copy = card.querySelector('.watch-path-copy');
    if (kicker) kicker.textContent = value.kicker;
    if (title) title.textContent = value.title;
    if (copy) copy.textContent = value.copy;
    card.href = value.href;
    if (value.thumb) {
      card.style.setProperty('--watch-path-thumb', 'url("' + value.thumb + '")');
      card.setAttribute('data-watch-thumbnail-ready', 'true');
    } else {
      card.style.removeProperty('--watch-path-thumb');
      card.removeAttribute('data-watch-thumbnail-ready');
    }
    if (value.external) {
      card.target = '_blank';
      card.rel = 'noopener noreferrer';
    } else {
      card.removeAttribute('target');
      card.removeAttribute('rel');
    }
  }

  function setTheme(theme) {
    const selected = data[theme] || data.christ;
    Object.entries(cards).forEach(([key, card]) => renderCard(card, selected[key]));
    root.querySelectorAll('[data-watch-theme]').forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.watchTheme === theme));
    });
  }

  root.querySelectorAll('[data-watch-theme]').forEach((button) => {
    button.addEventListener('click', () => setTheme(button.dataset.watchTheme));
  });

  setTheme('christ');
})();
