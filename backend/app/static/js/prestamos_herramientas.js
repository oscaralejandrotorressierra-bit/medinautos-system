// ======================================================
// PRESTAMOS DE HERRAMIENTAS - MEDINAUTOS
// ======================================================

const API_BASE = "/api";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-prestamo");
    const tabla = document.getElementById("prestamos-body");
    const herramientaSelect = document.querySelector("[data-role='herramienta-select']");
    const mecanicoSelect = document.querySelector("[data-role='mecanico-select']");

    if (herramientaSelect) {
        cargarHerramientasSelect(herramientaSelect);
    }

    if (mecanicoSelect) {
        cargarMecanicosSelect(mecanicoSelect);
    }

    if (tabla) {
        cargarPrestamos(tabla);
    }

    if (form) {
        prepararFormulario(form, tabla);
    }
});

async function cargarHerramientasSelect(select) {
    try {
        const response = await fetch(`${API_BASE}/herramientas/`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar las herramientas.");
        }

        const herramientas = await response.json();
        herramientas
            .filter((h) => h.activo)
            .forEach((herramienta) => {
                const option = document.createElement("option");
                option.value = herramienta.id;
                option.textContent = `${herramienta.nombre} - ${herramienta.codigo}`;
                select.appendChild(option);
            });
    } catch (error) {
        console.error(error);
    }
}

async function cargarMecanicosSelect(select) {
    try {
        const response = await fetch(`${API_BASE}/mecanicos/`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar los mecanicos.");
        }

        const mecanicos = await response.json();
        mecanicos
            .filter((m) => m.activo)
            .forEach((mecanico) => {
                const option = document.createElement("option");
                option.value = mecanico.id;
                option.textContent = `${mecanico.nombres} ${mecanico.apellidos}`;
                select.appendChild(option);
            });
    } catch (error) {
        console.error(error);
    }
}

function prepararFormulario(formulario, tabla) {
    formulario.addEventListener("submit", async (event) => {
        event.preventDefault();

        const herramientaId = Number(formulario.herramienta_id.value);
        const mecanicoId = Number(formulario.mecanico_id.value);
        const observaciones = formulario.observaciones.value.trim();

        if (!herramientaId || !mecanicoId) {
            Swal.fire({
                icon: "warning",
                title: "Datos invalidos",
                text: "Selecciona herramienta y mecanico."
            });
            return;
        }

        try {
        const response = await fetch(`${API_BASE}/herramientas/prestamos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({
                herramienta_id: herramientaId,
                mecanico_id: mecanicoId,
                    observaciones: observaciones || null
                })
            });

            if (!response.ok) {
                const detalle = await obtenerDetalleError(response);
                throw new Error(detalle || "No se pudo registrar el prestamo.");
            }

            formulario.reset();
            await cargarPrestamos(tabla);
            Swal.fire({
                icon: "success",
                title: "Prestamo registrado",
                text: "La herramienta fue asignada correctamente."
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

async function cargarPrestamos(tabla) {
    try {
        const [prestamosRes, herramientasRes, mecanicosRes] = await Promise.all([
            fetch(`${API_BASE}/herramientas/prestamos`),
            fetch(`${API_BASE}/herramientas/`),
            fetch(`${API_BASE}/mecanicos/`),
        ]);

        if (!prestamosRes.ok) {
            throw new Error("No se pudieron cargar los prestamos.");
        }

        const prestamos = await prestamosRes.json();
        const herramientas = herramientasRes.ok ? await herramientasRes.json() : [];
        const mecanicos = mecanicosRes.ok ? await mecanicosRes.json() : [];

        const herramientasMap = Object.fromEntries(
            herramientas.map((h) => [h.id, `${h.nombre} - ${h.codigo}`])
        );
        const mecanicosMap = Object.fromEntries(
            mecanicos.map((m) => [m.id, `${m.nombres} ${m.apellidos}`])
        );

        renderPrestamos(tabla, prestamos, herramientasMap, mecanicosMap);
        prepararAcciones(tabla);
    } catch (error) {
        tabla.innerHTML = `
            <tr>
                <td colspan="6" class="servicios-empty">${error.message}</td>
            </tr>
        `;
    }
}

function renderPrestamos(tabla, prestamos, herramientasMap, mecanicosMap) {
    if (!prestamos || prestamos.length === 0) {
        tabla.innerHTML = `
            <tr>
                <td colspan="6" class="servicios-empty">No hay prestamos registrados.</td>
            </tr>
        `;
        return;
    }

    tabla.innerHTML = prestamos.map((prestamo) => {
        const herramienta = herramientasMap[prestamo.herramienta_id] || "Herramienta";
        const mecanico = mecanicosMap[prestamo.mecanico_id] || "Mecanico";
        const prestamoFecha = formatearFecha(prestamo.fecha_prestamo);
        const devolucionFecha = prestamo.fecha_devolucion
            ? formatearFecha(prestamo.fecha_devolucion)
            : "-";
        const acciones = prestamo.fecha_devolucion
            ? "-"
            : `<button type="button" class="btn-icon btn-edit btn-devolver" data-id="${prestamo.id}">
                    <i class="fa-solid fa-rotate-left"></i>
                </button>`;

        return `
            <tr data-id="${prestamo.id}">
                <td class="servicio-nombre">${herramienta}</td>
                <td>${mecanico}</td>
                <td>${prestamoFecha}</td>
                <td>${devolucionFecha}</td>
                <td>${prestamo.observaciones || "-"}</td>
                <td class="acciones">${acciones}</td>
            </tr>
        `;
    }).join("");
}

function prepararAcciones(tabla) {
    tabla.querySelectorAll(".btn-devolver").forEach((boton) => {
        boton.addEventListener("click", () => devolverHerramienta(boton.dataset.id, tabla));
    });
}

async function devolverHerramienta(prestamoId, tabla) {
    const { value: observaciones } = await Swal.fire({
        title: "Devolver herramienta",
        input: "text",
        inputLabel: "Observaciones (opcional)",
        showCancelButton: true,
        confirmButtonText: "Registrar devolucion",
        cancelButtonText: "Cancelar"
    });

    if (observaciones === undefined) {
        return;
    }

    try {
        const payload = observaciones ? { observaciones } : {};
        const response = await fetch(`${API_BASE}/herramientas/prestamos/${prestamoId}/devolver`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const detalle = await obtenerDetalleError(response);
            throw new Error(detalle || "No se pudo registrar la devolucion.");
        }

        await cargarPrestamos(tabla);
    } catch (error) {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: error.message
        });
    }
}

function formatearFecha(valor) {
    if (!valor) {
        return "-";
    }

    let fechaTexto = valor;
    if (typeof fechaTexto === "string" && !/[zZ]|[+-]\\d{2}:\\d{2}$/.test(fechaTexto)) {
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
            return data.detail;
        }
        return null;
    } catch (error) {
        try {
            const texto = await response.text();
            return texto || null;
        } catch (err) {
            return null;
        }
    }
}
