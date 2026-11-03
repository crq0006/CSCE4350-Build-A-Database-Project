#main.py

#class for record keeping
class Record:
    def __init__(self, key, value):
        self.key = key
        self.value = value

#list to store all records in the database
database = []

#add to db file
def write_to_database(command, key, value=""):
    with open("database.db", "a") as file:
        file.write(f"{command} {key} {value}\n")

#update memory function for the in-memory database
def update_memory(key, value):
    for record in database:
        if record.key == key:
            record.value = value
            return
    database.append(Record(key, value))

#function to read database file at startup for database list
def read_database():
    try:
        with open("database.db", "r") as file:
            for line in file:
                parts = line.strip().split()
                command = parts[0]
                key = parts[1]

                if command == "SET":
                    value = parts[2]
                    update_memory(key, value)

                elif command == "DELETE":
                    for record in database:
                        if record.key == key:
                            database.remove(record)
                            break
 
    except FileNotFoundError:
        pass

#SET command
def SET(key, value):
    write_to_database("SET",key, value)
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

#DELETE command
def DELETE(key):
    write_to_database("DELETE", key)
    for record in database:
        if record.key == key:
            database.remove(record)
            write_to_database("DELETE", key)
            return

#EXISTS command
def EXISTS(key):
    for record in database:
        if record.key == key:
            return True
    return False

#MSET command
def MSET(pairs):
    for i in range(0, len(pairs), 2):
        key = pairs[i]
        value = pairs[i + 1]
        SET(key, value)

#MGET command
def MGET(keys):
    values = []
    for key in keys:
        value = GET(key)
        values.append(value if value is not None else "NULL")
    return values

#INCR command
def INCR(key):
    value = GET(key)
    if value is None:
        value = 0
    try:
        value = int(value) + 1
    except ValueError:
        return None
    SET(key, str(value))
    return value

#DECR command
def DECR(key):
    value = GET(key)
    if value is None:
        value = 0
    try:
        value = int(value) - 1
    except ValueError:
        return None
    SET(key, str(value))
    return value

read_database()

while True:
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

    if command.startswith("MSET"):
        pairs = parts[1:]
        if len(pairs) > 0 and len(pairs) % 2 == 0:
            MSET(pairs)
        else:
            print("ERROR")

    if command.startswith("MGET"):
        keys = parts[1:]
        values = MGET(keys)
        for value in values:
            print(value)
    
    if command.startswith("EXISTS"):
        key = parts[1]
        print("TRUE" if EXISTS(key) else "FALSE")

    if command.startswith("INCR"):
        if parts[0] == "INCR":
            if len(parts) != 2:
                print("ERROR")
                continue

            key = parts[1]
            value = INCR(key)

            if value is not None:
                print(value)
            else:
                print("ERROR")

    if command.startswith("DECR"):
        if parts[0] == "DECR":
            if len(parts) != 2:
                print("ERROR")
                continue

            key = parts[1]
            value = DECR(key)

            if value is not None:
                print(value)
            else:
                print("ERROR")
