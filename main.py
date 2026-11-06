#main.py

#class for record keeping
from time import time
import copy

transaction_active = False
transaction_backup = None
transaction_log = []

class Record:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.expires_at = None
        self.hash_data = None
        self.list_data = None

#list to store all records in the database
database = []

#add to db file
def write_to_database(command, key, value=""):
    if transaction_active:
        transaction_log.append((command, key, value))
    else:
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

#HSET helper function for updating hash data in memory
def update_hash_memory(key, field, value):
    for record in database:
        if record.key == key:
            if record.hash_data is None:
                return False

            for i in range(len(record.hash_data)):
                if record.hash_data[i][0] == field:
                    record.hash_data[i] = (field, value)
                    return True

            record.hash_data.append((field, value))
            return True

    record = Record(key, None)
    record.hash_data = [(field, value)]
    database.append(record)
    return True

#Helper function for updating list data in memory
# Helper function for updating list data in memory
def update_list_memory(key, value, left=True):
    for record in database:
        if record.key == key:
            if record.list_data is None:
                return False

            if left:
                record.list_data.insert(0, value)
            else:
                record.list_data.append(value)

            return True

    record = Record(key, None)
    record.list_data = [value]
    database.append(record)
    return True

#function to read database file at startup for database list
def read_database():
    try:
        with open("data.db", "r") as file:
            for line in file:
                parts = line.strip().split()
                command = parts[0]
                
                if command == "FLUSHDB":
                    database.clear()
                    continue

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
                elif command == "HSET":
                    field = parts[2]
                    value = parts[3]
                    update_hash_memory(key, field, value)
                elif command == "LPUSH":
                    value = parts[2]
                    update_list_memory(key, value, True)

                elif command == "RPUSH":
                    value = parts[2]
                    update_list_memory(key, value, False)
                elif command == "FLUSHDB":
                    database.clear()

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

#BEGIN command
def BEGIN():
    global transaction_active, transaction_backup, transaction_log

    if transaction_active:
        return False

    transaction_backup = copy.deepcopy(database)
    transaction_log = []
    transaction_active = True

    return True

#COMMIT command
def COMMIT():
    global transaction_active, transaction_backup, transaction_log

    if not transaction_active:
        return False

    with open("data.db", "a") as file:
        for command, key, value in transaction_log:
            file.write(f"{command} {key} {value}\n")

    transaction_active = False
    transaction_backup = None
    transaction_log = []

    return True

#ABORT command
def ABORT():
    global transaction_active, transaction_backup, transaction_log

    if not transaction_active:
        return False

    database.clear()
    database.extend(transaction_backup)

    transaction_active = False
    transaction_backup = None
    transaction_log = []

    return True

#HSET command
def HSET(key, field, value):
    success = update_hash_memory(key, field, value)

    if success:
        write_to_database("HSET", key, f"{field} {value}")

    return success

def HGET(key, field):
    for record in database:
        if record.key == key:
            if record.hash_data is None:
                return None
            for f, v in record.hash_data:
                if f == field:
                    return v
            return None
    return None

def HGETALL(key):
    for record in database:
        if record.key == key:
            if record.hash_data is None:
                return []
            return record.hash_data
    return []

def LPUSH(key, value):
    success = update_list_memory(key, value, True)

    if success:
        write_to_database("LPUSH", key, value)

    return success

def RPUSH(key, value):
    success = update_list_memory(key, value, False)

    if success:
        write_to_database("RPUSH", key, value)

    return success

def LRANGE(key, start, end):
    for record in database:
        if record.key == key:
            if record.list_data is None:
                return []
            data = record.list_data
            size = len(data)

            start = max(0, start if start >= 0 else size + start)
            end = min(size - 1, end if end >= 0 else size + end)

            return data[start:end + 1]
        
    return []

def FLUSHDB():
    write_to_database("FLUSHDB", "", "")
    database.clear()
    return True

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
        if len(parts) != 3:
            print("ERROR")
            continue

        start = parts[1]
        end = parts[2]
        values = RANGE(start, end)
        for key, value in values:
            print(key, value)

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
        if len(parts) != 2:
            print("ERROR")
            continue

        key = parts[1]
        print(TTL(key))
            
    if parts[0] == "BEGIN":
        success = BEGIN()
        print("TRUE" if success else "ERROR")

    if parts[0] == "COMMIT":
        success = COMMIT()
        print("TRUE" if success else "ERROR")

    if parts[0] == "ABORT":
        success = ABORT()
        print("TRUE" if success else "ERROR")

    if parts[0] == "HSET":
        if len(parts) != 4:
            print("NULL")
            continue

        key = parts[1]
        field = parts[2]
        value = parts[3]
        success = HSET(key, field, value)
        print("TRUE" if success else "NULL")

    if parts[0] == "HGET":
        if len(parts) != 3:
            print("NULL")
            continue

        key = parts[1]
        field = parts[2]
        value = HGET(key, field)
        if value is not None:
            print(value)
        else:
            print("NULL")

    if parts[0] == "HGETALL":
        if len(parts) != 2:
            print("NULL")
            continue

        key = parts[1]
        fields = HGETALL(key)
        for field, value in fields:
            print(field, value)

    if parts[0] == "LPUSH":
        if len(parts) != 3:
            print("ERROR")
            continue

        key = parts[1]
        value = parts[2]

        success = LPUSH(key, value)
        print("TRUE" if success else "ERROR")

    if parts[0] == "RPUSH":
        if len(parts) != 3:
            print("ERROR")
            continue

        key = parts[1]
        value = parts[2]

        success = RPUSH(key, value)
        print("TRUE" if success else "ERROR")

    if parts[0] == "LRANGE":
        if len(parts) != 4:
            print("ERROR")
            continue

        key = parts[1]
        try:
            start = int(parts[2])
            end = int(parts[3])
        except ValueError:
            print("ERROR")
            continue

        values = LRANGE(key, start, end)
        for value in values:
            print(value)

    if parts[0] == "FLUSHDB":
        success = FLUSHDB()
        print("TRUE" if success else "ERROR")

    


