/**
 * Prescription Form – Dynamic Medicine Rows & Stock Validation
 *
 * Uses window.medicineData (array of medicine objects pre-loaded from Jinja).
 * Serializes items as JSON into the hidden #itemsJson field on submit.
 */

document.addEventListener('DOMContentLoaded', function () {
    const rowsContainer = document.getElementById('medicineRows');
    const addBtn = document.getElementById('addMedicineRow');
    const form = document.getElementById('prescriptionForm');
    const itemsJsonField = document.getElementById('itemsJson');
    const emptyMessage = document.getElementById('emptyMessage');
    const medicines = window.medicineData || [];

    let rowCounter = 0;

    // ─── Add Row Button ───
    if (addBtn) {
        addBtn.addEventListener('click', function () {
            addMedicineRow();
        });
    }

    // ─── Form Submit ───
    if (form) {
        form.addEventListener('submit', function (e) {
            const items = collectItems();

            if (items.length === 0) {
                e.preventDefault();
                showAlert('Please add at least one medicine item.', 'danger');
                return;
            }

            // Client-side validation
            let valid = true;
            for (let i = 0; i < items.length; i++) {
                const item = items[i];
                if (!item.medicine_id) {
                    showAlert(`Row ${i + 1}: Please select a medicine.`, 'danger');
                    valid = false; break;
                }
                if (!item.quantity || item.quantity < 1) {
                    showAlert(`Row ${i + 1}: Quantity must be at least 1.`, 'danger');
                    valid = false; break;
                }

                // Check stock
                const med = medicines.find(m => m.id === parseInt(item.medicine_id));
                if (med) {
                    if (med.is_expired) {
                        showAlert(`Row ${i + 1}: ${med.name} is expired and cannot be prescribed.`, 'danger');
                        valid = false; break;
                    }
                    if (item.quantity > med.available_balance) {
                        showAlert(`Row ${i + 1}: Insufficient stock for ${med.name}. Available: ${med.available_balance}`, 'danger');
                        valid = false; break;
                    }
                }
            }

            if (!valid) {
                e.preventDefault();
                return;
            }

            itemsJsonField.value = JSON.stringify(items);
        });
    }

    // ═══════════════════════════════════════════════════════════════
    // Add a Medicine Row
    // ═══════════════════════════════════════════════════════════════
    function addMedicineRow() {
        rowCounter++;
        const rowId = 'med-row-' + rowCounter;

        const tr = document.createElement('tr');
        tr.className = 'medicine-row';
        tr.id = rowId;

        tr.innerHTML = `
            <td>
                <div class="position-relative">
                    <input type="text" class="form-control form-control-sm medicine-search"
                           placeholder="Search medicine..." autocomplete="off"
                           data-row="${rowCounter}">
                    <input type="hidden" class="medicine-id" value="">
                    <div class="medicine-search-results" id="results-${rowCounter}"></div>
                    <div class="stock-info mt-1" id="stock-${rowCounter}"></div>
                </div>
            </td>
            <td>
                <input type="text" class="form-control form-control-sm dosage-field"
                       placeholder="e.g., 500mg">
            </td>
            <td>
                <select class="form-select form-select-sm frequency-field">
                    <option value="">Select</option>
                    <option value="Once daily">Once daily</option>
                    <option value="Twice daily">Twice daily</option>
                    <option value="Thrice daily">Thrice daily</option>
                    <option value="Four times daily">Four times daily</option>
                    <option value="Every 4 hours">Every 4 hours</option>
                    <option value="Every 6 hours">Every 6 hours</option>
                    <option value="Every 8 hours">Every 8 hours</option>
                    <option value="As needed (SOS)">As needed (SOS)</option>
                    <option value="At bedtime">At bedtime</option>
                    <option value="Before meals">Before meals</option>
                    <option value="After meals">After meals</option>
                </select>
            </td>
            <td>
                <select class="form-select form-select-sm duration-field">
                    <option value="">Select</option>
                    <option value="1 day">1 day</option>
                    <option value="2 days">2 days</option>
                    <option value="3 days">3 days</option>
                    <option value="5 days">5 days</option>
                    <option value="7 days">7 days</option>
                    <option value="10 days">10 days</option>
                    <option value="14 days">14 days</option>
                    <option value="21 days">21 days</option>
                    <option value="30 days">30 days</option>
                    <option value="As needed">As needed</option>
                    <option value="Until finished">Until finished</option>
                </select>
            </td>
            <td>
                <input type="number" class="form-control form-control-sm quantity-field"
                       min="1" value="1" placeholder="Qty">
            </td>
            <td>
                <input type="text" class="form-control form-control-sm instructions-field"
                       placeholder="Special instructions">
            </td>
            <td>
                <button type="button" class="btn btn-sm btn-outline-danger remove-row" title="Remove">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;

        rowsContainer.appendChild(tr);
        updateEmptyMessage();

        // Focus the search field
        tr.querySelector('.medicine-search').focus();

        // Bind events
        bindSearchEvents(tr, rowCounter);
        bindRemoveEvent(tr);
        bindQuantityValidation(tr);
    }


    // ═══════════════════════════════════════════════════════════════
    // Medicine Search (Local Filter from pre-loaded data)
    // ═══════════════════════════════════════════════════════════════
    function bindSearchEvents(row, rowNum) {
        const searchInput = row.querySelector('.medicine-search');
        const hiddenId = row.querySelector('.medicine-id');
        const resultsDiv = document.getElementById('results-' + rowNum);
        const stockInfo = document.getElementById('stock-' + rowNum);

        let debounceTimer;

        searchInput.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            const query = this.value.trim().toLowerCase();

            if (query.length < 1) {
                resultsDiv.style.display = 'none';
                return;
            }

            debounceTimer = setTimeout(function () {
                const filtered = medicines.filter(m =>
                    m.name.toLowerCase().includes(query)
                ).slice(0, 15);

                renderSearchResults(filtered, resultsDiv, searchInput, hiddenId, stockInfo);
            }, 200);
        });

        // Close results on outside click
        document.addEventListener('click', function (e) {
            if (!row.contains(e.target)) {
                resultsDiv.style.display = 'none';
            }
        });
    }

    function renderSearchResults(results, container, searchInput, hiddenId, stockInfo) {
        container.innerHTML = '';

        if (results.length === 0) {
            container.innerHTML = '<div class="search-item text-muted">No medicines found</div>';
            container.style.display = 'block';
            return;
        }

        results.forEach(function (med) {
            const item = document.createElement('div');
            item.className = 'search-item' + (med.is_expired ? ' disabled' : '');

            const stockColor = med.available_balance <= 0 ? 'danger' :
                               med.available_balance <= 10 ? 'warning' : 'success';

            item.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${escapeHtml(med.name)}</strong>
                        <span class="badge bg-light text-dark border ms-1" style="font-size:.65rem">${med.drug_type}</span>
                        ${med.is_expired ? '<span class="badge bg-danger ms-1" style="font-size:.65rem">EXPIRED</span>' : ''}
                    </div>
                    <span class="badge bg-${stockColor} stock-badge">${med.available_balance} left</span>
                </div>
                <small class="text-muted">Batch: ${med.batch_number || 'N/A'} | Exp: ${med.expiry_date}</small>
            `;

            if (!med.is_expired && med.available_balance > 0) {
                item.addEventListener('click', function () {
                    searchInput.value = med.name;
                    hiddenId.value = med.id;
                    container.style.display = 'none';

                    // Show stock info
                    stockInfo.innerHTML = `
                        <small class="text-${stockColor}">
                            <i class="bi bi-box-seam me-1"></i>${med.available_balance} available
                        </small>
                    `;
                });
            }

            container.appendChild(item);
        });

        container.style.display = 'block';
    }


    // ═══════════════════════════════════════════════════════════════
    // Remove Row
    // ═══════════════════════════════════════════════════════════════
    function bindRemoveEvent(row) {
        const btn = row.querySelector('.remove-row');
        btn.addEventListener('click', function () {
            row.remove();
            updateEmptyMessage();
        });
    }


    // ═══════════════════════════════════════════════════════════════
    // Quantity Validation (real-time)
    // ═══════════════════════════════════════════════════════════════
    function bindQuantityValidation(row) {
        const qtyField = row.querySelector('.quantity-field');
        const hiddenId = row.querySelector('.medicine-id');

        qtyField.addEventListener('change', function () {
            const medId = parseInt(hiddenId.value);
            if (!medId) return;

            const med = medicines.find(m => m.id === medId);
            if (!med) return;

            const qty = parseInt(this.value) || 0;
            if (qty > med.available_balance) {
                this.classList.add('is-invalid');
                this.title = `Only ${med.available_balance} available`;
            } else {
                this.classList.remove('is-invalid');
                this.title = '';
            }
        });
    }


    // ═══════════════════════════════════════════════════════════════
    // Collect Items for JSON
    // ═══════════════════════════════════════════════════════════════
    function collectItems() {
        const rows = rowsContainer.querySelectorAll('.medicine-row');
        const items = [];

        rows.forEach(function (row) {
            const medId = row.querySelector('.medicine-id').value;
            const qty = row.querySelector('.quantity-field').value;
            const dosage = row.querySelector('.dosage-field').value;
            const frequency = row.querySelector('.frequency-field').value;
            const duration = row.querySelector('.duration-field').value;
            const instructions = row.querySelector('.instructions-field').value;

            items.push({
                medicine_id: medId,
                quantity: parseInt(qty) || 0,
                dosage: dosage,
                frequency: frequency,
                duration: duration,
                instructions: instructions,
            });
        });

        return items;
    }


    // ═══════════════════════════════════════════════════════════════
    // Helpers
    // ═══════════════════════════════════════════════════════════════
    function updateEmptyMessage() {
        const rows = rowsContainer.querySelectorAll('.medicine-row');
        if (emptyMessage) {
            emptyMessage.style.display = rows.length === 0 ? 'block' : 'none';
        }
    }

    function showAlert(message, type) {
        // Remove existing alerts
        const existing = document.querySelectorAll('.prescription-alert');
        existing.forEach(el => el.remove());

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show prescription-alert`;
        alertDiv.innerHTML = `
            <i class="bi bi-exclamation-circle me-1"></i> ${escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        form.parentElement.insertBefore(alertDiv, form);

        // Auto-dismiss after 5s
        setTimeout(() => {
            if (alertDiv.parentElement) alertDiv.remove();
        }, 5000);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
