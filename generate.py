from sqlalchemy.orm import Session
from dbtypes import Building, Room, Campus, Worker, User, Request
from sqlalchemy.orm import sessionmaker
import sqlalchemy, faker, random, datetime
from config import CONNECTION_URL, WORK_TYPES, ROOM_TYPES, BUILDINGS

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
        session.add(campus)
        session.commit()
    return campus

def add_building(name, campus_name, session: Session):
    campus = add_campus(campus_name, session)
    address = generate_random_address()
    building = Building(name=name, address=address, campus_id=campus.id)
    session.add(building)
    session.commit()
    return building

def add_room(building, room_name, type, session: Session):
    room = Room(name=room_name, building_id=building.id, type=type)
    session.add(room)
    session.commit()
    return room

def add_worker(campus_name, session: Session):
    fake = faker.Faker()
    campus = add_campus(campus_name, session)
    firstname = fake.first_name()
    lastname = fake.last_name()
    email = fake.email()
    
    worker = Worker(email=email,
                    firstname=firstname,
                    lastname=lastname,
                    specialization=random.choice(WORK_TYPES),
                    campus_id=campus.id)

    session.add(worker)
    session.commit()
    return worker

def add_user(session: Session, firstname=None, lastname=None, email=None):
    fake = faker.Faker()
    firstname = firstname or fake.first_name()
    lastname = lastname or fake.last_name()
    email = email or fake.email()

    user = session.query(User).filter_by(email=email).first()
    if user is None:
        user = User(email=email, firstname=firstname, lastname=lastname)
        session.add(user)
        session.commit()
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
        description=description,
        reqtime=datetime.datetime.now(),
        worker_id=worker.email if worker else None,
        status_id="Incomplete"
    )

    session.add(request)
    session.commit()
    print(f"Request by user '{user.email}' added for room ID '{room.id}'")
    return request

def generate_buildings_and_rooms(session: Session, building_floors=2, rooms_per_floor=5, workers_per_campus=5):
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

    generate_buildings_and_rooms(session)
    session.close()

if __name__ == "__main__":
    main()