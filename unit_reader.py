import json

with open ("example_metadata/units.json", "r") as fi:
    my_file = json.load(fi)
    for i in my_file:
        print(i)
        print(my_file[i])

