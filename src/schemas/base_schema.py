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
    def build_fk_object(cls, row) -> 'Model':
        fks = cls._db_fks.keys()
        for fk in fks:
            fk_table = cls._db_fks.get(fk)
            fk_object = fk_table(**row[fk_table._db_table])
            row[fk_table._db_table] = fk_object
        return row
    
    @classmethod
    def get_fk_fields(cls,) -> dict:
        fk_field = []
        for key, value in cls._db_fks.items():
            fk_field.append({'table': key.split('_')[0], 'fields': value._db_table_fields})
        return fk_field
    
    @classmethod
    def get(cls, id:int) -> 'Model':
        fk_joins = cls.get_fk_fields()
        row = cls._sql_manager(table=cls._db_table, id=id, fks=cls._db_fks.keys()).select(join=fk_joins)[0]
        row = cls.build_fk_object(row)
        return cls(**row)
    
    @classmethod
    def list(cls,) -> list['Model']:
        fk_joins = cls.get_fk_fields()
        result_list = []
        rows = cls._sql_manager(table=cls._db_table, fks=cls._db_fks.keys()).select(join=fk_joins)
        for row in rows:
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
