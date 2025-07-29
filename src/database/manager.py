from .core import get_db


class Operator():

    def __init__(self, table):
        self.connection = get_db()
        self.table = table

    def _build_join_query(self, fks, primary_table_alias=None):
        fk_select_fields = []
        fk_join_clauses = []
        primary_table_prefix = f"{primary_table_alias}." if primary_table_alias else f"{self.table}."
        for fk in fks:
            fk_table = fk.split('_')[0]
            alias = f"{fk_table}_alias"
            fk_select_fields.append(f"{alias}.*")
            fk_join_clauses.append(
                f"INNER JOIN {fk_table} AS {alias} ON {alias}.id = {primary_table_prefix}{fk}"
            )
        return ", ".join(fk_select_fields), " ".join(fk_join_clauses)

    def select(self, id=None,fks=None):
        params = ()
        select_fields = f"{self.table}.*"
        join_clauses = ""
        if fks:
            fk_fields, fk_joins = self._build_join_query(fks, primary_table_alias=self.table)
            select_fields = f"{self.table}.*, {fk_fields}"
            join_clauses = fk_joins

        query = f"SELECT {select_fields} FROM {self.table} {join_clauses}"

        if id:
            query += f"WHERE {self.table}.id = %s"
            params = (id,)

        query += ";"

        cursor = self.connection.cursor()
        try:
            cursor.execute(
                operation=query,
                params=params
            )
            rows = cursor.fetchall()
            if id:
                rows = rows[0]
            headers = cursor.column_names
            return headers, rows
        except Exception as e:
            print(f"Error selecting data: {e}")
            raise
        finally:
            cursor.close()

    def update_record(self, id, data):
        fields_placeholders = [f'{key} = %s' for key in data.keys()]
        set_clause = ", ".join(fields_placeholders)
        values_to_insert = tuple(list(data.values()) + [id])
        query = f"UPDATE {self.table} SET {set_clause} WHERE id = %s;"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, values_to_insert)
            self.connection.commit()
            print(cursor.rowcount, "record(s) affected")
            return self.select(id)
        except Exception as e:
            self.connection.rollback()
            print(f"Error updating data: {e}")
            raise
        finally:
            cursor.close()

    def create(self, data):
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {self.table} ({fields}) VALUES ({placeholders});"
        values_to_insert = tuple(data.values())
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, values_to_insert)
            self.connection.commit()
            return self.select(cursor.lastrowid)
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


#     def fks(self,) -> None:
#         query = f"SELECT rental_order.*, customer.* FROM rental_order INNER JOIN customer on rental_order.customer_id = customer.id WHERE rental_order.id = 1;"
#         cursor = self.connection.cursor()
#         try:
#             cursor.execute(query)
#             row = cursor.fetchone()
#             if not row:
#                 raise Exception('Not found')
#             headers = cursor.column_names
#             return headers, row
#         except Exception as e:
#             print(f"Error selecting data: {e}")
#             raise e
#         finally:
#             cursor.close()


# if __name__ == '__main__':
#     Operator('rental_order').fks()