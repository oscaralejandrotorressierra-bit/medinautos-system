// ================================
// DASHBOARD MEDINAUTOS - REAL DATA
// ================================

document.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch("/dashboard/data");
        const data = await response.json();

        animateCounter(
            document.getElementById("total-clientes"),
            data.clientes,
            1200
        );

        animateCounter(
            document.getElementById("total-vehiculos"),
            data.vehiculos,
            1200
        );

        document.getElementById("estado-sistema").textContent = data.estado;

    } catch (error) {
        console.error("Error cargando datos del dashboard:", error);
    }
});


// ================================
// CONTADOR ANIMADO
// ================================
function animateCounter(element, target, duration) {
    let start = 0;
    const increment = Math.ceil(target / (duration / 16));

    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            start = target;
            clearInterval(timer);
        }
        element.textContent = start;
    }, 16);
}
