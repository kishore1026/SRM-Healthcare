/**
 * SRM Healthcare - Patients Module JavaScript
 * 
 * Handles:
 *  - Dynamic designation field toggling (Student/Staff/Other)
 *  - Patient name autocomplete
 *  - Search form enhancements
 */

// ============================================================
// DESIGNATION FIELD TOGGLING
// ============================================================

/**
 * Toggle visibility of student/staff fields based on designation selection.
 * Called on page load and whenever the designation dropdown changes.
 */
function toggleDesignationFields() {
    const designation = document.getElementById('designation');
    if (!designation) return;

    const studentFields = document.getElementById('student-fields');
    const staffFields = document.getElementById('staff-fields');

    if (!studentFields || !staffFields) return;

    const value = designation.value;

    // Hide all conditional fields first
    studentFields.style.display = 'none';
    staffFields.style.display = 'none';

    if (value === 'Student') {
        studentFields.style.display = 'block';
        // Add slide-down animation
        studentFields.classList.add('fade-in');
    } else if (value === 'Staff') {
        staffFields.style.display = 'block';
        staffFields.classList.add('fade-in');
    }
    // For 'Other' or empty, both remain hidden
}

// Attach change event listener to designation dropdown
document.addEventListener('DOMContentLoaded', function () {
    const designationSelect = document.getElementById('designation');
    if (designationSelect) {
        designationSelect.addEventListener('change', toggleDesignationFields);
        // Also trigger on load to handle pre-populated forms (edit mode)
        toggleDesignationFields();
    }
});


// ============================================================
// PATIENT NAME AUTOCOMPLETE
// ============================================================

/**
 * Simple autocomplete for patient name search fields.
 * Fetches results from /patients/api/autocomplete endpoint.
 */
function initPatientAutocomplete(inputId, onSelect) {
    const input = document.getElementById(inputId);
    if (!input) return;

    let debounceTimer = null;
    let resultsContainer = null;

    // Create results dropdown container
    resultsContainer = document.createElement('div');
    resultsContainer.className = 'autocomplete-results';
    resultsContainer.style.cssText = `
        position: absolute;
        z-index: 1050;
        width: 100%;
        max-height: 250px;
        overflow-y: auto;
        background: white;
        border: 1px solid #dee2e6;
        border-top: none;
        border-radius: 0 0 0.375rem 0.375rem;
        box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15);
        display: none;
    `;

    // Wrap input in a relative container if not already
    const wrapper = input.parentElement;
    if (getComputedStyle(wrapper).position === 'static') {
        wrapper.style.position = 'relative';
    }
    wrapper.appendChild(resultsContainer);

    // Input event handler with debounce
    input.addEventListener('input', function () {
        const term = this.value.trim();

        clearTimeout(debounceTimer);

        if (term.length < 2) {
            resultsContainer.style.display = 'none';
            resultsContainer.innerHTML = '';
            return;
        }

        debounceTimer = setTimeout(function () {
            fetchAutocompleteResults(term, resultsContainer, onSelect);
        }, 300);
    });

    // Hide results on click outside
    document.addEventListener('click', function (e) {
        if (!wrapper.contains(e.target)) {
            resultsContainer.style.display = 'none';
        }
    });

    // Navigate results with keyboard
    input.addEventListener('keydown', function (e) {
        const items = resultsContainer.querySelectorAll('.autocomplete-item');
        const active = resultsContainer.querySelector('.autocomplete-item.active');

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (active) {
                active.classList.remove('active');
                const next = active.nextElementSibling;
                if (next) next.classList.add('active');
                else if (items.length) items[0].classList.add('active');
            } else if (items.length) {
                items[0].classList.add('active');
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (active) {
                active.classList.remove('active');
                const prev = active.previousElementSibling;
                if (prev) prev.classList.add('active');
                else if (items.length) items[items.length - 1].classList.add('active');
            }
        } else if (e.key === 'Enter') {
            if (active) {
                e.preventDefault();
                active.click();
            }
        } else if (e.key === 'Escape') {
            resultsContainer.style.display = 'none';
        }
    });
}

/**
 * Fetch autocomplete results from the server.
 */
function fetchAutocompleteResults(term, container, onSelect) {
    fetch(`/patients/api/autocomplete?term=${encodeURIComponent(term)}`)
        .then(function (response) { return response.json(); })
        .then(function (data) {
            container.innerHTML = '';

            if (data.length === 0) {
                container.innerHTML = `
                    <div class="px-3 py-2 text-muted small">
                        <i class="bi bi-search me-1"></i>No patients found
                    </div>
                `;
                container.style.display = 'block';
                return;
            }

            data.forEach(function (patient) {
                const item = document.createElement('div');
                item.className = 'autocomplete-item';
                item.style.cssText = `
                    padding: 8px 12px;
                    cursor: pointer;
                    border-bottom: 1px solid #f0f0f0;
                    transition: background-color 0.15s;
                `;

                const designBadge = patient.designation === 'Student'
                    ? '<span class="badge bg-info bg-opacity-10 text-info" style="font-size:0.7em;">Student</span>'
                    : patient.designation === 'Staff'
                        ? '<span class="badge bg-success bg-opacity-10 text-success" style="font-size:0.7em;">Staff</span>'
                        : '<span class="badge bg-secondary bg-opacity-10 text-secondary" style="font-size:0.7em;">Other</span>';

                item.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${escapeHtml(patient.name)}</strong>
                            ${patient.display_id ? '<small class="text-muted ms-1">(' + escapeHtml(patient.display_id) + ')</small>' : ''}
                        </div>
                        ${designBadge}
                    </div>
                `;

                item.addEventListener('mouseenter', function () {
                    this.style.backgroundColor = '#f8f9fa';
                    container.querySelectorAll('.autocomplete-item').forEach(function (el) { el.classList.remove('active'); });
                    this.classList.add('active');
                });
                item.addEventListener('mouseleave', function () {
                    this.style.backgroundColor = '';
                });
                item.addEventListener('click', function () {
                    if (typeof onSelect === 'function') {
                        onSelect(patient);
                    }
                    container.style.display = 'none';
                });

                container.appendChild(item);
            });

            container.style.display = 'block';
        })
        .catch(function (err) {
            console.error('Autocomplete error:', err);
            container.style.display = 'none';
        });
}

/**
 * Escape HTML special characters to prevent XSS.
 */
function escapeHtml(text) {
    if (!text) return '';
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, function (m) { return map[m]; });
}


// ============================================================
// SEARCH FORM ENHANCEMENTS
// ============================================================

document.addEventListener('DOMContentLoaded', function () {

    // Initialize autocomplete on the search page patient name field
    initPatientAutocomplete('patient_name', function (patient) {
        document.getElementById('patient_name').value = patient.name;
    });

    // Quick-set date range buttons (for search page)
    const dateFromEl = document.getElementById('date_from');
    const dateToEl = document.getElementById('date_to');

    if (dateFromEl && dateToEl) {
        // Add today's date as max for date_to
        const today = new Date().toISOString().split('T')[0];
        dateToEl.setAttribute('max', today);
    }

    // Search form - prevent submission with all empty fields
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
            const inputs = searchForm.querySelectorAll('input[type="text"], input[type="date"], select');
            let hasValue = false;

            inputs.forEach(function (input) {
                if (input.value && input.value.trim()) {
                    hasValue = true;
                }
            });

            if (!hasValue) {
                e.preventDefault();
                // Show a gentle warning
                const alertHtml = `
                    <div class="alert alert-warning alert-dismissible fade show mt-2" role="alert">
                        <i class="bi bi-exclamation-circle me-1"></i>
                        Please enter at least one search filter.
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
                const existing = searchForm.querySelector('.alert');
                if (existing) existing.remove();
                searchForm.insertAdjacentHTML('beforeend', alertHtml);
            }
        });
    }
});


// ============================================================
// FORM VALIDATION VISUAL FEEDBACK
// ============================================================

document.addEventListener('DOMContentLoaded', function () {
    // Add Bootstrap validation classes on form fields that have errors
    const errorFields = document.querySelectorAll('.invalid-feedback.d-block');
    errorFields.forEach(function (errorDiv) {
        const input = errorDiv.previousElementSibling;
        if (input && (input.classList.contains('form-control') || input.classList.contains('form-select'))) {
            input.classList.add('is-invalid');
        }
    });
});
