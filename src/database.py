import mysql.connector
from config import DB_CONFIG
from flask import g



def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = mysql.connector.connect(**DB_CONFIG)
    return db

def select(table):
    db = get_db()
    query = f"SELECT * FROM {table};"
    cursor = db.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        result_list = []
        headers = cursor.column_names
        for row in rows:
            data = dict(zip(headers, row))
            result_list.append(data)
        return result_list
    except Exception as e:
        print(f"Error selecting data: {e}")
        raise
    finally:
        cursor.close()


def retrieve(table, id):

    def get_fk_data(order_data):
        fk1_data = retrieve('customer', order_data['customer_id'])
        fk2_data = retrieve('vehicle', order_data['vehicle_id'])
        order_data.update({'customer': fk1_data})
        order_data.update({'vehicle': fk2_data})
        return order_data

    db = get_db()
    query = f"SELECT * FROM {table} WHERE id = {id};"
    cursor = db.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        if not result:
            raise Exception('Not found')
        headers = cursor.column_names
        data = dict(zip(headers, result))
        if table == 'rental_order':
            # not scalable
            get_fk_data(data)
        return data
    except Exception as e:
        print(f"Error selecting data: {e}")
        raise e
    finally:
        cursor.close()


def update(table, id, data):
    db = get_db()
    new_attrs = "".join([f"{key} = '{value}', " for key, value in data.items() if key != 'id'])
    query = f"UPDATE {table} SET {new_attrs[:-2]} WHERE id = {id};"
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit()
        return retrieve(table, id)
    except Exception as e:
        db.rollback()
        print(f"Error updating data: {e}")
        raise
    finally:
        cursor.close()

def create(table, data):
    # https://g.co/gemini/share/ccf294437b44
    db = get_db()
    filtered_data = {key: value for key, value in data.items() if key != 'id'}
    fields = ", ".join(filtered_data.keys())
    placeholders = ", ".join(["%s"] * len(filtered_data))
    query = f"INSERT INTO {table} ({fields}) VALUES ({placeholders});"
    values_to_insert = tuple(filtered_data.values())
    cursor = db.cursor()
    try:
        cursor.execute(query, values_to_insert)
        db.commit()
        return retrieve(table, cursor.lastrowid)
    except Exception as e:
        db.rollback()
        print(f"Error inserting data: {e}")
        raise
    finally:
        cursor.close()

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_app_db(app):
    app.teardown_appcontext(close_connection)