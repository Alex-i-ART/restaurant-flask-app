document.addEventListener('DOMContentLoaded', () => {
    // Инициализация счетчика корзины
    updateCartCounterOnLoad();

    // Обработка добавления в корзину
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            const itemId = event.target.dataset.itemId;
            
            try {
                const response = await fetch('/add_to_cart', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ item_id: parseInt(itemId) })
                });

                const data = await response.json();

                if (data.success) {
                    showToast('Блюдо добавлено в корзину!');
                    updateCartCounter(data.total_items);
                } else {
                    showToast('Ошибка: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('Ошибка:', error);
                showToast('Произошла ошибка', 'error');
            }
        });
    });

    // Выбор столика
    const tableButtons = document.querySelectorAll('.table-btn');
    const selectedTableInput = document.getElementById('selected-table');
    const confirmBtn = document.querySelector('.confirm-btn');
    
    if (tableButtons.length > 0) {
        tableButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                tableButtons.forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                selectedTableInput.value = btn.dataset.tableId;
                
                if (confirmBtn) {
                    confirmBtn.textContent = `Подтвердить ${btn.textContent.trim()}`;
                }
            });
        });

        if (selectedTableInput.value) {
            const selectedBtn = document.querySelector(`.table-btn[data-table-id="${selectedTableInput.value}"]`);
            if (selectedBtn) selectedBtn.click();
        }
    }

    // Вспомогательные функции
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i> ${message}`;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
            setTimeout(() => toast.remove(), 3000);
        }, 100);
    }

    function updateCartCounter(count) {
        const counter = document.getElementById('cart-counter');
        if (counter) {
            counter.textContent = count;
            counter.style.display = count > 0 ? 'inline-flex' : 'none';
        }
    }

    async function updateCartCounterOnLoad() {
        try {
            const response = await fetch('/get_cart_count');
            const data = await response.json();
            if (data.success) {
                updateCartCounter(data.total_items);
            }
        } catch (error) {
            console.error('Ошибка при загрузке счетчика корзины:', error);
        }
    }
});

// Для старых браузеров
(function () {
    if ('HTMLDetailsElement' in window) return;
    
    document.addEventListener('click', (e) => {
        const el = e.target.closest('details');
        if (!el) return;
        el.hasAttribute('open') ? el.removeAttribute('open') : el.setAttribute('open', 'open');
    });
})();

// Управление шапкой при скролле
let lastScroll = 0;
const header = document.querySelector('header');
const headerHeight = header.offsetHeight;
const scrollThreshold = 20; // На сколько пикселей нужно проскроллить для срабатывания

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll <= headerHeight) {
        // Вверху страницы - всегда показываем
        header.classList.remove('hide');
        header.classList.add('show');
        return;
    }
    
    if (currentScroll > lastScroll && currentScroll > scrollThreshold) {
        // Прокрутка вниз
        header.classList.remove('show');
        header.classList.add('hide');
    } else if (currentScroll < lastScroll) {
        // Прокрутка вверх
        header.classList.remove('hide');
        header.classList.add('show');
    }
    
    lastScroll = currentScroll;
});

// Инициализация при загрузке
header.classList.add('show');

// Управление шапкой с учетом высоты
function initHeaderScroll() {
    const header = document.querySelector('header');
    const headerHeight = header.offsetHeight;
    let lastScroll = 0;
    const scrollThreshold = 20; // Меньший порог для мобильных

    // Устанавливаем правильный отступ для main
    document.querySelector('main').style.marginTop = `${headerHeight}px`;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll <= headerHeight) {
            header.classList.remove('hide');
            return;
        }
        
        if (currentScroll > lastScroll && currentScroll > scrollThreshold) {
            header.classList.add('hide');
        } else {
            header.classList.remove('hide');
        }
        
        lastScroll = currentScroll;
    });

    // Инициализация
    header.classList.add('show');
}

// Вызываем после загрузки DOM
document.addEventListener('DOMContentLoaded', initHeaderScroll);