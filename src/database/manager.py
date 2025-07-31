from .core import get_db


class Operator():

    def __init__(self, table, fields = '*', id=None, fks = None):
        self.connection = get_db()
        self.table = table
        self.fks = fks
        self.fields = fields
        self.id = id

    def _select_id_resolver(self, query: str) -> tuple[tuple, str]:
        updated_query = query + f" WHERE {self.table}.id = %s"
        return (self.id,), updated_query

    def _get_fk_table_data(self, table: str) -> dict:
        query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %s"
        cursor = self.connection.cursor()
        cursor.execute(
            operation=query,
            params=(table,)
        )
        result = cursor.fetchall()    
        return [col_name[0] for col_name in result] + ['id']

    def _build_join_query(self) -> list[str, str]:
        fk_select_fields = []
        fk_join_clauses = []
        for fk in self.fks:
            fk_table = fk.split('_')[0]
            columns = self._get_fk_table_data(fk_table)
            fk_select_fields += [f"{fk_table}.{col} as {fk_table}_{col}" for col in columns]
            fk_join_clauses.append(
                f"INNER JOIN {fk_table} on {fk_table}.id = {self.table}.{fk}"
            )
        return ", ".join(fk_select_fields), " ".join(fk_join_clauses)

    def _build_query_result(self, result: list) -> dict:
        fk_tables = [fk.split("_")[0] for fk in self.fks]
        for row in result:
            for fk_table in fk_tables:
                fields = [field for field in row.keys() if fk_table in field]
                row[fk_table] = {}
                for key in fields:
                    row[fk_table].update({key.split("_", 1)[1]: row.get(key)})
                    if key not in self.fks: row.pop(key)
        return result

    def _select_fk_resolver(self) -> dict:
        fk_fields, join_clauses = self._build_join_query()
        select_fields = f"{self.table}.{self.fields}, {fk_fields}"
        query = f"SELECT {select_fields} FROM {self.table} {join_clauses}"
        params = ()
        if self.id: params, query = self._select_id_resolver(query)
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(
                operation= f"{query};",
                params=params
            )
            result = cursor.fetchall()
            return self._build_query_result(result)
        except Exception as e:
            print(f"Error selecting data: {e}")
            raise
        finally:
            cursor.close()

    def select(self) -> dict:
        params, query = self._select_id_resolver(f"SELECT {self.table}.{self.fields} FROM {self.table}")
        if self.fks: return self._select_fk_resolver()
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(
                operation= f"{query};",
                params=params
            )
            result = cursor.fetchall()
            if len(params) != 0: result = result[0]
            return result
        except Exception as e:
            print(f"Error selecting data: {e}")
            raise
        finally:
            cursor.close()

    def update_record(self, data: dict) -> dict:
        fields_placeholders = [f'{key} = %s' for key in data.keys()]
        set_clause = ", ".join(fields_placeholders)
        values_to_insert = tuple(list(data.values()) + [self.id])
        query = f"UPDATE {self.table} SET {set_clause} WHERE id = %s;"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, values_to_insert)
            self.connection.commit()
            print(cursor.rowcount, "record(s) affected")
            return self.select()
        except Exception as e:
            self.connection.rollback()
            print(f"Error updating data: {e}")
            raise
        finally:
            cursor.close()

    def create(self, data) -> dict:
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {self.table} ({fields}) VALUES ({placeholders});"
        values_to_insert = tuple(data.values())
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, values_to_insert)
            self.connection.commit()
            return self.select(cursor.lastrowid, self.fks)
        except Exception as e:
            self.connection.rollback()
            print(f"Error inserting data: {e}")
            raise
        finally:
            cursor.close()

    def delete(self) -> None:
        cursor = self.connection.cursor()
        query = f"DELETE FROM {self.table} WHERE id = {self.idd};"
        try:
            cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"Error inserting data: {e}")
            raise
        finally:
            cursor.close()