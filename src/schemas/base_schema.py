from pydantic import BaseModel, model_validator
from typing import ClassVar
from ..database.manager import Operator



class Model(BaseModel):

    _sql_manager: ClassVar = Operator
    _db_table: ClassVar[str] = ''
    _db_fks: ClassVar[dict] = {}
    _db_fields: ClassVar[list] = ['id', 'created_at']

    def update(self, data:dict) -> None:
        row = self._sql_manager(table=self._db_table, id=self.id).update_record(data)
        updated_fields = self.model_fields_set.intersection(set(data.keys()))
        for field in updated_fields:
            setattr(self, field, row[field])

    def create(self,) -> BaseModel:
        new_entity = self.model_dump(exclude_none=True, include=self.model_fields.keys())
        fks = self._db_fks.keys()
        row = self._sql_manager(table=self._db_table, fks=fks).create(new_entity)
        row = self.check_fks(row)
        return self.__class__(**row)

    def remove(self) -> None:
        self._sql_manager(self._db_table).delete(self.id)

    @classmethod
    def check_fks(cls, row) -> 'Model':
        fks = cls._db_fks.keys()
        for fk in fks:
            fk_table = cls._db_fks.get(fk)
            fk_object = fk_table(**row[fk_table._db_table])
            row[fk_table._db_table] = fk_object
        return row
    
    @classmethod
    def get(cls, id:int) -> 'Model':
        row = cls._sql_manager(table=cls._db_table, id=id, fks=cls._db_fks.keys()).select()[0]
        row = cls.check_fks(row)
        return cls(**row)
    
    @classmethod
    def list(cls,) -> list['Model']:
        fks = cls._db_fks.keys()
        result_list = []
        rows = cls._sql_manager(table=cls._db_table, fks=cls._db_fks.keys()).select()
        for row in rows:
            row = cls.check_fks(row)
            obj = cls(**row)
            result_list.append(obj)
        return result_list
    
    class Config:
        extra = "allow"
