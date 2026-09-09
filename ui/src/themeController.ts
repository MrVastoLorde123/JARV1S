const STORAGE_KEY = 'jarvis-theme';

type Theme = 'dark' | 'light';

function readTheme(): Theme {
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return stored === 'light' ? 'light' : 'dark';
}

function applyTheme(theme: Theme, button: HTMLButtonElement) {
  document.documentElement.dataset.jarvisTheme = theme;
  button.dataset.theme = theme;
  button.title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
  button.setAttribute('aria-label', button.title);
  button.innerHTML = theme === 'dark'
    ? '<span class="theme-glyph" aria-hidden="true">☼</span><span>LIGHT</span>'
    : '<span class="theme-glyph" aria-hidden="true">◐</span><span>DARK</span>';
  window.localStorage.setItem(STORAGE_KEY, theme);
}

export function installThemeController() {
  if (document.querySelector('.global-theme-toggle')) return;

  const button = document.createElement('button');
  button.className = 'global-theme-toggle';
  button.type = 'button';
  button.addEventListener('click', () => {
    const next: Theme = document.documentElement.dataset.jarvisTheme === 'light' ? 'dark' : 'light';
    applyTheme(next, button);
  });

  window.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key.toLowerCase() === 'l') {
      event.preventDefault();
      const next: Theme = document.documentElement.dataset.jarvisTheme === 'light' ? 'dark' : 'light';
      applyTheme(next, button);
    }
  });

  document.body.appendChild(button);
  applyTheme(readTheme(), button);
}
