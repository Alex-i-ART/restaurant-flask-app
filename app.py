from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import uuid # Для генерации уникальных ID заказа
import os
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_super_secret_fallback_key_for_dev_only')

# Пример данных меню
menu_items = [
    {"id": 1, "name": "Борщ", "price": 350, "description": "Классический красный борщ с говядиной и сметаной.", "ingredients": ["свекла", "капуста", "картофель", "мясо говядины", "сметана", "зелень"]},
    {"id": 2, "name": "Салат Цезарь", "price": 420, "description": "Легендарный салат с курицей гриль, сухариками и пармезаном.", "ingredients": ["салат ромэн", "куриное филе", "гренки", "сыр пармезан", "помидоры черри", "соус Цезарь"]},
    {"id": 3, "name": "Паста Карбонара", "price": 550, "description": "Традиционная итальянская паста с беконом, яичным желтком и сыром.", "ingredients": ["спагетти", "бекон", "яичный желток", "сыр пармезан", "черный перец"]},
    {"id": 4, "name": "Стейк Рибай", "price": 1200, "description": "Сочный стейк из мраморной говядины с гарниром на выбор.", "ingredients": ["говядина рибай", "соль", "перец", "оливковое масло", "розмарин"]},
    {"id": 5, "name": "Чизкейк Нью-Йорк", "price": 300, "description": "Нежный сливочный десерт с ягодным соусом.", "ingredients": ["сливочный сыр", "печенье", "сливки", "сахар", "ягоды"]},
]

tables = [
    # Столики у окна (12 штук)
    *[{"id": i, "name": f"Столик у окна #{i}", "capacity": 2, "position": {"x": 5 + (i-1)*8, "y": 15}, "type": "window", "shape": "circle"} for i in range(1, 13)],
    
    # Столики с диванами (5 штук)
    *[{"id": i+12, "name": f"Угловой с диваном #{i+12}", "capacity": 4, "position": {"x": 15 + i*15, "y": 50}, "type": "sofa", "shape": "rectangle"} for i in range(1, 6)],
    
    # Центральные столики (6 штук)
    *[{"id": i+17, "name": f"Центральный #{i+17}", "capacity": 4, "position": {"x": 30 + (i-1)*10, "y": 70}, "type": "center", "shape": "circle"} for i in range(1, 7)],
    
    # Барная стойка (4 места)
    *[{"id": i+23, "name": f"Барное место #{i+23}", "capacity": 1, "position": {"x": 80 + (i-1)*5, "y": 10}, "type": "bar", "shape": "square"} for i in range(1, 5)],
    
    # Большой стол
    {"id": 28, "name": "Большой банкетный стол", "capacity": 10, "position": {"x": 85, "y": 30}, "type": "banquet", "shape": "rectangle"}
]

# Пример данных о бронированиях (в реальном приложении это будет в БД)
bookings = [
    {"id": 1, "table_id": 3, "date": "2023-12-25", "time": "19:00", "duration": 2},
    {"id": 2, "table_id": 15, "date": "2023-12-25", "time": "20:00", "duration": 3}
]

@app.context_processor
def utility_processor():
    def get_table_type_name(table_type):
        names = {
            'window': 'у окна',
            'sofa': 'с диваном',
            'center': 'центральный',
            'bar': 'барная стойка',
            'banquet': 'банкетный'
        }
        return names.get(table_type, table_type)
    return dict(get_table_type_name=get_table_type_name)

@app.route('/')
def index():
    """
    Главная страница: общая информация о ресторане и приветствие.
    """
    return render_template('index.html')

@app.route('/menu')
def menu():
    """
    Страница меню: отображает все доступные блюда.
    """
    return render_template('menu.html', menu_items=menu_items)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """
    Обрабатывает AJAX-запрос на добавление блюда в корзину.
    """
    item_id = request.json.get('item_id')
    item = next((item for item in menu_items if item['id'] == item_id), None)

    if not item:
        return jsonify({'success': False, 'message': 'Блюдо не найдено'}), 404

    # Инициализация корзины, если ее нет в сессии
    cart = session.get('cart', {})
    item_name = item['name']

    if item_name in cart:
        cart[item_name]['quantity'] += 1
    else:
        cart[item_name] = {'price': item['price'], 'quantity': 1, 'id': item['id']}

    session['cart'] = cart # Сохраняем обновленную корзину в сессии
    total_items_in_cart = sum(item_data['quantity'] for item_data in cart.values())
    return jsonify({'success': True, 'total_items': total_items_in_cart})

@app.route('/cart')
def view_cart():
    """
    Страница корзины: отображает выбранные блюда и форму для оформления заказа.
    """
    cart = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', cart=cart, total_price=total_price)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """
    Обновляет количество блюд в корзине или удаляет их.
    """
    item_name = request.form.get('item_name')
    action = request.form.get('action') # 'increase', 'decrease', 'remove'
    cart = session.get('cart', {})

    if item_name in cart:
        if action == 'increase':
            cart[item_name]['quantity'] += 1
        elif action == 'decrease':
            cart[item_name]['quantity'] -= 1
            if cart[item_name]['quantity'] <= 0:
                del cart[item_name] # Удаляем блюдо, если количество 0 или меньше
        elif action == 'remove':
            del cart[item_name]

    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/place_order', methods=['POST'])
def place_order():
    try:
        cart = session.get('cart', {})
        if not cart:
            return redirect(url_for('view_cart'))

        order_date = request.form.get('order_date')
        order_time = request.form.get('order_time')
        num_people = int(request.form.get('num_people'))
        table_id = int(request.form.get('table_id'))
        
        # Проверяем, что столик еще свободен
        requested_datetime = datetime.strptime(f"{order_date} {order_time}", "%Y-%m-%d %H:%M")
        for booking in bookings:
            booking_datetime = datetime.strptime(f"{booking['date']} {booking['time']}", "%Y-%m-%d %H:%M")
            booking_end = booking_datetime + timedelta(hours=booking['duration'])
            
            if booking['table_id'] == table_id and requested_datetime >= booking_datetime and requested_datetime < booking_end:
                return redirect(url_for('view_cart'))  # В реальном приложении нужно показать ошибку

        # Создаем бронирование (в реальном приложении сохраняем в БД)
        new_booking = {
            "id": len(bookings) + 1,
            "table_id": table_id,
            "date": order_date,
            "time": order_time,
            "duration": 2  # Стандартное время брони - 2 часа
        }
        bookings.append(new_booking)

        total_price = sum(item['price'] * item['quantity'] for item in cart.values())
        order_id = str(uuid.uuid4())

        session['last_order'] = {
            'id': order_id,
            'items': cart,
            'total': total_price,
            'date': order_date,
            'time': order_time,
            'people': num_people,
            'table_id': table_id
        }

        session.pop('cart', None)
        return redirect(url_for('order_confirmation'))
        
    except Exception as e:
        print(f"Error placing order: {e}")
        return redirect(url_for('view_cart'))

@app.route('/order_confirmation')
def order_confirmation():
    """
    Страница подтверждения заказа.
    """
    last_order = session.pop('last_order', None) # Получаем и сразу удаляем из сессии
    if not last_order:
        return redirect(url_for('index')) # Если нет информации о последнем заказе, перенаправляем на главную
    
    if last_order:
        print(f"DEBUG: last_order received: {last_order}")
        if 'items' in last_order and isinstance(last_order['items'], dict):
            print(f"DEBUG: order.items (cart) content: {last_order['items']}")
            for item_id, item_data in last_order['items'].items():
                print(f"DEBUG: Item: ID={item_id}, Data={item_data}, Type of Data={type(item_data)}")
                if isinstance(item_data, dict):
                    print(f"DEBUG: Item Data Keys: {item_data.keys()}")
                else:
                    print(f"DEBUG: WARNING: item_data is not a dict for {item_id}!")
        else:
            print("DEBUG: 'items' not found in last_order or not a dict.")
    else:
        print("DEBUG: No last_order in session.")

    return render_template('order_confirmation.html', order=last_order)

@app.route('/check_table_availability', methods=['POST'])
def check_table_availability():
    try:
        date_str = request.json.get('date')
        time_str = request.json.get('time')
        num_people = int(request.json.get('num_people'))
        
        if not date_str or not time_str:
            return jsonify({'success': False, 'message': 'Укажите дату и время'})
        
        requested_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        
        # Находим занятые столики
        booked_table_ids = []
        for booking in bookings:
            booking_datetime = datetime.strptime(f"{booking['date']} {booking['time']}", "%Y-%m-%d %H:%M")
            booking_end = booking_datetime + timedelta(hours=booking['duration'])
            
            if requested_datetime >= booking_datetime and requested_datetime < booking_end:
                booked_table_ids.append(booking['table_id'])
        
        # Фильтруем столики по вместимости и занятости
        available_tables = [
            table for table in tables 
            if table['capacity'] >= num_people 
            and table['id'] not in booked_table_ids
        ]
        
        return jsonify({
            'success': True,
            'available_tables': available_tables,
            'booked_table_ids': booked_table_ids
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

