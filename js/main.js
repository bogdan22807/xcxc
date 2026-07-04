(function () {
  const menuToggle = document.querySelector("[data-menu-toggle]");
  const mobileMenu = document.querySelector("[data-mobile-menu]");

  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener("click", () => {
      const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
      menuToggle.setAttribute("aria-expanded", String(!isOpen));
      mobileMenu.hidden = isOpen;
    });

    mobileMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        menuToggle.setAttribute("aria-expanded", "false");
        mobileMenu.hidden = true;
      });
    });
  }

  const quiz = document.querySelector("[data-quiz]");
  if (!quiz) return;

  const steps = [...quiz.querySelectorAll("[data-step]")];
  const dots = [...quiz.querySelectorAll("[data-dot]")];
  const nextBtn = quiz.querySelector("[data-quiz-next]");
  const submitBtn = quiz.querySelector("[data-quiz-submit]");
  let current = 0;

  function showStep(index) {
    steps.forEach((step, i) => {
      step.hidden = i !== index;
      step.classList.toggle("is-active", i === index);
    });

    dots.forEach((dot, i) => {
      dot.classList.toggle("is-active", i === index);
      dot.classList.toggle("is-done", i < index);
    });

    const isLast = index === steps.length - 1;
    nextBtn.hidden = isLast;
    submitBtn.hidden = !isLast;
    current = index;
  }

  function validateStep(index) {
    const step = steps[index];

    if (index === 0) {
      const checked = step.querySelector('input[name="site-type"]:checked');
      if (!checked) {
        alert("Оберіть тип сайту");
        return false;
      }
    }

    if (index === 1) {
      const checked = step.querySelector('input[name="budget"]:checked');
      if (!checked) {
        alert("Оберіть бюджет");
        return false;
      }
    }

    if (index === 3) {
      const name = step.querySelector('input[name="name"]');
      const phone = step.querySelector('input[name="phone"]');
      const email = step.querySelector('input[name="email"]');

      if (!name.value.trim() || !phone.value.trim() || !email.value.trim()) {
        alert("Заповніть усі поля");
        return false;
      }
    }

    return true;
  }

  nextBtn.addEventListener("click", () => {
    if (!validateStep(current)) return;
    if (current < steps.length - 1) showStep(current + 1);
  });

  submitBtn.addEventListener("click", () => {
    if (!validateStep(current)) return;

    const siteType = quiz.querySelector('input[name="site-type"]:checked')?.value;
    const budget = quiz.querySelector('input[name="budget"]:checked')?.value;
    const wishes = quiz.querySelector('textarea[name="wishes"]')?.value;
    const name = quiz.querySelector('input[name="name"]')?.value;
    const phone = quiz.querySelector('input[name="phone"]')?.value;
    const email = quiz.querySelector('input[name="email"]')?.value;

    submitBtn.textContent = "Заявку надіслано!";
    submitBtn.disabled = true;

    console.info("XTRA quiz submission:", { siteType, budget, wishes, name, phone, email });

    setTimeout(() => {
      quiz.querySelectorAll("input, textarea").forEach((el) => {
        if (el.type === "radio") el.checked = false;
        else el.value = "";
      });
      submitBtn.textContent = "Отримати розрахунок";
      submitBtn.disabled = false;
      showStep(0);
    }, 3000);
  });

  showStep(0);
})();
