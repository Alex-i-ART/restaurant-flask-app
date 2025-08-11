from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import uuid
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

# Данные о столиках
tables = [
    {"id": 1, "name": "Столик 1", "status": "available", "x1": 50, "y1": 50, "x2": 150, "y2": 150},
    {"id": 2, "name": "Столик 2", "status": "available", "x1": 200, "y1": 50, "x2": 300, "y2": 150},
    {"id": 3, "name": "Столик 3", "status": "available", "x1": 350, "y1": 50, "x2": 450, "y2": 150},
    {"id": 4, "name": "Столик 4", "status": "available", "x1": 50, "y1": 200, "x2": 150, "y2": 300},
    {"id": 5, "name": "Столик 5", "status": "available", "x1": 200, "y1": 200, "x2": 300, "y2": 300},
    {"id": 6, "name": "Столик 6", "status": "available", "x1": 350, "y1": 200, "x2": 450, "y2": 300},
    {"id": 7, "name": "Столик 7", "status": "available", "x1": 50, "y1": 350, "x2": 150, "y2": 450},
    {"id": 8, "name": "Столик 8", "status": "available", "x1": 200, "y1": 350, "x2": 300, "y2": 450},
    {"id": 9, "name": "Столик 9", "status": "available", "x1": 350, "y1": 350, "x2": 450, "y2": 450},
    {"id": 10, "name": "Столик 10", "status": "available", "x1": 500, "y1": 50, "x2": 600, "y2": 150},
    {"id": 11, "name": "Столик 11", "status": "available", "x1": 500, "y1": 200, "x2": 600, "y2": 300},
    {"id": 12, "name": "Столик 12", "status": "available", "x1": 500, "y1": 350, "x2": 600, "y2": 450},
    {"id": 13, "name": "Бар", "status": "available", "x1": 650, "y1": 200, "x2": 750, "y2": 300}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html', menu_items=menu_items)

@app.route('/select_table')
def select_table():
    """Страница выбора столика"""
    selected_table_id = session.get('selected_table_id')
    return render_template('select_table.html', tables=tables, selected_table_id=selected_table_id)

@app.route('/set_table', methods=['POST'])
def set_table():
    """Установка выбранного столика в сессии"""
    table_id = request.form.get('table_id')
    if table_id:
        session['selected_table_id'] = int(table_id)
        session['selected_table_name'] = next((t['name'] for t in tables if t['id'] == int(table_id)), 'Неизвестный столик')
    return redirect(url_for('view_cart'))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_id = request.json.get('item_id')
    item = next((item for item in menu_items if item['id'] == item_id), None)

    if not item:
        return jsonify({'success': False, 'message': 'Блюдо не найдено'}), 404

    cart = session.get('cart', {})
    item_name = item['name']

    if item_name in cart:
        cart[item_name]['quantity'] += 1
    else:
        cart[item_name] = {'price': item['price'], 'quantity': 1, 'id': item['id']}

    session['cart'] = cart
    total_items_in_cart = sum(item_data['quantity'] for item_data in cart.values())
    return jsonify({'success': True, 'total_items': total_items_in_cart})

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    selected_table_id = session.get('selected_table_id')
    selected_table_name = session.get('selected_table_name', 'Не выбран')
    
    return render_template('cart.html', 
                         cart=cart, 
                         total_price=total_price,
                         selected_table_id=selected_table_id,
                         selected_table_name=selected_table_name)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    item_name = request.form.get('item_name')
    action = request.form.get('action')
    cart = session.get('cart', {})

    if item_name in cart:
        if action == 'increase':
            cart[item_name]['quantity'] += 1
        elif action == 'decrease':
            cart[item_name]['quantity'] -= 1
            if cart[item_name]['quantity'] <= 0:
                del cart[item_name]
        elif action == 'remove':
            del cart[item_name]

    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/place_order', methods=['POST'])
def place_order():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('view_cart'))

    order_date = request.form.get('order_date')
    order_time = request.form.get('order_time')
    num_people = request.form.get('num_people')
    table_id = session.get('selected_table_id')
    table_name = session.get('selected_table_name')

    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    order_id = str(uuid.uuid4())

    session['last_order'] = {
        'id': order_id,
        'items': cart,
        'total': total_price,
        'date': order_date,
        'time': order_time,
        'people': num_people,
        'table': {'id': table_id, 'name': table_name}
    }

    session.pop('cart', None)
    session.pop('selected_table_id', None)
    session.pop('selected_table_name', None)
    return redirect(url_for('order_confirmation'))

@app.route('/order_confirmation')
def order_confirmation():
    last_order = session.pop('last_order', None)
    if not last_order:
        return redirect(url_for('index'))
    return render_template('order_confirmation.html', order=last_order)

if __name__ == '__main__':
    app.run(debug=True)