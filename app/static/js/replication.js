document.addEventListener("DOMContentLoaded", () => {
    const refreshButton = document.querySelector("#refresh-replication-button");
    const message = document.querySelector("#replication-message");
    const search = document.querySelector("#replication-search");
    const searchButton = document.querySelector("#replication-search-button");
    const filter = document.querySelector("#replication-status-filter");
    const tableBody = document.querySelector("#replication-table tbody");
    const generalStatus = document.querySelector("#replication-general-status");
    const lastCheck = document.querySelector("#replication-last-check");
    const required = [refreshButton, message, search, searchButton, filter, tableBody, generalStatus, lastCheck];
    if (required.some((element) => !element)) return;

    const nodeFields = {
        publisher: {
            name: document.querySelector("#publisher-name"),
            branch: document.querySelector("#publisher-branch"),
            server: document.querySelector("#publisher-server"),
            database: document.querySelector("#publisher-database"),
            status: document.querySelector("#publisher-status"),
        },
        subscriber: {
            name: document.querySelector("#subscriber-name"),
            branch: document.querySelector("#subscriber-branch"),
            server: document.querySelector("#subscriber-server"),
            database: document.querySelector("#subscriber-database"),
            status: document.querySelector("#subscriber-status"),
        },
    };
    const summaryFields = {
        productos_floresta: document.querySelector("#summary-floresta"),
        productos_sur: document.querySelector("#summary-sur"),
        sincronizados: document.querySelector("#summary-synchronized"),
        pendientes_sur: document.querySelector("#summary-pending"),
        solo_sur: document.querySelector("#summary-only-sur"),
        diferentes: document.querySelector("#summary-different"),
    };
    if (Object.values(nodeFields).some((group) => Object.values(group).some((element) => !element)) || Object.values(summaryFields).some((element) => !element)) return;

    let products = [];
    let loading = false;
    const numberFormatter = new Intl.NumberFormat("es-EC");
    const priceFormatter = new Intl.NumberFormat("es-EC", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    const setText = (element, value, fallback = "—") => {
        element.textContent = value === null || value === undefined || value === "" ? fallback : String(value);
    };
    const setBadge = (element, text, style) => {
        element.className = `badge ${style}`;
        element.textContent = text;
    };
    const tableMessage = (text) => {
        tableBody.replaceChildren();
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 6;
        cell.className = "text-center py-4 text-muted";
        cell.textContent = text;
        row.appendChild(cell);
        tableBody.appendChild(row);
    };
    const showMessage = (text, type) => {
        message.className = `alert alert-${type}`;
        message.textContent = text;
    };
    const hideMessage = () => {
        message.className = "d-none";
        message.textContent = "";
    };
    const displayNumber = (value) => value === null || value === undefined ? "—" : numberFormatter.format(Number(value));
    const displayPrice = (value) => value === null || value === undefined || value === "" ? "—" : priceFormatter.format(Number(value));
    const displayDate = (value) => {
        if (!value) return "—";
        const parsed = new Date(value);
        return Number.isNaN(parsed.getTime()) ? String(value).replace("T", " ") : parsed.toLocaleString("es-EC");
    };
    const statusStyle = (status) => ({
        "Sincronizado": "text-bg-success",
        "Pendiente en Sur": "text-bg-warning",
        "Solo existe en Sur": "text-bg-secondary",
        "Datos diferentes": "text-bg-danger",
    }[status] || "text-bg-secondary");

    const renderNode = (fields, node) => {
        setText(fields.name, node?.nodo);
        setText(fields.branch, node?.id_sede);
        setText(fields.server, node?.servidor);
        setText(fields.database, node?.base_datos);
        const available = node?.estado === "Disponible";
        setBadge(fields.status, available ? "Nodo disponible" : "Nodo no disponible", available ? "text-bg-success" : "text-bg-secondary");
    };
    const renderGeneralStatus = (status) => {
        const styles = {
            "Datos sincronizados": "text-bg-success",
            "Datos con diferencias": "text-bg-warning",
            "No fue posible comprobar": "text-bg-secondary",
        };
        setBadge(generalStatus, status || "No fue posible comprobar", styles[status] || "text-bg-secondary");
    };
    const visibleProducts = () => {
        const term = search.value.trim().toLowerCase();
        const selectedFilter = filter.value;
        return products.filter((product) => {
            const matchesTerm = !term || [
                product.id_producto,
                product.nombre_floresta,
                product.nombre_sur,
                product.estado,
            ].some((value) => String(value ?? "").toLowerCase().includes(term));
            const matchesFilter = selectedFilter === "all"
                || (selectedFilter === "synchronized" && product.estado === "Sincronizado")
                || (selectedFilter === "pending" && product.estado === "Pendiente en Sur")
                || (selectedFilter === "different" && ["Datos diferentes", "Solo existe en Sur"].includes(product.estado));
            return matchesTerm && matchesFilter;
        });
    };
    const renderTable = () => {
        const rows = visibleProducts();
        if (!rows.length) {
            tableMessage(products.length ? "No hay productos que coincidan con la búsqueda o el filtro." : "No hay datos comparativos disponibles.");
            return;
        }
        tableBody.replaceChildren();
        rows.forEach((product) => {
            const row = document.createElement("tr");
            [
                product.id_producto,
                product.nombre_floresta,
                product.nombre_sur,
                displayPrice(product.precio_floresta),
                displayPrice(product.precio_sur),
            ].forEach((value) => {
                const cell = document.createElement("td");
                setText(cell, value);
                row.appendChild(cell);
            });
            const statusCell = document.createElement("td");
            const badge = document.createElement("span");
            setBadge(badge, product.estado, statusStyle(product.estado));
            statusCell.appendChild(badge);
            row.appendChild(statusCell);
            tableBody.appendChild(row);
        });
    };
    const renderData = (data) => {
        products = Array.isArray(data.productos) ? data.productos : [];
        renderGeneralStatus(data.estado_general);
        setText(lastCheck, displayDate(data.ultima_comprobacion));
        renderNode(nodeFields.publisher, data.publicador);
        renderNode(nodeFields.subscriber, data.suscriptor);
        const summary = data.resumen || {};
        Object.entries(summaryFields).forEach(([key, element]) => setText(element, displayNumber(summary[key])));
        renderTable();
        if (data.estado_general === "No fue posible comprobar") {
            showMessage("No fue posible comprobar el suscriptor. La información local continúa disponible.", "warning");
        }
    };
    const loadStatus = async () => {
        if (loading) return;
        loading = true;
        refreshButton.disabled = true;
        refreshButton.textContent = "Comprobando...";
        hideMessage();
        tableMessage("Comprobando estado de replicación...");
        try {
            const response = await fetch("/api/replication/status", { headers: { Accept: "application/json" } });
            const payload = await response.json().catch(() => null);
            if (!response.ok || !payload?.success || !payload.data) throw new Error("Replication status request failed");
            renderData(payload.data);
        } catch (error) {
            console.error("Unable to load replication status", error);
            products = [];
            renderGeneralStatus("No fue posible comprobar");
            tableMessage("No fue posible comprobar el estado de replicación.");
            showMessage("No fue posible consultar el nodo publicador. Intente actualizar el estado más tarde.", "danger");
        } finally {
            loading = false;
            refreshButton.disabled = false;
            refreshButton.replaceChildren();
            const icon = document.createElement("i");
            icon.className = "fas fa-arrows-rotate me-2";
            refreshButton.appendChild(icon);
            refreshButton.appendChild(document.createTextNode("Actualizar estado"));
        }
    };

    search.addEventListener("input", renderTable);
    searchButton.addEventListener("click", renderTable);
    filter.addEventListener("change", renderTable);
    refreshButton.addEventListener("click", loadStatus);
    loadStatus();
});
