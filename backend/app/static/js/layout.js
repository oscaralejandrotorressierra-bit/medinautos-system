const sidebar = document.getElementById("sidebar");
const toggleSidebar = document.getElementById("toggleSidebar");
const toggleTheme = document.getElementById("toggleTheme");

// Sidebar colapsable
toggleSidebar.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
});

// Dark / Light mode
toggleTheme.addEventListener("click", () => {
    document.body.classList.toggle("dark");

    const icon = toggleTheme.querySelector("i");
    icon.classList.toggle("fa-moon");
    icon.classList.toggle("fa-sun");
});
