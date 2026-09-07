(() => {
  'use strict';

  const root = document.querySelector('[data-watch-theme-explorer]');
  if (!root || root.dataset.watchReady === 'true') return;
  root.dataset.watchReady = 'true';

  const data = {
    christ: {
      watch: {
        kicker: 'Watch',
        title: 'Jesus Christ Video Collection',
        copy: 'Return to the Savior-centered collection above and choose the message that fits your study.',
        href: '#life-of-christ'
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
        title: 'Prayer and Revelation Videos',
        copy: 'Return to the prayer and revelation collection and choose a message for the question you carry.',
        href: '#prayer-and-revelation'
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
        title: 'Book of Mormon Video Collection',
        copy: 'Return to the Book of Mormon collection and choose a scripture witness to watch and study.',
        href: '#book-of-mormon'
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
        title: 'Temple and Family Video Collection',
        copy: 'Return to the temple and family collection and choose the message that best serves your study.',
        href: '#temples-and-family'
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
