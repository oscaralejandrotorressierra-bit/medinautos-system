// ======================================================
// ORDENES DE TRABAJO - MEDINAUTOS
// ======================================================

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
                    const response = await fetch(`/ordenes/${ordenId}`, {
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
    const totalLabel = document.getElementById("orden-total");
    let serviciosMap = {};

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
                const response = await fetch(`/ordenes/${ordenId}`, {
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
                const response = await fetch(`/ordenes/${ordenId}/estado?nuevo_estado=${nuevoEstado}`, {
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
                const response = await fetch("/detalle-orden/", {
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
}

async function cargarServicios(select) {
    const mapa = {};

    try {
        const response = await fetch("/servicios/");
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
        const response = await fetch(`/detalle-orden/orden/${ordenId}`);
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
                const response = await fetch(`/detalle-orden/${detalleId}?cantidad=${nuevaCantidad}`, {
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
                    const response = await fetch(`/detalle-orden/${detalleId}`, {
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

async function refrescarOrden(ordenId, totalLabel) {
    if (!totalLabel) {
        return;
    }

    try {
        const response = await fetch(`/ordenes/${ordenId}`);
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
