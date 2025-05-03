from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dbtypes import Campus, Building, Room, Worker, Request, JobType, RoomType, RequestStatus, User
from config import CONNECTION_URL

def truncate_and_reset_all_data(session: Session):
    session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    session.commit()

    tables = [Room, Building, Campus, Worker, Request, JobType, RoomType, RequestStatus, User]
    
    for table in tables:
        try:
            session.execute(text(f"TRUNCATE TABLE {table.__tablename__}"))
            session.execute(text(f"ALTER TABLE {table.__tablename__} AUTO_INCREMENT = 1"))
            print(f"Table {table.__tablename__} truncated and auto-increment reset!")
        except Exception as e:
            print(f"Error truncating data in {table.__tablename__}: {e}")
    
    session.commit()
    session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    session.commit()

def main():
    engine = create_engine(CONNECTION_URL, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    truncate_and_reset_all_data(session)
    session.close()

if __name__ == "__main__":
    main()
