// ======================================================
// SERVICIOS - MEDINAUTOS
// Listado + CRUD via API
// ======================================================

const API_BASE = "/api";

document.addEventListener("DOMContentLoaded", () => {
    const formServicio = document.getElementById("form-servicio");
    const tablaServicios = document.getElementById("servicios-body");

    if (tablaServicios) {
        cargarServicios(tablaServicios);
    }

    if (formServicio) {
        prepararFormulario(formServicio);
    }
});

function prepararFormulario(formulario) {
    const modo = formulario.dataset.mode || "create";
    const servicioId = formulario.dataset.id;
    const submitBtn = formulario.querySelector("button[type='submit']");
    const precioInput = formulario.querySelector("input[name='precio']");
    const precioPreview = formulario.querySelector("[data-role='precio-preview']");

    const categoriasPromise = cargarCategoriasSelect(formulario);

    if (modo === "edit" && servicioId) {
        categoriasPromise.finally(() => cargarServicio(servicioId, formulario));
    }

    if (precioInput && precioPreview) {
        precioInput.addEventListener("input", () => actualizarPrecioPreview(formulario));
        actualizarPrecioPreview(formulario);
    }

    formulario.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = construirPayload(formulario, modo === "edit");

        if (!payload) {
            return;
        }

        const url = modo === "edit"
            ? `${API_BASE}/servicios/${servicioId}`
            : `${API_BASE}/servicios/`;
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
                throw new Error(detalle || "No se pudo guardar el servicio.");
            }

            await response.json();

            Swal.fire({
                icon: "success",
                title: modo === "edit" ? "Servicio actualizado" : "Servicio creado",
                text: modo === "edit"
                    ? "Los cambios se guardaron correctamente."
                    : "El servicio fue guardado correctamente.",
                confirmButtonText: "OK"
            }).then(() => {
                window.location.href = "/servicios";
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

async function cargarServicio(servicioId, formulario) {
    try {
        const response = await fetch(`${API_BASE}/servicios/${servicioId}`);

        if (!response.ok) {
            throw new Error("No se pudo cargar el servicio.");
        }

        const servicio = await response.json();

        formulario.nombre.value = servicio.nombre || "";
        formulario.descripcion.value = servicio.descripcion || "";
        formulario.precio.value = servicio.precio != null ? servicio.precio : "";
        if (formulario.categoria) {
            formulario.categoria.dataset.selectedValue = servicio.categoria || "";
            aplicarSeleccionCategoria(formulario.categoria);
        }

        if (formulario.activo) {
            formulario.activo.checked = Boolean(servicio.activo);
        }

        actualizarPrecioPreview(formulario);
    } catch (error) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: error.message
        }).then(() => {
            window.location.href = "/servicios";
        });
    }
}

function construirPayload(formulario, incluirActivo) {
    const nombre = formulario.nombre.value.trim();
    const descripcion = formulario.descripcion.value.trim();
    const categoria = formulario.categoria.value.trim();
    const precio = Number(formulario.precio.value);

    if (!nombre || !Number.isFinite(precio) || precio <= 0) {
        Swal.fire({
            icon: "warning",
            title: "Datos invalidos",
            text: "Revisa el nombre y el precio antes de continuar."
        });
        return null;
    }

    const payload = {
        nombre,
        descripcion: descripcion || null,
        precio,
        categoria: categoria || null
    };

    if (incluirActivo && formulario.activo) {
        payload.activo = Boolean(formulario.activo.checked);
    }

    return payload;
}

async function cargarServicios(tablaServicios) {
    try {
        const response = await fetch(`${API_BASE}/servicios/`);

        if (!response.ok) {
            throw new Error("No se pudo cargar el listado.");
        }

        const servicios = await response.json();
        renderServicios(tablaServicios, servicios);
        prepararAcciones(tablaServicios);
    } catch (error) {
        tablaServicios.innerHTML = `
            <tr>
                <td colspan="5" class="servicios-empty">${error.message}</td>
            </tr>
        `;
    }
}

function renderServicios(tablaServicios, servicios) {
    if (!servicios || servicios.length === 0) {
        tablaServicios.innerHTML = `
            <tr>
                <td colspan="5" class="servicios-empty">No hay servicios registrados.</td>
            </tr>
        `;
        return;
    }

    tablaServicios.innerHTML = servicios.map((servicio) => {
        const estadoClase = servicio.activo ? "badge-activo" : "badge-inactivo";
        const estadoTexto = servicio.activo ? "Activo" : "Inactivo";
        const precio = formatearPrecio(servicio.precio);

        return `
            <tr data-id="${servicio.id}">
                <td class="servicio-nombre">${servicio.nombre}</td>
                <td>${servicio.categoria || "-"}</td>
                <td>${precio}</td>
                <td data-role="estado">
                    <span class="badge ${estadoClase}">${estadoTexto}</span>
                </td>
                <td class="acciones">
                    <a href="/servicios/${servicio.id}/editar" class="btn-icon btn-edit" title="Editar servicio">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </a>
                    <button type="button"
                        class="btn-icon btn-toggle ${servicio.activo ? "" : "is-inactive"}"
                        data-id="${servicio.id}"
                        data-activo="${servicio.activo}">
                        <i class="fa-solid ${servicio.activo ? "fa-toggle-on" : "fa-toggle-off"}"></i>
                    </button>
                    <button type="button" class="btn-icon btn-delete"
                        data-id="${servicio.id}" data-nombre="${servicio.nombre}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function prepararAcciones(tablaServicios) {
    tablaServicios.querySelectorAll(".btn-delete").forEach((boton) => {
        boton.addEventListener("click", () => confirmarEliminacion(boton, tablaServicios));
    });

    tablaServicios.querySelectorAll(".btn-toggle").forEach((boton) => {
        boton.addEventListener("click", () => cambiarEstado(boton, tablaServicios));
    });
}

function confirmarEliminacion(boton, tablaServicios) {
    const servicioId = boton.dataset.id;
    const nombre = boton.dataset.nombre;

    Swal.fire({
        icon: "warning",
        title: "Eliminar servicio",
        html: `<p>Vas a eliminar el servicio:</p><strong>${nombre}</strong>`,
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
            const response = await fetch(`${API_BASE}/servicios/${servicioId}`, {
                method: "DELETE"
            });

            if (!response.ok) {
                const detalle = await obtenerDetalleError(response);
                throw new Error(detalle || "No se pudo eliminar el servicio.");
            }

            eliminarFila(tablaServicios, servicioId);

            Swal.fire({
                icon: "success",
                title: "Servicio eliminado",
                text: "El servicio fue eliminado correctamente."
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

async function cambiarEstado(boton, tablaServicios) {
    const servicioId = boton.dataset.id;

    try {
        const response = await fetch(`${API_BASE}/servicios/${servicioId}/toggle`, {
            method: "PATCH"
        });

        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudo cambiar el estado.");
        }

        const data = await response.json();
        actualizarEstadoFila(tablaServicios, data.id, data.activo);
    } catch (error) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: error.message
        });
    }
}

function actualizarEstadoFila(tablaServicios, servicioId, activo) {
    const fila = tablaServicios.querySelector(`tr[data-id='${servicioId}']`);
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
        toggleBtn.dataset.activo = activo;
        toggleBtn.classList.toggle("is-inactive", !activo);
        const icon = toggleBtn.querySelector("i");
        if (icon) {
            icon.className = `fa-solid ${activo ? "fa-toggle-on" : "fa-toggle-off"}`;
        }
    }
}

function eliminarFila(tablaServicios, servicioId) {
    const fila = tablaServicios.querySelector(`tr[data-id='${servicioId}']`);
    if (fila) {
        fila.remove();
    }

    if (tablaServicios.querySelectorAll("tr").length === 0) {
        tablaServicios.innerHTML = `
            <tr>
                <td colspan="5" class="servicios-empty">No hay servicios registrados.</td>
            </tr>
        `;
    }
}

function formatearPrecio(precio) {
    if (precio == null || Number.isNaN(Number(precio))) {
        return "-";
    }

    return Number(precio).toLocaleString("es-CO", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}

function actualizarPrecioPreview(formulario) {
    const precioInput = formulario.querySelector("input[name='precio']");
    const precioPreview = formulario.querySelector("[data-role='precio-preview']");

    if (!precioInput || !precioPreview) {
        return;
    }

    const valor = normalizarNumero(precioInput.value);
    if (!Number.isFinite(valor) || valor <= 0) {
        precioPreview.textContent = "";
        return;
    }

    precioPreview.textContent = `Valor: $${formatearPrecio(valor)}`;
}

async function cargarCategoriasSelect(formulario) {
    const select = formulario.querySelector("[data-role='categoria-select']");
    if (!select) {
        return Promise.resolve();
    }

    select.innerHTML = `<option value="">Sin categoria</option>`;

    try {
        const response = await fetch(`${API_BASE}/categorias-servicio/`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar las categorias.");
        }

        const categorias = await response.json();
        const activas = categorias.filter((categoria) => categoria.activo);

        activas.forEach((categoria) => {
            const option = document.createElement("option");
            option.value = categoria.nombre;
            option.textContent = categoria.nombre;
            select.appendChild(option);
        });

        aplicarSeleccionCategoria(select);
    } catch (error) {
        console.error(error);
    }
}

function aplicarSeleccionCategoria(select) {
    if (!select || !select.dataset.selectedValue) {
        return;
    }

    select.value = select.dataset.selectedValue;
}

function normalizarNumero(valor) {
    if (typeof valor !== "string") {
        return Number(valor);
    }

    const limpio = valor.replace(/[^0-9.,]/g, "").replace(",", ".");
    return Number(limpio);
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
