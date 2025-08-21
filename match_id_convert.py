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
    unit_file: Path = "example_metadata/units.json"

class MetadataConverter:
    def __init__(self, meta_convert_params: MatchIDFormat) -> None:
        self._params: MatchIDFormat = meta_convert_params
        self._mydict: dict = {}
        self._images: list = []
        self._search_type: str = "data_type"
        self._order = None
        self._units = None

    def open_units(self):
        with open (self._params.unit_file, "r") as fi:
            my_units = json.load(fi)
            self._units = my_units

    """open the metadata file and search through depending on the value of search_type"""
    def extract_metadata(self, metadata: Path):
        with open (metadata, "r") as fi:
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
                        dat_type = self.data_type_mark_search(ln)
                        self._order = None
                    elif self._search_type == "key_vals":
                        results = self.key_val_pair_search(ln, dat_type)
                    elif self._search_type == "check_order":
                        order = self.check_for_order(ln)
            
                        if order != None:
                            self._order = order
                            self._order = re.sub("[" + "% Order: " + "]", "", ln)
                            self._order = self._order.split(",")


    def make_int(self, val: str) -> int:
        """makes metadata value integer when specified"""
        stripped_val = re.sub("[" + self._params.bad_chars2 + "]", "", val)
        val2 = int(stripped_val)
        return val2

    def make_str(self, val: str) -> str:
        """makes metadata value string when specified"""
        stripped_val = re.sub("[" + "\n" + "]", "", val)
        val = str(stripped_val)
        return val

    def make_bool(self, val: str) -> bool:
        """makes metadata value boolean when specified"""
        stripped_val = re.sub("[" + "\n" + "]", "", val)
        if stripped_val == "True":
            boolval = True
        elif stripped_val == "False":
            boolval = False
        return boolval

    def make_double(self, val: str) -> float:
        """splits metadata value into list of individual values when specified"""
        val = val.split(";")
        stripped_val = re.sub("[" + "\n" + "]", "", val[-1])
        val[-1] = stripped_val
        for i in range(len(val)):
            val[i] = float(val[i])
        return val
    
    def make_list(self, val: str) -> list:
        val = val.split(";")
        stripped_val = re.sub("[" + "\n" + "]", "", val[-1])
        val[-1] = stripped_val
        for i in range(len(val)):
            val[i] = (val[i])
        return val

    def shape_case(self, line: str) -> str:
        """adds specific marker for non standard form parameter shape"""
        stripped = re.sub("[" + self._params.bad_chars + "]", "", line)
        return stripped


    def extensometer_case(self, line: str) -> str:
        """adds specific marker for non standard form parameter extensometer"""
        stripped = re.sub("[" + self._params.bad_chars + "]", "", line)
        return stripped
    

    def shape_list(self, shape_id: int, data: str) -> list:
        data = data.split(";")
        stripped_val = re.sub("[" + "\n" + "]", "", data[-1])
        data[-1] = stripped_val
        data.remove("")
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


    def data_type_mark_search(self, line: str) -> str:
        """search for data type labels when search_type is set to key_vals,
        switch search type to key_vals once label has been found to find paired metadata values"""
        for i in self._params.data_types:
            type_found = str(i) in line
            if type_found == True:
                self._search_type = "check_order"
                return str(i)


    def check_for_order(self, line: str) -> str:
        """check for order param names"""
        has_order = "Order: " in line
        self._search_type = "key_vals"

        if has_order == True:
            return line
        

    def deformed_image_case(self, line: str) -> str:
        deformed_imgs = line.split()
        part = deformed_imgs[0].replace('<Deformed$image>=','DeformedImage=')
        return part


    def key_val_pair_search(self, line: str, d_type: str):
        """search for metadata values when search_type is set to key_vals,
        swtich search type to data_type to look for the next data label"""
        if line.startswith("<"):
            if line.startswith("<Deformed$image"):
                stripped = self.deformed_image_case(line)
                d_type = "dimage_"
                self.write_to_dict(stripped, d_type)
            elif line.startswith("<Shape>"):
                stripped = self.shape_case(line)
                d_type = "shape_"
                self.write_to_dict(stripped, d_type)
            elif line.startswith("<Extensometer>"):
                stripped = self.extensometer_case(line)
                self.write_to_dict(stripped, d_type)
            else:
                stripped = re.sub("[" + self._params.bad_chars + "]", "", line)
                self.write_to_dict(stripped, d_type)

    def get_unit(self, value: str) -> str:
        unit = self._units[value]
        return unit
    
    def get_unit_with_order(self, value: str, order: str) -> str:
        print(self._units[order][value.replace('\n','')])
        unit = self._units[order][value.replace('\n','')]
        return unit

    def write_to_dict(self, stripped: str, d_type: str):
        pair = stripped.split("=")
        if self._order != None:
            dictionary1 = {}
            value = self.make_double(pair[1])
            for i in range(len(self._order)):
                key = self.make_str(self._order[i])
                my_unit = self.get_unit_with_order(value = self._order[i], order = pair[0])
                dictionary1[key]={"value":value[i],"unit":my_unit}
            self._mydict[pair[0]] = dictionary1
        else:
            value = self.assign_dtype(pair[1], d_type, pair[0])
            my_unit = self.get_unit(pair[0])
            self._mydict[pair[0]]={"value":value,"unit":my_unit}
        
        self._search_type = "data_type"


    """assign the right data type to each metadata value"""
    def assign_dtype(self, data: str, d_type: str, name):
        try:
            if d_type == "i_":
                val = self.make_int(data)
                return val
            elif d_type == "s_":
                val = self.make_str(data)
                return val
            elif d_type == "d_":
                val = self.make_double(data)
                return val
            elif d_type == "b_":
                val = self.make_bool(data)
                return val
            elif d_type == "shape_":
                val = self.shape_list(int(data[0]), data[1:])
                return val
            elif d_type == "extens_":
                val = self.make_double(data)
                return val
            elif d_type == "image_":
                val = self.make_double(data)
                return val
            else:
                val = data
                return val
        except:
            pass
        self.save_data()


    def save_data(self):
        with open(Path("dict_save_units.json"), 'w',encoding="utf-8") as file:
            json.dump(self._mydict,file,indent=4)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadatafile", default = "example_metadata/Test001_19-0kW.m3inp", type = str)
    args = parser.parse_args()

    meta_convert_params = MatchIDFormat()
    metadata_object = MetadataConverter(meta_convert_params)

    metadata_object.open_units()

    metadata_object.extract_metadata(Path(args.metadatafile))
    metadata_object.save_data()


if __name__ == "__main__":
    main()