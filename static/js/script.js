document.addEventListener('DOMContentLoaded', () => {
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
                    alert('Блюдо успешно добавлено в корзину!');
                } else {
                    alert('Ошибка при добавлении блюда: ' + data.message);
                }
            } catch (error) {
                console.error('Ошибка сети или сервера:', error);
                alert('Произошла ошибка при добавлении блюда. Попробуйте еще раз.');
            }
        });
    });

    // Обработка выбора столика
    const tableButtons = document.querySelectorAll('.table-btn, area');
    const selectedTableInput = document.getElementById('selected-table');
    
    tableButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const tableId = btn.dataset.tableId;
            
            // Удаляем предыдущее выделение
            document.querySelectorAll('.table-btn.selected, area.selected').forEach(el => {
                el.classList.remove('selected');
            });
            
            // Добавляем выделение к выбранному элементу
            btn.classList.add('selected');
            selectedTableInput.value = tableId;
        });
    });

    // Инициализация выбранного столика при загрузке
    if (selectedTableInput.value) {
        const selectedBtn = document.querySelector(`[data-table-id="${selectedTableInput.value}"]`);
        if (selectedBtn) {
            selectedBtn.classList.add('selected');
        }
    }
});