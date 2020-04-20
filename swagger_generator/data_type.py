import re

class DataType:

    TYPES = ["STRING", "INTEGER", "SCHEMA", "OBJECT", "CHOICE"]
    ALLOWED_KEYWORD_CHARS = r"^[A-Z_]+$"

    def __init__(self, type_string : str):
        self.type_string = type_string
        self.basic_type = ""

        self.special_data_type = ""
        self.special_data_arguments = []

        self.parse_basic_type_string()
        self.special_data_string = self.type_string[len(self.basic_type):]
        self.parse_special_data_type()
        self.parse_special_data_arguments()


    def parse_basic_type_string(self):
        current_key_word = ""
        for c in list(self.type_string):
            match = re.match(self.ALLOWED_KEYWORD_CHARS, c)
            if match:
                current_key_word += c
            else:
                break

        if current_key_word in self.TYPES:
            self.basic_type = current_key_word


    def parse_special_data_type(self):
        if self.basic_type == "CHOICE":
            special_data_type = ""
            for i, c in enumerate(list(self.special_data_string)):
                if i == 0:
                    if c == "<":
                        continue
                    else:
                        break
                if c == ">":
                    break
                else:
                    special_data_type += c

            if self.special_data_string:
                self.special_data_type = special_data_type
            else:
                Exception("Special data needs special data type")


    def parse_special_data_arguments(self):
        special_data_arguments_string = self.special_data_string[len(self.special_data_type) + 2:]
        current_special_data_argument = ""
        special_data_arguments = []
        for i, c in enumerate(list(special_data_arguments_string)):
            if i == 0:
                if c == "(":
                    continue
                else:
                    break
            if c == ")":
                special_data_arguments.append(current_special_data_argument)
                break
            else:
                if c == "|":
                    special_data_arguments.append(current_special_data_argument)
                    current_special_data_argument = ""
                else:
                    current_special_data_argument += c

        if len(special_data_arguments) < 1:
            Exception("Special data needs special data arguments")

        self.special_data_arguments = special_data_arguments


    def check_fill(self, value):
        if self.basic_type == "STRING" and not isinstance(value, self.get_python_type_from_basic_type()):
            print(f"Data type is string, but the given value has the type : {type(value)}")
            return False
        elif self.basic_type == "SCHEMA" and not isinstance(value, self.get_python_type_from_basic_type()):
            print(f"Data type is schema, but the given value has the type : {type(value)}")
            return False
        elif self.basic_type == "INTEGER" and not isinstance(value, self.get_python_type_from_basic_type()):
            print(f"Data type is integer, but the given value has the type : {type(value)}")
            return False
        elif self.basic_type == "CHOICE":
            if not isinstance(value, self.get_python_type_from_basic_type()):
                print(f"Special data type is {self.special_data_type.lower()}, but the given value has type : {type(value)}")
                return False
            elif self.special_data_type == "OBJECT":
                print("Special data type is a object, but objects can't be filled")
                return False
        elif self.basic_type == "OBJECT" and not isinstance(value, self.get_python_type_from_basic_type()):
            print(f"Data type is a object, but given value has the type : {type(value)}")
            return False

        return True


    def get_python_type_from_basic_type(self, input = None) -> type:
        if input == None:
            input = self.basic_type
        if input == "STRING" or input == "SCHEMA":
            return str
        elif input == "INTEGER":
            return int
        elif input == "OBJECT":
            return object
        elif input == "CHOICE":
            return self.get_python_type_from_basic_type(self.special_data_type)


    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.basic_type


    def __repr__(self):
        return self.type_string