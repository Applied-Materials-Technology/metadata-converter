import re
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--metadatafile", default = "example_metadata/Test001_19-0kW.m3inp", type = str)

args = parser.parse_args()

data_types = ["i_", "b_", "d_", "s_"]

bad_chars = "$<>"

search_type = "data_type"

bad_chars2 = "_.;"


def make_int(val):
    """makes metadata value integer when specified"""
    stripped_val = re.sub("[" + bad_chars2 + "]", "", val)
    val2 = int(stripped_val)
    return val2

def make_str(val):
    """makes metadata value string when specified"""
    val = str(val)
    return val

def make_bool(val):
    """makes metadata value boolean when specified"""
    if val == "True":
        boolval = True
    elif val == "False":
        boolval = False
    return boolval

def make_double(val):
    """splits metadata value into list of individual values when specified"""
    val = val.split(";")
    return val

def shape_case(id, line):
    """adds specific marker for non standard form parameter shape"""
    stripped = re.sub("[" + bad_chars + "]", "", line)
    id.append([stripped[:-1],"shape_"])


def extensometer_case(id, line):
    """adds specific marker for non standard form parameter extensometer"""
    stripped = re.sub("[" + bad_chars + "]", "", line)
    id.append([stripped[:-1],"extens_"])

def shape_list(shape_id, data):
    list_vals = []
    if shape_id == 0:
        shape = "rectangle"
    elif shape_id == 1:
        shape = "circle"
    elif shape_id == 2:
        shape = "polygon"
    elif shape_id == 3:
        shape = "extensometer"
    for i in data:
        try:
            correct_d_type = make_int(i)
        except:
            correct_d_type = make_bool(i)
        list_vals.append(correct_d_type)
    return list_vals




def data_type_mark_search(id, line):
    """search for data type labels when search_type is set to key_vals,
    switch search type to key_vals once label has been found to find paired metadata values"""
    global search_type
    for i in data_types:
        type_found = str(i) in line
        if type_found == True:
            search_type = "key_vals"
            return str(i)
    return id

def deformed_image_case(id,line):
    #print(line)
    deformed_imgs = line.split()
    for i in deformed_imgs:
        part1 = i.replace('<Deformed$image>=','')
        part2 = part1.split(';')
        print(part2)
    #print(deformed_imgs)
        
def key_val_pair_search(id, line, d_type):
    """search for metadata values when search_type is set to key_vals,
    swtich search type to data_type to look for the next data label"""
    global search_type
    if line.startswith("<"):
        if line.startswith("<Deformed$image"):
            deformed_image_case(id,line)
        elif line.startswith("<Shape>"):
            #stripped = re.sub("[" + bad_chars + "]", "", line)
            #id.append([stripped[:-1],"d_"])
            shape_case(id, line)
        elif line.startswith("<Extensometer>"):
            extensometer_case(id, line)
        else:
            stripped = re.sub("[" + bad_chars + "]", "", line)
            #id.append([stripped[:-1],d_type])
            id.append([stripped[:-1],d_type])
            search_type = "data_type"


"""open the metadata file and search through depending on the value of search_type"""
def read_file(metadata):
    with open (metadata, "r") as fi:
        id = []
        for ln in fi:
            if ln.startswith("*"):
                pass
            else:
                if search_type == "data_type":
                    dat_type = data_type_mark_search(id, ln)
                elif search_type == "key_vals":
                    results = key_val_pair_search(id, ln, dat_type)
    return id

id = read_file(args.metadatafile)
mydict = {}

"""assign the right data type to each metadata value"""
def assign_dtype(id):
    for i in id:
        pair = i[0].split("=")
        if i[1] == "i_":
            val = make_int(pair[1])
            mydict[pair[0]] = val
        elif i[1] == "d_":
            val = make_double(pair[1])
            mydict[pair[0]] = val
        elif i[1] == "b_":
            val = make_bool(pair[1])
            mydict[pair[0]] = val
        elif i[1] == "shape_":
            val = make_double(pair[1])
            shape_com = shape_list(int(val[0]), val[1:])
            #print(shape_com)
            mydict[pair[0]] = val
        elif i[1] == "extens_":
            val = make_double(pair[1])
            #extens_com = extens_list(int(val[0]), val[1:])
            mydict[pair[0]] = val
        else:
            val = pair[1]
            mydict[pair[0]] = val

assign_dtype(id)

class ExampleDB:
  def __init__(self, name, age):
    self.name = name
    self.age = age

filleddb = object.__new__(ExampleDB)
filleddb.__dict__ = mydict
"""
print(type(filleddb.Strainwindow))
print(type(filleddb.Delimiter))
print(type(filleddb.Automaticexport))
print(type(filleddb.Shape))

print(type(filleddb.Strainwindow))"""
#print(mydict)
with open('dict_save.txt', 'w') as file:
     file.write(json.dumps(mydict))
json_data = json.dumps(mydict)
#print(json_data)
