_username = "root"
_password = "root"
_host = "localhost"
_port = "3306"
_database = "CS440"
CONNECTION_URL = f"mysql+mysqlconnector://{_username}:{_password}@{_host}:{_port}/{_database}"

BUILDINGS = {
    "Downtown" : ["Hodges Hall", 
                    "Brooks Hall", 
                    "Woodburn Hall", 
                    "White Hall"],
    
    "Evansdale" : ["Engineering Research Building", 
                    "Engineering Sciences Building",
                    "Evansdale Crossing",
                    "Greenhouse"],
    
    "Heath" : ["Health Sciences North",
               "Health Sciences South"],
    }    
    
JOB_TYPES = ["Janitor", "Electrician", "HVAC", "Welder","Drywaller"]
ROOM_TYPES = ["Bathroom", "Lecture Hall", "Office", "Laboratory", "Utilities"]
STATUS_TYPES = ["Incomplete", "Complete"]