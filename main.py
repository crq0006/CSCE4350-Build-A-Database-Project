#main.py

#class for record keeping
from time import time


class Record:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.expires_at = None

#list to store all records in the database
database = []

#add to db file
def write_to_database(command, key, value=""):
    with open("data.db", "a") as file:
        file.write(f"{command} {key} {value}\n")

#update memory function for the in-memory database
def update_memory(key, value):
    for record in database:
        if record.key == key:
            record.value = value
            record.expires_at = None
            return
    database.append(Record(key, value))

#helper function for checking if a record has expired
def is_expired(record):
    return record.expires_at is not None and record.expires_at <= time()

#function to read database file at startup for database list
def read_database():
    try:
        with open("data.db", "r") as file:
            for line in file:
                parts = line.strip().split()
                command = parts[0]
                key = parts[1]

                if command == "SET":
                    value = parts[2]
                    update_memory(key, value)

                elif command == "DEL":
                    for record in database:
                        if record.key == key:
                            database.remove(record)
                            break
                elif command == "EXPIRE":
                    expires_at = float(parts[2])

                    for record in database:
                        if record.key == key:
                            record.expires_at = expires_at
                            break
                
    except FileNotFoundError:
        pass

#SET command
def SET(key, value):
    write_to_database("SET",key, value)
    for record in database:
        if record.key == key:
            record.value = value
            record.expires_at = None
            return
    database.append(Record(key, value))

#GET command
def GET(key):
    for record in database:
        if record.key == key:
            if is_expired(record):
                return None
            return record.value
    return None

#DELETE command
def DEL(key):
    for record in database:
        if record.key == key:
            database.remove(record)
            write_to_database("DEL", key)
            return

#EXISTS command
def EXISTS(key):
    for record in database:
        if record.key == key:
            if is_expired(record):
                return False
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

#RANGE command
def RANGE(start, end):
    values = []
    for record in database:
        if start <= record.key <= end:
            if is_expired(record):
                continue
            values.append((record.key, record.value))
    values.sort()
    return values

#EXPIRE command
def EXPIRE(key, seconds):
    for record in database:
        if record.key == key:
            record.expires_at = time() + seconds
            write_to_database("EXPIRE", key, record.expires_at)
            return True
    return False

#TTL command
def TTL(key):
    for record in database:
        if record.key == key:
            if record.expires_at is None:
                return -1

            remaining = record.expires_at - time()

            if remaining <= 0:
                return -2

            return int(remaining)

    return -2

read_database()

while True:
    command = input()
    parts = command.split()
    if not parts:
        continue

    
    if command == "EXIT":
        print("Exiting")
        exit()

    if parts[0] == "SET": #only updates in-memory database, should set up db file l8r, also add error handling for invalid syntax
        key = parts[1]
        value = parts[2]
        SET(key, value)

    if parts[0] == "GET":  #add error handling for invalid syntax
        key = parts[1]
        value = GET(key)
        if value is not None:
            print(value)
        else:
            print("NULL")

    if parts[0] == "DEL": #add error handling for invalid syntax
        key = parts[1]
        DEL(key)

    if parts[0] == "MSET":
        pairs = parts[1:]
        if len(pairs) > 0 and len(pairs) % 2 == 0:
            MSET(pairs)
        else:
            print("ERROR")

    if parts[0] == "MGET":
        keys = parts[1:]
        values = MGET(keys)
        for value in values:
            print(value)
    
    if parts[0] == "EXISTS":
        key = parts[1]
        print("TRUE" if EXISTS(key) else "FALSE")

    if parts[0] == "INCR":
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

    if parts[0] == "DECR":
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

    if parts[0] == "RANGE":
        if parts[0] == "RANGE":
            if len(parts) != 3:
                print("ERROR")
                continue

            start = parts[1]
            end = parts[2]
            values = RANGE(start, end)
            for key, value in values:
                print(key, value)

    if parts[0] == "EXPIRE":
        if parts[0] == "EXPIRE":
            if len(parts) != 3:
                print("ERROR")
                continue

            key = parts[1]
            try:
                seconds = int(parts[2])

                if seconds < 0:
                    print("ERROR")
                    continue

            except ValueError:
                print("ERROR")
                continue

            success = EXPIRE(key, seconds)
            print("TRUE" if success else "FALSE")

    if parts[0] == "TTL":
        if parts[0] == "TTL":
            if len(parts) != 2:
                print("ERROR")
                continue

            key = parts[1]
            print(TTL(key))
