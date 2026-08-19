(function () {
  function wireLangToggle() {
    document.querySelectorAll(".lang-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        window.I18n.setLang(btn.getAttribute("data-lang"));
        window.I18n.applyStatic();
        if (typeof window.renderGallery === "function") window.renderGallery();
        if (window.LessonShell && typeof window.LessonShell.refresh === "function") {
          window.LessonShell.refresh();
        }
        if (window.ComicsReader && typeof window.ComicsReader.refreshLabels === "function") {
          window.ComicsReader.refreshLabels();
        }
      });
    });
  }

  window.initI18n = function initI18n() {
    window.I18n.applyStatic();
    wireLangToggle();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", window.initI18n);
  } else {
    window.initI18n();
  }
})();
