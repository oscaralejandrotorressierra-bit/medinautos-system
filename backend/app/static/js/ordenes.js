// ======================================================
// ORDENES DE TRABAJO - MEDINAUTOS
// ======================================================

const API_BASE = "/api";

document.addEventListener("DOMContentLoaded", () => {
    const deleteButtons = document.querySelectorAll(".btn-orden-delete");
    if (deleteButtons.length > 0) {
        prepararEliminacionOrdenes(deleteButtons);
    }

    const ordenLayout = document.querySelector(".orden-layout");
    if (ordenLayout) {
        prepararDetalleOrden(ordenLayout);
    }
});

function prepararEliminacionOrdenes(botones) {
    botones.forEach((boton) => {
        boton.addEventListener("click", () => {
            const ordenId = boton.dataset.id;
            const numero = boton.dataset.numero || ordenId;

            Swal.fire({
                icon: "warning",
                title: "Eliminar orden",
                html: `<p>Estas a punto de eliminar la orden:</p><strong>#${numero}</strong>`,
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
                    const response = await fetch(`${API_BASE}/ordenes/${ordenId}`, {
                        method: "DELETE"
                    });

                    if (!response.ok) {
                        const detalle = await obtenerDetalleError(response);
                        throw new Error(detalle || "No se pudo eliminar la orden.");
                    }

                    const fila = boton.closest("tr");
                    if (fila) {
                        fila.remove();
                    }

                    Swal.fire({
                        icon: "success",
                        title: "Orden eliminada",
                        text: "La orden fue eliminada correctamente."
                    });
                } catch (error) {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: error.message
                    });
                }
            });
        });
    });
}

function prepararDetalleOrden(layout) {
    const ordenId = layout.dataset.ordenId;
    const formOrden = document.getElementById("form-orden");
    const estadoSelect = document.getElementById("estado-select");
    const detalleForm = document.getElementById("form-detalle");
    const detalleBody = document.getElementById("detalle-body");
    const servicioSelect = document.querySelector("[data-role='servicio-select']");
    const insumoForm = document.getElementById("form-insumo");
    const insumoBody = document.getElementById("insumo-body");
    const insumoSelect = document.querySelector("[data-role='insumo-select']");
    const mecanicoForm = document.getElementById("form-mecanico");
    const mecanicoBody = document.getElementById("mecanico-body");
    const mecanicoSelect = document.querySelector("[data-role='mecanico-select']");
    const totalLabel = document.getElementById("orden-total");
    let serviciosMap = {};
    let insumosMap = {};

    if (formOrden) {
        formOrden.addEventListener("submit", async (event) => {
            event.preventDefault();

            const payload = {
                descripcion: formOrden.descripcion.value.trim(),
                cliente_id: Number(formOrden.cliente_id.value),
                vehiculo_id: Number(formOrden.vehiculo_id.value)
            };

            if (!payload.descripcion || !payload.cliente_id || !payload.vehiculo_id) {
                Swal.fire({
                    icon: "warning",
                    title: "Datos invalidos",
                    text: "Completa la descripcion, cliente y vehiculo."
                });
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/ordenes/${ordenId}`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const detalle = await obtenerDetalleError(response);
                    throw new Error(detalle || "No se pudo actualizar la orden.");
                }

                Swal.fire({
                    icon: "success",
                    title: "Orden actualizada",
                    text: "Los cambios fueron guardados correctamente."
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

    if (estadoSelect) {
        estadoSelect.addEventListener("change", async () => {
            const nuevoEstado = estadoSelect.value;
            try {
                const response = await fetch(`${API_BASE}/ordenes/${ordenId}/estado?nuevo_estado=${nuevoEstado}`, {
                    method: "PUT"
                });

                if (!response.ok) {
                    const detalle = await obtenerDetalleError(response);
                    throw new Error(detalle || "No se pudo cambiar el estado.");
                }

                Swal.fire({
                    icon: "success",
                    title: "Estado actualizado",
                    text: "El estado de la orden se actualizo correctamente."
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

    if (detalleForm && detalleBody) {
        detalleForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const servicioId = Number(detalleForm.servicio_id.value);
            const cantidad = Number(detalleForm.cantidad.value);

            if (!servicioId || !cantidad || cantidad < 1) {
                Swal.fire({
                    icon: "warning",
                    title: "Datos invalidos",
                    text: "Selecciona un servicio y una cantidad valida."
                });
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/detalle-orden/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        orden_id: Number(ordenId),
                        servicio_id: servicioId,
                        cantidad
                    })
                });

                if (!response.ok) {
                    const detalle = await obtenerDetalleError(response);
                    throw new Error(detalle || "No se pudo agregar el servicio.");
                }

                detalleForm.reset();
                await cargarDetalleOrden(ordenId, detalleBody, serviciosMap);
                await refrescarOrden(ordenId, totalLabel);

                Swal.fire({
                    icon: "success",
                    title: "Servicio agregado",
                    text: "El servicio se agrego correctamente."
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

    if (servicioSelect) {
        cargarServicios(servicioSelect).then((mapa) => {
            serviciosMap = mapa;
            if (detalleBody) {
                cargarDetalleOrden(ordenId, detalleBody, serviciosMap);
            }
        });
    }

    if (insumoSelect) {
        cargarInsumos(insumoSelect).then((mapa) => {
            insumosMap = mapa;
            if (insumoBody) {
                cargarDetalleInsumos(ordenId, insumoBody, insumosMap);
            }
        });
    }

    if (insumoForm && insumoBody && insumoSelect) {
        insumoForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const itemId = Number(insumoForm.item_id.value);
            const cantidad = Number(insumoForm.cantidad.value);

            if (!itemId || !cantidad || cantidad <= 0) {
                Swal.fire({
                    icon: "warning",
                    title: "Datos invalidos",
                    text: "Selecciona un insumo y una cantidad valida."
                });
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/detalle-almacen/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        orden_id: Number(ordenId),
                        item_id: itemId,
                        cantidad
                    })
                });

                if (!response.ok) {
                    const detalle = await obtenerDetalleError(response);
                    throw new Error(detalle || "No se pudo agregar el insumo.");
                }

                insumoForm.reset();
                await cargarDetalleInsumos(ordenId, insumoBody, insumosMap);
                await refrescarOrden(ordenId, totalLabel);

                Swal.fire({
                    icon: "success",
                    title: "Insumo agregado",
                    text: "El insumo se agrego correctamente."
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

    if (mecanicoSelect) {
        cargarMecanicos(mecanicoSelect);
    }

    if (mecanicoBody) {
        cargarAsignacionesMecanicos(ordenId, mecanicoBody);
    }

    if (mecanicoForm && mecanicoBody && mecanicoSelect) {
        mecanicoForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const mecanicoId = Number(mecanicoForm.mecanico_id.value);
            const observaciones = mecanicoForm.observaciones.value.trim() || null;

            if (!mecanicoId) {
                Swal.fire({
                    icon: "warning",
                    title: "Datos invalidos",
                    text: "Selecciona un mecanico."
                });
                return;
            }

            try {
                const response = await fetch(
                    `${API_BASE}/mecanicos/${mecanicoId}/asignar/${ordenId}`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ observaciones })
                    }
                );

                if (!response.ok) {
                    const detalle = await obtenerDetalleError(response);
                    throw new Error(detalle || "No se pudo asignar el mecanico.");
                }

                mecanicoForm.reset();
                await cargarAsignacionesMecanicos(ordenId, mecanicoBody);

                Swal.fire({
                    icon: "success",
                    title: "Mecanico asignado",
                    text: "El mecanico fue asignado correctamente."
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
}

async function cargarServicios(select) {
    const mapa = {};

    try {
        const response = await fetch(`${API_BASE}/servicios/`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar los servicios.");
        }

        const servicios = await response.json();
        const activos = servicios.filter((servicio) => servicio.activo);

        activos.forEach((servicio) => {
            mapa[servicio.id] = servicio.nombre;
            const option = document.createElement("option");
            option.value = servicio.id;
            option.textContent = `${servicio.nombre} ($${formatearPrecio(servicio.precio)})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error(error);
    }

    return mapa;
}

async function cargarDetalleOrden(ordenId, detalleBody, serviciosMap) {
    try {
        const response = await fetch(`${API_BASE}/detalle-orden/orden/${ordenId}`);
        if (!response.ok) {
            throw new Error("No se pudo cargar el detalle.");
        }

        const detalles = await response.json();

        if (!detalles || detalles.length === 0) {
            detalleBody.innerHTML = `
                <tr>
                    <td colspan="5" class="servicios-empty">No hay servicios agregados.</td>
                </tr>
            `;
            return;
        }

        detalleBody.innerHTML = detalles.map((detalle) => {
            const nombreServicio = serviciosMap[detalle.servicio_id] || `Servicio #${detalle.servicio_id}`;
            return `
                <tr data-id="${detalle.id}">
                    <td>${nombreServicio}</td>
                    <td>${detalle.cantidad}</td>
                    <td>$${formatearPrecio(detalle.precio_unitario)}</td>
                    <td>$${formatearPrecio(detalle.subtotal)}</td>
                    <td class="acciones">
                        <button type="button" class="btn-icon btn-edit btn-detalle-edit" data-id="${detalle.id}"
                            data-cantidad="${detalle.cantidad}">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button type="button" class="btn-icon btn-delete btn-detalle-delete" data-id="${detalle.id}">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join("");

        prepararAccionesDetalle(detalleBody, ordenId, serviciosMap);
    } catch (error) {
        detalleBody.innerHTML = `
            <tr>
                <td colspan="5" class="servicios-empty">${error.message}</td>
            </tr>
        `;
    }
}

async function cargarMecanicos(select) {
    try {
        const response = await fetch(`${API_BASE}/mecanicos/`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar los mecanicos.");
        }

        const mecanicos = await response.json();
        const activos = mecanicos.filter((mecanico) => mecanico.activo);

        activos.forEach((mecanico) => {
            const option = document.createElement("option");
            option.value = mecanico.id;
            option.textContent = `${mecanico.nombres} ${mecanico.apellidos} - ${mecanico.documento}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error(error);
    }
}

async function cargarAsignacionesMecanicos(ordenId, mecanicoBody) {
    try {
        const response = await fetch(`${API_BASE}/mecanicos/ordenes/${ordenId}`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar los mecanicos.");
        }

        const asignaciones = await response.json();

        if (!asignaciones || asignaciones.length === 0) {
            mecanicoBody.innerHTML = `
                <tr>
                    <td colspan="5" class="servicios-empty">No hay mecanicos asignados.</td>
                </tr>
            `;
            return;
        }

        mecanicoBody.innerHTML = asignaciones.map((asignacion) => {
            const mecanico = asignacion.mecanico || {};
            const nombre = `${mecanico.nombres || ""} ${mecanico.apellidos || ""}`.trim();
            const especialidad = mecanico.especialidad || "-";
            const observaciones = asignacion.observaciones || "-";
            const fecha = formatearFecha(asignacion.fecha_asignacion);

            return `
                <tr data-mecanico-id="${mecanico.id}">
                    <td>${nombre || "Mecanico"}</td>
                    <td>${especialidad}</td>
                    <td>${fecha}</td>
                    <td>${observaciones}</td>
                    <td class="acciones">
                        <button type="button" class="btn-icon btn-delete btn-mecanico-delete" data-mecanico-id="${mecanico.id}">
                            <i class="fa-solid fa-user-minus"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join("");

        prepararAccionesMecanicos(mecanicoBody, ordenId);
    } catch (error) {
        mecanicoBody.innerHTML = `
            <tr>
                <td colspan="5" class="servicios-empty">${error.message}</td>
            </tr>
        `;
    }
}

function prepararAccionesMecanicos(mecanicoBody, ordenId) {
    mecanicoBody.querySelectorAll(".btn-mecanico-delete").forEach((boton) => {
        boton.addEventListener("click", () => {
            const mecanicoId = boton.dataset.mecanicoId;

            Swal.fire({
                icon: "warning",
                title: "Quitar mecanico",
                text: "Esta accion no se puede deshacer.",
                showCancelButton: true,
                confirmButtonText: "Si, quitar",
                cancelButtonText: "Cancelar",
                confirmButtonColor: "#d81822",
                cancelButtonColor: "#6b7280"
            }).then(async (result) => {
                if (!result.isConfirmed) {
                    return;
                }

                try {
                    const response = await fetch(
                        `${API_BASE}/mecanicos/${mecanicoId}/asignar/${ordenId}`,
                        { method: "DELETE" }
                    );

                    if (!response.ok) {
                        const detalle = await obtenerDetalleError(response);
                        throw new Error(detalle || "No se pudo quitar el mecanico.");
                    }

                    await cargarAsignacionesMecanicos(ordenId, mecanicoBody);
                } catch (error) {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: error.message
                    });
                }
            });
        });
    });
}

function prepararAccionesDetalle(detalleBody, ordenId, serviciosMap) {
    detalleBody.querySelectorAll(".btn-detalle-edit").forEach((boton) => {
        boton.addEventListener("click", async () => {
            const detalleId = boton.dataset.id;
            const cantidadActual = boton.dataset.cantidad;

            const result = await Swal.fire({
                title: "Editar cantidad",
                input: "number",
                inputLabel: "Cantidad",
                inputValue: cantidadActual,
                inputAttributes: {
                    min: 1
                },
                showCancelButton: true,
                confirmButtonText: "Guardar",
                cancelButtonText: "Cancelar",
                confirmButtonColor: "#d81822"
            });

            if (!result.isConfirmed) {
                return;
            }

            const nuevaCantidad = Number(result.value);
            if (!nuevaCantidad || nuevaCantidad < 1) {
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/detalle-orden/${detalleId}?cantidad=${nuevaCantidad}`, {
                    method: "PUT"
                });

                if (!response.ok) {
                    const detalle = await obtenerDetalleError(response);
                    throw new Error(detalle || "No se pudo actualizar el servicio.");
                }

                await cargarDetalleOrden(ordenId, detalleBody, serviciosMap);
                await refrescarOrden(ordenId, document.getElementById("orden-total"));
            } catch (error) {
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: error.message
                });
            }
        });
    });

    detalleBody.querySelectorAll(".btn-detalle-delete").forEach((boton) => {
        boton.addEventListener("click", () => {
            const detalleId = boton.dataset.id;

            Swal.fire({
                icon: "warning",
                title: "Eliminar servicio",
                text: "Esta accion no se puede deshacer.",
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
                    const response = await fetch(`${API_BASE}/detalle-orden/${detalleId}`, {
                        method: "DELETE"
                    });

                    if (!response.ok) {
                        const detalle = await obtenerDetalleError(response);
                        throw new Error(detalle || "No se pudo eliminar el servicio.");
                    }

                    await cargarDetalleOrden(ordenId, detalleBody, serviciosMap);
                    await refrescarOrden(ordenId, document.getElementById("orden-total"));
                } catch (error) {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: error.message
                    });
                }
            });
        });
    });
}

async function cargarInsumos(select) {
    const mapa = {};

    try {
        const response = await fetch(`${API_BASE}/almacen/items`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar los insumos.");
        }

        const items = await response.json();
        const activos = items.filter((item) => item.activo);

        activos.forEach((item) => {
            mapa[item.id] = {
                nombre: item.nombre,
                valor: item.valor_taller
            };

            const option = document.createElement("option");
            option.value = item.id;
            option.textContent = `${item.nombre} (${item.unidad}) - $${formatearPrecio(item.valor_taller)}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error(error);
    }

    return mapa;
}

async function cargarDetalleInsumos(ordenId, insumoBody, insumosMap) {
    try {
        const response = await fetch(`${API_BASE}/detalle-almacen/orden/${ordenId}`);
        if (!response.ok) {
            throw new Error("No se pudo cargar el detalle de insumos.");
        }

        const detalles = await response.json();

        if (!detalles || detalles.length === 0) {
            insumoBody.innerHTML = `
                <tr>
                    <td colspan="5" class="servicios-empty">No hay insumos agregados.</td>
                </tr>
            `;
            return;
        }

        insumoBody.innerHTML = detalles.map((detalle) => {
            const item = insumosMap[detalle.item_id];
            const nombre = item ? item.nombre : `Insumo #${detalle.item_id}`;
            return `
                <tr data-id="${detalle.id}">
                    <td>${nombre}</td>
                    <td>${detalle.cantidad}</td>
                    <td>$${formatearPrecio(detalle.precio_unitario)}</td>
                    <td>$${formatearPrecio(detalle.subtotal)}</td>
                    <td class="acciones">
                        <button type="button" class="btn-icon btn-edit btn-insumo-edit" data-id="${detalle.id}"
                            data-cantidad="${detalle.cantidad}">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button type="button" class="btn-icon btn-delete btn-insumo-delete" data-id="${detalle.id}">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join("");

        prepararAccionesInsumos(insumoBody, ordenId, insumosMap);
    } catch (error) {
        insumoBody.innerHTML = `
            <tr>
                <td colspan="5" class="servicios-empty">${error.message}</td>
            </tr>
        `;
    }
}

function prepararAccionesInsumos(insumoBody, ordenId, insumosMap) {
    insumoBody.querySelectorAll(".btn-insumo-edit").forEach((boton) => {
        boton.addEventListener("click", async () => {
            const detalleId = boton.dataset.id;
            const cantidadActual = boton.dataset.cantidad;

            const result = await Swal.fire({
                title: "Editar cantidad",
                input: "number",
                inputLabel: "Cantidad",
                inputValue: cantidadActual,
                inputAttributes: {
                    min: 0.01,
                    step: 0.01
                },
                showCancelButton: true,
                confirmButtonText: "Guardar",
                cancelButtonText: "Cancelar",
                confirmButtonColor: "#d81822"
            });

            if (!result.isConfirmed) {
                return;
            }

            const nuevaCantidad = Number(result.value);
            if (!nuevaCantidad || nuevaCantidad <= 0) {
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/detalle-almacen/${detalleId}?cantidad=${nuevaCantidad}`, {
                    method: "PUT"
                });

                if (!response.ok) {
                    const detalle = await obtenerDetalleError(response);
                    throw new Error(detalle || "No se pudo actualizar el insumo.");
                }

                await cargarDetalleInsumos(ordenId, insumoBody, insumosMap);
                await refrescarOrden(ordenId, document.getElementById("orden-total"));
            } catch (error) {
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: error.message
                });
            }
        });
    });

    insumoBody.querySelectorAll(".btn-insumo-delete").forEach((boton) => {
        boton.addEventListener("click", () => {
            const detalleId = boton.dataset.id;

            Swal.fire({
                icon: "warning",
                title: "Eliminar insumo",
                text: "Esta accion no se puede deshacer.",
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
                    const response = await fetch(`${API_BASE}/detalle-almacen/${detalleId}`, {
                        method: "DELETE"
                    });

                    if (!response.ok) {
                        const detalle = await obtenerDetalleError(response);
                        throw new Error(detalle || "No se pudo eliminar el insumo.");
                    }

                    await cargarDetalleInsumos(ordenId, insumoBody, insumosMap);
                    await refrescarOrden(ordenId, document.getElementById("orden-total"));
                } catch (error) {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: error.message
                    });
                }
            });
        });
    });
}

async function refrescarOrden(ordenId, totalLabel) {
    if (!totalLabel) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/ordenes/${ordenId}`);
        if (!response.ok) {
            return;
        }

        const data = await response.json();
        totalLabel.textContent = `$${formatearPrecio(data.total || 0)}`;
    } catch (error) {
        console.error(error);
    }
}

function formatearPrecio(valor) {
    return Number(valor).toLocaleString("es-CO", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}

function formatearFecha(valor) {
    if (!valor) {
        return "-";
    }

    let fechaTexto = valor;
    if (typeof fechaTexto === "string" && !/[zZ]|[+-]\d{2}:\d{2}$/.test(fechaTexto)) {
        fechaTexto = `${fechaTexto}Z`;
    }

    const fecha = new Date(fechaTexto);
    if (Number.isNaN(fecha.getTime())) {
        return valor;
    }

    return fecha.toLocaleString("es-CO", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit"
    });
}

async function obtenerDetalleError(response) {
    try {
        const data = await response.json();
        if (data && data.detail) {
            if (Array.isArray(data.detail)) {
                return data.detail.map((item) => item.msg || "Solicitud invalida").join(", ");
            }
            if (typeof data.detail === "string") {
                return data.detail;
            }
            return "Solicitud invalida";
        }
        return null;
    } catch (error) {
        return null;
    }
}
