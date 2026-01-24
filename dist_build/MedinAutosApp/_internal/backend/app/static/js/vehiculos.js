// ======================================================
// VEHÍCULOS - MEDINAUTOS
// SweetAlert2
// ======================================================

document.addEventListener("DOMContentLoaded", () => {
    console.log("Vehículos JS cargado 🚗");

    const params = new URLSearchParams(window.location.search);

    if (params.has("duplicate")) {
        Swal.fire({
            icon: "error",
            title: "Placa duplicada",
            text: "La placa ya existe en el sistema y no se puede registrar nuevamente.",
            confirmButtonColor: "#d81822"
        }).then(() => {
            window.history.replaceState({}, document.title, window.location.pathname);
        });
    }

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
});
