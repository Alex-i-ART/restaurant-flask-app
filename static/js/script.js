// Замените содержимое script.js на этот код
document.addEventListener('DOMContentLoaded', () => {
    // Обработка кликов по кнопкам "Добавить в корзину"
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
    
    // Проверка доступности столиков при изменении количества человек
    if (document.getElementById('num_people')) {
        window.checkTables = async function() {
            const numPeople = document.getElementById('num_people').value;
            const date = document.getElementById('order_date').value;
            const time = document.getElementById('order_time').value;
            
            if (!date || !time) {
                alert('Пожалуйста, сначала выберите дату и время');
                return;
            }
            
            try {
                const response = await fetch('/check_table_availability', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        date: date,
                        time: time,
                        num_people: numPeople
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    renderTables(data.available_tables);
                } else {
                    alert('Ошибка при проверке столиков');
                }
            } catch (error) {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при проверке столиков');
            }
        };
    }
    
    // Отрисовка столиков на карте
    // Обновите функцию renderTables в script.js
function renderTables(tables, booked_table_ids = []) {
    const map = document.getElementById('restaurant-map');
    const list = document.getElementById('tables-list');
    const tableIdInput = document.getElementById('table_id');
    
    // Очищаем предыдущие столики
    map.innerHTML = '';
    list.innerHTML = '';
    
    // Добавляем элементы интерьера
    const barCounter = document.createElement('div');
    barCounter.className = 'bar-counter';
    map.appendChild(barCounter);
    
    if (tables.length === 0) {
        list.innerHTML = '<p>Нет доступных столиков для выбранного количества гостей</p>';
        return;
    }
    
    // Создаем элементы столиков на карте
    tables.forEach(table => {
        const tableElement = document.createElement('div');
        tableElement.className = `table-${table.shape} table-${table.type}`;
        tableElement.style.left = `${table.position.x}%`;
        tableElement.style.top = `${table.position.y}%`;
        tableElement.dataset.tableId = table.id;
        tableElement.title = `${table.name}\nВместимость: ${table.capacity} чел.`;
        tableElement.textContent = table.id;
        
        // Помечаем занятые столики
        if (booked_table_ids.includes(table.id)) {
            tableElement.classList.add('table-unavailable');
            tableElement.title += '\n(Занят)';
            tableElement.style.opacity = '0.5';
            tableElement.style.cursor = 'not-allowed';
        } else {
            tableElement.addEventListener('click', function() {
                selectTable(this, table);
            });
        }
        
        map.appendChild(tableElement);
    });
    
    // Создаем список столиков
    tables.forEach(table => {
        const tableItem = document.createElement('div');
        tableItem.className = `table-item ${booked_table_ids.includes(table.id) ? 'unavailable' : ''}`;
        tableItem.dataset.tableId = table.id;
        tableItem.innerHTML = `
            <strong>${table.name}</strong><br>
            Вместимость: до ${table.capacity} человек<br>
            Тип: ${getTableTypeName(table.type)}
        `;
        
        if (!booked_table_ids.includes(table.id)) {
            tableItem.addEventListener('click', function() {
                selectTable(document.querySelector(`.table-${table.shape}[data-table-id="${table.id}"]`), table);
            });
        } else {
            tableItem.innerHTML += '<br><span style="color:red">Занят</span>';
        }
        
        list.appendChild(tableItem);
    });
    
    // Добавляем легенду
    const legend = document.createElement('div');
    legend.className = 'table-legends';
    legend.innerHTML = `
        <div class="legend-item"><div class="legend-color" style="background-color:#4CAF50"></div>У окна</div>
        <div class="legend-item"><div class="legend-color" style="background-color:#2196F3"></div>С диваном</div>
        <div class="legend-item"><div class="legend-color" style="background-color:#9C27B0"></div>Центральный</div>
        <div class="legend-item"><div class="legend-color" style="background-color:#FF9800"></div>Барная стойка</div>
        <div class="legend-item"><div class="legend-color" style="background-color:#607D8B"></div>Банкетный</div>
    `;
    list.appendChild(legend);
}

function selectTable(element, table) {
    // Снимаем выделение со всех столиков
    document.querySelectorAll('.table-circle, .table-square, .table-rectangle, .table-item').forEach(el => {
        el.classList.remove('table-selected', 'selected');
    });
    
    // Выделяем выбранный столик
    element.classList.add('table-selected');
    document.querySelector(`.table-item[data-table-id="${table.id}"]`).classList.add('selected');
    
    // Сохраняем ID выбранного столика
    document.getElementById('table_id').value = table.id;
    
    // Показываем информацию о столике
    const infoDiv = document.createElement('div');
    infoDiv.className = 'table-info active';
    infoDiv.innerHTML = `
        <h4>${table.name}</h4>
        <p>Вместимость: до ${table.capacity} человек</p>
        <p>Тип: ${getTableTypeName(table.type)}</p>
        <p>Расположение: ${getTablePosition(table.position)}</p>
    `;
    
    const oldInfo = document.querySelector('.table-info');
    if (oldInfo) oldInfo.remove();
    document.getElementById('tables-list').prepend(infoDiv);
}

function getTableTypeName(type) {
    const types = {
        'window': 'У окна',
        'sofa': 'С диваном',
        'center': 'Центральный',
        'bar': 'Барная стойка',
        'banquet': 'Банкетный'
    };
    return types[type] || type;
}

function getTablePosition(pos) {
    if (pos.y < 30) return "Передняя часть зала";
    if (pos.y > 70) return "Центр зала";
    if (pos.x > 70) return "Барная зона";
    return "Основная зона";
}
    
    // Автоматическая проверка столиков при выборе даты/времени
    const dateInput = document.getElementById('order_date');
    const timeInput = document.getElementById('order_time');
    
    if (dateInput && timeInput) {
        dateInput.addEventListener('change', function() {
            if (this.value && timeInput.value) {
                checkTables();
            }
        });
        
        timeInput.addEventListener('change', function() {
            if (this.value && dateInput.value) {
                checkTables();
            }
        });
    }
});