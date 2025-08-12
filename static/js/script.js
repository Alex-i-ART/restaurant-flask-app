document.addEventListener('DOMContentLoaded', () => {
    // ==================== ОБРАБОТКА КОРЗИНЫ ====================
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

    // ==================== ВЫБОР СТОЛИКА ====================
    const tableButtons = document.querySelectorAll('.table-btn');
    const selectedTableInput = document.getElementById('selected-table');
    const confirmBtn = document.querySelector('.confirm-btn');
    
    if (tableButtons.length > 0) {
        tableButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Снимаем выделение со всех кнопок
                tableButtons.forEach(b => b.classList.remove('selected'));
                
                // Выделяем текущую кнопку
                btn.classList.add('selected');
                
                // Обновляем скрытое поле формы
                selectedTableInput.value = btn.dataset.tableId;
                
                // Обновляем текст кнопки подтверждения
                if (confirmBtn) {
                    confirmBtn.textContent = `Подтвердить ${btn.textContent.trim()}`;
                    confirmBtn.style.display = 'block';
                }
            });
        });

        // Инициализация выбранного столика при загрузке
        if (selectedTableInput.value) {
            const selectedBtn = document.querySelector(`.table-btn[data-table-id="${selectedTableInput.value}"]`);
            if (selectedBtn) {
                selectedBtn.click(); // Программный клик для активации всех обработчиков
            }
        }
    }

    // ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }, 100);
    }

    function updateCartCounter(count) {
        const counter = document.getElementById('cart-counter');
        if (counter) {
            counter.textContent = count;
            counter.style.display = count > 0 ? 'flex' : 'none';
        }
    }

    // ==================== АДАПТИВНОЕ МЕНЮ ДЛЯ МОБИЛЬНЫХ ====================
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            mobileMenuBtn.classList.toggle('open');
        });
    }

    // ==================== ДИНАМИЧЕСКАЯ ПОДГРУЗКА ИЗОБРАЖЕНИЙ ====================
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback для старых браузеров
        lazyImages.forEach(img => {
            img.src = img.dataset.src;
        });
    }
});

// ==================== ПОЛИФИЛЛ ДЛЯ ДЕТАЛЕЙ ====================
(function () {
    if ('HTMLDetailsElement' in window) return;
    
    document.addEventListener('click', (e) => {
        const el = e.target.closest('details');
        if (!el) return;
        
        if (el.hasAttribute('open')) {
            el.removeAttribute('open');
        } else {
            el.setAttribute('open', 'open');
        }
    });
})();