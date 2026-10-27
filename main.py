#main.py

#class for record keeping
class Record:
    def __init__(self, key, value):
        self.key = key
        self.value = value

#list to store all records in the database
database = []

#add to db file
def write_to_database(key, value):
    with open("database.db", "a") as file:
        file.write(f"{key} {value}\n")

#function to read database file at startup for database list
def read_database():
    try:
        with open("database.db", "r") as file:
            for line in file:
                key, value = line.strip().split()
                database.append(Record(key, value))
    except FileNotFoundError:
        pass

#SET command
def SET(key, value):
    write_to_database(key, value)
    for record in database:
        if record.key == key:
            record.value = value
            return
    database.append(Record(key, value))

#GET command
def GET(key):
    for record in database:
        if record.key == key:
            return record.value
    return None

def DELETE(key):
        for record in database:
            if record.key == key:
                database.remove(record)
                #update db file
                with open("database.db", "w") as file:
                    for rec in database:
                        file.write(f"{rec.key} {rec.value}\n")
                break

def EXISTS(key):
    for record in database:
        if record.key == key:
            return True
    return False

while True:
    database.clear()
    read_database()
    command = input()
    parts = command.split()

    
    if command == "EXIT":
        print("Exiting")
        exit()

    if command.startswith("SET"): #only updates in-memory database, should set up db file l8r, also add error handling for invalid syntax
        key = parts[1]
        value = parts[2]
        SET(key, value)

    if command.startswith("GET"):  #add error handling for invalid syntax
        key = parts[1]
        value = GET(key)
        if value is not None:
            print(value)
        else:
            print("NULL")

    if command.startswith("DELETE"): #add error handling for invalid syntax
        key = parts[1]
        DELETE(key)

    if command.startswith("EXISTS"): #add error handling for invalid syntax
        key = parts[1]
        print("TRUE" if EXISTS(key) else "FALSE")
