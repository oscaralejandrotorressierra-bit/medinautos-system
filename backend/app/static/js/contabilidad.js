// ======================================================
// CONTABILIDAD - MEDINAUTOS
// Caja, movimientos, proveedores y liquidaciones
// ======================================================

const API_BASE = "/api";
let cajaActual = null;
let mecanicosCache = [];
let itemsCache = new Map();

document.addEventListener("DOMContentLoaded", () => {
    const formAbrir = document.getElementById("form-abrir-caja");
    const formCerrar = document.getElementById("form-cerrar-caja");
    const formMovimiento = document.getElementById("form-movimiento-caja");
    const btnRecargar = document.getElementById("btn-recargar-movimientos");
    const proveedorSelect = document.getElementById("proveedor-select");
    const proveedorMovimientoSelect = document.getElementById("proveedor-movimiento-select");
    const ordenSelect = document.getElementById("orden-select");
    const formLiquidacion = document.getElementById("form-liquidacion");
    const tipoSelect = formMovimiento ? formMovimiento.querySelector("select[name='tipo']") : null;
    const frecuenciaSelect = formLiquidacion ? formLiquidacion.querySelector("select[name='frecuencia']") : null;
    const montoInput = formMovimiento ? formMovimiento.querySelector("input[name='monto']") : null;

    if (formAbrir) {
        formAbrir.addEventListener("submit", onAbrirCaja);
    }
    if (formCerrar) {
        formCerrar.addEventListener("submit", onCerrarCaja);
    }
    if (formMovimiento) {
        formMovimiento.addEventListener("submit", onCrearMovimiento);
    }
    if (btnRecargar) {
        btnRecargar.addEventListener("click", () => cargarMovimientos());
    }
    if (proveedorSelect) {
        proveedorSelect.addEventListener("change", () => cargarProveedorDetalle());
    }
    if (formLiquidacion) {
        formLiquidacion.addEventListener("submit", onCrearLiquidacion);
    }
    if (tipoSelect) {
        activarSelectBuscable(tipoSelect, "Buscar tipo...");
    }
    if (frecuenciaSelect) {
        activarSelectBuscable(frecuenciaSelect, "Buscar frecuencia...");
    }
    if (montoInput) {
        prepararInputMoneda(montoInput);
    }
    if (ordenSelect) {
        cargarOrdenesParaMovimiento(ordenSelect);
    }
    if (proveedorMovimientoSelect) {
        cargarProveedoresMovimiento(proveedorMovimientoSelect);
    }

    inicializarContabilidad();
});

async function inicializarContabilidad() {
    await cargarCaja();
    await cargarMovimientos();
    await cargarItems();
    await cargarProveedores();
    await cargarMecanicos();
    await cargarLiquidaciones();
    iniciarAutoRefresco();
}

function iniciarAutoRefresco() {
    const REFRESCO_MS = 30000;
    setInterval(async () => {
        if (cajaActual) {
            await cargarCaja();
            await cargarMovimientos();
        }
    }, REFRESCO_MS);
}

async function cargarCaja() {
    try {
        const response = await fetch(`${API_BASE}/contabilidad/cajas/abierta`);
        if (response.status === 404) {
            cajaActual = null;
            actualizarCajaUI(null);
            return;
        }
        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudo cargar la caja.");
        }
        cajaActual = await response.json();
        actualizarCajaUI(cajaActual);
    } catch (error) {
        mostrarError("Caja", error.message);
    }
}

function actualizarCajaUI(caja) {
    const estado = document.getElementById("caja-estado");
    const saldoInicial = document.getElementById("caja-saldo-inicial");
    const saldoFinal = document.getElementById("caja-saldo-final");
    const saldoActual = document.getElementById("caja-saldo-actual");
    const fechaApertura = document.getElementById("caja-fecha-apertura");
    const formAbrir = document.getElementById("form-abrir-caja");
    const formCerrar = document.getElementById("form-cerrar-caja");

    if (!estado || !saldoInicial || !saldoFinal || !fechaApertura) {
        return;
    }

    if (caja) {
        estado.textContent = "Abierta";
        estado.classList.add("is-open");
        saldoInicial.textContent = formatearMoneda(caja.saldo_inicial);
        if (saldoActual) {
            saldoActual.textContent = formatearMoneda(caja.saldo_final);
        }
        saldoFinal.textContent = formatearMoneda(caja.saldo_final);
        fechaApertura.textContent = formatearFecha(caja.fecha_apertura);
        if (formAbrir) {
            setFormDisabled(formAbrir, true);
        }
        if (formCerrar) {
            setFormDisabled(formCerrar, false);
        }
    } else {
        estado.textContent = "Cerrada";
        estado.classList.remove("is-open");
        saldoInicial.textContent = "$0";
        if (saldoActual) {
            saldoActual.textContent = "$0";
        }
        saldoFinal.textContent = "$0";
        fechaApertura.textContent = "-";
        if (formAbrir) {
            setFormDisabled(formAbrir, false);
        }
        if (formCerrar) {
            setFormDisabled(formCerrar, true);
        }
    }
}

function setFormDisabled(form, disabled) {
    form.querySelectorAll("input, select, button").forEach((element) => {
        element.disabled = disabled;
    });
}

async function onAbrirCaja(event) {
    event.preventDefault();
    const form = event.target;
    const saldoInicial = parseFloat(form.saldo_inicial.value || "0");
    const observaciones = form.observaciones.value.trim();

    try {
        const response = await fetch(`${API_BASE}/contabilidad/cajas/abrir`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                saldo_inicial: saldoInicial,
                observaciones: observaciones || null
            })
        });

        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudo abrir la caja.");
        }

        await response.json();
        form.reset();
        await cargarCaja();
        await cargarMovimientos();
        Swal.fire({ icon: "success", title: "Caja abierta", text: "La caja diaria esta activa." });
    } catch (error) {
        mostrarError("Caja", error.message);
    }
}

async function onCerrarCaja(event) {
    event.preventDefault();
    if (!cajaActual) {
        mostrarError("Caja", "No hay caja abierta.");
        return;
    }

    const form = event.target;
    const saldoFinal = form.saldo_final.value ? parseFloat(form.saldo_final.value) : null;
    const observaciones = form.observaciones.value.trim();

    try {
        const response = await fetch(`${API_BASE}/contabilidad/cajas/${cajaActual.id}/cerrar`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                saldo_final: saldoFinal,
                observaciones: observaciones || null
            })
        });

        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudo cerrar la caja.");
        }

        await response.json();
        form.reset();
        await cargarCaja();
        await cargarMovimientos();
        Swal.fire({ icon: "success", title: "Caja cerrada", text: "El cierre fue registrado." });
    } catch (error) {
        mostrarError("Caja", error.message);
    }
}

async function onCrearMovimiento(event) {
    event.preventDefault();
    const form = event.target;
    const montoValor = obtenerMontoDesdeInput(form.monto);

    const payload = {
        tipo: form.tipo.value,
        concepto: form.concepto.value.trim(),
        monto: montoValor,
        motivo: form.motivo.value.trim() || null,
        orden_id: form.orden_id.value ? Number(form.orden_id.value) : null,
        proveedor_id: form.proveedor_id.value ? Number(form.proveedor_id.value) : null
    };

    if (!payload.tipo || !payload.concepto || Number.isNaN(payload.monto) || payload.monto <= 0) {
        mostrarError("Movimiento", "Completa concepto y monto.");
        return;
    }

    if (payload.proveedor_id) {
        const saldoValido = await validarSaldoProveedor(payload.proveedor_id, payload.monto);
        if (!saldoValido) {
            return;
        }
    }

    try {
        const response = await fetch(`${API_BASE}/contabilidad/movimientos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudo registrar el movimiento.");
        }

        await response.json();
        form.reset();
        if (form.monto) {
            prepararInputMoneda(form.monto);
        }
        await cargarCaja();
        await cargarMovimientos();
        if (payload.proveedor_id) {
            const proveedorSelect = document.getElementById("proveedor-select");
            if (proveedorSelect) {
                proveedorSelect.value = String(payload.proveedor_id);
            }
            await cargarProveedorDetalle();
        }
        Swal.fire({ icon: "success", title: "Movimiento registrado" });
    } catch (error) {
        mostrarError("Movimiento", error.message);
    }
}

async function cargarMovimientos() {
    const tabla = document.querySelector("#tabla-movimientos tbody");
    if (!tabla) {
        return;
    }

    try {
        let url = `${API_BASE}/contabilidad/movimientos`;
        if (cajaActual) {
            url = `${url}?caja_id=${cajaActual.id}`;
        }
        const response = await fetch(url);
        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudieron cargar los movimientos.");
        }
        const movimientos = await response.json();
        if (!movimientos.length) {
            tabla.innerHTML = `<tr><td colspan="6" class="table-empty">Sin movimientos registrados.</td></tr>`;
            return;
        }
        tabla.innerHTML = movimientos.map((mov) => `
            <tr>
                <td>${formatearFecha(mov.fecha)}</td>
                <td>${mov.tipo}</td>
                <td>${mov.concepto}</td>
                <td>${formatearMoneda(mov.monto)}</td>
                <td>${mov.orden_id ?? "-"}</td>
                <td>${mov.proveedor_id ?? "-"}</td>
            </tr>
        `).join("");
    } catch (error) {
        tabla.innerHTML = `<tr><td colspan="6" class="table-empty">${error.message}</td></tr>`;
    }
}

async function cargarProveedores() {
    const select = document.getElementById("proveedor-select");
    if (!select) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/almacen/proveedores`);
        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudieron cargar los proveedores.");
        }
        const proveedores = await response.json();
        select.innerHTML = `<option value="">Seleccione un proveedor</option>` +
            proveedores.map((prov) => `<option value="${prov.id}">${prov.nombre}</option>`).join("");
        activarSelectBuscable(select, "Buscar proveedor...");
    } catch (error) {
        mostrarError("Proveedores", error.message);
    }
}

async function cargarProveedoresMovimiento(select) {
    try {
        const response = await fetch(`${API_BASE}/almacen/proveedores`);
        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudieron cargar los proveedores.");
        }
        const proveedores = await response.json();
        select.innerHTML = `<option value="">Sin proveedor</option>` +
            proveedores.map((prov) => `<option value="${prov.id}">${prov.nombre}</option>`).join("");
        activarSelectBuscable(select, "Buscar proveedor...");
    } catch (error) {
        mostrarError("Proveedores", error.message);
    }
}

async function cargarOrdenesParaMovimiento(select) {
    try {
        const response = await fetch(`${API_BASE}/ordenes/`);
        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudieron cargar las ordenes.");
        }
        const ordenes = await response.json();
        const visibles = ordenes.filter((orden) => ["abierta", "en_proceso", "cerrada"].includes(orden.estado));
        select.innerHTML = `<option value="">Sin orden</option>` +
            visibles.map((orden) => {
                const cliente = orden.cliente ? orden.cliente.nombre : "";
                const vehiculo = orden.vehiculo ? orden.vehiculo.placa : "";
                const estado = formatearEstado(orden.estado);
                const total = formatearMoneda(orden.total || 0);
                const texto = `#${orden.id} | ${estado} | ${cliente} ${vehiculo} | ${total}`.trim();
                return `<option value="${orden.id}">${texto}</option>`;
            }).join("");
        activarSelectBuscable(select, "Buscar orden...");
    } catch (error) {
        mostrarError("Ordenes", error.message);
    }
}

async function cargarProveedorDetalle() {
    const select = document.getElementById("proveedor-select");
    const proveedorId = select ? select.value : null;
    const tabla = document.querySelector("#tabla-proveedor tbody");

    if (!select || !tabla) {
        return;
    }

    if (!proveedorId) {
        tabla.innerHTML = `<tr><td colspan="6" class="table-empty">Selecciona un proveedor.</td></tr>`;
        actualizarSaldoProveedor(null);
        return;
    }

    try {
        const [saldoResp, movResp] = await Promise.all([
            fetch(`${API_BASE}/contabilidad/proveedores/${proveedorId}/saldo`),
            fetch(`${API_BASE}/contabilidad/proveedores/${proveedorId}/movimientos`)
        ]);

        if (!saldoResp.ok || !movResp.ok) {
            const detalle = await obtenerDetalleError(saldoResp.ok ? movResp : saldoResp);
            throw new Error(detalle || "No se pudo cargar el proveedor.");
        }

        const saldo = await saldoResp.json();
        const movimientos = await movResp.json();
        actualizarSaldoProveedor(saldo);

        if (!movimientos.length) {
            tabla.innerHTML = `<tr><td colspan="7" class="table-empty">No hay movimientos.</td></tr>`;
            return;
        }

        tabla.innerHTML = movimientos.map((mov) => `
            <tr>
                <td>${formatearFecha(mov.fecha)}</td>
                <td>${mov.tipo}</td>
                <td>${formatearMoneda(mov.subtotal)}</td>
                <td>${mov.orden_id ?? "-"}</td>
                <td>${obtenerNombreItem(mov.item_id)}</td>
                <td>${mov.cantidad ?? "-"}</td>
                <td>${mov.motivo ?? "-"}</td>
            </tr>
        `).join("");
    } catch (error) {
        tabla.innerHTML = `<tr><td colspan="7" class="table-empty">${error.message}</td></tr>`;
    }
}

async function cargarItems() {
    try {
        const response = await fetch(`${API_BASE}/almacen/items`);
        if (!response.ok) {
            return;
        }
        const items = await response.json();
        itemsCache = new Map(items.map((item) => [item.id, item.nombre]));
    } catch (error) {
        itemsCache = new Map();
    }
}

function obtenerNombreItem(itemId) {
    if (!itemId) {
        return "-";
    }
    return itemsCache.get(itemId) || `#${itemId}`;
}

async function validarSaldoProveedor(proveedorId, monto) {
    try {
        const response = await fetch(`${API_BASE}/contabilidad/proveedores/${proveedorId}/saldo`);
        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudo validar el saldo del proveedor.");
        }
        const saldo = await response.json();
        if (monto > saldo.saldo) {
            mostrarError("Proveedor", "El monto excede el saldo pendiente del proveedor.");
            return false;
        }
        return true;
    } catch (error) {
        mostrarError("Proveedor", error.message);
        return false;
    }
}

function actualizarSaldoProveedor(data) {
    const saldo = document.getElementById("proveedor-saldo");
    const cargos = document.getElementById("proveedor-cargos");
    const pagos = document.getElementById("proveedor-pagos");

    if (!saldo || !cargos || !pagos) {
        return;
    }

    if (!data) {
        saldo.textContent = "$0";
        cargos.textContent = "$0";
        pagos.textContent = "$0";
        return;
    }

    saldo.textContent = formatearMoneda(data.saldo);
    cargos.textContent = formatearMoneda(data.cargos);
    pagos.textContent = formatearMoneda(data.pagos);
}

async function cargarMecanicos() {
    const select = document.getElementById("mecanico-select");
    if (!select) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/mecanicos/`);
        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudieron cargar los tecnicos.");
        }
        mecanicosCache = await response.json();
        select.innerHTML = `<option value="">Seleccione un tecnico</option>` +
            mecanicosCache.map((mecanico) => {
            const nombre = `${mecanico.nombres} ${mecanico.apellidos}`.trim();
            return `<option value="${mecanico.id}">${nombre}</option>`;
        }).join("");
        activarSelectBuscable(select, "Buscar tecnico...");
    } catch (error) {
        mostrarError("Tecnicos", error.message);
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
        mostrarError("Liquidaciones", "Completa tecnico y fechas.");
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
        mostrarError("Liquidaciones", error.message);
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
        const liquidaciones = await response.json();
        if (!liquidaciones.length) {
            tabla.innerHTML = `<tr><td colspan="6" class="table-empty">Sin liquidaciones registradas.</td></tr>`;
            return;
        }

        const mecanicosMap = new Map(
            mecanicosCache.map((mecanico) => [mecanico.id, `${mecanico.nombres} ${mecanico.apellidos}`.trim()])
        );

        tabla.innerHTML = liquidaciones.map((liq) => `
            <tr>
                <td>${formatearFecha(liq.fecha_creacion)}</td>
                <td>${mecanicosMap.get(liq.mecanico_id) || `#${liq.mecanico_id}`}</td>
                <td>${formatearFecha(liq.fecha_inicio)} - ${formatearFecha(liq.fecha_fin)}</td>
                <td>${formatearMoneda(liq.total_base)}</td>
                <td>${formatearMoneda(liq.total_pagado)}</td>
                <td>${liq.estado}</td>
            </tr>
        `).join("");
    } catch (error) {
        tabla.innerHTML = `<tr><td colspan="6" class="table-empty">${error.message}</td></tr>`;
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

function formatearEstado(estado) {
    const valor = (estado || "abierta").replace("_", " ");
    return valor.charAt(0).toUpperCase() + valor.slice(1);
}

function formatearFecha(fecha) {
    if (!fecha) {
        return "-";
    }
    const texto = String(fecha);
    const dateObj = texto.length === 10 ? new Date(`${texto}T00:00:00`) : new Date(texto);
    if (Number.isNaN(dateObj.getTime())) {
        return fecha;
    }
    const base = dateObj.toLocaleDateString("es-CO", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit"
    });
    const hora = dateObj.toLocaleTimeString("es-CO", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true
    });
    return `${base} ${hora}`;
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

function prepararInputMoneda(input) {
    if (!input || input.dataset.currencyReady === "true") {
        return;
    }

    const formatear = () => {
        const valor = obtenerMontoDesdeInput(input);
        if (!Number.isNaN(valor) && valor > 0) {
            input.value = formatearMoneda(valor);
        }
    };

    input.addEventListener("focus", () => {
        const valor = obtenerMontoDesdeInput(input);
        input.value = valor ? String(valor) : "";
    });

    input.addEventListener("blur", formatear);
    input.addEventListener("input", () => {
        input.value = input.value.replace(/[^\d]/g, "");
    });

    input.dataset.currencyReady = "true";
}

function obtenerMontoDesdeInput(input) {
    if (!input) {
        return NaN;
    }
    const limpio = String(input.value || "").replace(/[^\d]/g, "");
    if (!limpio) {
        return NaN;
    }
    return Number(limpio);
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
