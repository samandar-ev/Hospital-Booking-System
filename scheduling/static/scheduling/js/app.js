// Progressive enhancements. Every form still works without this file.
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.addEventListener('click', (e) => {
    const dismiss = e.target.closest('[data-dismiss]');
    if (dismiss) dismiss.closest('.message')?.remove();

    const open = e.target.closest('[data-open]');
    if (open) document.getElementById(open.dataset.open)?.showModal();

    const close = e.target.closest('[data-close]');
    if (close) close.closest('dialog')?.close();

    const toggle = e.target.closest('[data-toggle-row]');
    if (toggle) {
      const row = document.getElementById(toggle.dataset.toggleRow);
      if (!row) return;
      row.hidden = !row.hidden;
      toggle.setAttribute('aria-expanded', String(!row.hidden));
      if (!row.hidden) row.querySelector('textarea, input, select')?.focus();
    }
  });

  // Drop placeholders that only repeat the field label.
  document.querySelectorAll('.field').forEach((field) => {
    const label = field.querySelector('label')?.textContent.trim().toLowerCase();
    const input = field.querySelector('[placeholder]');
    if (input && [label, 'none', 'yyyy-mm-dd'].includes(input.placeholder.trim().toLowerCase())) input.removeAttribute('placeholder');
  });

  // Replace Django's "---------" empty choice with a readable prompt.
  document.querySelectorAll('select.form-select option[value=""]').forEach((o) => {
    if (/^-+$/.test(o.textContent.trim())) o.textContent = 'Select';
  });

  // A custom decline reason requires a note.
  document.querySelectorAll('[data-reason-select]').forEach((select) => {
    const group = document.getElementById(select.dataset.customTarget);
    const sync = () => {
      const custom = select.value === 'CUSTOM';
      group.hidden = !custom;
      group.querySelector('textarea').required = custom;
    };
    select.addEventListener('change', sync);
    sync();
  });

  // Accept: fade the row's status bar to confirmed, then submit.
  document.querySelectorAll('form[data-accept]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      const row = form.closest('tr');
      if (!row || reduce || form.dataset.sent) return;
      e.preventDefault();
      form.dataset.sent = '1';
      form.querySelector('button').disabled = true;
      row.classList.add('is-accepting');
      setTimeout(() => form.submit(), 260);
    });
  });
})();
