/* Shared controls; content remains accessible without JavaScript. */
(function () {
  const root = document.documentElement;
  const theme = document.getElementById("theme-toggle");
  const system = window.matchMedia("(prefers-color-scheme: dark)");
  function isDark() {
    const forced = root.getAttribute("data-theme");
    return forced ? forced === "dark" : system.matches;
  }
  function showTheme() {
    const dark = isDark();
    theme.setAttribute("aria-pressed", String(dark));
    theme.setAttribute("aria-label", dark ? theme.dataset.lightLabel : theme.dataset.darkLabel);
    theme.title = theme.getAttribute("aria-label");
  }
  theme.addEventListener("click", function () {
    const next = isDark() ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("conceito-theme", next); } catch (e) {}
    showTheme();
  });
  system.addEventListener("change", showTheme);
  window.addEventListener("storage", function (event) {
    if (event.key !== "conceito-theme") return;
    if (event.newValue === "dark" || event.newValue === "light") root.setAttribute("data-theme", event.newValue);
    else root.removeAttribute("data-theme");
    showTheme();
  });
  showTheme();
  document.querySelectorAll("[data-language-select]").forEach(function (select) {
    select.addEventListener("change", function () { select.form.submit(); });
  });
  const sidebar = document.getElementById("workspace-menu");
  const overlay = document.querySelector(".menu-overlay");
  const toggles = document.querySelectorAll("[data-menu-toggle]");
  let opener;
  function setMenu(open) {
    if (!sidebar) return;
    document.body.classList.toggle("menu-open", open);
    overlay.hidden = !open;
    toggles.forEach(function (button) { button.setAttribute("aria-expanded", String(open)); });
    if (open) sidebar.querySelector("a, button").focus();
    else if (opener) opener.focus();
  }
  toggles.forEach(function (button) {
    button.addEventListener("click", function () {
      opener = button;
      setMenu(!document.body.classList.contains("menu-open"));
    });
  });
  document.querySelectorAll("[data-menu-close]").forEach(function (button) {
    button.addEventListener("click", function () { setMenu(false); });
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      if (document.body.classList.contains("menu-open")) setMenu(false);
      document.querySelectorAll(".dropdown[open]").forEach(function (menu) {
        menu.open = false;
        menu.querySelector("summary").focus();
      });
    }
    if (event.key === "Tab" && document.body.classList.contains("menu-open")) {
      const elements = sidebar.querySelectorAll("a[href], button");
      const first = elements[0], last = elements[elements.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
  document.addEventListener("click", function (event) {
    document.querySelectorAll(".dropdown[open]").forEach(function (menu) {
      if (!menu.contains(event.target)) menu.open = false;
    });
  });
  window.matchMedia("(min-width: 1024px)").addEventListener("change", function (event) {
    if (event.matches && document.body.classList.contains("menu-open")) setMenu(false);
  });
})();
