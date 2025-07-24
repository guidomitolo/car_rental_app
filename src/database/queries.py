from .core import get_db


class SQLQuery():

    def __init__(self, table):
        self.connection = get_db()
        self.table = table

    def select(self,):
        query = f"SELECT * FROM {self.table};"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            headers = cursor.column_names
            return headers, rows
        except Exception as e:
            print(f"Error selecting data: {e}")
            raise
        finally:
            cursor.close()

    def retrieve(self, id):
        query = f"SELECT * FROM {self.table} WHERE id = {id};"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            row = cursor.fetchone()
            if not row:
                raise Exception('Not found')
            headers = cursor.column_names
            return headers, row
        except Exception as e:
            print(f"Error selecting data: {e}")
            raise e
        finally:
            cursor.close()

    def update_record(self, id, data):
        new_attrs = "".join([f"{key} = '{value}', " for key, value in data.items() if key != 'id'])
        query = f"UPDATE {self.table} SET {new_attrs[:-2]} WHERE id = {id};"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            return self.retrieve(id)
        except Exception as e:
            self.connection.rollback()
            print(f"Error updating data: {e}")
            raise
        finally:
            cursor.close()

    def create(self, data):
        data.pop('id')
        data.pop('created_at')
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {self.table} ({fields}) VALUES ({placeholders});"
        values_to_insert = tuple(data.values())
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, values_to_insert)
            self.connection.commit()
            return self.retrieve(cursor.lastrowid)
        except Exception as e:
            self.connection.rollback()
            print(f"Error inserting data: {e}")
            raise
        finally:
            cursor.close()

    def delete(self, id) -> None:
        cursor = self.connection.cursor()
        query = f"DELETE FROM {self.table} WHERE id = {id};"
        try:
            cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"Error inserting data: {e}")
            raise
        finally:
            cursor.close()