import re
from enum import Enum

class DataType(Enum):
    SPRING = 1
    SUMMER = 2
    AUTUMN = 3
    WINTER = 4



def make_int(val):
    val = int(val)
    return val

def make_str(val):
    val = str(val)
    return val

def make_bool(val):
    val = val
    return val

def make_double(val):
    val = val
    return val




data_types = ["i_", "b_", "d_", "s_"]

bad_chars = "$<>"

search_type = "data_type"

"""
with open("example_metadata/Test001_19-0kW.m3inp","r") as fi:
    id = []
    for ln in fi:
        if ln.startswith("<"):
            if ln.startswith("<Deformed$image"):
                pass
            else:
                stripped = re.sub("[" + bad_chars + "]", "", ln)
                id.append(stripped[:-1])"""

"""
with open("example_metadata/Test001_19-0kW.m3inp","r") as fi:
    id = []
    for ln in fi:
       print(ln)
       for i in data_types:
        type_found = str(i) in ln
        if type_found == True:
           print("True")
        else:
           print("False")"""

def data_type_mark_search(line):
    #print("hi")
    global search_type
    print(search_type)
    for i in data_types:
        type_found = str(i) in line
        if type_found == True:
            search_type = "key_vals"
            print(search_type)
            return type_found
        
def key_val_pair_search(line, d_type):
    global search_type
    if line.startswith("<"):
        if line.startswith("<Deformed$image"):
            pass
        else:
            stripped = re.sub("[" + bad_chars + "]", "", line)
            id.append([stripped[:-1],d_type])
            search_type = "data_type"



with open("example_metadata/Test001_19-0kW.m3inp","r") as fi:
    id = []
    for ln in fi:
        if search_type == "data_type":
            dat_type = data_type_mark_search(ln)
        elif search_type == "key_vals":
            results = key_val_pair_search(ln, dat_type)

mydict = {"one":1, "two":2,"three":3}


for i in id:
    print(i)
    pair = i[0].split("=")
    if i[1] == "i_":
        val = make_int(pair[1])
        mydict[pair[0]] = val
    else:
        val = pair[1]
        mydict[pair[0]] = val
    #print(type(val))
    #print(pair[0])




class ExampleDB:
  def __init__(self, name, age):
    self.name = name
    self.age = age

filleddb = object.__new__(ExampleDB)
filleddb.__dict__ = mydict

print(filleddb.Strainwindow)