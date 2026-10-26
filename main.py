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

    if command.startswith("SET"):
        key = parts[1]
        value = parts[2]
        SET(key, value)
    if command.startswith("GET"):
        key = parts[1]
        value = GET(key)
        if value is not None:
            print(value)
        else:
            print("NULL")

    # first record (for debugging)
    print(database[0].key)
    print(database[0].value)

    if command == "EXIT":
        print("Exiting")
        exit()
