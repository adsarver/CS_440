from sqlalchemy.orm import Session
from dbtypes import Building, Room, Campus, Worker, User, Request, RoomType, JobType, RequestStatus, Base
from sqlalchemy.orm import sessionmaker
import sqlalchemy, faker, random, datetime
from config import CONNECTION_URL, JOB_TYPES, ROOM_TYPES, BUILDINGS, STATUS_TYPES
from custom_sql import custom_sql
sql = None
def generate_random_address():
    fake = faker.Faker()
    street_name = fake.street_name()
    street_number = random.randint(100, 999)
    return f"{street_number} {street_name}, Morgantown, WV {random.randint(26505, 26508)}"

def add_campus(name, session: Session):
    campus = session.query(Campus).filter_by(name=name).first()
    if campus is None:
        address = generate_random_address()
        campus = Campus(name=name, address=address)

    return sql.create_entry(campus)

def add_building(name, campus_name, session: Session):
    campus = add_campus(campus_name, session)
    address = generate_random_address()
    building = Building(name=name, address=address, campus_id=campus.id, campus=campus)

    return sql.create_entry(building)

def add_room(building, room_name, room_type_name, session: Session):
    room_type = session.query(RoomType).filter_by(name=room_type_name).first()
    if not room_type:
        room_type = RoomType(name=room_type_name)
        room_type = sql.create_entry(RoomType)
    
    room = Room(name=room_name, building_id=building.id, type_id=room_type.id, room_type=room_type, building=building)
    return sql.create_entry(room)


def add_worker(campus_name, session: Session):
    fake = faker.Faker()
    campus = add_campus(campus_name, session)
    firstname = fake.first_name()
    lastname = fake.last_name()
    email = fake.email()
    
    worker = Worker(email= email,
                    firstname= firstname,
                    lastname= lastname,
                    job_type_id= random.choice(session.query(JobType).all()).id,
                    campus_id= campus.id,
                    campus=campus)

    return sql.create_entry(worker)

def add_user(session: Session, firstname=None, lastname=None, email=None):
    fake = faker.Faker()
    firstname = firstname or fake.first_name()
    lastname = lastname or fake.last_name()
    email = email or fake.email()

    user = session.query(User).filter_by(email=email).first()
    if user is None:
        user = User(email=email, firstname=firstname, lastname=lastname)
        user = sql.create_entry(user)
        print(f"User '{firstname} {lastname}' added with email '{email}'")
    else:
        print(f"User with email '{email}' already exists.")
    return user

def add_request(session: Session, user_email, room_id, description, worker_email=None):
    user = session.query(User).filter_by(email=user_email).first()
    room = session.query(Room).filter_by(id=room_id).first()
    worker = session.query(Worker).filter_by(email=worker_email).first() if worker_email else None

    if not user:
        raise ValueError(f"No user found with email: {user_email}")
    if not room:
        raise ValueError(f"No room found with ID: {room_id}")
    if worker_email and not worker:
        raise ValueError(f"No worker found with email: {worker_email}")

    request = Request(
        user_email=user.email,
        room_id=room.id,
        room=room,
        description=description,
        reqtime=datetime.datetime.now(),
        worker_id=worker.email if worker else None,
        worker=worker if worker else None,
        status_id="Incomplete",
    )

    print(f"Request by user '{user.email}' added for room ID '{room.id}'")
    return sql.create_entry(request)

def generate_data(session: Session, building_floors=2, rooms_per_floor=5, workers_per_campus=5):
    
    [session.add(JobType(name=type)) for type in JOB_TYPES]
    [session.add(RoomType(name=room)) for room in ROOM_TYPES]
    [session.add(RequestStatus(name=status)) for status in STATUS_TYPES]
    session.commit()
    
    
    room_numbers = [x * 100 + y for x in range(1, building_floors+1) for y in range(1, rooms_per_floor+1)]

    for campus_name in BUILDINGS.keys():
        add_campus(campus_name, session)

    for campus_name, building_list in BUILDINGS.items():
        for building_name in building_list:
            building = add_building(building_name, campus_name, session)
            for room_num in room_numbers:
                room_type = random.choice(ROOM_TYPES)
                add_room(building, room_num, room_type, session)

        for _ in range(workers_per_campus):
            add_worker(campus_name, session)
            


            

def main():
    engine = sqlalchemy.create_engine(CONNECTION_URL, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    sql = custom_sql(session, engine)
    
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    generate_data(session)
    session.close()

if __name__ == "__main__":
    main()