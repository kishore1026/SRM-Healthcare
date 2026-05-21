/**
 * Medicine Module – Form validation, alerts, and UI helpers.
 */

document.addEventListener('DOMContentLoaded', function () {

    // ─── Expiry Date Validation ───
    // Warn if the expiry date entered is in the past
    const expiryField = document.getElementById('expiry_date');
    if (expiryField) {
        expiryField.addEventListener('change', function () {
            const selected = new Date(this.value);
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            if (selected < today) {
                this.classList.add('is-invalid');
                showFieldWarning(this, 'Warning: This date is in the past. The medicine will be marked as expired.');
            } else {
                this.classList.remove('is-invalid');
                removeFieldWarning(this);
            }
        });
    }

    // ─── Stock Quantity Validation ───
    const stockField = document.getElementById('stock_added');
    if (stockField) {
        stockField.addEventListener('input', function () {
            const val = parseInt(this.value);
            if (isNaN(val) || val < 0) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    }

    // ─── Add Stock Quantity Validation ───
    const addQtyField = document.getElementById('quantity');
    if (addQtyField) {
        addQtyField.addEventListener('input', function () {
            const val = parseInt(this.value);
            if (isNaN(val) || val < 1) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    }

    // ─── Medicine Name – prevent duplicates warning ───
    const nameField = document.getElementById('medicine_name');
    if (nameField) {
        let debounce;
        nameField.addEventListener('input', function () {
            clearTimeout(debounce);
            const name = this.value.trim();
            if (name.length < 3) return;

            debounce = setTimeout(function () {
                // A subtle UX check – no duplicate prevention, just naming
                // Could be extended with an AJAX call
            }, 500);
        });
    }

    // ─── Confirm Stock Addition ───
    const stockForm = document.querySelector('form[action*="add_stock"]');
    if (stockForm) {
        // We can't easily select by action containing add_stock since
        // it's POST to the same URL. Instead let's handle by detecting
        // the hidden action=add_stock
    }

    // ─── Table Row Click (navigate to edit) ───
    const tableRows = document.querySelectorAll('table tbody tr[data-href]');
    tableRows.forEach(function (row) {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function () {
            window.location.href = this.dataset.href;
        });
    });

    // ─── Auto-dismiss alerts after 5 seconds ───
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });
});


// ═══════════════════════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════════════════════

function showFieldWarning(field, message) {
    removeFieldWarning(field);
    const warning = document.createElement('div');
    warning.className = 'text-warning small mt-1 field-warning';
    warning.innerHTML = '<i class="bi bi-exclamation-triangle me-1"></i>' + message;
    field.parentElement.appendChild(warning);
}

function removeFieldWarning(field) {
    const existing = field.parentElement.querySelector('.field-warning');
    if (existing) existing.remove();
}
