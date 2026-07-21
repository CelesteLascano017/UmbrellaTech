document.addEventListener("DOMContentLoaded", () => {
    const body = document.querySelector("#products-table tbody");
    const search = document.querySelector("#product-search");
    const editButton = document.querySelector("#edit-product-button");
    const deleteButton = document.querySelector("#delete-product-button");
    const refreshButton = document.querySelector("#refresh-products-button");
    const createForm = document.querySelector("#product-create-form");
    const editForm = document.querySelector("#product-edit-form");
    const createButton = document.querySelector("#product-create-submit");
    const editSubmit = document.querySelector("#product-edit-submit");
    const deleteConfirm = document.querySelector("#product-delete-confirm");
    let products = [];
    let selected = null;

    const required = [body, search, editButton, deleteButton, refreshButton, createForm, editForm, createButton, editSubmit, deleteConfirm];
    if (required.some((element) => !element)) return;

    const message = (id, text, type) => { const element = document.querySelector(id); element.className = `alert alert-${type}`; element.textContent = text; };
    const clearMessage = (id) => { const element = document.querySelector(id); element.className = "d-none"; element.textContent = ""; };
    const clearSelection = () => { selected = null; editButton.disabled = true; deleteButton.disabled = true; body.querySelectorAll("tr.table-active").forEach((row) => row.classList.remove("table-active")); };
    const tableMessage = (text) => { body.replaceChildren(); const row = document.createElement("tr"); const cell = document.createElement("td"); cell.colSpan = 6; cell.className = "text-center py-4 text-muted"; cell.textContent = text; row.appendChild(cell); body.appendChild(row); };
    const displayPrice = (value) => value === null || value === undefined || value === "" ? "" : Number(value).toFixed(2);
    const filteredProducts = () => { const term = search.value.trim().toLowerCase(); return term ? products.filter((item) => [item.id_producto, item.nombre, item.marca, item.modelo, item.descripcion].some((value) => String(value ?? "").toLowerCase().includes(term))) : products; };
    const render = () => { clearSelection(); const rows = filteredProducts(); if (!rows.length) return tableMessage("No hay productos registrados."); body.replaceChildren(); rows.forEach((product) => { const row = document.createElement("tr"); row.tabIndex = 0; [product.id_producto, product.nombre, product.marca, product.modelo, product.descripcion, displayPrice(product.precio)].forEach((value) => { const cell = document.createElement("td"); cell.textContent = value ?? ""; row.appendChild(cell); }); const choose = () => { clearSelection(); selected = product; row.classList.add("table-active"); editButton.disabled = false; deleteButton.disabled = false; }; row.addEventListener("click", choose); row.addEventListener("keydown", (event) => { if (["Enter", " "].includes(event.key)) { event.preventDefault(); choose(); } }); body.appendChild(row); }); };
    const load = async () => { tableMessage("Cargando productos..."); try { const response = await fetch("/api/products", { headers: { Accept: "application/json" } }); const payload = await response.json(); if (!response.ok || !payload.success || !Array.isArray(payload.data)) throw new Error("Product API request failed"); products = payload.data; render(); } catch (error) { console.error("Unable to load products", error); tableMessage("No fue posible cargar los productos."); } };
    const optionalValues = (payload) => { ["marca", "modelo", "descripcion", "precio"].forEach((field) => { if (payload[field].trim() === "") payload[field] = null; }); };
    const request = async (url, method, payload) => { const response = await fetch(url, { method, headers: { "Content-Type": "application/json", Accept: "application/json" }, ...(payload === undefined ? {} : { body: JSON.stringify(payload) }) }); const result = await response.json(); if (!response.ok || !result.success) throw new Error("Product operation failed"); return result; };
    const submitForm = (form, button, messageId, url, method, successText, modalId) => form.addEventListener("submit", async (event) => { event.preventDefault(); if (button.disabled || !form.reportValidity()) return; const payload = Object.fromEntries(new FormData(form).entries()); if (payload.id_producto !== undefined) payload.id_producto = Number(payload.id_producto); optionalValues(payload); clearMessage(messageId); button.disabled = true; button.textContent = "Guardando..."; try { await request(url(), method, payload); await load(); bootstrap.Modal.getOrCreateInstance(document.querySelector(modalId)).hide(); form.reset(); clearMessage(messageId); } catch (error) { console.error("Unable to save product", error); message(messageId, successText, "danger"); } finally { button.disabled = false; button.textContent = method === "POST" ? "Guardar producto" : "Guardar cambios"; } });
    submitForm(createForm, createButton, "#product-create-message", () => "/api/products", "POST", "No fue posible crear el producto.", "#productCreateModal");
    editButton.addEventListener("click", () => { if (!selected) return; clearMessage("#product-edit-message"); document.querySelector("#edit-id_producto").value = selected.id_producto; ["nombre", "marca", "modelo", "descripcion", "precio"].forEach((field) => { document.querySelector(`#edit-${field}`).value = selected[field] ?? ""; }); bootstrap.Modal.getOrCreateInstance(document.querySelector("#productEditModal")).show(); });
    submitForm(editForm, editSubmit, "#product-edit-message", () => `/api/products/${encodeURIComponent(selected.id_producto)}`, "PUT", "No fue posible actualizar el producto.", "#productEditModal");
    deleteButton.addEventListener("click", () => { if (!selected) return; clearMessage("#product-delete-message"); document.querySelector("#delete-product-id").textContent = selected.id_producto; document.querySelector("#delete-product-name").textContent = selected.nombre ?? ""; document.querySelector("#delete-product-brand").textContent = selected.marca ?? ""; bootstrap.Modal.getOrCreateInstance(document.querySelector("#productDeleteModal")).show(); });
    deleteConfirm.addEventListener("click", async () => { if (!selected || deleteConfirm.disabled) return; clearMessage("#product-delete-message"); deleteConfirm.disabled = true; deleteConfirm.textContent = "Eliminando..."; try { await request(`/api/products/${encodeURIComponent(selected.id_producto)}`, "DELETE"); await load(); bootstrap.Modal.getOrCreateInstance(document.querySelector("#productDeleteModal")).hide(); } catch (error) { console.error("Unable to delete product", error); message("#product-delete-message", "No fue posible eliminar el producto.", "danger"); } finally { deleteConfirm.disabled = false; deleteConfirm.textContent = "Sí, eliminar producto"; } });
    search.addEventListener("input", render);
    document.querySelector("#product-search-button").addEventListener("click", render);
    refreshButton.addEventListener("click", load);
    load();
});
