document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.querySelector("#clients-table tbody");
    const createForm = document.querySelector("#client-create-form");
    const createSubmitButton = document.querySelector("#client-submit-button");
    const createFormMessage = document.querySelector("#client-form-message");
    const createModal = document.querySelector("#clientCreateModal");
    const editButton = document.querySelector("#edit-client-button");
    const editForm = document.querySelector("#client-edit-form");
    const editSubmitButton = document.querySelector("#client-edit-submit-button");
    const editFormMessage = document.querySelector("#client-edit-form-message");
    const editModal = document.querySelector("#clientEditModal");
    const deleteButton = document.querySelector("#delete-client-button");
    const deleteConfirmButton = document.querySelector("#client-delete-confirm-button");
    const deleteFormMessage = document.querySelector("#client-delete-form-message");
    const deleteModal = document.querySelector("#clientDeleteModal");
    let selectedClient = null;

    if (!tableBody || !createForm || !createSubmitButton || !createFormMessage || !createModal || !editButton || !editForm || !editSubmitButton || !editFormMessage || !editModal || !deleteButton || !deleteConfirmButton || !deleteFormMessage || !deleteModal) return;

    const showTableMessage = (message) => {
        tableBody.replaceChildren();
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 7;
        cell.className = "text-center py-4 text-muted";
        cell.textContent = message;
        row.appendChild(cell);
        tableBody.appendChild(row);
    };

    const clearSelection = () => {
        selectedClient = null;
        editButton.disabled = true;
        deleteButton.disabled = true;
        tableBody.querySelectorAll("tr.table-active").forEach((row) => row.classList.remove("table-active"));
    };

    const selectClient = (client, row) => {
        clearSelection();
        selectedClient = client;
        row.classList.add("table-active");
        editButton.disabled = false;
        deleteButton.disabled = false;
    };

    const appendClient = (client) => {
        const row = document.createElement("tr");
        row.tabIndex = 0;
        ["id_cliente", "nombre", "apellido", "direccion", "email", "telefono", "id_sede"].forEach((field) => {
            const cell = document.createElement("td");
            cell.textContent = client[field] ?? "";
            row.appendChild(cell);
        });
        row.addEventListener("click", () => selectClient(client, row));
        row.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                selectClient(client, row);
            }
        });
        tableBody.appendChild(row);
    };

    const loadClients = async () => {
        clearSelection();
        showTableMessage("Cargando clientes...");
        try {
            const response = await fetch("/api/clients", { headers: { Accept: "application/json" } });
            const payload = await response.json();
            if (!response.ok || !payload.success || !Array.isArray(payload.data)) throw new Error("Client API request failed");
            if (payload.data.length === 0) return showTableMessage("No hay clientes registrados.");
            tableBody.replaceChildren();
            payload.data.forEach(appendClient);
        } catch (error) {
            console.error("Unable to load clients", error);
            showTableMessage("No fue posible cargar los clientes.");
        }
    };

    const showFormMessage = (element, message, type) => {
        element.className = `alert alert-${type}`;
        element.textContent = message;
    };

    const clearFormMessage = (element) => {
        element.className = "d-none";
        element.textContent = "";
    };

    const optionalFieldsToNull = (payload) => {
        ["direccion", "email", "telefono"].forEach((field) => {
            if (payload[field].trim() === "") payload[field] = null;
        });
    };

    createForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (createSubmitButton.disabled || !createForm.reportValidity()) return;
        const payload = Object.fromEntries(new FormData(createForm).entries());
        payload.id_cliente = Number(payload.id_cliente);
        optionalFieldsToNull(payload);
        clearFormMessage(createFormMessage);
        createSubmitButton.disabled = true;
        createSubmitButton.textContent = "Guardando...";
        try {
            const response = await fetch("/api/clients", { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(payload) });
            const responsePayload = await response.json();
            if (!response.ok || !responsePayload.success) throw new Error("Client creation failed");
            await loadClients();
            bootstrap.Modal.getOrCreateInstance(createModal).hide();
            createForm.reset();
            clearFormMessage(createFormMessage);
        } catch (error) {
            console.error("Unable to create client", error);
            showFormMessage(createFormMessage, "No fue posible registrar el cliente.", "danger");
        } finally {
            createSubmitButton.disabled = false;
            createSubmitButton.textContent = "Guardar cliente";
        }
    });

    editButton.addEventListener("click", () => {
        if (!selectedClient) return;
        clearFormMessage(editFormMessage);
        document.querySelector("#edit-id_cliente").value = selectedClient.id_cliente;
        document.querySelector("#edit-id_sede").value = selectedClient.id_sede;
        ["nombre", "apellido", "direccion", "email", "telefono"].forEach((field) => {
            document.querySelector(`#edit-${field}`).value = selectedClient[field] ?? "";
        });
        bootstrap.Modal.getOrCreateInstance(editModal).show();
    });

    editForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (!selectedClient || editSubmitButton.disabled || !editForm.reportValidity()) return;
        const payload = Object.fromEntries(new FormData(editForm).entries());
        optionalFieldsToNull(payload);
        clearFormMessage(editFormMessage);
        editSubmitButton.disabled = true;
        editSubmitButton.textContent = "Guardando...";
        try {
            const response = await fetch(`/api/clients/${encodeURIComponent(selectedClient.id_cliente)}/${encodeURIComponent(selectedClient.id_sede)}`, { method: "PUT", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(payload) });
            const responsePayload = await response.json();
            if (!response.ok || !responsePayload.success) throw new Error("Client update failed");
            await loadClients();
            bootstrap.Modal.getOrCreateInstance(editModal).hide();
            editForm.reset();
            clearFormMessage(editFormMessage);
        } catch (error) {
            console.error("Unable to update client", error);
            showFormMessage(editFormMessage, "No fue posible actualizar el cliente.", "danger");
        } finally {
            editSubmitButton.disabled = false;
            editSubmitButton.textContent = "Guardar cambios";
        }
    });

    deleteButton.addEventListener("click", () => {
        if (!selectedClient) return;
        clearFormMessage(deleteFormMessage);
        document.querySelector("#delete-client-id").textContent = selectedClient.id_cliente;
        document.querySelector("#delete-client-name").textContent = `${selectedClient.nombre ?? ""} ${selectedClient.apellido ?? ""}`.trim();
        document.querySelector("#delete-client-branch").textContent = selectedClient.id_sede;
        bootstrap.Modal.getOrCreateInstance(deleteModal).show();
    });

    deleteConfirmButton.addEventListener("click", async () => {
        if (!selectedClient || deleteConfirmButton.disabled) return;
        clearFormMessage(deleteFormMessage);
        deleteConfirmButton.disabled = true;
        deleteConfirmButton.textContent = "Eliminando...";
        try {
            const response = await fetch(`/api/clients/${encodeURIComponent(selectedClient.id_cliente)}/${encodeURIComponent(selectedClient.id_sede)}`, { method: "DELETE", headers: { Accept: "application/json" } });
            const payload = await response.json();
            if (!response.ok || !payload.success) throw new Error("Client deletion failed");
            await loadClients();
            bootstrap.Modal.getOrCreateInstance(deleteModal).hide();
            clearFormMessage(deleteFormMessage);
        } catch (error) {
            console.error("Unable to delete client", error);
            showFormMessage(deleteFormMessage, "No fue posible eliminar el cliente.", "danger");
        } finally {
            deleteConfirmButton.disabled = false;
            deleteConfirmButton.textContent = "Sí, eliminar cliente";
        }
    });

    loadClients();
});
