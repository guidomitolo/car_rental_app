from pydantic import BaseModel
from ..database.queries import SQLQuery
from ..database.helpers import format_db_input



class Model(BaseModel):

    @classmethod
    def format_input(cls, data:dict) -> dict:
        for key, value in data.items():
            if isinstance(value, bool):
                data[key] = int(value)
        return data
    
    @classmethod
    def fk_resolver(cls, data:dict) -> None:
        for fk in cls.Meta.__db_fks__:
            table, id = fk.split("_")
            headers, row = SQLQuery(table).retrieve(data[fk])
            data[table] = dict(zip(headers, row))

    @classmethod
    def get(cls, id:int) -> BaseModel:
        headers, row = SQLQuery(cls.Meta.__db_table__).retrieve(id)
        data = dict(zip(headers, row))
        cls.fk_resolver(data)
        return cls(**data)
    
    @classmethod
    def list(cls,) -> list[BaseModel]:
        result_list = []
        headers, rows = SQLQuery(cls.Meta.__db_table__).select()
        for row in rows:
            data = cls(**dict(zip(headers, row)))
            cls.fk_resolver(data)
            result_list.append(data)
        return result_list
    
    @format_db_input
    def update(self, data:dict) -> None:
        headers, row = SQLQuery(self.Meta.__db_table__).update_record(self.id, data)
        updated_fields = self.model_fields_set.intersection(set(data.keys()))
        data = dict(zip(headers, row))
        for field in updated_fields:
            setattr(self, field, data[field])

    @classmethod
    @format_db_input
    def create(cls, data:dict) -> BaseModel:
        return SQLQuery(cls.Meta.__db_table__).create(data)

    def remove(self) -> None:
        SQLQuery(self.Meta.__db_table__).delete(self.id)

    class Meta:
        __db_table__ = ''
        __db_fks__ = []

