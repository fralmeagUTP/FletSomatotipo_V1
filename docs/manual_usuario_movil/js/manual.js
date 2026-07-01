const sidebar = document.querySelector("#sidebar");
const menuButton = document.querySelector(".menu-button");
const search = document.querySelector("#manual-search");
const searchStatus = document.querySelector(".search-status");
const sections = [...document.querySelectorAll("[data-search-section]")];

menuButton?.addEventListener("click", () => {
  const open = sidebar.classList.toggle("open");
  menuButton.setAttribute("aria-expanded", String(open));
});

sidebar?.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
  sidebar.classList.remove("open");
  menuButton?.setAttribute("aria-expanded", "false");
}));

search?.addEventListener("input", () => {
  const query = search.value.trim().toLocaleLowerCase("es");
  let visible = 0;
  sections.forEach((section) => {
    const matches = !query || section.textContent.toLocaleLowerCase("es").includes(query);
    section.classList.toggle("search-hidden", !matches);
    visible += Number(matches);
  });
  searchStatus.textContent = query ? `${visible} sección(es) encontrada(s)` : "";
});

document.querySelector("[data-print]")?.addEventListener("click", () => window.print());

const lightbox = document.querySelector(".lightbox");
document.querySelectorAll(".image-button").forEach((button) => button.addEventListener("click", () => {
  const source = button.querySelector("img");
  const preview = lightbox.querySelector("img");
  preview.src = source.src;
  preview.alt = source.alt;
  lightbox.querySelector("p").textContent = button.closest("figure")?.querySelector("figcaption")?.textContent || "";
  lightbox.showModal();
}));

lightbox?.querySelector(".lightbox-close")?.addEventListener("click", () => lightbox.close());
lightbox?.addEventListener("click", (event) => {
  if (event.target === lightbox) lightbox.close();
});
