// ======================================================
// HERRAMIENTAS - MEDINAUTOS
// ======================================================

const API_BASE = "/api";

document.addEventListener("DOMContentLoaded", () => {
    const tabla = document.getElementById("herramientas-body");
    const form = document.getElementById("form-herramienta");

    if (tabla) {
        cargarHerramientas(tabla);
    }

    if (form) {
        prepararFormulario(form);
    }
});

async function cargarHerramientas(tabla) {
    try {
        const response = await fetch(`${API_BASE}/herramientas/`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar las herramientas.");
        }

        const herramientas = await response.json();
        renderHerramientas(tabla, herramientas);
        prepararAcciones(tabla);
    } catch (error) {
        tabla.innerHTML = `
            <tr>
                <td colspan="6" class="servicios-empty">${error.message}</td>
            </tr>
        `;
    }
}

function renderHerramientas(tabla, herramientas) {
    if (!herramientas || herramientas.length === 0) {
        tabla.innerHTML = `
            <tr>
                <td colspan="6" class="servicios-empty">No hay herramientas registradas.</td>
            </tr>
        `;
        return;
    }

    tabla.innerHTML = herramientas.map((herramienta) => {
        const estadoClase = herramienta.activo ? "badge-activo" : "badge-inactivo";
        const estadoTexto = herramienta.activo ? "Activo" : "Inactivo";
        const estadoHerr = herramienta.estado || "disponible";

        return `
            <tr data-id="${herramienta.id}">
                <td class="servicio-nombre">${herramienta.nombre}</td>
                <td>${herramienta.codigo}</td>
                <td>${herramienta.ubicacion || "-"}</td>
                <td>$${formatearNumero(herramienta.valor)}</td>
                <td data-role="estado">
                    <span class="badge ${estadoClase}">${estadoTexto}</span>
                    <span class="badge badge-estado-${estadoHerr}">${estadoHerr}</span>
                </td>
                <td class="acciones">
                    <a href="/herramientas/${herramienta.id}/editar" class="btn-icon btn-edit" title="Editar herramienta">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </a>
                    <button type="button"
                        class="btn-icon btn-toggle ${herramienta.activo ? "" : "is-inactive"}"
                        data-id="${herramienta.id}">
                        <i class="fa-solid ${herramienta.activo ? "fa-toggle-on" : "fa-toggle-off"}"></i>
                    </button>
                    <button type="button" class="btn-icon btn-delete"
                        data-id="${herramienta.id}" data-nombre="${herramienta.nombre}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function prepararAcciones(tabla) {
    tabla.querySelectorAll(".btn-toggle").forEach((boton) => {
        boton.addEventListener("click", () => toggleHerramienta(boton, tabla));
    });

    tabla.querySelectorAll(".btn-delete").forEach((boton) => {
        boton.addEventListener("click", () => eliminarHerramienta(boton, tabla));
    });
}

async function toggleHerramienta(boton, tabla) {
    const herramientaId = boton.dataset.id;
    try {
        const response = await fetch(`${API_BASE}/herramientas/${herramientaId}/toggle`, {
            method: "PATCH"
        });
        if (!response.ok) {
            throw new Error("No se pudo cambiar el estado.");
        }
        await cargarHerramientas(tabla);
    } catch (error) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: error.message
        });
    }
}

function eliminarHerramienta(boton, tabla) {
    const herramientaId = boton.dataset.id;
    const nombre = boton.dataset.nombre;

    Swal.fire({
        icon: "warning",
        title: "Eliminar herramienta",
        html: `<p>Vas a eliminar la herramienta:</p><strong>${nombre}</strong>`,
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
            const response = await fetch(`${API_BASE}/herramientas/${herramientaId}`, {
                method: "DELETE"
            });
            if (!response.ok) {
                const detalle = await obtenerDetalleError(response);
                throw new Error(detalle || "No se pudo eliminar la herramienta.");
            }
            await cargarHerramientas(tabla);
        } catch (error) {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: error.message
            });
        }
    });
}

function prepararFormulario(formulario) {
    const modo = formulario.dataset.mode || "create";
    const herramientaId = formulario.dataset.id;
    const submitBtn = formulario.querySelector("button[type='submit']");

    if (modo === "edit" && herramientaId) {
        cargarHerramienta(herramientaId, formulario);
    }

    formulario.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = construirPayload(formulario, modo === "edit");
        if (!payload) {
            return;
        }

        const url = modo === "edit"
            ? `${API_BASE}/herramientas/${herramientaId}`
            : `${API_BASE}/herramientas/`;
        const method = modo === "edit" ? "PUT" : "POST";

        try {
            if (submitBtn) {
                submitBtn.disabled = true;
            }

            const response = await fetch(url, {
                method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const detalle = await obtenerDetalleError(response);
                throw new Error(detalle || "No se pudo guardar la herramienta.");
            }

            await response.json();
            Swal.fire({
                icon: "success",
                title: modo === "edit" ? "Herramienta actualizada" : "Herramienta creada",
                text: "Los cambios se guardaron correctamente."
            }).then(() => {
                window.location.href = "/herramientas";
            });
        } catch (error) {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: error.message
            });
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
            }
        }
    });
}

function construirPayload(formulario, incluirActivo) {
    const nombre = formulario.nombre.value.trim();
    const codigo = formulario.codigo.value.trim();
    const descripcion = formulario.descripcion.value.trim();
    const ubicacion = formulario.ubicacion.value.trim();
    const valor = Number(formulario.valor.value || 0);
    const estado = formulario.estado.value;

    if (!nombre || !codigo) {
        Swal.fire({
            icon: "warning",
            title: "Datos invalidos",
            text: "Completa el nombre y el codigo."
        });
        return null;
    }

    const payload = {
        nombre,
        codigo,
        descripcion: descripcion || null,
        ubicacion: ubicacion || null,
        valor,
        estado
    };

    if (incluirActivo && formulario.activo) {
        payload.activo = Boolean(formulario.activo.checked);
    }

    return payload;
}

async function cargarHerramienta(herramientaId, formulario) {
    try {
        const response = await fetch(`${API_BASE}/herramientas/${herramientaId}`);
        if (!response.ok) {
            throw new Error("No se pudo cargar la herramienta.");
        }

        const herramienta = await response.json();
        formulario.nombre.value = herramienta.nombre || "";
        formulario.codigo.value = herramienta.codigo || "";
        formulario.descripcion.value = herramienta.descripcion || "";
        formulario.ubicacion.value = herramienta.ubicacion || "";
        formulario.valor.value = herramienta.valor ?? 0;
        if (formulario.estado) {
            formulario.estado.value = herramienta.estado || "disponible";
        }
        if (formulario.activo) {
            formulario.activo.checked = Boolean(herramienta.activo);
        }
    } catch (error) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: error.message
        }).then(() => {
            window.location.href = "/herramientas";
        });
    }
}

function formatearNumero(valor) {
    return Number(valor || 0).toLocaleString("es-CO", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
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
