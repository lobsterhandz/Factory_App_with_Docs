from sqlalchemy import func, desc
from models import db, Employee, Order, Product, Customer, Production


# Task 1: Analyze Employee Performance
def analyze_employee_performance():
    result = db.session.query(
        Employee.name,
        func.sum(Production.quantity_produced).label('total_quantity')
    ).join(Production, Employee.id == Production.product_id) \
        .group_by(Employee.name) \
        .all()
    return [{"employee": row[0], "total_quantity": row[1]} for row in result]


# Task 2: Identify Top-Selling Products
def top_selling_products():
    result = db.session.query(
        Product.name,
        func.sum(Order.quantity).label('total_sold')
    ).join(Order, Product.id == Order.product_id) \
        .group_by(Product.name) \
        .order_by(desc('total_sold')) \
        .all()
    return [{"product": row[0], "total_sold": row[1]} for row in result]


# Task 3: Determine Customer Lifetime Value
def customer_lifetime_value(threshold=1000):
    result = db.session.query(
        Customer.name,
        func.sum(Order.total_price).label('lifetime_value')
    ).join(Order, Customer.id == Order.customer_id) \
        .group_by(Customer.name) \
        .having(func.sum(Order.total_price) >= threshold) \
        .all()
    return [{"customer": row[0], "lifetime_value": row[1]} for row in result]


# Task 4: Evaluate Production Efficiency
def evaluate_production_efficiency(production_date):
    result = db.session.query(
        Product.name,
        func.sum(Production.quantity_produced).label('total_produced')
    ).join(Production, Product.id == Production.product_id) \
        .filter(Production.date_produced == production_date) \
        .group_by(Product.name) \
        .all()
    return [{"product": row[0], "total_produced": row[1]} for row in result]
