from pydantic import BaseModel, model_validator
from typing import ClassVar
from ..database.manager import Operator



class Model(BaseModel):

    _sql_manager: ClassVar = Operator
    _db_table: ClassVar[str] = ''
    _db_fks: ClassVar[dict] = {}
    _db_fields: ClassVar[list] = ['id', 'created_at']

    def update(self, data:dict) -> None:
        headers, row = self._sql_manager(self._db_table).update_record(self.id, data)
        updated_fields = self.model_fields_set.intersection(set(data.keys()))
        data = dict(zip(headers, row))
        for field in updated_fields:
            setattr(self, field, data[field])

    def create(self,) -> BaseModel:
        new_entity = self.model_dump(exclude_none=True, include=self.model_fields_set)
        headers, row = self._sql_manager(self._db_table).create(new_entity)
        return self.__class__(**dict(zip(headers, row)))

    def remove(self) -> None:
        self._sql_manager(self._db_table).delete(self.id)

    @model_validator(mode='after')
    def check_fks(self,) -> 'Model':
        if self._db_fks:
            headers, row = self._sql_manager(self._db_table).select(self.id, self._db_fks.keys())
            # fk_obj = model(**dict(zip(headers, row)))
            # setattr(self, table, fk_obj)
            # for fk, model in self.Meta._db_fks__.items():
            #     table, id = fk.split("_")
            #     headers, row = self._sql_manager(table).retrieve(getattr(self, fk))
            #     fk_obj = model(**dict(zip(headers, row)))
            #     setattr(self, table, fk_obj)
        return self
    
    @classmethod
    def get(cls, id:int) -> 'Model':
        headers, row = cls._sql_manager(cls._db_table).select(id, cls._db_fks.keys())
        return cls(**dict(zip(headers, row)))
    
    @classmethod
    def list(cls,) -> list['Model']:
        result_list = []
        headers, rows = cls._sql_manager(cls._db_table).select()
        for row in rows:
            obj = cls(**dict(zip(headers, row)))
            result_list.append(obj)
        return result_list
    
    class Config:
        extra = "allow"
