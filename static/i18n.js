/* Shared live-shop / static-preview language conveniences. No customer data is stored. */
(() => {
  let messages = {};
  try {
    const parsed = JSON.parse(document.querySelector('#mahrukh-i18n')?.textContent || '{}');
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) messages = parsed;
  } catch { /* English remains usable if the optional catalog is unavailable. */ }
  function t(message, values = {}) {
    const translated = Object.prototype.hasOwnProperty.call(messages, message) &&
      typeof messages[message] === 'string' ? messages[message] : message;
    return translated.replace(/\{([A-Za-z_][A-Za-z0-9_]*)\}/g, (match, key) =>
      Object.prototype.hasOwnProperty.call(values, key) ? String(values[key]) : match);
  }

  const sizeInputs = [...document.querySelectorAll('input[type=radio][name=size], input[type=radio][name=demo-size]')];
  const designPreview = document.body.dataset.designPreview === 'true';
  const selectedSize = new URLSearchParams(location.search).get('size');
  const restoredSize = sizeInputs.find(input => input.value === selectedSize && !input.disabled);
  if (restoredSize) restoredSize.checked = true;

  function updateLanguageLinks() {
    const selected = sizeInputs.find(input => input.checked);
    document.querySelectorAll('[data-language-link]').forEach(link => {
      const destination = new URL(link.href, location.href);
      // The server or static exporter owns the target path and language. Keep all
      // other current filters, including future filters, without copying form data.
      new URLSearchParams(location.search).forEach((value, key) => {
        if (key !== 'lang') destination.searchParams.set(key, value);
      });
      if (designPreview && ['en', 'ur'].includes(link.dataset.language)) {
        destination.searchParams.set('lang', link.dataset.language);
      }
      if (selected) destination.searchParams.set('size', selected.value);
      destination.hash = location.hash;
      link.href = destination.href;
    });
  }
  updateLanguageLinks();
  sizeInputs.forEach(input => input.addEventListener('change', updateLanguageLinks));
  window.addEventListener('hashchange', updateLanguageLinks);

  function rememberPreviewLanguage(language) {
    if (!designPreview || !['en', 'ur'].includes(language)) return;
    try { localStorage.setItem('mahrukh-preview-language', language); } catch { /* Optional preference only. */ }
  }
  if (designPreview) {
    const explicit = new URLSearchParams(location.search).get('lang');
    let remembered = '';
    try { remembered = localStorage.getItem('mahrukh-preview-language'); } catch { /* Both languages still work. */ }
    const current = document.documentElement.lang;
    // A direct Urdu path is already an explicit destination. On the default
    // English entry page, honour a previous Urdu choice when no override exists.
    const wanted = ['en', 'ur'].includes(explicit) ? explicit :
      current === 'en' && remembered === 'ur' ? 'ur' : current;
    if (wanted !== current) {
      const target = [...document.querySelectorAll('[data-language-link]')].find(link => link.dataset.language === wanted);
      if (target) window.location.replace(target.href);
    } else rememberPreviewLanguage(current);
  }

  const languageSwitchers = [...document.querySelectorAll('[data-language-switcher]')];
  function closeLanguageSwitcher(switcher, restoreFocus = false) {
    if (!switcher?.open) return;
    switcher.open = false;
    if (restoreFocus) switcher.querySelector('summary')?.focus();
  }
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    const opened = languageSwitchers.find(switcher => switcher.open);
    if (!opened) return;
    event.preventDefault();
    closeLanguageSwitcher(opened, true);
  });
  function dismissOutsideLanguage(event) {
    languageSwitchers.filter(switcher => switcher.open && !switcher.contains(event.target))
      .forEach(switcher => closeLanguageSwitcher(switcher));
  }
  document.addEventListener('click', dismissOutsideLanguage);
  document.addEventListener('focusin', dismissOutsideLanguage);

  let submittingCheckout = false;
  function hasUnsavedCheckout() {
    if (submittingCheckout) return false;
    return [...document.querySelectorAll('[data-checkout-form], form.checkout-form')].some(form =>
      [...form.elements].some(field => {
        if (!field.name || field.disabled || ['hidden', 'submit', 'button', 'reset'].includes(field.type)) return false;
        if (['checkbox', 'radio'].includes(field.type)) return field.checked !== field.defaultChecked;
        if (field.tagName === 'SELECT') {
          const original = [...field.options].find(option => option.defaultSelected) || field.options[0];
          return field.value !== (original?.value || '');
        }
        return field.value !== field.defaultValue;
      })
    );
  }
  document.addEventListener('click', event => {
    const link = event.target.closest('[data-language-link]');
    if (!link) return;
    updateLanguageLinks();
    rememberPreviewLanguage(link.dataset.language);
    if (link.getAttribute('aria-current') === 'true' || link.getAttribute('aria-current') === 'page') {
      event.preventDefault();
      closeLanguageSwitcher(link.closest('[data-language-switcher]'), true);
      return;
    }
    // Opening another tab leaves this draft intact. A normal switch may reload
    // the checkout, so customers explicitly choose whether to leave it.
    if (!event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey && hasUnsavedCheckout()) {
      const leave = window.confirm(t('Your checkout details have not been submitted. Switching language will clear these details. Cancel to keep editing, or continue to switch language.'));
      if (!leave) { event.preventDefault(); return; }
      submittingCheckout = true;
    }
    closeLanguageSwitcher(link.closest('[data-language-switcher]'));
  });
  document.addEventListener('submit', event => {
    if (event.target.matches('[data-checkout-form], form.checkout-form')) submittingCheckout = true;
  });
  window.addEventListener('beforeunload', event => {
    if (!hasUnsavedCheckout()) return;
    event.preventDefault();
    event.returnValue = '';
  });
  window.addEventListener('pageshow', () => { submittingCheckout = false; });

  // Browser-generated validation usually follows the device language. Supply
  // customer-language messages while retaining native validation and focus.
  document.addEventListener('invalid', event => {
    const field = event.target;
    if (!field.matches('input, select, textarea') || field.closest('.studio')) return;
    field.setCustomValidity('');
    const state = field.validity;
    let message = '';
    if (state.valueMissing) message = ['radio', 'checkbox'].includes(field.type) || field.tagName === 'SELECT'
      ? t('Please choose an option.') : t('Please complete this field.');
    else if (state.typeMismatch) message = field.type === 'email'
      ? t('Please enter a valid email address.') : t('Please enter a valid value.');
    else if (state.rangeUnderflow) message = t('Please enter {min} or more.', {min: field.min});
    else if (state.rangeOverflow) message = t('Please enter {max} or less.', {max: field.max});
    else if (state.stepMismatch || state.badInput) message = t('Please enter a valid number.');
    else if (state.tooLong) message = t('Please use no more than {max} characters.', {max: field.maxLength});
    else if (state.patternMismatch) message = t('Please use the requested format.');
    if (message) field.setCustomValidity(message);
  }, true);
  function clearValidation(event) {
    const field = event.target;
    if (!field.matches('input, select, textarea')) return;
    field.setCustomValidity('');
    // Native required validation marks every radio in an empty group invalid.
    // Clear their custom messages together once an option has been selected.
    if (field.type === 'radio' && field.form) {
      [...field.form.elements].filter(other => other.type === 'radio' && other.name === field.name)
        .forEach(other => other.setCustomValidity(''));
    }
  }
  document.addEventListener('input', clearValidation);
  document.addEventListener('change', clearValidation);
  window.MahrukhI18n = Object.freeze({t, hasUnsavedCheckout});
})();
