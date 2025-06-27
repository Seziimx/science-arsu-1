document.addEventListener("DOMContentLoaded", function () {
  fetch('/get-role')
    .then(response => response.json())
    .then(data => {
      const role = data.role;
      const nav = document.getElementById("navMenu");

      let links = [];
      if (role === "admin") {
        links = [
          { href: "/moderation", text: "Модерация" },
          { href: "/stats", text: "Есептер" }
        ];
      } else if (role === "student") {
        links = [
          { href: "/upload", text: "Жарияланым жүктеу" },
          { href: "/my-publications", text: "Менің жарияланымдарым" },
          { href: "/messages", text: "Хабарламалар" }
        ];
      }

      nav.innerHTML = links.map(link => `<li class="nav-item"><a class="nav-link" href="${link.href}">${link.text}</a></li>`).join("");
    });
});

function logout() {
  window.location.href = "/logout";
}
