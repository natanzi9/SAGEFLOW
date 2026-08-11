document.addEventListener('DOMContentLoaded', function() {
    // Transaction Form Dynamic Fields
    const txTypeSelect = document.getElementById('tx-type');
    if (txTypeSelect) {
        const payMethodContainer = document.getElementById('pay-method-container');
        const accountSelectContainer = document.getElementById('account-select-container');
        const cardSelectContainer = document.getElementById('card-select-container');
        const destAccountContainer = document.getElementById('dest-account-container');
        
        const payMethodSelect = document.getElementById('pay_method');
        
        function updateFormFields() {
            const type = txTypeSelect.value;
            
            // Default hides
            payMethodContainer.style.display = 'none';
            accountSelectContainer.style.display = 'none';
            cardSelectContainer.style.display = 'none';
            destAccountContainer.style.display = 'none';
            
            if (type === 'income') {
                accountSelectContainer.style.display = 'block';
            } else if (type === 'expense') {
                payMethodContainer.style.display = 'block';
                const method = payMethodSelect.value;
                if (method === 'account') {
                    accountSelectContainer.style.display = 'block';
                } else {
                    cardSelectContainer.style.display = 'block';
                }
            } else if (type === 'transfer') {
                accountSelectContainer.style.display = 'block';
                destAccountContainer.style.display = 'block';
            }
        }
        
        txTypeSelect.addEventListener('change', updateFormFields);
        if (payMethodSelect) {
            payMethodSelect.addEventListener('change', updateFormFields);
        }
        
        // Run once on load
        updateFormFields();
    }
    
    // Auto-dismiss Alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.6s ease';
            setTimeout(() => alert.remove(), 600);
        }, 4000);
    });

    // Theme Toggling (Dark Mode)
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Check local storage for theme
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme === 'dark') {
        body.classList.add('dark-theme');
        updateToggleLabel(true);
    }
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            body.classList.toggle('dark-theme');
            const isDark = body.classList.contains('dark-theme');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            updateToggleLabel(isDark);
        });
    }
    
    function updateToggleLabel(isDark) {
        if (!themeToggle) return;
        const textSpan = themeToggle.querySelector('span');
        if (textSpan) {
            textSpan.textContent = isDark ? 'Modo Claro' : 'Modo Escuro';
        }
    }
});
