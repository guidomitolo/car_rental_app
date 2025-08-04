from .core import get_db


class Operator():

    def __init__(self, table):
        self.table = table
        self._connection = get_db()

    def _build_join_query(self, joins) -> list[str, str]:
        fk_select_fields = []
        fk_join_clauses = []
        for fk_table, fk_fields in joins.items():
            fk_select_fields += [f"{fk_table}.{col} as {fk_table}_{col}" for col in fk_fields]
            fk_join_clauses.append(
                f"INNER JOIN {fk_table} on {fk_table}.id = {self.table}.{fk_table}_id"
            )
        return ", ".join(fk_select_fields), " ".join(fk_join_clauses)

    def _execute_query(self, query: str, params: tuple = None, dictionary_cursor: bool = False):
        cursor_type = self._connection.cursor(dictionary=dictionary_cursor)
        try:
            cursor_type.execute(query, params)
            if query.strip().lower().startswith(('update', 'delete', 'insert')):
                self._connection.commit()
                return cursor_type.lastrowid
            else:
                return cursor_type.fetchall()
        except Exception as e:
            self._connection.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            cursor_type.close()

    def select(self, fields: str = '*', id: int = None, joins: list = None) -> list:
        query = f"SELECT {self.table}.{fields} FROM {self.table}"
        params = ()
        if joins:
            fk_fields, join_clauses = self._build_join_query(joins)
            select_fields = f"{self.table}.{fields}, {fk_fields}"
            query = f"SELECT {select_fields} FROM {self.table} {join_clauses}"
            params = ()
        if id:
            query = query + f" WHERE {self.table}.id = %s"
            params = (id,)
        return self._execute_query(query, params, True)

    def update_record(self, id: int, data: dict) -> dict:
        fields_placeholders = [f'{key} = %s' for key in data.keys()]
        set_clause = ", ".join(fields_placeholders)
        values_to_insert = tuple(list(data.values()) + [id])
        query = f"UPDATE {self.table} SET {set_clause} WHERE id = %s;"
        return self._execute_query(query, values_to_insert, True)

    def create(self, data) -> dict:
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {self.table} ({fields}) VALUES ({placeholders});"
        values_to_insert = tuple(data.values())
        return self._execute_query(query, values_to_insert, True)

    def delete(self, id: int) -> None:
        query = f"DELETE FROM {self.table} WHERE id = %s;"
        return self._execute_query(query, (id,), True)