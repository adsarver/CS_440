from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, UniqueConstraint, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Mixin:
    sql = None
    def create(self):
        return self.__class__.sql.create_entry(self)
        
    def __repr__(self):
        package = self.__class__.__module__
        class_ = self.__class__.__name__
        attrs = sorted((k, getattr(self, k)) for k in self.__mapper__.columns.keys())
        sattrs = ', '.join(f'{key}={value!r}' for key, value in attrs)
        return f'{package}.{class_}({sattrs})'
    
    def __str__(self):
        class_ = self.__class__.__name__
        attrs = dict()
        for k in self.__mapper__.columns.keys():
            attrs[k] = getattr(self, k)

        Text = f"| {class_}:\n"
        for key, value in attrs.items():
            if key == "firstname":
                Text += f"| \tName: {attrs['lastname'].capitalize().rstrip()}, {value.capitalize().rstrip()}\n"
                continue
            elif key == "lastname":
                continue
            elif key == "status" and value is None:
                Text += f"| \tCompleted on: {attrs['status']}\n"
                continue
            elif key == "comptime" and value is not None: 
                comptime = value.strftime("%A %d/%m/%Y at %H:%M:%S")
                Text += f"| \tCompleted on: {comptime}\n"
                continue
            
            Text += f"| \t{key.capitalize()}: {value}\n"
        
        return Text
            

class Campus(Mixin, Base):
    __tablename__ = "campus"
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    address = Column(Text)
    buildings = relationship("Building", backref="campus")
    workers = relationship("Worker", backref="campus")
    __table_args__ = tuple(UniqueConstraint("name"))
        
class Building(Mixin, Base):
    __tablename__ = "building"
    id = Column(Integer, primary_key=True)
    campus_id = Column(Integer, ForeignKey('campus.id'))
    name = Column(Text, nullable=True)
    address = Column(Text)
    rooms = relationship("Room", backref="building")
    __table_args__ = tuple(UniqueConstraint("name"))

class Room(Mixin, Base):
    __tablename__ = "room"
    id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey('building.id'))
    name = Column(Text, nullable=True)
    type_id = Column(Integer, ForeignKey('room_types.id'), nullable=True)  # Make sure this matches your table name!
    room_type = relationship("RoomType", back_populates="rooms")  # <-- This is what's missing!
    requests = relationship("Request", backref="room")
    __table_args__ = tuple(UniqueConstraint("building_id", "name"))
    
class User(Mixin, Base):
    __tablename__ = "user"
    email = Column(String(255), primary_key=True)
    firstname = Column(Text, nullable=True)
    lastname = Column(Text, nullable=True)
    requests = relationship("Request", backref="user")
        
class Worker(Mixin, Base):
    __tablename__ = "worker"
    email = Column(String(255), primary_key=True)
    firstname = Column(Text, nullable=True)
    lastname = Column(Text, nullable=True)
    job_type_id = Column(Integer, ForeignKey("job_types.id"))  # Add this line
    job_type = relationship("JobType", back_populates="workers")  # Add this line
    campus_id = Column(Integer, ForeignKey('campus.id'), nullable=True)
    assignments = relationship("Request",backref="worker",foreign_keys="[Request.worker_email]")


class Request(Mixin, Base):
    __tablename__ = "request"
    id = Column(Integer, primary_key=True)
    status_id = Column(Integer, ForeignKey("request_status.id"))
    request_status = relationship("RequestStatus", back_populates="requests")
    user_email = Column(String(255), ForeignKey('user.email'))
    reqtime = Column(DateTime)
    worker_email = Column(String(255), ForeignKey("worker.email"), nullable=True)
    description = Column(String(255), nullable=True)
    comptime = Column(DateTime, nullable=True)
    room_id = Column(Integer, ForeignKey("room.id"))

class RoomType(Mixin, Base):
    __tablename__ = "room_types"
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    rooms = relationship('Room', back_populates='room_type') 

class JobType(Mixin, Base):
    __tablename__ = "job_types"
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    workers = relationship("Worker", back_populates="job_type")

class RequestStatus(Mixin, Base):
    __tablename__ = "request_status"
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    requests = relationship("Request", back_populates="request_status")
