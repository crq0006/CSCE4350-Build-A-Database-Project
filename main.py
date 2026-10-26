#main.py

#class for record keeping
class Record:
    def __init__(self, key, value):
        self.key = key
        self.value = value

#list to store all records in the database
database = []

while True:
    command = input()

    #test key and value parsing
    entry = Record("name", "Cash")
    database.append(entry)

    print(database[0].key)
    print(database[0].value)

    if command == "EXIT":
        print("Exiting")
        exit()
