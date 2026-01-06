// ======================================================
// VEHÍCULOS - MEDINAUTOS
// SweetAlert2 + Animaciones
// ======================================================

document.addEventListener("DOMContentLoaded", () => {
    console.log("Vehículos JS cargado 🚗");

    // ==================================================
    // SWEETALERT - CONFIRMAR ELIMINACIÓN
    // ==================================================

    const deleteForms = document.querySelectorAll(".form-delete");

    deleteForms.forEach(form => {
        form.addEventListener("submit", function (e) {
            e.preventDefault(); // Evitamos envío inmediato

            Swal.fire({
                title: "¿Eliminar vehículo?",
                text: "Esta acción no se puede deshacer",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d81822",
                cancelButtonColor: "#6c757d",
                confirmButtonText: "Sí, eliminar",
                cancelButtonText: "Cancelar"
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit(); // Ahora sí enviamos
                }
            });
        });
    });

    // ==================================================
    // SWEETALERT - MENSAJES DE ÉXITO (CRUD)
    // ==================================================

    const params = new URLSearchParams(window.location.search);

    if (params.has("created")) {
        Swal.fire({
            icon: "success",
            title: "Vehículo creado",
            text: "El vehículo fue registrado correctamente",
            confirmButtonColor: "#d81822"
        });
    }

    if (params.has("updated")) {
        Swal.fire({
            icon: "success",
            title: "Vehículo actualizado",
            text: "Los cambios se guardaron correctamente",
            confirmButtonColor: "#d81822"
        });
    }

    if (params.has("deleted")) {
        Swal.fire({
            icon: "success",
            title: "Vehículo eliminado",
            text: "El vehículo fue eliminado del sistema",
            confirmButtonColor: "#d81822"
        });
    }

    // ==================================================
    // ANIMACIÓN SUAVE EN FILAS DE LA TABLA
    // ==================================================

    const rows = document.querySelectorAll(".vehiculos-table tbody tr");

    rows.forEach((row, index) => {
        row.style.opacity = "0";
        row.style.transform = "translateY(10px)";

        setTimeout(() => {
            row.style.transition = "all 0.4s ease";
            row.style.opacity = "1";
            row.style.transform = "translateY(0)";
        }, index * 60);
    });

});
