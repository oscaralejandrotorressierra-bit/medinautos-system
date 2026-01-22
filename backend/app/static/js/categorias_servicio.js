// ======================================================
// CATEGORIAS DE SERVICIO - MEDINAUTOS
// CRUD via API
// ======================================================

document.addEventListener("DOMContentLoaded", () => {
    const tablaCategorias = document.getElementById("categorias-body");
    const formCategoria = document.getElementById("form-categoria");
    const btnCancelar = document.getElementById("btn-cancelar");

    if (tablaCategorias) {
        cargarCategorias(tablaCategorias);
    }

    if (formCategoria) {
        prepararFormulario(formCategoria, tablaCategorias);
    }

    if (btnCancelar && formCategoria) {
        btnCancelar.addEventListener("click", () => resetFormulario(formCategoria));
    }
});

function prepararFormulario(formulario, tablaCategorias) {
    formulario.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = construirPayload(formulario);
        if (!payload) {
            return;
        }

        const modo = formulario.dataset.mode || "create";
        const categoriaId = formulario.dataset.id;
        const url = modo === "edit" ? `/categorias-servicio/${categoriaId}` : "/categorias-servicio/";
        const method = modo === "edit" ? "PUT" : "POST";

        try {
            const response = await fetch(url, {
                method,
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const detalle = await obtenerDetalleError(response);
                throw new Error(detalle || "No se pudo guardar la categoria.");
            }

            await response.json();
            resetFormulario(formulario);
            await cargarCategorias(tablaCategorias);

            Swal.fire({
                icon: "success",
                title: modo === "edit" ? "Categoria actualizada" : "Categoria creada",
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

async function cargarCategorias(tablaCategorias) {
    if (!tablaCategorias) {
        return;
    }

    try {
        const response = await fetch("/categorias-servicio/");
        if (!response.ok) {
            throw new Error("No se pudieron cargar las categorias.");
        }

        const categorias = await response.json();
        renderCategorias(tablaCategorias, categorias);
        prepararAcciones(tablaCategorias);
    } catch (error) {
        tablaCategorias.innerHTML = `
            <tr>
                <td colspan="4" class="categorias-empty">${error.message}</td>
            </tr>
        `;
    }
}

function renderCategorias(tablaCategorias, categorias) {
    if (!categorias || categorias.length === 0) {
        tablaCategorias.innerHTML = `
            <tr>
                <td colspan="4" class="categorias-empty">No hay categorias registradas.</td>
            </tr>
        `;
        return;
    }

    tablaCategorias.innerHTML = categorias.map((categoria) => {
        const estadoClase = categoria.activo ? "badge-activo" : "badge-inactivo";
        const estadoTexto = categoria.activo ? "Activa" : "Inactiva";

        return `
            <tr data-id="${categoria.id}">
                <td class="servicio-nombre">${categoria.nombre}</td>
                <td>${categoria.descripcion || "-"}</td>
                <td data-role="estado">
                    <span class="badge ${estadoClase}">${estadoTexto}</span>
                </td>
                <td class="acciones">
                    <button type="button" class="btn-icon btn-edit" data-id="${categoria.id}">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button type="button"
                        class="btn-icon btn-toggle ${categoria.activo ? "" : "is-inactive"}"
                        data-id="${categoria.id}">
                        <i class="fa-solid ${categoria.activo ? "fa-toggle-on" : "fa-toggle-off"}"></i>
                    </button>
                    <button type="button" class="btn-icon btn-delete"
                        data-id="${categoria.id}" data-nombre="${categoria.nombre}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function prepararAcciones(tablaCategorias) {
    tablaCategorias.querySelectorAll(".btn-edit").forEach((boton) => {
        boton.addEventListener("click", () => editarCategoria(boton.dataset.id));
    });

    tablaCategorias.querySelectorAll(".btn-toggle").forEach((boton) => {
        boton.addEventListener("click", () => toggleCategoria(boton.dataset.id, tablaCategorias));
    });

    tablaCategorias.querySelectorAll(".btn-delete").forEach((boton) => {
        boton.addEventListener("click", () => eliminarCategoria(boton, tablaCategorias));
    });
}

async function editarCategoria(categoriaId) {
    const formulario = document.getElementById("form-categoria");
    if (!formulario) {
        return;
    }

    try {
        const response = await fetch(`/categorias-servicio/${categoriaId}`);
        if (!response.ok) {
            throw new Error("No se pudo cargar la categoria.");
        }

        const categoria = await response.json();

        formulario.nombre.value = categoria.nombre || "";
        formulario.descripcion.value = categoria.descripcion || "";
        if (formulario.activo) {
            formulario.activo.checked = Boolean(categoria.activo);
        }

        formulario.dataset.mode = "edit";
        formulario.dataset.id = categoria.id;

        const titulo = document.querySelector("[data-role='form-title']");
        if (titulo) {
            titulo.textContent = "Editar categoria";
        }
    } catch (error) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: error.message
        });
    }
}

async function toggleCategoria(categoriaId, tablaCategorias) {
    try {
        const response = await fetch(`/categorias-servicio/${categoriaId}/toggle`, {
            method: "PATCH"
        });

        if (!response.ok) {
            throw new Error("No se pudo cambiar el estado.");
        }

        const data = await response.json();
        actualizarEstadoFila(tablaCategorias, data.id, data.activo);
    } catch (error) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: error.message
        });
    }
}

function eliminarCategoria(boton, tablaCategorias) {
    const categoriaId = boton.dataset.id;
    const nombre = boton.dataset.nombre;

    Swal.fire({
        icon: "warning",
        title: "Eliminar categoria",
        html: `<p>Vas a eliminar la categoria:</p><strong>${nombre}</strong>`,
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
            const response = await fetch(`/categorias-servicio/${categoriaId}`, {
                method: "DELETE"
            });

            if (!response.ok) {
                const detalle = await obtenerDetalleError(response);
                throw new Error(detalle || "No se pudo eliminar la categoria.");
            }

            await cargarCategorias(tablaCategorias);

            Swal.fire({
                icon: "success",
                title: "Categoria eliminada",
                text: "La categoria fue eliminada correctamente."
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

function actualizarEstadoFila(tablaCategorias, categoriaId, activo) {
    const fila = tablaCategorias.querySelector(`tr[data-id='${categoriaId}']`);
    if (!fila) {
        return;
    }

    const estadoCell = fila.querySelector("[data-role='estado']");
    const badge = estadoCell ? estadoCell.querySelector(".badge") : null;

    if (badge) {
        badge.textContent = activo ? "Activa" : "Inactiva";
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

function construirPayload(formulario) {
    const nombre = formulario.nombre.value.trim();
    const descripcion = formulario.descripcion.value.trim();

    if (!nombre) {
        Swal.fire({
            icon: "warning",
            title: "Datos invalidos",
            text: "El nombre de la categoria es obligatorio."
        });
        return null;
    }

    const payload = {
        nombre,
        descripcion: descripcion || null
    };

    if (formulario.activo) {
        payload.activo = Boolean(formulario.activo.checked);
    }

    return payload;
}

function resetFormulario(formulario) {
    formulario.reset();
    formulario.dataset.mode = "create";
    delete formulario.dataset.id;

    const titulo = document.querySelector("[data-role='form-title']");
    if (titulo) {
        titulo.textContent = "Nueva categoria";
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
