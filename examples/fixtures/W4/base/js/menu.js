// Mobile navigation toggle.
document.addEventListener("DOMContentLoaded", function () {
  var button = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (!button || !nav) {
    return;
  }
  button.addEventListener("click", function () {
    var open = nav.classList.toggle("is-open");
    button.setAttribute("aria-expanded", String(open));
  });
});
