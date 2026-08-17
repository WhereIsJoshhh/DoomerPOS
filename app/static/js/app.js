document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.confirm-form').forEach(form => {
    form.addEventListener('submit', (event) => {
      const msg = form.dataset.confirm || '¿Confirmas esta acción?';
      if (!confirm(msg)) event.preventDefault();
    });
  });

  document.querySelectorAll('form').forEach(form => {
    if (window.DOOMERPOS_CSRF && !form.querySelector('input[name="_csrf_token"]')) {
      const token = document.createElement('input');
      token.type = 'hidden';
      token.name = '_csrf_token';
      token.value = window.DOOMERPOS_CSRF;
      form.appendChild(token);
    }
    form.addEventListener('submit', () => {
      const btn = form.querySelector('button[type="submit"], button:not([type])');
      if (btn && !btn.dataset.noLock) {
        btn.dataset.originalText = btn.textContent;
        btn.textContent = 'Procesando...';
        btn.disabled = true;
      }
    });
  });
});
