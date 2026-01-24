// ======================================================
// PROVEEDORES - MEDINAUTOS
// ======================================================

const API_BASE = "/api";

document.addEventListener("DOMContentLoaded", () => {
    const tabla = document.getElementById("proveedores-body");
    const form = document.getElementById("form-proveedor");
    const btnCancelar = document.getElementById("btn-cancelar");

    if (tabla) {
        cargarProveedores(tabla);
    }

    if (form) {
        prepararFormulario(form, tabla);
    }

    if (btnCancelar && form) {
        btnCancelar.addEventListener("click", () => resetFormulario(form));
    }
});

function prepararFormulario(formulario, tabla) {
    formulario.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = construirPayload(formulario);
        if (!payload) {
            return;
        }

        const modo = formulario.dataset.mode || "create";
        const proveedorId = formulario.dataset.id;
        const url = modo === "edit"
            ? `${API_BASE}/almacen/proveedores/${proveedorId}`
            : `${API_BASE}/almacen/proveedores`;
        const method = modo === "edit" ? "PUT" : "POST";

        try {
            const response = await fetch(url, {
                method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const detalle = await obtenerDetalleError(response);
                throw new Error(detalle || "No se pudo guardar el proveedor.");
            }

            await response.json();
            resetFormulario(formulario);
            await cargarProveedores(tabla);

            Swal.fire({
                icon: "success",
                title: modo === "edit" ? "Proveedor actualizado" : "Proveedor creado",
                text: "Los cambios se guardaron correctamente."
            });
        } catch (error) {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: error.message
            });
        }
    });
}

async function cargarProveedores(tabla) {
    try {
        const response = await fetch(`${API_BASE}/almacen/proveedores`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar los proveedores.");
        }

        const proveedores = await response.json();
        renderProveedores(tabla, proveedores);
        prepararAcciones(tabla);
    } catch (error) {
        tabla.innerHTML = `
            <tr>
                <td colspan="4" class="categorias-empty">${error.message}</td>
            </tr>
        `;
    }
}

function renderProveedores(tabla, proveedores) {
    if (!proveedores || proveedores.length === 0) {
        tabla.innerHTML = `
            <tr>
                <td colspan="4" class="categorias-empty">No hay proveedores registrados.</td>
            </tr>
        `;
        return;
    }

    tabla.innerHTML = proveedores.map((proveedor) => {
        return `
            <tr data-id="${proveedor.id}">
                <td class="servicio-nombre">${proveedor.nombre}</td>
                <td>${proveedor.telefono || "-"}</td>
                <td>${proveedor.email || "-"}</td>
                <td class="acciones">
                    <button type="button" class="btn-icon btn-edit" data-id="${proveedor.id}">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button type="button" class="btn-icon btn-delete"
                        data-id="${proveedor.id}" data-nombre="${proveedor.nombre}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function prepararAcciones(tabla) {
    tabla.querySelectorAll(".btn-edit").forEach((boton) => {
        boton.addEventListener("click", () => editarProveedor(boton.dataset.id));
    });

    tabla.querySelectorAll(".btn-delete").forEach((boton) => {
        boton.addEventListener("click", () => eliminarProveedor(boton, tabla));
    });
}

async function editarProveedor(proveedorId) {
    const formulario = document.getElementById("form-proveedor");
    if (!formulario) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/almacen/proveedores/${proveedorId}`);
        if (!response.ok) {
            throw new Error("No se pudo cargar el proveedor.");
        }

        const proveedor = await response.json();
        formulario.nombre.value = proveedor.nombre || "";
        formulario.nit.value = proveedor.nit || "";
        formulario.telefono.value = proveedor.telefono || "";
        formulario.email.value = proveedor.email || "";
        formulario.direccion.value = proveedor.direccion || "";
        formulario.dataset.mode = "edit";
        formulario.dataset.id = proveedor.id;

        const titulo = document.querySelector("[data-role='form-title']");
        if (titulo) {
            titulo.textContent = "Editar proveedor";
        }
    } catch (error) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: error.message
        });
    }
}

function eliminarProveedor(boton, tabla) {
    const proveedorId = boton.dataset.id;
    const nombre = boton.dataset.nombre;

    Swal.fire({
        icon: "warning",
        title: "Eliminar proveedor",
        html: `<p>Vas a eliminar el proveedor:</p><strong>${nombre}</strong>`,
        showCancelButton: true,
        confirmButtonText: "Si, eliminar",
        cancelButtonText: "Cancelar",
        confirmButtonColor: "#d81822",
        cancelButtonColor: "#6b7280"
    }).then(async (result) => {
        if (!result.isConfirmed) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/almacen/proveedores/${proveedorId}`, {
                method: "DELETE"
            });

            if (!response.ok) {
                const detalle = await obtenerDetalleError(response);
                throw new Error(detalle || "No se pudo eliminar el proveedor.");
            }

            await cargarProveedores(tabla);
        } catch (error) {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: error.message
            });
        }
    });
}

function construirPayload(formulario) {
    const nombre = formulario.nombre.value.trim();
    const nit = formulario.nit.value.trim();
    const telefono = formulario.telefono.value.trim();
    const email = formulario.email.value.trim();
    const direccion = formulario.direccion.value.trim();

    if (!nombre) {
        Swal.fire({
            icon: "warning",
            title: "Datos invalidos",
            text: "El nombre del proveedor es obligatorio."
        });
        return null;
    }

    return {
        nombre,
        nit: nit || null,
        telefono: telefono || null,
        email: email || null,
        direccion: direccion || null
    };
}

function resetFormulario(formulario) {
    formulario.reset();
    formulario.dataset.mode = "create";
    delete formulario.dataset.id;

    const titulo = document.querySelector("[data-role='form-title']");
    if (titulo) {
        titulo.textContent = "Nuevo proveedor";
    }
}

async function obtenerDetalleError(response) {
    try {
        const data = await response.json();
        if (data && data.detail) {
            return data.detail;
        }
        return null;
    } catch (error) {
        return null;
    }
}
