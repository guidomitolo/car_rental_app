from pydantic import BaseModel, model_validator
from typing import ClassVar
from ..database.queries import SQLQuery
from ..database.helpers import format_db_input



class Model(BaseModel, extra='allow'):

    sql_manager:ClassVar = SQLQuery

    @format_db_input
    def update(self, data:dict) -> None:
        headers, row = self.sql_manager(self.Meta.__db_table__).update_record(self.id, data)
        updated_fields = self.model_fields_set.intersection(set(data.keys()))
        data = dict(zip(headers, row))
        for field in updated_fields:
            setattr(self, field, data[field])

    @format_db_input
    def create(self,) -> BaseModel:
        headers, row = self.sql_manager(self.Meta.__db_table__).create(self.__dict__)
        return self.__class__(**dict(zip(headers, row)))

    def remove(self) -> None:
        self.sql_manager(self.Meta.__db_table__).delete(self.id)

    @model_validator(mode='after')
    def check_fks(self,) -> 'Model':
        if hasattr(self.Meta, '__db_fks__'):
            for fk, model in self.Meta.__db_fks__.items():
                table, id = fk.split("_")
                headers, row = self.sql_manager(table).retrieve(getattr(self, fk))
                fk_obj = model(**dict(zip(headers, row)))
                setattr(self, table, fk_obj)
        return self

    @classmethod
    def format_input(cls, data:dict) -> dict:
        for key, value in data.items():
            if isinstance(value, bool):
                data[key] = int(value)
        return data

    @classmethod
    def get(cls, id:int) -> 'Model':
        headers, row = cls.sql_manager(cls.Meta.__db_table__).retrieve(id)
        return cls(**dict(zip(headers, row)))
    
    @classmethod
    def list(cls,) -> list['Model']:
        result_list = []
        headers, rows = cls.sql_manager(cls.Meta.__db_table__).select()
        for row in rows:
            obj = cls(**dict(zip(headers, row)))
            result_list.append(obj)
        return result_list

    class Meta:
        __db_table__ = ''
        __db_fks__ = {}

