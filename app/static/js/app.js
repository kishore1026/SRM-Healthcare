/**
 * SRM Healthcare — Core Application JavaScript
 * CSRF setup, session timeout management, sidebar toggle, utilities
 */

(function () {
    'use strict';

    /* ======================================================================
       1. CSRF Token Setup for AJAX
       ====================================================================== */
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const CSRF_TOKEN = csrfMeta ? csrfMeta.getAttribute('content') : '';

    /**
     * Override native fetch to include CSRF token on mutating requests.
     */
    const _originalFetch = window.fetch;
    window.fetch = function (url, options) {
        options = options || {};
        const method = (options.method || 'GET').toUpperCase();

        if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
            options.headers = options.headers || {};
            // Only set if not already present and not FormData (let browser handle that)
            if (!(options.body instanceof FormData)) {
                if (!options.headers['Content-Type']) {
                    options.headers['Content-Type'] = 'application/json';
                }
            }
            if (!options.headers['X-CSRFToken']) {
                options.headers['X-CSRFToken'] = CSRF_TOKEN;
            }
        }

        return _originalFetch(url, options);
    };

    /**
     * Setup CSRF for jQuery AJAX if jQuery is loaded.
     */
    if (typeof jQuery !== 'undefined') {
        jQuery.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', CSRF_TOKEN);
                }
            }
        });
    }

    /* ======================================================================
       2. Sidebar Toggle (Mobile)
       ====================================================================== */
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const mainWrapper = document.getElementById('mainWrapper');

    function openSidebar() {
        if (!sidebar) return;
        sidebar.classList.add('show');
        if (sidebarOverlay) sidebarOverlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        if (!sidebar) return;
        sidebar.classList.remove('show');
        if (sidebarOverlay) sidebarOverlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function () {
            if (sidebar.classList.contains('show')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    // Close sidebar on ESC key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeSidebar();
        }
    });

    // Close sidebar when resizing to desktop
    window.addEventListener('resize', function () {
        if (window.innerWidth >= 992) {
            closeSidebar();
        }
    });

    /* ======================================================================
       3. Session Timeout Manager
       Auto-redirect after 30 minutes of inactivity.
       Shows a warning modal 60 seconds before expiry.
       ====================================================================== */
    const SESSION_TIMEOUT_MS = 30 * 60 * 1000;   // 30 minutes
    const WARNING_BEFORE_MS  = 60 * 1000;         // 60 second warning
    const LOGIN_URL = '/auth/login';

    let sessionTimer = null;
    let warningTimer = null;
    let countdownInterval = null;
    let countdownValue = 60;

    const timeoutModal = document.getElementById('sessionTimeoutModal');
    const countdownEl = document.getElementById('sessionCountdown');
    const extendBtn = document.getElementById('sessionExtendBtn');
    let bsModal = null;

    // Initialize Bootstrap modal if element exists
    if (timeoutModal && typeof bootstrap !== 'undefined') {
        bsModal = new bootstrap.Modal(timeoutModal);
    }

    function resetSessionTimers() {
        clearTimeout(sessionTimer);
        clearTimeout(warningTimer);
        clearInterval(countdownInterval);

        // Hide modal if visible
        if (bsModal) {
            try { bsModal.hide(); } catch (e) { /* ignore */ }
        }

        // Set warning timer (fires 60s before session end)
        warningTimer = setTimeout(function () {
            showSessionWarning();
        }, SESSION_TIMEOUT_MS - WARNING_BEFORE_MS);

        // Set final timer
        sessionTimer = setTimeout(function () {
            window.location.href = LOGIN_URL + '?timeout=1';
        }, SESSION_TIMEOUT_MS);
    }

    function showSessionWarning() {
        if (!bsModal) {
            // If no modal, just redirect
            return;
        }

        countdownValue = 60;
        if (countdownEl) countdownEl.textContent = countdownValue;

        bsModal.show();

        countdownInterval = setInterval(function () {
            countdownValue--;
            if (countdownEl) countdownEl.textContent = countdownValue;

            if (countdownValue <= 0) {
                clearInterval(countdownInterval);
                window.location.href = LOGIN_URL + '?timeout=1';
            }
        }, 1000);
    }

    // Extend session button
    if (extendBtn) {
        extendBtn.addEventListener('click', function () {
            // Ping the server to refresh session
            fetch('/auth/login', { method: 'GET' }).catch(function () {});
            resetSessionTimers();
        });
    }

    // Activity events that reset the timer
    const ACTIVITY_EVENTS = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];

    ACTIVITY_EVENTS.forEach(function (evt) {
        document.addEventListener(evt, function () {
            // Only reset if the warning modal is NOT showing
            if (!timeoutModal || !timeoutModal.classList.contains('show')) {
                resetSessionTimers();
            }
        }, { passive: true });
    });

    // Start session timers on page load (only if we're logged in, i.e., sidebar exists)
    if (sidebar) {
        resetSessionTimers();
    }

    /* ======================================================================
       4. Counter Animation for Dashboard Stats
       ====================================================================== */
    function animateCounters() {
        const counters = document.querySelectorAll('[data-counter]');

        counters.forEach(function (el) {
            const target = parseInt(el.getAttribute('data-counter'), 10);
            if (isNaN(target)) return;

            const duration = 1200;
            const startTime = performance.now();
            const startValue = 0;

            function updateCounter(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);

                // Ease out cubic
                const eased = 1 - Math.pow(1 - progress, 3);
                const current = Math.round(startValue + (target - startValue) * eased);

                el.textContent = current.toLocaleString();

                if (progress < 1) {
                    requestAnimationFrame(updateCounter);
                }
            }

            requestAnimationFrame(updateCounter);
        });
    }

    // Run counter animation when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', animateCounters);
    } else {
        animateCounters();
    }

    /* ======================================================================
       5. Tooltip Initialization
       ====================================================================== */
    function initTooltips() {
        if (typeof bootstrap === 'undefined') return;
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipTriggerList.forEach(function (el) {
            new bootstrap.Tooltip(el);
        });
    }

    initTooltips();

    /* ======================================================================
       6. Confirm Delete Dialogs
       ====================================================================== */
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('[data-confirm]');
        if (!btn) return;

        const message = btn.getAttribute('data-confirm') || 'Are you sure you want to delete this record?';
        if (!confirm(message)) {
            e.preventDefault();
            e.stopImmediatePropagation();
        }
    });

    /* ======================================================================
       7. Toast Notification Utility
       ====================================================================== */
    window.SRM = window.SRM || {};

    /**
     * Show a toast notification.
     * @param {string} message - The message to display.
     * @param {string} type - 'success' | 'danger' | 'warning' | 'info'
     */
    window.SRM.toast = function (message, type) {
        type = type || 'info';

        const iconMap = {
            success: 'bi-check-circle-fill',
            danger: 'bi-exclamation-triangle-fill',
            warning: 'bi-exclamation-circle-fill',
            info: 'bi-info-circle-fill'
        };

        const container = document.getElementById('toastContainer') || createToastContainer();

        const toast = document.createElement('div');
        toast.className = 'toast align-items-center border-0 show';
        toast.setAttribute('role', 'alert');
        toast.style.cssText = 'margin-bottom: 0.5rem; animation: slideInAlert 0.3s ease-out;';

        toast.innerHTML =
            '<div class="d-flex">' +
                '<div class="toast-body d-flex align-items-center gap-2">' +
                    '<i class="bi ' + (iconMap[type] || iconMap.info) + ' text-' + type + '"></i>' +
                    '<span>' + message + '</span>' +
                '</div>' +
                '<button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>' +
            '</div>';

        container.appendChild(toast);

        // Auto-remove after 4s
        setTimeout(function () {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(function () { toast.remove(); }, 300);
        }, 4000);
    };

    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1090';
        document.body.appendChild(container);
        return container;
    }

    /* ======================================================================
       8. Form Helpers
       ====================================================================== */

    /**
     * Auto-resize textareas.
     */
    document.querySelectorAll('textarea[data-autoresize]').forEach(function (textarea) {
        function resize() {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }
        textarea.addEventListener('input', resize);
        resize();
    });

    /**
     * Disable form double-submit.
     */
    document.querySelectorAll('form[data-no-double-submit]').forEach(function (form) {
        form.addEventListener('submit', function () {
            const btn = form.querySelector('[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Processing...';
            }
        });
    });

    /* ======================================================================
       9. Page Loading Indicator
       ====================================================================== */
    window.addEventListener('beforeunload', function () {
        document.body.style.opacity = '0.7';
        document.body.style.transition = 'opacity 0.2s';
    });

})();
