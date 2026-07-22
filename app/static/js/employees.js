document.addEventListener("DOMContentLoaded", () => {
    const reconstructedBody = document.querySelector("#employees-table tbody");
    const adminBody = document.querySelector("#employees-admin-table tbody");
    const payrollBody = document.querySelector("#employees-payroll-table tbody");
    const search = document.querySelector("#employee-search");
    const branchFilter = document.querySelector("#employee-branch-filter");
    const reconstructedView = document.querySelector("#employees-reconstructed-view");
    const fragmentView = document.querySelector("#employees-fragment-view");
    const reconstructedDescription = document.querySelector("#employee-reconstructed-description");
    const fragmentDescription = document.querySelector("#employee-fragment-description");
    const adminTitle = document.querySelector("#employees-admin-title");
    const payrollSection = document.querySelector("#employees-payroll-section");
    const createForm = document.querySelector("#employee-create-form");
    const editForm = document.querySelector("#employee-edit-form");
    const editButton = document.querySelector("#edit-employee-button");
    const deleteButton = document.querySelector("#delete-employee-button");
    const createButton = document.querySelector("#employee-create-submit");
    const updateButton = document.querySelector("#employee-edit-submit");
    const deleteConfirmButton = document.querySelector("#employee-delete-confirm");

    if ([reconstructedBody, adminBody, payrollBody, search, branchFilter,
        reconstructedView, fragmentView, reconstructedDescription,
        fragmentDescription, adminTitle, payrollSection, createForm, editForm,
        editButton, deleteButton, createButton, updateButton,
        deleteConfirmButton].some(element => !element)) return;

    let rows = [];
    let fragments = {admin: [], payroll: []};
    let selectedEmployee = null;
    let fragmentRequest = 0;

    const showMessage = (selector, text, kind) => {
        const element = document.querySelector(selector);
        element.className = `alert alert-${kind}`;
        element.textContent = text;
    };

    const money = value => value == null ? "" : Number(value).toFixed(2);

    const clearSelection = () => {
        selectedEmployee = null;
        editButton.disabled = true;
        deleteButton.disabled = true;
        [reconstructedBody, adminBody, payrollBody].forEach(body => {
            body.querySelectorAll(".table-active").forEach(row => row.classList.remove("table-active"));
        });
    };

    const tableMessage = (body, colspan, text) => {
        body.replaceChildren();
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = colspan;
        cell.className = "text-center py-4 text-muted";
        cell.textContent = text;
        row.append(cell);
        body.append(row);
    };

    const matchesSearch = values => {
        const query = search.value.toLowerCase();
        return !query || values.some(value => String(value ?? "").toLowerCase().includes(query));
    };

    const fullEmployeeFor = (fragment, branch = null) => {
        const matches = rows.filter(employee =>
            String(employee.id_empleado) === String(fragment.id_empleado)
            && (!branch || employee.id_sede === branch)
        );
        return matches.length === 1 ? matches[0] : null;
    };

    const appendSelectableRow = (body, values, fragment, branch = null) => {
        const row = document.createElement("tr");
        row.tabIndex = 0;
        values.forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value ?? "";
            row.append(cell);
        });
        const select = () => {
            const fullEmployee = fullEmployeeFor(fragment, branch);
            clearSelection();
            if (!fullEmployee) return;
            selectedEmployee = fullEmployee;
            row.classList.add("table-active");
            editButton.disabled = false;
            deleteButton.disabled = false;
        };
        row.onclick = select;
        row.onkeydown = event => {
            if (["Enter", " "].includes(event.key)) {
                event.preventDefault();
                select();
            }
        };
        body.append(row);
    };

    const renderReconstructed = () => {
        clearSelection();
        const data = rows.filter(employee =>
            (!branchFilter.value || employee.id_sede === branchFilter.value)
            && matchesSearch([
                employee.id_empleado, employee.id_sede, employee.nombre,
                employee.apellido, employee.NIC, employee.edad,
                employee.telefono, employee.sueldo
            ])
        );
        if (!data.length) return tableMessage(reconstructedBody, 8, "No hay empleados registrados.");
        reconstructedBody.replaceChildren();
        data.forEach(employee => appendSelectableRow(reconstructedBody, [
            employee.id_empleado, employee.id_sede, employee.nombre,
            employee.apellido, employee.NIC, employee.edad,
            employee.telefono, money(employee.sueldo)
        ], employee, employee.id_sede));
    };

    const renderAdminFragment = branch => {
        const data = fragments.admin.filter(employee => matchesSearch([
            employee.id_empleado, employee.nombre, employee.apellido,
            employee.NIC, employee.edad, employee.id_sede
        ]));
        if (!data.length) return tableMessage(adminBody, 6, "No hay empleados en el fragmento administrativo.");
        adminBody.replaceChildren();
        data.forEach(employee => appendSelectableRow(adminBody, [
            employee.id_empleado, employee.nombre, employee.apellido,
            employee.NIC, employee.edad, employee.id_sede
        ], employee, branch));
    };

    const renderPayrollFragment = () => {
        const data = fragments.payroll.filter(employee => matchesSearch([
            employee.id_empleado, employee.telefono, employee.sueldo
        ]));
        if (!data.length) return tableMessage(payrollBody, 3, "No hay empleados en el fragmento de nómina.");
        payrollBody.replaceChildren();
        data.forEach(employee => appendSelectableRow(payrollBody, [
            employee.id_empleado, employee.telefono, money(employee.sueldo)
        ], employee));
    };

    const renderFragments = branch => {
        clearSelection();
        renderAdminFragment(branch);
        if (branch === "001") renderPayrollFragment();
    };

    const showReconstructedView = () => {
        reconstructedDescription.classList.remove("d-none");
        fragmentDescription.classList.add("d-none");
        reconstructedView.classList.remove("d-none");
        fragmentView.classList.add("d-none");
    };

    const showFragmentView = branch => {
        reconstructedDescription.classList.add("d-none");
        fragmentDescription.classList.remove("d-none");
        reconstructedView.classList.add("d-none");
        fragmentView.classList.remove("d-none");
        adminTitle.textContent = `Empleado_Admin_${branch}`;
        payrollSection.classList.toggle("d-none", branch !== "001");
    };

    const renderCurrentView = () => {
        if (branchFilter.value) renderFragments(branchFilter.value);
        else renderReconstructed();
    };

    const loadReconstructedEmployees = async () => {
        if (!branchFilter.value) tableMessage(reconstructedBody, 8, "Cargando empleados...");
        try {
            const response = await fetch("/api/employees");
            const payload = await response.json();
            if (!response.ok || !payload.success) throw Error();
            rows = payload.data;
            if (!branchFilter.value) renderReconstructed();
        } catch {
            if (!branchFilter.value) tableMessage(reconstructedBody, 8, "No fue posible cargar los empleados.");
        }
    };

    const loadFragments = async branch => {
        const request = ++fragmentRequest;
        showFragmentView(branch);
        tableMessage(adminBody, 6, "Cargando fragmento administrativo...");
        if (branch === "001") tableMessage(payrollBody, 3, "Cargando fragmento de nómina...");
        try {
            const response = await fetch(`/api/employees/fragments/${branch}`);
            const payload = await response.json();
            if (!response.ok || !payload.success) throw Error();
            if (request !== fragmentRequest || branchFilter.value !== branch) return;
            fragments = {
                admin: Array.isArray(payload.data.admin) ? payload.data.admin : [],
                payroll: Array.isArray(payload.data.payroll) ? payload.data.payroll : []
            };
            renderFragments(branch);
        } catch {
            if (request !== fragmentRequest || branchFilter.value !== branch) return;
            clearSelection();
            tableMessage(adminBody, 6, "No fue posible cargar el fragmento administrativo.");
            if (branch === "001") tableMessage(payrollBody, 3, "No fue posible cargar el fragmento de nómina.");
        }
    };

    const reloadCurrentView = async () => {
        if (!branchFilter.value) return loadReconstructedEmployees();
        const branch = branchFilter.value;
        await Promise.all([loadReconstructedEmployees(), loadFragments(branch)]);
    };

    const send = async (url, method, employeeData) => {
        const response = await fetch(url, {
            method,
            headers: {"Content-Type": "application/json"},
            ...(employeeData ? {body: JSON.stringify(employeeData)} : {})
        });
        const payload = await response.json();
        if (!response.ok || !payload.success) throw Error();
        return payload;
    };

    const formData = form => {
        const data = Object.fromEntries(new FormData(form));
        if (data.id_empleado !== undefined) data.id_empleado = +data.id_empleado;
        data.edad = data.edad === "" ? null : +data.edad;
        ["NIC", "telefono", "sueldo"].forEach(key => {
            if (data[key] === "") data[key] = null;
        });
        return data;
    };

    createForm.onsubmit = async event => {
        event.preventDefault();
        if (createButton.disabled || !createForm.reportValidity()) return;
        createButton.disabled = true;
        createButton.textContent = "Guardando...";
        try {
            await send("/api/employees", "POST", formData(createForm));
            await reloadCurrentView();
            bootstrap.Modal.getOrCreateInstance(document.querySelector("#employeeCreateModal")).hide();
            createForm.reset();
        } catch {
            showMessage("#employee-create-message", "No fue posible registrar el empleado.", "danger");
        } finally {
            createButton.disabled = false;
            createButton.textContent = "Guardar empleado";
        }
    };

    editButton.onclick = () => {
        if (!selectedEmployee) return;
        ["id", "sede", "nombre", "apellido", "nic", "edad", "telefono", "sueldo"].forEach(key => {
            const map = {id: "id_empleado", sede: "id_sede", nic: "NIC"};
            document.querySelector(`#edit-${key}`).value = selectedEmployee[map[key] ?? key] ?? "";
        });
        bootstrap.Modal.getOrCreateInstance(document.querySelector("#employeeEditModal")).show();
    };

    editForm.onsubmit = async event => {
        event.preventDefault();
        if (!selectedEmployee || updateButton.disabled || !editForm.reportValidity()) return;
        updateButton.disabled = true;
        updateButton.textContent = "Guardando...";
        try {
            await send(`/api/employees/${selectedEmployee.id_empleado}/${selectedEmployee.id_sede}`, "PUT", formData(editForm));
            await reloadCurrentView();
            bootstrap.Modal.getOrCreateInstance(document.querySelector("#employeeEditModal")).hide();
        } catch {
            showMessage("#employee-edit-message", "No fue posible actualizar el empleado.", "danger");
        } finally {
            updateButton.disabled = false;
            updateButton.textContent = "Guardar cambios";
        }
    };

    deleteButton.onclick = () => {
        if (!selectedEmployee) return;
        document.querySelector("#employee-delete-summary").textContent = `${selectedEmployee.id_empleado} - ${selectedEmployee.nombre} ${selectedEmployee.apellido}, sede ${selectedEmployee.id_sede}, NIC ${selectedEmployee.NIC ?? ""}, teléfono ${selectedEmployee.telefono ?? ""}, sueldo ${money(selectedEmployee.sueldo)}`;
        bootstrap.Modal.getOrCreateInstance(document.querySelector("#employeeDeleteModal")).show();
    };

    deleteConfirmButton.onclick = async () => {
        if (!selectedEmployee || deleteConfirmButton.disabled) return;
        deleteConfirmButton.disabled = true;
        deleteConfirmButton.textContent = "Eliminando...";
        try {
            await send(`/api/employees/${selectedEmployee.id_empleado}/${selectedEmployee.id_sede}`, "DELETE");
            await reloadCurrentView();
            bootstrap.Modal.getOrCreateInstance(document.querySelector("#employeeDeleteModal")).hide();
        } catch {
            showMessage("#employee-delete-message", "No fue posible eliminar el empleado.", "danger");
        } finally {
            deleteConfirmButton.disabled = false;
            deleteConfirmButton.textContent = "Sí, eliminar empleado";
        }
    };

    search.oninput = renderCurrentView;
    branchFilter.onchange = () => {
        clearSelection();
        if (branchFilter.value) loadFragments(branchFilter.value);
        else {
            fragmentRequest++;
            showReconstructedView();
            renderReconstructed();
        }
    };
    document.querySelector("#employee-search-button").onclick = renderCurrentView;
    document.querySelector("#refresh-employees-button").onclick = reloadCurrentView;

    showReconstructedView();
    loadReconstructedEmployees();
});
