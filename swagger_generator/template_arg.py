import re
import random
from copy import deepcopy
from swagger_generator.data_type import DataType


class TemplateArg:

    TEMPLATE_ARGUMENTS_ARGUMENTS = {
        0 : r"^[A-Z_]+$",
        1 : ["STRING", "INTEGER", "OBJECT", "SCHEMA", r"", DataType.SPECIAL_DATA_REGEX.format(name="CHOOSE_ONE"), DataType.SPECIAL_DATA_REGEX.format(name="CHOOSE_ANY"), DataType.SPECIAL_DATA_REGEX.format(name="CHOOSE_ANY_LIST")],
        2 : ["REQUIRED", "OPTIONAL"],
        3 : ["SINGLE", "ONE_OR_MORE", "ONE_OR_MORE_LIST"],
        4 : r"^.+\.yaml$"
    }

    def __init__(self, arg_data_string : str, line_index : int, char_index_start : int, char_index_end : int, id : int, file_name : str):
        self.arg_data_string = arg_data_string
        self.file_name = file_name
        self.line_index = line_index
        self.char_index_start = char_index_start
        self.char_index_end = char_index_end
        self.id = id
        self.real_unique_id = random.randint(0, 4294967296)

        self.key_name = None
        self.data_type = None
        self.required = True
        self.multiple_type = "SINGLE"
        self.reference_template_path = None

        self.reference_object = None

        self.value = None
        self.is_filled = False

    def parse_argument_data_string(self):
        args = self.arg_data_string.split(",")

        if 1 >= len(args):
            raise Exception(f"Template argument is invalid in file {self.file_name} at line {self.line_index+1} : Key name and data type need to be defined")

        for i, arg in enumerate(args):
            arg = arg.replace(" ", "").replace("\t", "")
            possible_arguments_for_index = self.TEMPLATE_ARGUMENTS_ARGUMENTS[i]
            valid_argument = True
            if isinstance(possible_arguments_for_index, str):
                match = re.match(possible_arguments_for_index, arg)
                if not match:
                    valid_argument = False
            elif isinstance(possible_arguments_for_index, list):
                for possible_args in possible_arguments_for_index:
                    match = re.match(possible_args, arg)
                    if match:
                        valid_argument = True
                        break
                    valid_argument = False

            if not valid_argument:
                raise Exception(f"Template argument is invalid in file {self.file_name} at line {self.line_index+1} : Argument at index {i} can only be {possible_arguments_for_index}, but is '{arg}'")

            if i == 0:
                self.key_name = arg
            elif i == 1:
                self.data_type = DataType(arg, self.file_name, self.line_index)
            elif i == 2:
                if arg == possible_arguments_for_index[0]:
                    self.required = True
                elif arg == possible_arguments_for_index[1]:
                    self.required = False
            elif i == 3:
                self.multiple_type = arg
            elif i == 4:
                if self.data_type == "OBJECT":
                    self.reference_template_path = arg
                else:
                    raise Exception(f"Template argument is invalid in file {self.file_name} at line {self.line_index + 1} : Argument references a template, but the data_type is {self.data_type} and not OBJECT")
        return True

    def fill(self, value):
        if value == None:
            return
        if self.multiple_type == "SINGLE" and isinstance(value, list):
            self.is_filled = False
            raise Exception(f"multiple type is SINGLE, but the given value contains a list")
        elif isinstance(value, list):
            self.value = []
            for i in value:
                if self.data_type.check_fill(i):
                    self.is_filled = True
                    self.value.append(i)
                else:
                    self.is_filled = False
        else:
            if self.data_type.check_fill(value):
                self.is_filled = True
                self.value = value
            else:
                self.is_filled = False


    def __deepcopy__(self, memodict={}):
        new_object = TemplateArg(self.arg_data_string, self.line_index, self.char_index_start, self.char_index_end, self.id, self.file_name)
        new_object.key_name = deepcopy(self.key_name, memo=memodict)
        new_object.data_type = deepcopy(self.data_type, memo=memodict)
        new_object.required = deepcopy(self.required, memo=memodict)
        new_object.multiple_type = deepcopy(self.multiple_type, memo=memodict)
        new_object.reference_template_path = deepcopy(self.reference_template_path, memo=memodict)
        new_object.reference_object = deepcopy(self.reference_object, memo=memodict)
        new_object.value = deepcopy(self.value, memo=memodict)
        new_object.is_filled = deepcopy(self.is_filled, memo=memodict)
        return new_object


    def __repr__(self):
        return f"TemplateArg<argument_data : '{self.arg_data_string}' value : '{self.value}' line: {self.line_index} char_index_start : {self.char_index_start} char_index_end : {self.char_index_end} id : {self.id} file : {self.file_name} reference_object: {self.reference_object}>"