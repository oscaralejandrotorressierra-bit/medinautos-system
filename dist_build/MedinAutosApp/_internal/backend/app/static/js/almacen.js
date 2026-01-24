// ======================================================
// ALMACEN - MEDINAUTOS
// ======================================================

const API_BASE = "/api";

document.addEventListener("DOMContentLoaded", () => {
    const tabla = document.getElementById("almacen-body");
    const form = document.getElementById("form-almacen");
    const proveedorSelect = document.querySelector("[data-role='proveedor-select']");

    if (tabla) {
        cargarItems(tabla);
    }

    if (proveedorSelect) {
        cargarProveedoresSelect(proveedorSelect);
    }

    if (form) {
        prepararInputsMoneda(form);
        prepararFormulario(form);
    }
});

function prepararInputsMoneda(formulario) {
    const inputs = formulario.querySelectorAll("[data-role='money-input']");
    inputs.forEach((input) => {
        input.addEventListener("input", () => {
            input.value = formatearMoneda(input.value);
        });
    });
}

async function cargarProveedoresSelect(select) {
    try {
        const response = await fetch(`${API_BASE}/almacen/proveedores`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar los proveedores.");
        }

        const proveedores = await response.json();
        proveedores.forEach((proveedor) => {
            const option = document.createElement("option");
            option.value = proveedor.id;
            option.textContent = proveedor.nombre;
            select.appendChild(option);
        });
    } catch (error) {
        console.error(error);
    }
}

async function cargarItems(tabla) {
    try {
        const [itemsRes, provRes] = await Promise.all([
            fetch(`${API_BASE}/almacen/items`),
            fetch(`${API_BASE}/almacen/proveedores`)
        ]);

        if (!itemsRes.ok) {
            throw new Error("No se pudo cargar el inventario.");
        }

        const items = await itemsRes.json();
        const proveedores = provRes.ok ? await provRes.json() : [];
        const proveedoresMap = Object.fromEntries(
            proveedores.map((prov) => [prov.id, prov.nombre])
        );

        renderItems(tabla, items, proveedoresMap);
        prepararAcciones(tabla);
    } catch (error) {
        tabla.innerHTML = `
            <tr>
                <td colspan="9" class="servicios-empty">${error.message}</td>
            </tr>
        `;
    }
}

function renderItems(tabla, items, proveedoresMap) {
    if (!items || items.length === 0) {
        tabla.innerHTML = `
            <tr>
                <td colspan="9" class="servicios-empty">No hay insumos registrados.</td>
            </tr>
        `;
        return;
    }

    tabla.innerHTML = items.map((item) => {
        const estadoClase = item.activo ? "badge-activo" : "badge-inactivo";
        const estadoTexto = item.activo ? "Activo" : "Inactivo";
        const proveedor = item.proveedor_id ? (proveedoresMap[item.proveedor_id] || "-") : "-";
        const alerta = item.stock_minimo > 0 && item.stock_actual <= item.stock_minimo;
        const stockClase = alerta ? "badge-alerta" : "badge-activo";

        return `
            <tr data-id="${item.id}">
                <td class="servicio-nombre">${item.nombre}</td>
                <td>${item.categoria || "-"}</td>
                <td>${item.unidad}</td>
                <td>
                    <span class="badge ${stockClase}">${formatearNumero(item.stock_actual)}</span>
                </td>
                <td>${formatearNumero(item.stock_minimo)}</td>
                <td>$${formatearNumero(item.valor_taller)}</td>
                <td>${proveedor}</td>
                <td data-role="estado">
                    <span class="badge ${estadoClase}">${estadoTexto}</span>
                </td>
                <td class="acciones">
                    <button type="button" class="btn-icon btn-edit btn-entrada" title="Entrada de stock"
                        data-id="${item.id}">
                        <i class="fa-solid fa-box"></i>
                    </button>
                    <a href="/almacen/${item.id}/editar" class="btn-icon btn-edit" title="Editar insumo">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </a>
                    <button type="button"
                        class="btn-icon btn-toggle ${item.activo ? "" : "is-inactive"}"
                        data-id="${item.id}">
                        <i class="fa-solid ${item.activo ? "fa-toggle-on" : "fa-toggle-off"}"></i>
                    </button>
                    <button type="button" class="btn-icon btn-delete"
                        data-id="${item.id}" data-nombre="${item.nombre}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

function prepararAcciones(tabla) {
    tabla.querySelectorAll(".btn-toggle").forEach((boton) => {
        boton.addEventListener("click", () => toggleItem(boton, tabla));
    });

    tabla.querySelectorAll(".btn-delete").forEach((boton) => {
        boton.addEventListener("click", () => eliminarItem(boton, tabla));
    });

    tabla.querySelectorAll(".btn-entrada").forEach((boton) => {
        boton.addEventListener("click", () => registrarEntrada(boton.dataset.id, tabla));
    });
}

async function registrarEntrada(itemId, tabla) {
    const { value: confirmed } = await Swal.fire({
        title: "Entrada de stock",
        html: `
            <input id="entrada-cantidad" type="number" min="0.01" step="0.01" class="swal2-input" placeholder="Cantidad">
            <input id="entrada-costo" type="number" min="0" step="0.01" class="swal2-input" placeholder="Valor proveedor (opcional)">
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: "Registrar",
        cancelButtonText: "Cancelar",
        preConfirm: () => {
            const cantidad = Number(document.getElementById("entrada-cantidad").value);
            const costo = document.getElementById("entrada-costo").value;

            if (!cantidad || cantidad <= 0) {
                Swal.showValidationMessage("Ingresa una cantidad valida.");
                return false;
            }

            return {
                cantidad,
                valor_unitario: costo ? Number(costo) : null
            };
        }
    });

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/almacen/items/${itemId}/entrada`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(confirmed)
        });

        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudo registrar la entrada.");
        }

        await cargarItems(tabla);
        Swal.fire({
            icon: "success",
            title: "Entrada registrada",
            text: "El stock fue actualizado correctamente."
        });
    } catch (error) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: error.message
        });
    }
}

async function toggleItem(boton, tabla) {
    const itemId = boton.dataset.id;

    try {
        const response = await fetch(`${API_BASE}/almacen/items/${itemId}/toggle`, {
            method: "PATCH"
        });

        if (!response.ok) {
            throw new Error("No se pudo cambiar el estado.");
        }

        await cargarItems(tabla);
    } catch (error) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: error.message
        });
    }
}

function eliminarItem(boton, tabla) {
    const itemId = boton.dataset.id;
    const nombre = boton.dataset.nombre;

    Swal.fire({
        icon: "warning",
        title: "Eliminar insumo",
        html: `<p>Vas a eliminar el insumo:</p><strong>${nombre}</strong>`,
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
            const response = await fetch(`${API_BASE}/almacen/items/${itemId}`, {
                method: "DELETE"
            });

            if (!response.ok) {
                const detalle = await obtenerDetalleError(response);
                throw new Error(detalle || "No se pudo eliminar el insumo.");
            }

            await cargarItems(tabla);
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
    const itemId = formulario.dataset.id;
    const submitBtn = formulario.querySelector("button[type='submit']");

    if (modo === "edit" && itemId) {
        cargarItem(itemId, formulario);
    }

    formulario.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = construirPayload(formulario, modo === "edit");
        if (!payload) {
            return;
        }

        const url = modo === "edit"
            ? `${API_BASE}/almacen/items/${itemId}`
            : `${API_BASE}/almacen/items`;
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
                throw new Error(detalle || "No se pudo guardar el insumo.");
            }

            await response.json();

            Swal.fire({
                icon: "success",
                title: modo === "edit" ? "Insumo actualizado" : "Insumo creado",
                text: "Los cambios se guardaron correctamente.",
                confirmButtonText: "OK"
            }).then(() => {
                window.location.href = "/almacen";
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
    const categoria = formulario.categoria.value.trim();
    const descripcion = formulario.descripcion.value.trim();
    const unidad = formulario.unidad.value.trim();
    const stockMinimo = Number(formulario.stock_minimo.value || 0);
    const valorProveedor = parsearMoneda(formulario.valor_proveedor.value);
    const valorTaller = parsearMoneda(formulario.valor_taller.value);
    const proveedorId = formulario.proveedor_id ? Number(formulario.proveedor_id.value) : null;

    if (!nombre || !unidad) {
        Swal.fire({
            icon: "warning",
            title: "Datos invalidos",
            text: "Completa el nombre y la unidad."
        });
        return null;
    }

    const payload = {
        nombre,
        categoria: categoria || null,
        descripcion: descripcion || null,
        unidad,
        stock_minimo: stockMinimo,
        valor_proveedor: valorProveedor,
        valor_taller: valorTaller,
        proveedor_id: proveedorId || null
    };

    if (incluirActivo && formulario.activo) {
        payload.activo = Boolean(formulario.activo.checked);
    }

    return payload;
}

async function cargarItem(itemId, formulario) {
    try {
        const response = await fetch(`${API_BASE}/almacen/items/${itemId}`);
        if (!response.ok) {
            throw new Error("No se pudo cargar el insumo.");
        }

        const item = await response.json();
        formulario.nombre.value = item.nombre || "";
        formulario.categoria.value = item.categoria || "";
        formulario.descripcion.value = item.descripcion || "";
        formulario.unidad.value = item.unidad || "unidad";
        formulario.stock_minimo.value = item.stock_minimo ?? 0;
        formulario.valor_proveedor.value = formatearMoneda(item.valor_proveedor ?? 0);
        formulario.valor_taller.value = formatearMoneda(item.valor_taller ?? 0);
        if (formulario.proveedor_id) {
            formulario.proveedor_id.value = item.proveedor_id || "";
        }
        if (formulario.activo) {
            formulario.activo.checked = Boolean(item.activo);
        }
    } catch (error) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: error.message
        }).then(() => {
            window.location.href = "/almacen";
        });
    }
}

function formatearNumero(valor) {
    return Number(valor || 0).toLocaleString("es-CO", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}

function formatearMoneda(valor) {
    if (valor == null || valor === "") {
        return "";
    }

    const numero = parsearMoneda(valor);
    if (!Number.isFinite(numero)) {
        return "";
    }

    return `$${Number(numero).toLocaleString("es-CO", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    })}`;
}

function parsearMoneda(valor) {
    if (valor == null || valor === "") {
        return 0;
    }

    const limpio = String(valor).replace(/[^0-9]/g, "");
    return limpio ? Number(limpio) : 0;
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
