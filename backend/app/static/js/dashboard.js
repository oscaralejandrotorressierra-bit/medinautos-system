// ================================
// DASHBOARD MEDINAUTOS - REAL DATA
// ================================

document.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch("/dashboard/data");
        const data = await response.json();

        animateCounter(
            document.getElementById("total-clientes"),
            data.clientes,
            1200
        );

        animateCounter(
            document.getElementById("total-vehiculos"),
            data.vehiculos,
            1200
        );

        document.getElementById("estado-sistema").textContent = data.estado;
        renderCumpleanios(
            document.getElementById("cumple-hoy"),
            data.cumple_hoy
        );
        renderCumpleanios(
            document.getElementById("cumple-proximos"),
            data.cumple_proximos
        );
        renderAlertasVencidas(
            document.getElementById("alertas-vencidas"),
            data.alertas_vencidas
        );
        renderIngresosSemana(
            document.getElementById("ingresos-semana"),
            data.ingresos_semana || []
        );
        renderResumenMensual(
            document.getElementById("resumen-mensual"),
            data
        );
        renderOrdenesEstado(
            document.getElementById("ordenes-estado"),
            data
        );
        renderTopServicios(
            document.getElementById("top-servicios"),
            data.top_servicios || []
        );
        renderAlertasResumen(
            document.getElementById("alertas-resumen"),
            data
        );
        animateCounter(
            document.getElementById("cumple-hoy-total"),
            data.cumple_hoy_total || 0,
            900
        );
    } catch (error) {
        console.error("Error cargando datos del dashboard:", error);
    }
});


// ================================
// CONTADOR ANIMADO
// ================================
function animateCounter(element, target, duration) {
    let start = 0;
    const increment = Math.ceil(target / (duration / 16));

    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            start = target;
            clearInterval(timer);
        }
        element.textContent = start;
    }, 16);
}

function renderCumpleanios(contenedor, items) {
    if (!contenedor) {
        return;
    }

    if (!items || items.length === 0) {
        contenedor.innerHTML = `<li class="empty">Sin alertas.</li>`;
        return;
    }

    contenedor.innerHTML = items.map((item) => {
        const telefono = item.telefono ? ` · ${item.telefono}` : "";
        const fecha = item.fecha ? ` · ${formatearFecha(item.fecha)}` : "";
        return `<li><strong>${item.nombre}</strong>${telefono}${fecha}</li>`;
    }).join("");
}

function renderAlertasVencidas(contenedor, items) {
    if (!contenedor) {
        return;
    }

    if (!items || items.length === 0) {
        contenedor.innerHTML = `<li class="empty">Sin alertas.</li>`;
        return;
    }

    const ordenadas = [...items].sort((a, b) => (b.total || 0) - (a.total || 0));

    contenedor.innerHTML = ordenadas.map((item) => {
        const placa = item.placa || "-";
        const cliente = item.cliente || "-";
        const telefono = item.telefono || "-";
        const total = Number(item.total || 0);
        const totalLabel = `${total} vencida${total === 1 ? "" : "s"}`;
        const href = item.vehiculo_id ? `/novedades#vehiculo-${item.vehiculo_id}` : "";
        const placaHtml = href
            ? `<span class="alerta-placa-link">${placa}</span>`
            : `<span class="alerta-placa">${placa}</span>`;
        return `
            <li class="alerta-vencida-item">
                ${href ? `<a class="alerta-vencida-link" href="${href}">` : `<div class="alerta-vencida-link">`}
                    <div class="alerta-item-main">
                        ${placaHtml}
                        <span class="alerta-total">${totalLabel}</span>
                    </div>
                    <div class="alerta-item-meta">Cliente: ${cliente} | Tel: ${telefono}</div>
                ${href ? `</a>` : `</div>`}
            </li>
        `;
    }).join("");
}

function renderIngresosSemana(contenedor, items) {
    if (!contenedor) {
        return;
    }

    if (!items || items.length === 0) {
        contenedor.innerHTML = `<div class="chart-empty">Sin datos recientes.</div>`;
        return;
    }

    const maxValor = Math.max(
        ...items.map((item) => Math.max(item.ingresos || 0, item.egresos || 0)),
        1
    );

    contenedor.innerHTML = items.map((item) => {
        const ingresos = item.ingresos || 0;
        const egresos = item.egresos || 0;
        const alturaIngresos = Math.round((ingresos / maxValor) * 100);
        const alturaEgresos = Math.round((egresos / maxValor) * 100);
        const etiqueta = formatearDia(item.dia);
        return `
            <div class="chart-bar">
                <div class="bar-values">
                    <span class="bar bar-ingresos" style="height: ${alturaIngresos}%;"></span>
                    <span class="bar bar-egresos" style="height: ${alturaEgresos}%;"></span>
                </div>
                <div class="bar-label">${etiqueta}</div>
            </div>
        `;
    }).join("");
}

function renderResumenMensual(contenedor, data) {
    if (!contenedor) {
        return;
    }
    const ingresos = formatCurrency(data.ingresos_mes || 0);
    const egresos = formatCurrency(data.egresos_mes || 0);
    const utilidad = formatCurrency(data.utilidad_mes || 0);
    contenedor.innerHTML = `
        <div class="metric-card">
            <span>Ingresos</span>
            <strong>${ingresos}</strong>
        </div>
        <div class="metric-card">
            <span>Egresos</span>
            <strong>${egresos}</strong>
        </div>
        <div class="metric-card">
            <span>Utilidad</span>
            <strong>${utilidad}</strong>
        </div>
    `;
}

function renderOrdenesEstado(contenedor, data) {
    if (!contenedor) {
        return;
    }
    const total = data.ordenes_total || 0;
    const estados = [
        { label: "Abiertas", value: data.ordenes_abiertas || 0, className: "estado-abierta" },
        { label: "En proceso", value: data.ordenes_proceso || 0, className: "estado-proceso" },
        { label: "Cerradas", value: data.ordenes_cerradas || 0, className: "estado-cerrada" },
        { label: "Canceladas", value: data.ordenes_canceladas || 0, className: "estado-cancelada" }
    ];
    contenedor.innerHTML = estados.map((estado) => {
        const porcentaje = total > 0 ? Math.round((estado.value / total) * 100) : 0;
        return `
            <div class="status-item">
                <div class="status-label">${estado.label}</div>
                <div class="status-bar">
                    <span class="status-fill ${estado.className}" style="width: ${porcentaje}%;"></span>
                </div>
                <div class="status-meta">${estado.value} (${porcentaje}%)</div>
            </div>
        `;
    }).join("");
}

function renderTopServicios(contenedor, items) {
    if (!contenedor) {
        return;
    }
    if (!items || items.length === 0) {
        contenedor.innerHTML = `<div class="chart-empty">Sin ventas registradas.</div>`;
        return;
    }
    const maxValor = Math.max(...items.map((item) => item.total || 0), 1);
    contenedor.innerHTML = items.map((item) => {
        const porcentaje = Math.round(((item.total || 0) / maxValor) * 100);
        return `
            <div class="top-servicio-item">
                <div class="top-servicio-header">
                    <span>${item.nombre}</span>
                    <strong>${formatCurrency(item.total || 0)}</strong>
                </div>
                <div class="top-servicio-bar">
                    <span style="width: ${porcentaje}%;"></span>
                </div>
                <div class="top-servicio-meta">${item.cantidad || 0} servicios</div>
            </div>
        `;
    }).join("");
}

function renderAlertasResumen(contenedor, data) {
    if (!contenedor) {
        return;
    }
    const vencidas = data.alertas_vencidas_total || 0;
    const proximas = data.alertas_proximas_total || 0;
    contenedor.innerHTML = `
        <div class="metric-card">
            <span>Vencidas</span>
            <strong>${vencidas}</strong>
        </div>
        <div class="metric-card">
            <span>Proximas</span>
            <strong>${proximas}</strong>
        </div>
    `;
}

function formatearFecha(valor) {
    if (!valor) {
        return "-";
    }
    const texto = String(valor);
    const dateObj = texto.length === 10 ? new Date(`${texto}T00:00:00`) : new Date(texto);
    if (Number.isNaN(dateObj.getTime())) {
        return valor;
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

function formatearDia(valor) {
    if (!valor) {
        return "-";
    }
    const texto = String(valor);
    const dateObj = new Date(`${texto}T00:00:00`);
    if (Number.isNaN(dateObj.getTime())) {
        return texto;
    }
    return dateObj.toLocaleDateString("es-CO", { day: "2-digit", month: "short" });
}

function formatCurrency(valor) {
    const numero = Number(valor || 0);
    return numero.toLocaleString("es-CO", {
        style: "currency",
        currency: "COP",
        maximumFractionDigits: 0
    });
}
