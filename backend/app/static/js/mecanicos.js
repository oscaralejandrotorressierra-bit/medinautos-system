// ======================================================
// MECANICOS - MEDINAUTOS
// Listado + CRUD via API
// ======================================================

const API_BASE = "/api";

document.addEventListener("DOMContentLoaded", () => {
    const tablaMecanicos = document.getElementById("mecanicos-body");
    const formMecanico = document.getElementById("form-mecanico");

    if (tablaMecanicos) {
        cargarMecanicos(tablaMecanicos);
    }

    if (formMecanico) {
        prepararFormulario(formMecanico);
    }
});

function prepararFormulario(formulario) {
    const modo = formulario.dataset.mode || "create";
    const mecanicoId = formulario.dataset.id;
    const submitBtn = formulario.querySelector("button[type='submit']");

    if (modo === "edit" && mecanicoId) {
        cargarMecanico(mecanicoId, formulario);
    }

    formulario.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = construirPayload(formulario, modo === "edit");
        if (!payload) {
            return;
        }

        const url = modo === "edit"
            ? `${API_BASE}/mecanicos/${mecanicoId}`
            : `${API_BASE}/mecanicos/`;
        const method = modo === "edit" ? "PUT" : "POST";

        try {
            if (submitBtn) {
                submitBtn.disabled = true;
            }

            const response = await fetch(url, {
                method,
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const detalle = await obtenerDetalleError(response);
                throw new Error(detalle || "No se pudo guardar el mecanico.");
            }

            await response.json();

            Swal.fire({
                icon: "success",
                title: modo === "edit" ? "Mecanico actualizado" : "Mecanico creado",
                text: "Los cambios se guardaron correctamente.",
                confirmButtonText: "OK"
            }).then(() => {
                window.location.href = "/mecanicos";
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
    const nombres = formulario.nombres.value.trim();
    const apellidos = formulario.apellidos.value.trim();
    const documento = formulario.documento.value.trim();
    const telefono = formulario.telefono.value.trim();
    const email = formulario.email.value.trim();
    const especialidad = formulario.especialidad.value.trim();
    const fechaIngreso = formulario.fecha_ingreso.value;

    if (!nombres || !apellidos || !documento) {
        Swal.fire({
            icon: "warning",
            title: "Datos invalidos",
            text: "Completa nombres, apellidos y documento."
        });
        return null;
    }

    const payload = {
        nombres,
        apellidos,
        documento,
        telefono: telefono || null,
        email: email || null,
        especialidad: especialidad || null,
        fecha_ingreso: fechaIngreso || null
    };

    if (incluirActivo && formulario.activo) {
        payload.activo = Boolean(formulario.activo.checked);
    }

    return payload;
}

async function cargarMecanico(mecanicoId, formulario) {
    try {
        const response = await fetch(`${API_BASE}/mecanicos/${mecanicoId}`);
        if (!response.ok) {
            throw new Error("No se pudo cargar el mecanico.");
        }

        const mecanico = await response.json();
        formulario.nombres.value = mecanico.nombres || "";
        formulario.apellidos.value = mecanico.apellidos || "";
        formulario.documento.value = mecanico.documento || "";
        formulario.telefono.value = mecanico.telefono || "";
        formulario.email.value = mecanico.email || "";
        formulario.especialidad.value = mecanico.especialidad || "";
        if (formulario.fecha_ingreso) {
            formulario.fecha_ingreso.value = mecanico.fecha_ingreso || "";
        }
        if (formulario.activo) {
            formulario.activo.checked = Boolean(mecanico.activo);
        }
    } catch (error) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: error.message
        }).then(() => {
            window.location.href = "/mecanicos";
        });
    }
}

async function cargarMecanicos(tablaMecanicos) {
    try {
        const response = await fetch(`${API_BASE}/mecanicos/`);
        if (!response.ok) {
            throw new Error("No se pudo cargar el listado.");
        }

        const mecanicos = await response.json();
        renderMecanicos(tablaMecanicos, mecanicos);
        prepararAcciones(tablaMecanicos);
    } catch (error) {
        tablaMecanicos.innerHTML = `
            <tr>
                <td colspan="6" class="servicios-empty">${error.message}</td>
            </tr>
        `;
    }
}

function renderMecanicos(tablaMecanicos, mecanicos) {
    if (!mecanicos || mecanicos.length === 0) {
        tablaMecanicos.innerHTML = `
            <tr>
                <td colspan="6" class="servicios-empty">No hay mecanicos registrados.</td>
            </tr>
        `;
        return;
    }

    tablaMecanicos.innerHTML = mecanicos.map((mecanico) => {
        const estadoClase = mecanico.activo ? "badge-activo" : "badge-inactivo";
        const estadoTexto = mecanico.activo ? "Activo" : "Inactivo";
        const nombre = `${mecanico.nombres} ${mecanico.apellidos}`.trim();

        return `
            <tr data-id="${mecanico.id}">
                <td class="servicio-nombre">${nombre}</td>
                <td>${mecanico.documento}</td>
                <td>${mecanico.telefono || "-"}</td>
                <td>${mecanico.especialidad || "-"}</td>
                <td data-role="estado">
                    <span class="badge ${estadoClase}">${estadoTexto}</span>
                </td>
                <td class="acciones">
                    <a href="/mecanicos/${mecanico.id}/editar" class="btn-icon btn-edit" title="Editar mecanico">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </a>
                    <button type="button"
                        class="btn-icon btn-toggle ${mecanico.activo ? "" : "is-inactive"}"
                        data-id="${mecanico.id}">
                        <i class="fa-solid ${mecanico.activo ? "fa-toggle-on" : "fa-toggle-off"}"></i>
                    </button>
                    <button type="button" class="btn-icon btn-delete"
                        data-id="${mecanico.id}" data-nombre="${nombre}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function prepararAcciones(tablaMecanicos) {
    tablaMecanicos.querySelectorAll(".btn-delete").forEach((boton) => {
        boton.addEventListener("click", () => confirmarEliminacion(boton, tablaMecanicos));
    });

    tablaMecanicos.querySelectorAll(".btn-toggle").forEach((boton) => {
        boton.addEventListener("click", () => cambiarEstado(boton, tablaMecanicos));
    });
}

function confirmarEliminacion(boton, tablaMecanicos) {
    const mecanicoId = boton.dataset.id;
    const nombre = boton.dataset.nombre;

    Swal.fire({
        icon: "warning",
        title: "Eliminar mecanico",
        html: `<p>Vas a eliminar al mecanico:</p><strong>${nombre}</strong>`,
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
            const response = await fetch(`${API_BASE}/mecanicos/${mecanicoId}`, {
                method: "DELETE"
            });

            if (!response.ok) {
                const detalle = await obtenerDetalleError(response);
                throw new Error(detalle || "No se pudo eliminar el mecanico.");
            }

            eliminarFila(tablaMecanicos, mecanicoId);

            Swal.fire({
                icon: "success",
                title: "Mecanico eliminado",
                text: "El mecanico fue eliminado correctamente."
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

async function cambiarEstado(boton, tablaMecanicos) {
    const mecanicoId = boton.dataset.id;

    try {
        const response = await fetch(`${API_BASE}/mecanicos/${mecanicoId}/toggle`, {
            method: "PATCH"
        });

        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudo cambiar el estado.");
        }

        const data = await response.json();
        actualizarEstadoFila(tablaMecanicos, data.id, data.activo);
    } catch (error) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: error.message
        });
    }
}

function actualizarEstadoFila(tablaMecanicos, mecanicoId, activo) {
    const fila = tablaMecanicos.querySelector(`tr[data-id='${mecanicoId}']`);
    if (!fila) {
        return;
    }

    const estadoCell = fila.querySelector("[data-role='estado']");
    const badge = estadoCell ? estadoCell.querySelector(".badge") : null;

    if (badge) {
        badge.textContent = activo ? "Activo" : "Inactivo";
        badge.classList.toggle("badge-activo", activo);
        badge.classList.toggle("badge-inactivo", !activo);
    }

    const toggleBtn = fila.querySelector(".btn-toggle");
    if (toggleBtn) {
        toggleBtn.classList.toggle("is-inactive", !activo);
        const icon = toggleBtn.querySelector("i");
        if (icon) {
            icon.className = `fa-solid ${activo ? "fa-toggle-on" : "fa-toggle-off"}`;
        }
    }
}

function eliminarFila(tablaMecanicos, mecanicoId) {
    const fila = tablaMecanicos.querySelector(`tr[data-id='${mecanicoId}']`);
    if (fila) {
        fila.remove();
    }

    if (tablaMecanicos.querySelectorAll("tr").length === 0) {
        tablaMecanicos.innerHTML = `
            <tr>
                <td colspan="6" class="servicios-empty">No hay mecanicos registrados.</td>
            </tr>
        `;
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
