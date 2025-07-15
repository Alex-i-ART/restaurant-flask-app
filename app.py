from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import uuid # Для генерации уникальных ID заказа
import os

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
    """
    Обрабатывает оформление заказа.
    """
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('view_cart')) # Нельзя оформить пустой заказ

    order_date = request.form.get('order_date')
    order_time = request.form.get('order_time')
    num_people = request.form.get('num_people')

    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    order_id = str(uuid.uuid4()) # Генерируем уникальный ID заказа

    # В реальном приложении эти данные сохранялись бы в базу данных
    # Для примера сохраним в сессию, чтобы показать на странице подтверждения
    session['last_order'] = {
        'id': order_id,
        'items': cart,
        'total': total_price,
        'date': order_date,
        'time': order_time,
        'people': num_people
    }

    session.pop('cart', None) # Очищаем корзину после оформления заказа
    return redirect(url_for('order_confirmation'))

@app.route('/order_confirmation')
def order_confirmation():
    """
    Страница подтверждения заказа.
    """
    last_order = session.pop('last_order', None) # Получаем и сразу удаляем из сессии
    if not last_order:
        return redirect(url_for('index')) # Если нет информации о последнем заказе, перенаправляем на главную
    return render_template('order_confirmation.html', order=last_order)

# if __name__ == '__main__':
#     app.run() # debug=True для разработки, отключите в продакшене
