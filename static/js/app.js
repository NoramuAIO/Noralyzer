/* ==================== NORALYZER - MAIN JS ==================== */

document.addEventListener('DOMContentLoaded', function() {
    initAlerts();
    initModals();
    initTabs();
    initFavorites();
    initConfirmDelete();
    initMobileMenu();
    initCharts();
    initIBANFormatter();
});

/* ==================== ALERTS ==================== */
function initAlerts() {
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.alert').remove();
        });
    });
    
    // Auto dismiss after 5s
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}

/* ==================== MODALS ==================== */
function initModals() {
    // Open modal
    document.querySelectorAll('[data-modal]').forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = this.dataset.modal;
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('show');
                document.body.style.overflow = 'hidden';
            }
        });
    });
    
    // Close modal
    document.querySelectorAll('.modal-close, .modal-backdrop').forEach(el => {
        el.addEventListener('click', closeModal);
    });
    
    // Close on escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeModal();
    });
    
    // Close when clicking outside
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });
    });
}


function closeModal() {
    document.querySelectorAll('.modal.show').forEach(modal => {
        modal.classList.remove('show');
    });
    document.body.style.overflow = '';
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

/* ==================== TABS ==================== */
function initTabs() {
    document.querySelectorAll('[data-tab]').forEach(tab => {
        tab.addEventListener('click', function() {
            const tabGroup = this.closest('.tabs');
            const contentGroup = this.dataset.tabGroup;
            const targetId = this.dataset.tab;
            
            // Update tabs
            tabGroup.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Update content
            document.querySelectorAll(`[data-tab-content="${contentGroup}"]`).forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(targetId)?.classList.add('active');
            
            // Update URL hash
            history.pushState(null, null, '#' + targetId);
        });
    });
    
    // Settings nav tabs
    document.querySelectorAll('.settings-nav-item').forEach(item => {
        item.addEventListener('click', function() {
            const targetId = this.dataset.target;
            
            // Update nav
            document.querySelectorAll('.settings-nav-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // Update content
            document.querySelectorAll('.settings-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            document.getElementById(targetId)?.classList.add('active');
            
            // Update URL
            history.pushState(null, null, '#' + targetId);
        });
    });
    
    // Handle URL hash on load
    if (window.location.hash) {
        const hash = window.location.hash.substring(1);
        const navItem = document.querySelector(`[data-target="${hash}"]`);
        if (navItem) navItem.click();
    }
}

/* ==================== FAVORITES ==================== */
function initFavorites() {
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.dataset.type;
            const id = this.dataset.id;
            
            fetch(`/${type}s/${id}/toggle-favorite`, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    const icon = this.querySelector('i');
                    if (data.is_favorite) {
                        icon.classList.remove('bi-star');
                        icon.classList.add('bi-star-fill');
                        this.classList.add('active');
                    } else {
                        icon.classList.remove('bi-star-fill');
                        icon.classList.add('bi-star');
                        this.classList.remove('active');
                    }
                });
        });
    });
}

/* ==================== CONFIRM DELETE ==================== */
function initConfirmDelete() {
    document.querySelectorAll('[data-confirm]').forEach(form => {
        form.addEventListener('submit', function(e) {
            const message = this.dataset.confirm || 'Bu işlemi silmek istediğinize emin misiniz?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}


/* ==================== MOBILE MENU ==================== */
function initMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });
        
        // Close on outside click
        document.addEventListener('click', function(e) {
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }
}

/* ==================== CHARTS ==================== */
function initCharts() {
    // Charts are initialized in their respective templates (dashboard.html, reports.html)
    // using data passed directly from the backend to avoid extra API calls.
}
/* ==================== IBAN FORMATTER ==================== */
function initIBANFormatter() {
    const ibanInputs = document.querySelectorAll('input[name="iban"]');
    ibanInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            
            // Auto-add TR if starts with number or empty but intended to be TR IBAN
            if (value.length > 0 && !isNaN(value[0])) {
                value = 'TR' + value;
            } else if (value.length > 0 && !value.startsWith('TR')) {
                // If user typed something else that isn't TR, maybe let them? 
                // But for this app let's assume TR is dominant or enforce it if they clear it
            }
            
            // Format in groups of 4
            let formatted = '';
            for(let i = 0; i < value.length; i++) {
                if (i > 0 && i % 4 === 0) formatted += ' ';
                formatted += value[i];
            }
            
            e.target.value = formatted;
        });
    });
}

/* ==================== UTILITY FUNCTIONS ==================== */
function formatCurrency(amount, currency = 'TRY') {
    const symbols = {
        'TRY': '₺', 'USD': '$', 'EUR': '€', 'CAD': 'C$',
        'BTC': '₿', 'DOGE': 'Ð'
    };
    return (symbols[currency] || '') + amount.toLocaleString('tr-TR', { minimumFractionDigits: 2 });
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
        <button class="alert-close"><i class="bi bi-x"></i></button>
    `;
    document.querySelector('.main-content').prepend(toast);
    initAlerts();
}

// Transaction type toggle for transfer fields
document.addEventListener('change', function(e) {
    if (e.target.name === 'transaction_type') {
        const transferFields = document.getElementById('transferFields');
        if (transferFields) {
            transferFields.style.display = e.target.value === 'transfer' ? 'flex' : 'none';
        }
    }
});
