const LABELS: Record<string, string> = {
  'WORK': 'PROJECTS',
  'Open Work': 'Open Projects',
  'Open work →': 'Open projects →',
  'WORK · PROJECT CONTROL': 'PROJECTS · PROJECT CONTROL',
  'ACTIVE WORK': 'ACTIVE PROJECT',
};

function rewrite(root: ParentNode = document) {
  root.querySelectorAll<HTMLElement>('.top-context,.nav-item span,.command-list button b,.panel-kicker,.panel-heading > span,.panel-action,.workspace-project-link > span').forEach((node) => {
    const value = node.textContent?.trim();
    const replacement = value ? LABELS[value] : undefined;
    if (replacement && node.textContent !== replacement) node.textContent = replacement;
  });
}

export function installProjectLanguage() {
  rewrite();
  const observer = new MutationObserver(() => rewrite());
  observer.observe(document.body, { childList: true, subtree: true, characterData: true });
  window.addEventListener('beforeunload', () => observer.disconnect(), { once: true });
}
