document.addEventListener('DOMContentLoaded', () => {
    // Обработка кликов по кнопкам "Добавить в корзину"
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');

    addToCartButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            const itemId = event.target.dataset.itemId; // Получаем ID блюда из data-атрибута

            try {
                const response = await fetch('/add_to_cart', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ item_id: parseInt(itemId) }) // Отправляем ID блюда
                });

                const data = await response.json();

                if (data.success) {
                    alert('Блюдо успешно добавлено в корзину!');
                    // Здесь можно обновить счетчик товаров в корзине на навигационной панели, если он есть
                    // Пример: const cartCountElement = document.getElementById('cart-count');
                    // if (cartCountElement) { cartCountElement.textContent = data.total_items; }
                } else {
                    alert('Ошибка при добавлении блюда: ' + data.message);
                }
            } catch (error) {
                console.error('Ошибка сети или сервера:', error);
                alert('Произошла ошибка при добавлении блюда. Попробуйте еще раз.');
            }
        });
    });

    // Дополнительный JS, если потребуется (например, для модальных окон)
});
