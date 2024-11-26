from pathlib import Path
from dataclasses import dataclass
import re
import json
import argparse

# TODO - metadata
# Check everything works for *.m2inp and *.m3inp
# - Extract "Stereo" or "2D" if the word stereo is not found in the header
#   - if "stereo" in 2nd row
#   - "Input Type": "2D" | "Stereo"
# - Extract version number of the software e.g. "2024.1.0" as
#    - "Version": "2024.1.0"
# - Camera Intrinsic:
#   - Split list into separate parameters:
#    - "Camera1Intrinsic"
#       - "Fx": 19488.99
#       - "Fy": 19487.46
# -
# - Camera Extrinsic as above - split list into sub dicttionary
# - Remove path from image list - keep other parameters
# - Remove <> from image list
# - Add support for multiple shape in the region of interest
#   - RegionOfInterest:
#        - Shape: list[]
#        - Shape: list[]

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


#FIX ISSUE WITH ADDING
def deformed_image_case(id, line):
    deformed_imgs = line.split()
    part = deformed_imgs[0].replace('<Deformed$image>=','DeformedImage=')
    id.append([part, "image_"])
    return id

def key_val_pair_search(id, line: str, d_type, search_type) -> str:
    """search for metadata values when search_type is set to key_vals,
    swtich search type to data_type to look for the next data label"""

    if line.startswith("<"):
        if line.startswith("<Deformed$image"):
            deformed_image_case(id,line)
        elif line.startswith("<Shape>"):
            shape_case(id, line)
        elif line.startswith("<Extensometer>"):
            extensometer_case(id, line)
        else:
            stripped = re.sub("[" + bad_chars + "]", "", line)
            id.append([stripped[:-1],d_type])
            search_type = "data_type"

    return search_type


"""open the metadata file and search through depending on the value of search_type"""
def extract_metadata(metadata_path: Path) -> :
    with open (metadata_path, "r") as fi:
        id = []
        for ln in fi:
            if ln.startswith("*"):
                pass
            else:
                if search_type == "data_type":
                    dat_type = data_type_mark_search(id, ln)
                elif search_type == "key_vals":
                    key_val_pair_search(id, ln, dat_type)
    return id



"""assign the right data type to each metadata value"""
def assign_dtype(id):
    try:
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
                mydict[pair[0]] = val
            elif i[1] == "extens_":
                val = make_double(pair[1])
                mydict[pair[0]] = val
            elif i[1] == "image_":
                val = make_double(pair[1])
                images.append(val)
            else:
                val = pair[1]
                mydict[pair[0]] = val
    except:
        pass


@dataclass
class MatchIDFormat
    data_types: tuple[str,str,str,str] = ("i_", "b_", "d_", "s_")
    bad_chars: str = "$<>"
    bad_chars2: str = "_.;"



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadatafile", default = "example_metadata/Test001_19-0kW.m3inp", type = str)
    args = parser.parse_args()


    search_type: str = "data_type"

    id = extract_metadata(Path(args.metadatafile))

    mydict = {}
    images = []
    assign_dtype(id)
    mydict["DeformedImages"] = images

    class ExampleDB:
        def __init__(self, name, age):
            self.name = name
            self.age = age

    filleddb = object.__new__(ExampleDB)
    filleddb.__dict__ = mydict

    with open(Path("dict_save.json"), 'w',encoding="utf-8") as file:
        json.dump(mydict,file,indent=4)

    json_data = json.dumps(mydict)
    print(json_data)

if __name__ == "__main__":
    main()
