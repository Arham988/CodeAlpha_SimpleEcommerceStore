/**
 * ShopAlpha - Storefront Vanilla JavaScript
 * Pure JavaScript - No libraries or external frameworks.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Quantity Selector logic for Product Details page
    setupQuantitySelector();

    // Auto-dismiss Django flash messages after 4 seconds
    setupMessageDismissal();
});

/**
 * Handles plus/minus and input boundaries for product quantity
 */
function setupQuantitySelector() {
    const qtyInput = document.getElementById('quantity-input');
    const decreaseBtn = document.querySelector('.qty-decrease');
    const increaseBtn = document.querySelector('.qty-increase');

    if (!qtyInput || !decreaseBtn || !increaseBtn) return;

    const maxStock = parseInt(qtyInput.getAttribute('max'), 10) || 1;
    const minStock = 1;

    decreaseBtn.addEventListener('click', () => {
        let current = parseInt(qtyInput.value, 10) || 1;
        if (current > minStock) {
            qtyInput.value = current - 1;
        }
    });

    increaseBtn.addEventListener('click', () => {
        let current = parseInt(qtyInput.value, 10) || 1;
        if (current < maxStock) {
            qtyInput.value = current + 1;
        } else {
            showTemporaryToast(`Cannot exceed maximum available stock (${maxStock})`);
        }
    });

    qtyInput.addEventListener('change', () => {
        let current = parseInt(qtyInput.value, 10);
        if (isNaN(current) || current < minStock) {
            qtyInput.value = minStock;
        } else if (current > maxStock) {
            qtyInput.value = maxStock;
            showTemporaryToast(`Capped to maximum available stock (${maxStock})`);
        }
    });
}

/**
 * Smoothly fades out flash notification messages
 */
function setupMessageDismissal() {
    const alerts = document.querySelectorAll('.alert-banner');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 400);
        }, 4000);
    });
}

/**
 * Creates and displays a non-intrusive notification toast
 */
function showTemporaryToast(message) {
    let toast = document.getElementById('shopalpha-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'shopalpha-toast';
        toast.style.position = 'fixed';
        toast.style.bottom = '24px';
        toast.style.right = '24px';
        toast.style.backgroundColor = '#0f172a';
        toast.style.color = '#ffffff';
        toast.style.padding = '12px 20px';
        toast.style.borderRadius = '8px';
        toast.style.boxShadow = '0 8px 16px rgba(0,0,0,0.2)';
        toast.style.fontSize = '0.9rem';
        toast.style.fontWeight = '500';
        toast.style.zIndex = '9999';
        toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';

    if (window.toastTimeout) {
        clearTimeout(window.toastTimeout);
    }

    window.toastTimeout = setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
    }, 2800);
}
