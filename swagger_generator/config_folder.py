from swagger_generator.util import read_file_yaml, unwrap_first_dict, get_first_key_in_dict, write_file_yaml
from swagger_generator import *
from swagger_generator.template_arg import TemplateArg
from swagger_generator import DataType
import os
import glob
import copy

class ConfigFolder:

    def __init__(self, verbose : bool, path : str, dir : str = ""):
        self.verbose = verbose
        self.path = path
        self.dir = dir

        self.build_output = ""
        self.config_data = {}
        self.template_paths = []
        self.routes = []
        self.responses = []
        self.schemas = []


    def get_data_value(self, arg : TemplateArg, template_data : dict):
        if arg.required:
            try:
                return template_data[arg.key_name]
            except KeyError:
                raise KeyError(f"Config file at {self.path}/config.yaml needs attribute '{arg.key_name}'")
        else:
            try:
                return template_data[arg.key_name]
            except KeyError:
                pass


    def fill_object(self, arg: TemplateArg, template_data : dict):
        if arg.multiple_type in ["ONE_OR_MORE", "ONE_OR_MORE_LIST"]:
            ref_copy = copy.deepcopy(arg.reference_object)
            arg.reference_object = []

            for item in self.get_data_value(arg, template_data):
                arg.reference_object.append(copy.deepcopy(ref_copy))
                self.fill_args(arg.reference_object[-1], item)

            arg.is_filled = True
        elif arg.multiple_type == "SINGLE":
            self.fill_args(arg.reference_object, self.get_data_value(arg, template_data))
            arg.is_filled = True


    def fill_args(self, args : TemplateArgs, template_data : dict):
        for argument_index, arg in enumerate(args.template_args):
            if arg.data_type == "STRING":
                arg.fill(self.get_data_value(arg, template_data))
            elif arg.data_type == "INTEGER":
                arg.fill(self.get_data_value(arg, template_data))
            elif arg.data_type == "SCHEMA":
                arg.fill(self.get_data_value(arg, template_data))
            elif arg.data_type == "CHOOSE_ONE" or arg.data_type == "CHOOSE_ANY" or arg.data_type == "CHOOSE_ANY_LIST":
                if arg.data_type == "CHOOSE_ONE":
                    selected_value = self.get_data_value(arg, template_data)
                elif arg.data_type == "CHOOSE_ANY" or arg.data_type == "CHOOSE_ANY_LIST":
                    selected_value = self.get_data_value(arg, template_data)
                    if arg.data_type == "CHOOSE_ANY":
                        arg.multiple_type = "ONE_OR_MORE"
                    elif arg.data_type == "CHOOSE_ANY_LIST":
                        arg.multiple_type = "ONE_OR_MORE_LIST"

                real_data_type = copy.deepcopy(arg.data_type)
                arg.data_type = DataType(arg.data_type.special_data_type, arg.data_type.file_name, arg.data_type.line_index)

                if arg.data_type == "OBJECT":
                    # TODO think of a way to implement this case
                    raise NotImplementedError("CHOOSE_ANY, CHOOSE_ONE or CHOOSE_ANY_LIST can not be used with the special data type OBJECT.")
                else:
                    if real_data_type == "CHOOSE_ANY" or real_data_type == "CHOOSE_ANY_LIST":
                        for i, selection in enumerate(selected_value):
                            selected_value[i] = selection
                    arg.fill(selected_value)
            elif arg.data_type == "OBJECT":
                if self.get_data_value(arg, template_data):
                    self.fill_object(arg, template_data)

    def build(self):
        if self.verbose:
            print(f"[*] Building config folder at '{self.path}'")

        try:
            # handel routes
            routes = self.config_data["routes"]
            for route in routes:
                template_name = get_first_key_in_dict(route)
                template = from_template(f"{template_name}.yaml", f"{self.path}/templates")
                template_data = unwrap_first_dict(route)
                self.fill_args(template, template_data)
                self.routes.append(template.build())

            # check if components key is present
            try:
                components = self.config_data["components"]
            except KeyError:
                components = None
            if components:
                # handel responses
                try:
                    responses = components["responses"]
                except KeyError:
                    responses = None
                if responses:
                    for response in responses:
                        template_name = get_first_key_in_dict(response)
                        template = from_template(f"{template_name}.yaml", f"{self.path}/templates")
                        template_data = unwrap_first_dict(response)
                        self.fill_args(template, template_data)
                        self.responses.append(template.build())

                # handel schemas
                try:
                    schemas = components["schemas"]
                except KeyError:
                    schemas = None
                if schemas:
                    for schema in schemas:
                        template_name = get_first_key_in_dict(schema)
                        template = from_template(f"{template_name}.yaml", f"{self.path}/templates")
                        template_data = unwrap_first_dict(schema)
                        self.fill_args(template, template_data)
                        self.schemas.append(template.build())

            config_data_copy = deepcopy(self.config_data)
            del config_data_copy["routes"]
            config_data_copy["paths"] = {}
            config_data_copy["components"]["responses"] = {}
            config_data_copy["components"]["schemas"] = {}
            for route in self.routes:
                config_data_copy["paths"][get_first_key_in_dict(route)] = unwrap_first_dict(route)
            for response in self.responses:
                config_data_copy["components"]["responses"][get_first_key_in_dict(response)] = unwrap_first_dict(response)
            for schema in self.schemas:
                config_data_copy["components"]["schemas"][get_first_key_in_dict(schema)] = unwrap_first_dict(schema)
            config_data_copy = move_dict_key(config_data_copy, "components", len(config_data_copy)-1)
            if self.dir:
                write_file_yaml(f"{self.dir}/{self.build_output}", config_data_copy)
            else:
                write_file_yaml(f"{self.build_output}", config_data_copy)
            if self.verbose:
                print(f"[*] Done Building at '{self.path}'")

        except KeyError as e:
            raise e


    def parse(self):
        config_info = read_file_yaml(f"{self.path}/config.yaml")
        if os.path.isdir(f"{self.path}/templates"):
            templates = []
            for file in glob.glob(f"{self.path}/templates/*.yaml"):
                file = file.replace("\\", "/")
                file = file.split("/")[-1]
                templates.append(file)
            self.template_paths = templates
        self.parse_config_data(config_info)


    def parse_config_data(self, config_info):
        try:
            build_information = config_info["build"]
        except KeyError:
            raise KeyError(f"Config file at {self.path}/config.yaml needs attribute 'build'")

        try:
            self.build_output = build_information["output"]
        except KeyError:
            raise KeyError(f"Config file at {self.path}/config.yaml needs attribute 'output' under attribute 'build'")

        try:
            self.config_data = config_info["data"]
        except KeyError:
            raise KeyError(f"Config file at {self.path}/config.yaml needs attribute 'data'")


    def __repr__(self):
        return f"<ConfigFolder: path: {self.path}, templates: {self.template_paths}, config: {self.config_data}>"


