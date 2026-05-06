(function () {
  var year = document.getElementById("shellYear");
  if (year) {
    year.textContent = new Date().getFullYear();
  }

  var sidebar = document.getElementById("shellSidebar");
  var toggle = document.getElementById("shellSidebarToggle");
  var curtain = document.getElementById("shellMobileCurtain");

  if (!sidebar || !toggle || !curtain) {
    return;
  }

  function setOpen(open) {
    sidebar.classList.toggle("is-open", open);
    curtain.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    curtain.setAttribute("aria-hidden", open ? "false" : "true");
  }

  toggle.addEventListener("click", function () {
    setOpen(!sidebar.classList.contains("is-open"));
  });

  curtain.addEventListener("click", function () {
    setOpen(false);
  });
})();
