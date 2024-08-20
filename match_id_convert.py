import re


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


def data_type_mark_search(line):
    """search for data type labels when search_type is set to key_vals,
    switch search type to key_vals once label has been found to find paired metadata values"""
    global search_type
    for i in data_types:
        type_found = str(i) in line
        if type_found == True:
            search_type = "key_vals"
            return str(i)
        
def key_val_pair_search(line, d_type):
    """search for metadata values when search_type is set to key_vals,
    swtich search type to data_type to look for the next data label"""
    global search_type
    if line.startswith("<"):
        if line.startswith("<Deformed$image"):
            pass
        elif line.startswith("<Shape>"):
            stripped = re.sub("[" + bad_chars + "]", "", line)
            id.append([stripped[:-1],"d_"])
        else:
            stripped = re.sub("[" + bad_chars + "]", "", line)
            id.append([stripped[:-1],d_type])
            search_type = "data_type"


"""open the metadata file and search through depending on the value of search_type"""
with open("example_metadata/Test001_19-0kW.m3inp","r") as fi:
    id = []
    for ln in fi:
        if ln.startswith("*"):
            pass
        else:
            if search_type == "data_type":
                dat_type = data_type_mark_search(ln)
            elif search_type == "key_vals":
                results = key_val_pair_search(ln, dat_type)


mydict = {}

"""assign the right data type to each metadata value"""
for i in id:
    print(i)
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
    else:
        val = pair[1]
        mydict[pair[0]] = val



class ExampleDB:
  def __init__(self, name, age):
    self.name = name
    self.age = age

filleddb = object.__new__(ExampleDB)
filleddb.__dict__ = mydict

print(type(filleddb.Strainwindow))
print(type(filleddb.Delimiter))
print(filleddb.Shape)
print(type(filleddb.Automaticexport))