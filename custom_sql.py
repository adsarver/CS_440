from datetime import datetime
from typing import Union
import dbtypes
from sqlalchemy.sql import text
from sqlalchemy import Engine
from sqlalchemy.orm import Session
import inspect

class custom_sql():
    def __init__(self, session:Session, engine:Engine):
        self.session = session
        self.engine = engine
    
    # Accepts class type and string input
    def query_all(self, cls: Union[dbtypes.Mixin, str]):
        attrs = dict()
        
        if type(cls) is str:
            cls = cls.lower()
            if "_" in cls:
                cls = cls.replace('_', '')
            for name, obj in inspect.getmembers(dbtypes):
                if name.lower() == cls:
                    cls = obj()
                    break
        
        for k in cls.__mapper__.columns.keys():
            attrs[k] = getattr(cls, k)
            
        objslist = attrs.copy()

        with self.engine.connect() as con:
            statement = text(""f"SELECT * FROM {cls.__tablename__ if type(cls) is not str else cls}""")
            rs = con.execute(statement)

            found = list()
            for tup in rs:
                if isinstance(cls, dbtypes.Mixin):
                    temp = cls
                else:
                    temp = cls()
                
                for i in range(len(list(attrs.keys()))):
                    key = list(attrs.keys())[i]
                    setattr(temp, key, tup[i])
                    
                    if "_id" in key and tup[i] is not None:
                        setattr(temp, key[:-3], self.query_where(key[:-3], f"id={tup[i] if type(tup[i]) == int else tup[i].id}")[0])

                
                found.append(temp)
                
            return found
        
    # Get all from cls where case
    def query_where(self, cls: Union[dbtypes.Mixin, str], where: str):
        attrs = dict()
        
        if type(cls) is str:
            cls = cls.lower()
            if "_" in cls:
                cls = cls.replace('_', '')
            for name, obj in inspect.getmembers(dbtypes):
                if name.lower() == cls:
                    cls = obj
                    break
        
        for k in cls.__mapper__.columns.keys():
            attrs[k] = getattr(cls, k)
                            
        with self.engine.connect() as con:            
            statement = text(""f"SELECT * FROM {cls.__tablename__ if type(cls) is not str else cls} WHERE {where}""")
            rs = con.execute(statement)  

            found = list()
            for tup in rs:
                if isinstance(cls, dbtypes.Mixin):
                    temp = cls
                else:
                    temp = cls()
                    
                for i in range(len(list(attrs.keys()))):
                    key = list(attrs.keys())[i]
                    setattr(temp, key, tup[i])
                    
                    if "_id" in key and tup[i] is not None:
                        setattr(temp, key[:-3], self.query_where(key[:-3], f"id={tup[i] if type(tup[i]) == int else tup[i].id}")[0])
                
                found.append(temp)
                
            return found
        
    def create_entry(self, data: dbtypes.Mixin):
        attrs = dict()
        keys = ""
        colkeys = ""
        query = ""

        for k in data.__mapper__.columns.keys():
            attrs[k] = getattr(data, k)
            keys = keys + k + ", "
            colkeys = colkeys + ":" + k + ", "
        
        objslist = attrs.copy()
        
        for k, val in attrs.items():
            if "_id" in k and attrs[k] is not None:
                objslist[k[:-3]] = self.query_where(k[:-3], f"id={val}")[0]
            elif "_id" in k and attrs[k] is None:
                objslist[k] = getattr(data, k[:-3]).id
        
        for k, val in attrs.items():
            if val is not None:
                if type(val) == str:
                    query = query + f"{k}=\'{val}\' AND "
                elif type(val) == datetime:
                    val = val.strftime("%Y-%m-%d %H:%M:%S")
                    query = query + f"{k}=\'{val}\' AND "
                elif not isinstance(val, dbtypes.Mixin) and not isinstance(val, list):
                    query = query + f"{k}={val} AND "

        with self.engine.connect() as con:
            statement = text(f"INSERT INTO {data.__tablename__}({keys[:-2]}) VALUES({colkeys[:-2]})")
            con.execute(statement, attrs)
            con.commit()
            
            rs = self.query_where(data, query[:-5])[0]
            for key, val in objslist.items():
                setattr(rs, key, val)
            return rs
                
    def update_entry(self, data: dbtypes.Mixin):
        attrs = dict()
        values = ""
        for k in data.__mapper__.columns.keys():
            val = getattr(data, k)
            attrs[k] = getattr(data, k)
            values = values + k + "=" + " :" + k + ", "
            
        with self.engine.connect() as con:
                statement = text(""f"UPDATE {data.__tablename__} SET {values[:-2]} WHERE ID={data.id}""")
                con.execute(statement, attrs)
                con.commit()
                
    def delete_entry(self, data: dbtypes.Mixin):
        with self.engine.connect() as con:
            statement = text(""f"DELETE FROM {data.__tablename__} WHERE id=\'{data.id}\'""")
            con.execute(statement)
            con.commit()

            
    def create_tables(self):        
        for clas in self.classes:
            with self.engine.connect() as con:
                statement = text(""f"CREATE TABLE {clas.__tablename__} (""")
                # con.execute(statement)
                # con.commit()