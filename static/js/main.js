// Функція для показу сповіщень
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast show bg-${type} text-white`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="toast-body">
            ${message}
            <button type="button" class="btn-close btn-close-white ms-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Анімація появи елементів при прокрутці
function handleScrollAnimation() {
    const elements = document.querySelectorAll('.fade-in');
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementBottom = element.getBoundingClientRect().bottom;
        
        if (elementTop < window.innerHeight && elementBottom > 0) {
            element.style.opacity = '1';
        }
    });
}

// Ініціалізація підказок
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Функція для оновлення кількості товарів у кошику
function updateCartCount(count) {
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        cartCount.textContent = count;
        cartCount.classList.add('bounce');
        setTimeout(() => cartCount.classList.remove('bounce'), 300);
    }
}

// Додавання товару до кошика
function addToCart(productId) {
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Товар додано до кошика!');
            updateCartCount(data.cart_count);
        } else {
            showToast('Помилка додавання товару', 'danger');
        }
    })
    .catch(error => {
        showToast('Помилка з\'єднання з сервером', 'danger');
    });
}

// Функція для отримання CSRF токену
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Функція для швидкого перегляду товару
function quickView(productId) {
    fetch(`/product/${productId}/quick-view/`)
    .then(response => response.text())
    .then(html => {
        const modal = document.getElementById('quickViewModal');
        modal.querySelector('.modal-body').innerHTML = html;
        new bootstrap.Modal(modal).show();
    });
}

// Функція для фільтрації товарів
function filterProducts(category) {
    const products = document.querySelectorAll('.product-card');
    products.forEach(product => {
        if (category === 'all' || product.dataset.category === category) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });
}

// Функція для сортування товарів
function sortProducts(method) {
    const productContainer = document.querySelector('.product-container');
    const products = Array.from(document.querySelectorAll('.product-card'));
    
    products.sort((a, b) => {
        const priceA = parseFloat(a.dataset.price);
        const priceB = parseFloat(b.dataset.price);
        
        if (method === 'price-asc') {
            return priceA - priceB;
        } else if (method === 'price-desc') {
            return priceB - priceA;
        }
    });
    
    products.forEach(product => productContainer.appendChild(product));
}

// Ініціалізація при завантаженні сторінки
document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    window.addEventListener('scroll', handleScrollAnimation);
    handleScrollAnimation();
    
    // Обробка форми пошуку
    const searchForm = document.querySelector('#searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = this.querySelector('input').value;
            window.location.href = `/search/?q=${encodeURIComponent(query)}`;
        });
    }
});

// Анімація для кнопок
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('mouseenter', function(e) {
        const x = e.pageX - this.offsetLeft;
        const y = e.pageY - this.offsetTop;
        
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    });
}); 