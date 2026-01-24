// ======================================================
// NOMINA - MEDINAUTOS
// ======================================================

const API_BASE = "/api";
let mecanicosCache = [];
let liquidacionesCache = [];

document.addEventListener("DOMContentLoaded", () => {
    const formLiquidacion = document.getElementById("form-liquidacion");
    const mecanicoSelect = document.getElementById("mecanico-select");
    const filtroMecanico = document.getElementById("filtro-mecanico");
    const filtroDesde = document.getElementById("filtro-desde");
    const filtroHasta = document.getElementById("filtro-hasta");
    const filtroEstado = document.getElementById("filtro-estado");
    const limpiarFiltros = document.getElementById("btn-limpiar-filtros");

    if (formLiquidacion) {
        formLiquidacion.addEventListener("submit", onCrearLiquidacion);
    }

    cargarMecanicos().then(() => {
        if (mecanicoSelect) {
            activarSelectBuscable(mecanicoSelect, "Buscar mecanico...");
        }
        if (filtroMecanico) {
            cargarFiltroMecanico(filtroMecanico);
            activarSelectBuscable(filtroMecanico, "Filtrar mecanico...");
        }
    });
    cargarLiquidaciones();

    [filtroMecanico, filtroDesde, filtroHasta, filtroEstado].forEach((control) => {
        if (control) {
            control.addEventListener("change", aplicarFiltros);
        }
    });
    if (limpiarFiltros) {
        limpiarFiltros.addEventListener("click", () => {
            if (filtroMecanico) filtroMecanico.value = "";
            if (filtroDesde) filtroDesde.value = "";
            if (filtroHasta) filtroHasta.value = "";
            if (filtroEstado) filtroEstado.value = "";
            aplicarFiltros();
        });
    }
});

async function cargarMecanicos() {
    const select = document.getElementById("mecanico-select");
    if (!select) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/mecanicos/`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar los mecanicos.");
        }
        mecanicosCache = await response.json();
        select.innerHTML = `<option value="">Seleccione un mecanico</option>` +
            mecanicosCache.map((mecanico) => {
                const nombre = `${mecanico.nombres} ${mecanico.apellidos}`.trim();
                return `<option value="${mecanico.id}">${nombre}</option>`;
            }).join("");
    } catch (error) {
        mostrarError("Mecanicos", error.message);
    }
}

async function onCrearLiquidacion(event) {
    event.preventDefault();
    const form = event.target;
    const payload = {
        mecanico_id: Number(form.mecanico_id.value),
        fecha_inicio: form.fecha_inicio.value,
        fecha_fin: form.fecha_fin.value,
        frecuencia: form.frecuencia.value,
        observaciones: form.observaciones.value.trim() || null
    };

    if (!payload.mecanico_id || !payload.fecha_inicio || !payload.fecha_fin) {
        mostrarError("Nomina", "Completa mecanico y fechas.");
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/contabilidad/liquidaciones/mecanicos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudo crear la liquidacion.");
        }

        await response.json();
        form.reset();
        await cargarLiquidaciones();
        Swal.fire({ icon: "success", title: "Liquidacion creada" });
    } catch (error) {
        mostrarError("Nomina", error.message);
    }
}

async function cargarLiquidaciones() {
    const tabla = document.querySelector("#tabla-liquidaciones tbody");
    if (!tabla) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/contabilidad/liquidaciones/mecanicos`);
        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudieron cargar las liquidaciones.");
        }
        liquidacionesCache = await response.json();
        if (!liquidacionesCache.length) {
            tabla.innerHTML = `<tr><td colspan="7" class="table-empty">Sin liquidaciones registradas.</td></tr>`;
            return;
        }

        const mecanicosMap = new Map(
            mecanicosCache.map((mecanico) => [mecanico.id, `${mecanico.nombres} ${mecanico.apellidos}`.trim()])
        );

        tabla.innerHTML = liquidacionesCache.map((liq) => `
            <tr data-id="${liq.id}">
                <td>${formatearFecha(liq.fecha_creacion)}</td>
                <td>${mecanicosMap.get(liq.mecanico_id) || `#${liq.mecanico_id}`}</td>
                <td>${liq.fecha_inicio} - ${liq.fecha_fin}</td>
                <td>${formatearMoneda(liq.total_base)}</td>
                <td>${formatearMoneda(liq.total_pagado)}</td>
                <td><span class="badge-estado ${liq.estado === "pagado" ? "badge-pagado" : "badge-pendiente"}">${liq.estado}</span></td>
                <td class="acciones">
                    <button type="button" class="btn-icon btn-edit btn-detalle" data-id="${liq.id}">
                        <i class="fa-solid fa-eye"></i>
                    </button>
                    <button type="button" class="btn-icon btn-pdf btn-pdf-nomina" data-id="${liq.id}" data-estado="${liq.estado}">
                        <i class="fa-solid fa-file-pdf"></i>
                    </button>
                    ${liq.estado !== "pagado" ? `
                        <button type="button" class="btn-icon btn-toggle btn-marcar-pagado" data-id="${liq.id}">
                            <i class="fa-solid fa-check"></i>
                        </button>
                    ` : ""}
                </td>
            </tr>
        `).join("");
        prepararAcciones(tabla);
        aplicarFiltros();
    } catch (error) {
        tabla.innerHTML = `<tr><td colspan="7" class="table-empty">${error.message}</td></tr>`;
    }
}

function cargarFiltroMecanico(select) {
    select.innerHTML = `<option value="">Todos</option>` +
        mecanicosCache.map((mecanico) => {
            const nombre = `${mecanico.nombres} ${mecanico.apellidos}`.trim();
            return `<option value="${mecanico.id}">${nombre}</option>`;
        }).join("");
}

function aplicarFiltros() {
    const filtroMecanico = document.getElementById("filtro-mecanico");
    const filtroDesde = document.getElementById("filtro-desde");
    const filtroHasta = document.getElementById("filtro-hasta");
    const filtroEstado = document.getElementById("filtro-estado");
    const tabla = document.querySelector("#tabla-liquidaciones tbody");
    if (!tabla) {
        return;
    }

    const mecanicoId = filtroMecanico ? filtroMecanico.value : "";
    const desde = filtroDesde ? filtroDesde.value : "";
    const hasta = filtroHasta ? filtroHasta.value : "";
    const estado = filtroEstado ? filtroEstado.value : "";
    let totalBase = 0;
    let totalPagado = 0;

    const filas = Array.from(tabla.querySelectorAll("tr")).filter((row) => row.dataset.id);
    filas.forEach((row) => {
        const liqId = Number(row.dataset.id);
        const liq = liquidacionesCache.find((item) => item.id === liqId);
        if (!liq) {
            return;
        }

        const coincideMecanico = !mecanicoId || String(liq.mecanico_id) === mecanicoId;
        const coincideEstado = !estado || liq.estado === estado;
        const coincideDesde = !desde || liq.fecha_inicio >= desde;
        const coincideHasta = !hasta || liq.fecha_fin <= hasta;

        const visible = coincideMecanico && coincideEstado && coincideDesde && coincideHasta;
        row.style.display = visible ? "" : "none";
        const detalleRow = tabla.querySelector(`tr[data-detalle='${liqId}']`);
        if (detalleRow && row.style.display === "none") {
            detalleRow.remove();
        }

        if (visible) {
            totalBase += Number(liq.total_base || 0);
            totalPagado += Number(liq.total_pagado || 0);
        }
    });

    const totalBaseLabel = document.getElementById("total-base");
    const totalPagadoLabel = document.getElementById("total-pagado");
    if (totalBaseLabel) {
        totalBaseLabel.textContent = formatearMoneda(totalBase);
    }
    if (totalPagadoLabel) {
        totalPagadoLabel.textContent = formatearMoneda(totalPagado);
    }
}

function prepararAcciones(tabla) {
    tabla.querySelectorAll(".btn-detalle").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const liqId = Number(btn.dataset.id);
            await toggleDetalle(liqId, tabla);
        });
    });

    tabla.querySelectorAll(".btn-pdf-nomina").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const liqId = Number(btn.dataset.id);
            const estado = btn.dataset.estado || "";
            let metodoPago = "";

            if (estado === "pagado") {
                const result = await Swal.fire({
                    title: "Metodo de pago",
                    input: "select",
                    inputOptions: {
                        efectivo: "Efectivo",
                        transferencia: "Transferencia"
                    },
                    inputPlaceholder: "Selecciona un metodo",
                    showCancelButton: true,
                    confirmButtonText: "Generar PDF",
                    cancelButtonText: "Cancelar"
                });
                if (!result.isConfirmed) {
                    return;
                }
                metodoPago = result.value || "";
            }

            const query = metodoPago ? `?metodo_pago=${encodeURIComponent(metodoPago)}` : "";
            window.open(`${API_BASE}/contabilidad/liquidaciones/mecanicos/${liqId}/pdf${query}`, "_blank");
        });
    });

    tabla.querySelectorAll(".btn-marcar-pagado").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const liqId = Number(btn.dataset.id);
            await marcarPagado(liqId);
        });
    });
}

async function toggleDetalle(liqId, tabla) {
    const existente = tabla.querySelector(`tr[data-detalle='${liqId}']`);
    if (existente) {
        existente.remove();
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/contabilidad/liquidaciones/mecanicos/${liqId}`);
        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudo cargar el detalle.");
        }
        const liquidacion = await response.json();
        const detalles = liquidacion.detalles || [];
        const detalleHtml = detalles.length
            ? detalles.map((det) => `
                <tr>
                    <td>#${det.orden_id}</td>
                    <td>${det.porcentaje}%</td>
                    <td>${formatearMoneda(det.base_calculo)}</td>
                    <td>${formatearMoneda(det.monto)}</td>
                </tr>
            `).join("")
            : `<tr><td colspan="4">Sin detalle disponible.</td></tr>`;

        const row = document.querySelector(`tr[data-id='${liqId}']`);
        if (!row) {
            return;
        }
        const detalleRow = document.createElement("tr");
        detalleRow.dataset.detalle = String(liqId);
        detalleRow.className = "detalle-row";
        detalleRow.innerHTML = `
            <td colspan="7">
                <div class="detalle-wrapper">
                    <div class="detalle-title">Detalle por orden</div>
                    <table class="detalle-table">
                        <thead>
                            <tr>
                                <th>Orden</th>
                                <th>%</th>
                                <th>Base</th>
                                <th>Monto</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${detalleHtml}
                        </tbody>
                    </table>
                </div>
            </td>
        `;
        row.insertAdjacentElement("afterend", detalleRow);
    } catch (error) {
        mostrarError("Nomina", error.message);
    }
}

async function marcarPagado(liqId) {
    try {
        const response = await fetch(
            `${API_BASE}/contabilidad/liquidaciones/mecanicos/${liqId}/estado?estado=pagado`,
            { method: "PATCH" }
        );
        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudo actualizar la liquidacion.");
        }
        await cargarLiquidaciones();
        Swal.fire({ icon: "success", title: "Liquidacion marcada como pagada" });
    } catch (error) {
        mostrarError("Nomina", error.message);
    }
}

function formatearMoneda(valor) {
    const numero = Number(valor || 0);
    return new Intl.NumberFormat("es-CO", {
        style: "currency",
        currency: "COP",
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(numero);
}

function formatearFecha(fecha) {
    if (!fecha) {
        return "-";
    }
    const dateObj = new Date(fecha);
    if (Number.isNaN(dateObj.getTime())) {
        return fecha;
    }
    return dateObj.toLocaleDateString("es-CO", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit"
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

function mostrarError(titulo, mensaje) {
    Swal.fire({
        icon: "error",
        title: titulo,
        text: mensaje
    });
}

function activarSelectBuscable(select, placeholder) {
    if (!select || select.dataset.searchReady === "true") {
        return;
    }

    const wrapper = document.createElement("div");
    wrapper.className = "select-search";

    const input = document.createElement("input");
    input.type = "text";
    input.className = "select-input";
    input.placeholder = placeholder || "Buscar...";
    input.autocomplete = "off";

    const menu = document.createElement("div");
    menu.className = "select-menu";

    const parent = select.parentElement;
    parent.insertBefore(wrapper, select);
    wrapper.appendChild(input);
    wrapper.appendChild(select);
    wrapper.appendChild(menu);

    const construirMenu = () => {
        menu.innerHTML = "";
        const options = Array.from(select.options);
        options.forEach((option, index) => {
            const item = document.createElement("div");
            item.className = "select-option";
            item.textContent = option.textContent;
            item.dataset.value = option.value;

            if (index === 0 && option.value === "") {
                item.classList.add("is-placeholder");
            }

            item.addEventListener("click", () => {
                if (item.classList.contains("is-placeholder")) {
                    select.value = "";
                    input.value = "";
                } else {
                    select.value = option.value;
                    input.value = option.textContent;
                }
                select.dispatchEvent(new Event("change"));
                menu.classList.remove("is-open");
            });

            menu.appendChild(item);
        });
    };

    const sincronizar = () => {
        const selected = select.options[select.selectedIndex];
        if (selected && selected.value) {
            input.value = selected.textContent;
        } else {
            input.value = "";
        }
    };

    const filtrar = () => {
        const term = input.value.trim().toLowerCase();
        const items = Array.from(menu.children);
        items.forEach((item) => {
            if (item.classList.contains("is-placeholder")) {
                item.style.display = term ? "none" : "block";
                return;
            }
            const texto = item.textContent.toLowerCase();
            item.style.display = texto.includes(term) ? "block" : "none";
        });
    };

    input.addEventListener("focus", () => {
        construirMenu();
        filtrar();
        menu.classList.add("is-open");
    });

    input.addEventListener("input", () => {
        filtrar();
        menu.classList.add("is-open");
    });

    input.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            menu.classList.remove("is-open");
        }
    });

    document.addEventListener("click", (event) => {
        if (!wrapper.contains(event.target)) {
            menu.classList.remove("is-open");
        }
    });

    select.addEventListener("change", sincronizar);

    construirMenu();
    sincronizar();
    select.dataset.searchReady = "true";
}
