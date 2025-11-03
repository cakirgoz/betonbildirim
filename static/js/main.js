// Beton Bildirim Sistemi - Custom JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form[novalidate]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Confirm delete actions
    const deleteForms = document.querySelectorAll('form[action*="delete"]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            const confirmed = confirm('Bu işlemi gerçekleştirmek istediğinizden emin misiniz?');
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });

    // Time input helper - format as HH:MM with auto-navigation
    const timeInputs = document.querySelectorAll('.time-input, input[id*="dokum_zamani"]');
    timeInputs.forEach(function(input) {
        // Input event için otomatik format
        input.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, ''); // Sadece rakamlar
            
            // Maksimum 4 rakam
            if (value.length > 4) {
                value = value.substring(0, 4);
            }
            
            // Saat kısmı 23'ten büyük olamaz
            if (value.length >= 2) {
                let hours = parseInt(value.substring(0, 2));
                if (hours > 23) {
                    value = '23' + value.substring(2);
                }
            }
            
            // Dakika kısmı 59'dan büyük olamaz
            if (value.length >= 4) {
                let minutes = parseInt(value.substring(2, 4));
                if (minutes > 59) {
                    value = value.substring(0, 2) + '59';
                }
            }
            
            // Format: 4 rakam girildiğinde otomatik olarak HH:MM formatına çevir
            if (value.length === 4) {
                const hours = value.substring(0, 2);
                const minutes = value.substring(2, 4);
                this.value = hours + ':' + minutes;
            } else if (value.length > 0) {
                // Kullanıcı yazarken sadece rakamları göster
                this.value = value;
            }
        });
        
        // Blur olayında format kontrolü
        input.addEventListener('blur', function() {
            let value = this.value.replace(/\D/g, '');
            
            if (value.length === 3) {
                // 3 rakam varsa (örn: 930 -> 09:30)
                value = '0' + value;
            } else if (value.length === 2) {
                // 2 rakam varsa (örn: 09 -> 09:00)
                value = value + '00';
            } else if (value.length === 1) {
                // 1 rakam varsa (örn: 9 -> 09:00)
                value = '0' + value + '00';
            }
            
            if (value.length >= 4) {
                const hours = value.substring(0, 2);
                const minutes = value.substring(2, 4);
                this.value = hours + ':' + minutes;
            } else if (value.length > 0) {
                this.value = value;
            }
        });
        
        // Paste olayı için
        input.addEventListener('paste', function(e) {
            setTimeout(() => {
                let value = this.value.replace(/\D/g, '');
                if (value.length >= 4) {
                    const hours = value.substring(0, 2);
                    const minutes = value.substring(2, 4);
                    this.value = hours + ':' + minutes;
                }
            }, 10);
        });
    });

    // Set default date to today for notification forms
    const dateInput = document.querySelector('input[id="dokum_tarihi"]');
    if (dateInput && !dateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }

    // Toggle password visibility
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            }
        });
    });

    // Smooth scroll to top
    const scrollToTopBtn = document.getElementById('scrollToTop');
    if (scrollToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.style.display = 'block';
            } else {
                scrollToTopBtn.style.display = 'none';
            }
        });

        scrollToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Table row click to edit (optional enhancement)
    const editableRows = document.querySelectorAll('tr[data-edit-url]');
    editableRows.forEach(function(row) {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on buttons or forms
            if (!e.target.closest('button') && !e.target.closest('form') && !e.target.closest('a')) {
                window.location.href = this.getAttribute('data-edit-url');
            }
        });
    });

    // Bootstrap tooltip initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Loading state for forms
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.closest('form').addEventListener('submit', function() {
            button.disabled = true;
            const originalText = button.innerHTML;
            button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> İşleniyor...';
            
            // Re-enable after 5 seconds as fallback
            setTimeout(function() {
                button.disabled = false;
                button.innerHTML = originalText;
            }, 5000);
        });
    });

});

// Utility function to format date
function formatDate(date) {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}.${month}.${year}`;
}

// Utility function to format time
function formatTime(time) {
    if (time && time.includes(':')) {
        const parts = time.split(':');
        return `${parts[0].padStart(2, '0')}:${parts[1].padStart(2, '0')}`;
    }
    return time;
}

// Console welcome message
console.log('%c Beton Bildirim Sistemi ', 'background: #0d6efd; color: white; font-size: 16px; padding: 10px;');
console.log('%c Sistem başarıyla yüklendi. ', 'color: #198754; font-size: 12px;');

