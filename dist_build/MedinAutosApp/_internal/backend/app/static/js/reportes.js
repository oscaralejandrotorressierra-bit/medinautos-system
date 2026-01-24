// ======================================================
// REPORTES - MEDINAUTOS
// ======================================================

const API_BASE = "/api";

document.addEventListener("DOMContentLoaded", () => {
    const btnAplicar = document.getElementById("btn-aplicar-reportes");
    const btnLimpiar = document.getElementById("btn-limpiar-reportes");
    const btnPdf = document.getElementById("btn-pdf-ordenes");
    const btnExcel = document.getElementById("btn-excel-ingresos");

    btnAplicar?.addEventListener("click", aplicarFiltros);
    btnLimpiar?.addEventListener("click", () => limpiarFiltros(true));
    btnPdf?.addEventListener("click", descargarPdfOrdenes);
    btnExcel?.addEventListener("click", descargarExcelIngresos);

    cargarReportes();
});

async function cargarReportes() {
    await Promise.all([
        cargarIngresosTotales(),
        cargarServicios(),
        cargarOrdenes()
    ]);
}

function obtenerRango() {
    const desde = document.getElementById("reporte-desde")?.value || "";
    const hasta = document.getElementById("reporte-hasta")?.value || "";
    return { desde, hasta };
}

function armarQuery(desde, hasta) {
    const params = new URLSearchParams();
    if (desde) params.append("fecha_inicio", desde);
    if (hasta) params.append("fecha_fin", hasta);
    const query = params.toString();
    return query ? `?${query}` : "";
}

async function aplicarFiltros() {
    const { desde, hasta } = obtenerRango();
    if (!validarRango(desde, hasta)) {
        return;
    }
    mostrarCargando();
    await Promise.all([
        cargarIngresosRango(desde, hasta),
        cargarOrdenes(desde, hasta),
        actualizarEtiquetasRango(desde, hasta)
    ]);
}

function limpiarFiltros(recargar = false) {
    const desdeInput = document.getElementById("reporte-desde");
    const hastaInput = document.getElementById("reporte-hasta");
    if (desdeInput) desdeInput.value = "";
    if (hastaInput) hastaInput.value = "";

    const rangoLabel = document.getElementById("kpi-rango-fecha");
    const ordenesLabel = document.getElementById("kpi-ordenes-fecha");
    if (rangoLabel) rangoLabel.textContent = "Sin filtro";
    if (ordenesLabel) ordenesLabel.textContent = "Sin filtro";

    const kpiRango = document.getElementById("kpi-rango");
    if (kpiRango) kpiRango.textContent = "-";

    if (recargar) {
        cargarOrdenes();
    }
}

async function cargarIngresosTotales() {
    const kpiTotal = document.getElementById("kpi-total");
    try {
        const response = await fetch(`${API_BASE}/reportes/ingresos-totales`);
        if (!response.ok) throw new Error();
        const data = await response.json();
        if (kpiTotal) {
            kpiTotal.textContent = formatearMoneda(data.ingresos_totales);
        }
    } catch (error) {
        if (kpiTotal) kpiTotal.textContent = "$0";
    }
}

async function cargarIngresosRango(desde, hasta) {
    const kpiRango = document.getElementById("kpi-rango");
    if (!desde || !hasta) {
        if (kpiRango) kpiRango.textContent = "-";
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/reportes/ingresos-por-fecha${armarQuery(desde, hasta)}`);
        if (!response.ok) throw new Error();
        const data = await response.json();
        if (kpiRango) {
            kpiRango.textContent = formatearMoneda(data.ingresos);
        }
    } catch (error) {
        if (kpiRango) kpiRango.textContent = "$0";
    }
}

async function cargarServicios() {
    const tabla = document.querySelector("#tabla-servicios tbody");
    if (!tabla) return;

    try {
        const response = await fetch(`${API_BASE}/reportes/servicios-mas-vendidos`);
        if (!response.ok) throw new Error();
        const data = await response.json();

        if (!data.length) {
            tabla.innerHTML = `<tr><td colspan="3" class="table-empty">Sin datos registrados.</td></tr>`;
            return;
        }

        tabla.innerHTML = data.map((item) => `
            <tr>
                <td>${item.servicio}</td>
                <td>${item.cantidad_vendida}</td>
                <td>${formatearMoneda(item.total_generado)}</td>
            </tr>
        `).join("");
    } catch (error) {
        tabla.innerHTML = `<tr><td colspan="3" class="table-empty">No se pudo cargar.</td></tr>`;
    }
}

async function cargarOrdenes(desde = "", hasta = "") {
    const tabla = document.querySelector("#tabla-ordenes tbody");
    if (!tabla) return;

    try {
        const response = await fetch(`${API_BASE}/reportes/ordenes-cerradas${armarQuery(desde, hasta)}`);
        if (!response.ok) throw new Error();
        const data = await response.json();
        const kpiOrdenes = document.getElementById("kpi-ordenes");

        if (!data.length) {
            tabla.innerHTML = `<tr><td colspan="6" class="table-empty">Sin ordenes en el rango.</td></tr>`;
            if (kpiOrdenes) kpiOrdenes.textContent = "0";
            return;
        }

        if (kpiOrdenes) kpiOrdenes.textContent = String(data.length);

        tabla.innerHTML = data.map((orden) => `
            <tr>
                <td>#${orden.id}</td>
                <td>${formatearFecha(orden.fecha)}</td>
                <td><span class="${obtenerClaseEstado(orden.estado)}">${formatearEstado(orden.estado)}</span></td>
                <td>${orden.cliente?.nombre || "-"}</td>
                <td>${orden.vehiculo?.placa || "-"}</td>
                <td>${formatearMoneda(orden.total)}</td>
            </tr>
        `).join("");
    } catch (error) {
        tabla.innerHTML = `<tr><td colspan="6" class="table-empty">No se pudo cargar.</td></tr>`;
    }
}

function actualizarEtiquetasRango(desde, hasta) {
    const rangoLabel = document.getElementById("kpi-rango-fecha");
    const ordenesLabel = document.getElementById("kpi-ordenes-fecha");
    const texto = desde && hasta ? `${desde} a ${hasta}` : "Sin filtro";
    if (rangoLabel) rangoLabel.textContent = texto;
    if (ordenesLabel) ordenesLabel.textContent = texto;
}

function descargarPdfOrdenes() {
    const { desde, hasta } = obtenerRango();
    if (!validarRango(desde, hasta)) {
        return;
    }
    const url = `${API_BASE}/reportes/ordenes-cerradas/pdf${armarQuery(desde, hasta)}`;
    window.open(url, "_blank");
}

function descargarExcelIngresos() {
    const { desde, hasta } = obtenerRango();
    if (!validarRango(desde, hasta)) {
        return;
    }
    const url = `${API_BASE}/reportes/ingresos/excel${armarQuery(desde, hasta)}`;
    window.open(url, "_blank");
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
    if (!fecha) return "-";
    const dateObj = new Date(fecha);
    if (Number.isNaN(dateObj.getTime())) return fecha;
    return dateObj.toLocaleDateString("es-CO", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit"
    });
}

function formatearEstado(estado) {
    if (!estado) return "-";
    if (estado === "cerrada") return "Cerrada";
    if (estado === "cancelada") return "Cancelada";
    return estado;
}

function obtenerClaseEstado(estado) {
    if (estado === "cerrada") return "badge-estado badge-cerrada";
    if (estado === "cancelada") return "badge-estado badge-cancelada";
    return "badge-estado";
}

function validarRango(desde, hasta) {
    if (desde && hasta && desde > hasta) {
        Swal.fire({
            icon: "warning",
            title: "Fechas invalidas",
            text: "La fecha inicial no puede ser mayor a la fecha final."
        });
        return false;
    }
    return true;
}

function mostrarCargando() {
    const tabla = document.querySelector("#tabla-ordenes tbody");
    if (tabla) {
        tabla.innerHTML = `<tr><td colspan="6" class="table-empty">Cargando ordenes...</td></tr>`;
    }
}
