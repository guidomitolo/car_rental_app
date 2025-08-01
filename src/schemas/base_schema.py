from pydantic import BaseModel, model_validator
from typing import ClassVar
from ..database.manager import Operator



class Model(BaseModel):

    _sql_manager: ClassVar = Operator
    _db_table: ClassVar[str] = ''
    _db_fks: ClassVar[dict] = {}
    _db_fields: ClassVar[list] = ['id', 'created_at']

    def update(self, data:dict) -> None:
        row = self._sql_manager(table=self._db_table).update_record(id=self.id, data=data)
        updated_fields = self.model_fields_set.intersection(set(data.keys()))
        for field in updated_fields:
            setattr(self, field, row[field])

    def create(self,) -> BaseModel:
        new_entity = self.model_dump(exclude_none=True, include=self.model_fields.keys())
        new_id = self._sql_manager(table=self._db_table).create(new_entity)
        return self.get(new_id)

    def remove(self) -> None:
        self._sql_manager(self._db_table).delete(self.id)

    @classmethod
    def build_query_result(self, row: dict, joins) -> dict:
        fk_tables = list(joins.keys())
        for fk_table in fk_tables:
            fields = joins[fk_table]
            row[fk_table] = {}
            for field in fields:
                alias_field = f"{fk_table}_{field}"
                row[fk_table].update({field: row.get(alias_field)})
                if alias_field != f"{fk_table}_id": row.pop(alias_field)
        return row

    @classmethod
    def build_fk_object(cls, row) -> 'Model':
        fks = cls._db_fks.keys()
        for fk in fks:
            fk_table = cls._db_fks.get(fk)
            fk_object = fk_table(**row[fk_table._db_table])
            row[fk_table._db_table] = fk_object
        return row
    
    @classmethod
    def get_fk_fields(cls,) -> dict:
        fk_fields = {}
        for key, value in cls._db_fks.items():
            fk_fields[key.split('_')[0]] = value._db_table_fields
        return fk_fields
    
    @classmethod
    def get(cls, id:int) -> 'Model':
        fk_joins = cls.get_fk_fields()
        row = cls._sql_manager(table=cls._db_table).select(id=id, joins=fk_joins)[0]
        row = cls.build_query_result(row, fk_joins)
        row = cls.build_fk_object(row)
        return cls(**row)
    
    @classmethod
    def list(cls,) -> list['Model']:
        fk_joins = cls.get_fk_fields()
        result_list = []
        rows = cls._sql_manager(table=cls._db_table).select(joins=fk_joins)
        for row in rows:
            row = cls.build_query_result(row, fk_joins)
            row = cls.build_fk_object(row)
            obj = cls(**row)
            result_list.append(obj)
        return result_list
    
    @classmethod
    @property
    def _db_table_fields(cls):
        return list(cls.model_fields.keys())
    
    class Config:
        extra = "allow"
