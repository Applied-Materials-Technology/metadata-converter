import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass

@dataclass
class MatchIDFormat:
    data_types: tuple[str,str,str,str] = ("i_", "b_", "d_", "s_")
    bad_chars: str = "$<>"
    bad_chars2: str = "_.;"

class MetadataConverter:
    def __init__(self, meta_convert_params: MatchIDFormat) -> None:
        self._params: MatchIDFormat = meta_convert_params
        self._mydict: dict = {}
        self._images: list = []
        self._search_type: str = "data_type"

    """open the metadata file and search through depending on the value of search_type"""
    def extract_metadata(self, metadata: Path):
        with open (metadata, "r") as fi:
            id = []
            for ln in fi:
                if ln.startswith("*"):
                    version_info = "MatchID" in ln
                    if version_info == True:
                        inp_type = re.search('MatchID (.+?) Input', ln).group(1)
                        version = re.search('file (.+?) ', ln).group(1)
                        self._mydict["InputType"] = inp_type
                        self._mydict["Version"] = version
                else:
                    if self._search_type == "data_type":
                        dat_type = self.data_type_mark_search(id, ln)
                    elif self._search_type == "key_vals":
                        results = self.key_val_pair_search(id, ln, dat_type)
        self.assign_dtype(id)

    def make_int(self, val):
        """makes metadata value integer when specified"""
        stripped_val = re.sub("[" + self._params.bad_chars2 + "]", "", val)
        val2 = int(stripped_val)
        return val2

    def make_str(self, val):
        """makes metadata value string when specified"""
        val = str(val)
        return val

    def make_bool(self, val):
        """makes metadata value boolean when specified"""
        if val == "True":
            boolval = True
        elif val == "False":
            boolval = False
        return boolval

    def make_double(self, val):
        """splits metadata value into list of individual values when specified"""
        val = val.split(";")
        return val

    def shape_case(self, id, line):
        """adds specific marker for non standard form parameter shape"""
        stripped = re.sub("[" + self._params.bad_chars + "]", "", line)
        id.append([stripped[:-1],"shape_"])


    def extensometer_case(self, id, line):
        """adds specific marker for non standard form parameter extensometer"""
        stripped = re.sub("[" + self._params.bad_chars + "]", "", line)
        id.append([stripped[:-1],"extens_"])

    def shape_list(self, shape_id, data):
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
                correct_d_type = self.make_int(i)
            except:
                correct_d_type = self.make_bool(i)
            list_vals.append(correct_d_type)
        return list_vals




    def data_type_mark_search(self, id, line):
        """search for data type labels when search_type is set to key_vals,
        switch search type to key_vals once label has been found to find paired metadata values"""
        for i in self._params.data_types:
            type_found = str(i) in line
            if type_found == True:
                #self.check_for_order(line)
                self._search_type = "key_vals"
                return str(i)
        return id

    def check_for_order(self,line):
        """check for order param names"""
        order_true = "Order:" in line
        print(line)

    #FIX ISSUE WITH ADDING
    def deformed_image_case(self, id, line):
        deformed_imgs = line.split()
        part = deformed_imgs[0].replace('<Deformed$image>=','DeformedImage=')
        id.append([part, "image_"])
        #return id
            
    def key_val_pair_search(self, id, line, d_type):
        """search for metadata values when search_type is set to key_vals,
        swtich search type to data_type to look for the next data label"""
        if line.startswith("<"):
            if line.startswith("<Deformed$image"):
                self.deformed_image_case(id,line)
            elif line.startswith("<Shape>"):
                self.shape_case(id, line)
            elif line.startswith("<Extensometer>"):
                self.extensometer_case(id, line)
            else:
                stripped = re.sub("[" + self._params.bad_chars + "]", "", line)
                id.append([stripped[:-1],d_type])
                self._search_type = "data_type"




    """assign the right data type to each metadata value"""
    def assign_dtype(self, id):
        try:
            for i in id:
                pair = i[0].split("=")
                if i[1] == "i_":
                    val = self.make_int(pair[1])
                    self._mydict[pair[0]] = val
                elif i[1] == "d_":
                    val = self.make_double(pair[1])
                    self._mydict[pair[0]] = val
                elif i[1] == "b_":
                    val = self.make_bool(pair[1])
                    self._mydict[pair[0]] = val
                elif i[1] == "shape_":
                    val = self.make_double(pair[1])
                    shape_com = self.shape_list(int(val[0]), val[1:])
                    self._mydict[pair[0]] = val
                elif i[1] == "extens_":
                    val = self.make_double(pair[1])
                    self._mydict[pair[0]] = val
                elif i[1] == "image_":
                    val = self.make_double(pair[1])
                    self._images.append(val)
                else:
                    val = pair[1]
                    self._mydict[pair[0]] = val
        except:
            pass
        self.save_data()

    def save_data(self):
        with open(Path("dict_save.json"), 'w',encoding="utf-8") as file:
            json.dump(self._mydict,file,indent=4)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadatafile", default = "example_metadata/Test001_19-0kW.m3inp", type = str)
    args = parser.parse_args()

    meta_convert_params = MatchIDFormat()
    metadata_object = MetadataConverter(meta_convert_params)

    metadata_object.extract_metadata(Path(args.metadatafile))


if __name__ == "__main__":
    main()