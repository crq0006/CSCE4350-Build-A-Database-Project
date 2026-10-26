#main.py

#class for record keeping
class Record:
    def __init__(self, key, value):
        self.key = key
        self.value = value

#list to store all records in the database
database = []

#SET command
def SET(key, value):
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
        for record in database:
            if record.key == key:
                database.remove(record)
                break
    if command.startswith("EXISTS"): #add error handling for invalid syntax
        key = parts[1]
        exists = False
        for record in database:
            if record.key == key:
                exists = True
                break
        print("TRUE" if exists else "FALSE")
