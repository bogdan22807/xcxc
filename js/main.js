(function () {
  const header = document.querySelector('[data-header]');
  const form = document.querySelector('.contact-form');

  if (header) {
    const onScroll = () => {
      header.classList.toggle('is-scrolled', window.scrollY > 24);
    };

    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  if (form) {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const button = form.querySelector('.btn--submit');
      const original = button.textContent;

      button.textContent = 'Message sent';
      button.disabled = true;

      window.setTimeout(() => {
        form.reset();
        button.textContent = original;
        button.disabled = false;
      }, 2400);
    });
  }
})();
