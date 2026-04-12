/* ============================================================================
   ACT v2 — Base Interactions
   Dark mode toggle, client switcher, toast notifications
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // -------------------------------------------------------------------------
  // THEME TOGGLE (animated sun/moon)
  // -------------------------------------------------------------------------
  const themeToggle = document.querySelector('.theme-toggle');
  if (themeToggle) {
    // Restore saved theme
    const saved = localStorage.getItem('act-theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
    if (saved === 'dark') themeToggle.classList.add('night');

    themeToggle.addEventListener('click', () => {
      const html = document.documentElement;
      const goingDark = html.getAttribute('data-theme') === 'light';
      themeToggle.classList.add('transitioning');
      if (goingDark) themeToggle.classList.add('night'); else themeToggle.classList.remove('night');
      setTimeout(() => {
        html.setAttribute('data-theme', goingDark ? 'dark' : 'light');
        localStorage.setItem('act-theme', goingDark ? 'dark' : 'light');
      }, 400);
      setTimeout(() => themeToggle.classList.remove('transitioning'), 1000);
    });
  }

  // -------------------------------------------------------------------------
  // CLIENT SWITCHER
  // -------------------------------------------------------------------------
  const clientBtn = document.getElementById('clientSwitcher');
  const clientMenu = document.getElementById('clientMenu');
  if (clientBtn && clientMenu) {
    clientBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      clientMenu.classList.toggle('show');
    });
    document.addEventListener('click', () => clientMenu.classList.remove('show'));

    clientMenu.querySelectorAll('.dropdown-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const clientId = item.dataset.clientId;
        if (clientId) {
          // Navigate to same page with new client
          const url = new URL(window.location.href);
          url.searchParams.set('client', clientId);
          window.location.href = url.toString();
        }
      });
    });
  }

});

// -------------------------------------------------------------------------
// TOAST NOTIFICATIONS (global)
// -------------------------------------------------------------------------
function showToast(message, type) {
  type = type || 'info';
  document.querySelectorAll('.act-toast').forEach(t => t.remove());
  const toast = document.createElement('div');
  toast.className = 'act-toast act-toast--' + type;
  const icons = { success: 'check_circle', warning: 'undo', error: 'error', info: 'info' };
  toast.innerHTML = '<span class="material-symbols-outlined" style="font-size:18px">' +
    (icons[type] || 'info') + '</span>' + message;
  document.body.appendChild(toast);
  requestAnimationFrame(() => { requestAnimationFrame(() => toast.classList.add('show')); });
  setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 300); }, 3000);
}
