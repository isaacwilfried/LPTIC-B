// Menu mobile : seul script du site. Sans JavaScript, le menu reste visible.
document.documentElement.classList.add("js");
const btn = document.querySelector(".menu-btn");
const menu = document.getElementById("menu");
if (btn && menu) {
  btn.addEventListener("click", () => {
    const open = btn.getAttribute("aria-expanded") === "true";
    btn.setAttribute("aria-expanded", String(!open));
    menu.classList.toggle("open", !open);
  });
}
