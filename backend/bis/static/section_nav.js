document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#content-main form");
  const fieldsets = [...form.querySelectorAll("h2.fieldset-heading")]
    .filter((heading) => !heading.closest(".djn-group"))
    .map((heading) => ({ heading, section: heading.closest("fieldset") }));
  // Only top-level inlines: nested ones live inside their parent's section.
  const inlines = [...form.querySelectorAll(".djn-group-root")].map(
    (group) => ({ heading: group.querySelector("h2.inline-heading"), section: group }),
  );

  const nav = document.createElement("nav");
  nav.className = "section-nav";
  const addLink = (text, onClick) => {
    const link = document.createElement("a");
    link.href = "#";
    link.textContent = text;
    link.addEventListener("click", (event) => {
      event.preventDefault();
      onClick();
    });
    nav.append(link);
  };

  addLink("Základní údaje", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  for (const { heading, section } of [...fieldsets, ...inlines]) {
    addLink(heading.textContent.trim(), () => {
      const details = heading.closest("details");
      if (details) details.open = true;
      window.scrollTo({
        top: section.getBoundingClientRect().top + window.scrollY - nav.offsetHeight,
        behavior: "smooth",
      });
    });
  }
  form.prepend(nav);
});
