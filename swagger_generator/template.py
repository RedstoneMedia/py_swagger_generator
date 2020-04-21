from swagger_generator.template_arg import TemplateArg
from swagger_generator.util import move_dict_key, find_dict, get_first_key_in_dict, unwrap_first_dict, remove_keys_from_dict
import random

from os import path
from copy import deepcopy
import math

import yaml


class TemplateArgs:

    INDENT = "  "

    def __init__(self, template_path : str, auto_read = True):
        self.template_path = template_path
        self.template_string = None
        if auto_read:
            self.template_string = self.__read_template(template_path)
        self.template_args = []

        self.args = {}
        self.__lines = []
        self.__parsed_yaml_string = ""
        self.__yaml_data = {}

    def parse_template_data(self):
        self.__lines = self.template_string.split("\n")
        for i, line in enumerate(self.__lines):
            line = line.replace("\r", "").replace("\n", "")
            if len(line) == 0:
                continue
            self.__parse_one_line(i, line)


    def __parse_one_line(self, line_index, line):
        char_index_start = None
        char_index_end = None
        last_char = ""
        in_arg = False
        argument_data = ""
        for i, c in enumerate(list(line)):
            if in_arg:
                if c == "}" and last_char == "}":
                    char_index_end = i + 1
                    break
                if c != "}":
                    argument_data += c

            if c == "{" and last_char == "{" and not in_arg:
                in_arg = True
                char_index_start = i - 1
            last_char = c

        if char_index_start != None and char_index_end != None and len(argument_data) > 0:
            argument_id = random.randint(0, 4294967296)
            argument = TemplateArg(argument_data, line_index, char_index_start, char_index_end, argument_id, self.template_path)
            argument.parse_argument_data_string()
            if argument.reference_template_path:
                argument.reference_object = from_template(argument.reference_template_path)
            self.__lines[line_index] = line.replace(line[char_index_start:char_index_end], "{{"+ str(argument_id) +"}}")
            self.template_args.append(argument)


    def __read_template(self, template_path):
        if path.isfile(template_path):
            file = open(template_path, mode="r", encoding="utf-8")
            template_string = file.read()
            file.close()
            return template_string
        else:
            raise FileNotFoundError(f"The Template file at : '{template_path}' could not be found")


    def build(self):
        self.__convert_template_args_to_dict(self.template_args, self.args)
        self.__insert_values_into_lines(self, self.args)
        return self.__yaml_data

    def __create_placeholder_yaml_insert(self, arg : TemplateArg, indent : int):
        return f"PLACEHOLDER_SWAGGER_GEN_REAL_ID_{arg.real_unique_id}:\n" + self.INDENT * indent + self.INDENT + f"'{arg.real_unique_id}'"

    def __create_placeholders_yaml_insert(self, arg : TemplateArg, indent : int, for_list : bool = False):
        add_to_line = ""
        if for_list:
            add_to_line = "- "
        return_string = ""
        for i in range(0, len(arg.reference_object)):
            if i == 0:
                return_string += f"{add_to_line}PLACEHOLDER_SWAGGER_GEN_REAL_ID_{arg.real_unique_id}_{i}: '{arg.real_unique_id}_{i}'"
            else:
                return_string += "\n"+ self.INDENT * indent + f"{add_to_line}PLACEHOLDER_SWAGGER_GEN_REAL_ID_{arg.real_unique_id}_{i}: '{arg.real_unique_id}_{i}'"
        return return_string

    def __create_placeholders_pair_insert(self, arg : TemplateArg, index : int):
        return f"PLACEHOLDER_SWAGGER_GEN_REAL_ID_{arg.real_unique_id}_{index}", f"{arg.real_unique_id}_{index}"

    def __create_placeholder_pair_insert(self, arg : TemplateArg):
        return f"PLACEHOLDER_SWAGGER_GEN_REAL_ID_{arg.real_unique_id}", str(arg.real_unique_id)

    def __insert_values_into_lines(self, template_args, args_dict):
        reference_args_and_indents = {}
        for key in args_dict:
            for arg in template_args.template_args:
                if arg.key_name == key:
                    if arg.reference_object and arg.is_filled:
                        if arg.multiple_type == "SINGLE":
                            self.__insert_values_into_lines(arg.reference_object, args_dict[key])
                            for i, line in enumerate(template_args.__lines):
                                if line.find("{{" + str(arg.id) + "}}") != -1:
                                    indent = math.floor(len(line[:arg.char_index_start]) / len(self.INDENT))
                                    reference_args_and_indents[arg] = indent
                                    template_args.__lines[i] = line.replace("{{" + str(arg.id) + "}}", self.__create_placeholder_yaml_insert(arg, indent))
                        elif arg.multiple_type in ["ONE_OR_MORE", "ONE_OR_MORE_LIST"]:
                            for i, list_args in enumerate(args_dict[key]):
                                self.__insert_values_into_lines(arg.reference_object[i], list_args)
                            for i, line in enumerate(template_args.__lines):
                                if line.find("{{" + str(arg.id) + "}}") != -1:
                                    indent = math.floor(len(line[:arg.char_index_start]) / len(self.INDENT))
                                    reference_args_and_indents[arg] = indent
                                    if arg.multiple_type == "ONE_OR_MORE_LIST":
                                        template_args.__lines[i] = line.replace("{{" + str(arg.id) + "}}",self.__create_placeholders_yaml_insert(arg, indent, for_list=True))
                                    else:
                                        template_args.__lines[i] = line.replace("{{" + str(arg.id) + "}}", self.__create_placeholders_yaml_insert(arg, indent))

                    elif arg.is_filled:
                        for i, line in enumerate(template_args.__lines):
                            template_args.__lines[i] = line.replace("{{" + str(arg.id) + "}}", str(arg.value))

        # remove leftover optional ids
        for arg in template_args.template_args:
            for i, line in enumerate(template_args.__lines):
                template_args.__lines[i] = line.replace("{{" + str(arg.id) + "}}", "")

        # convert lines back into full string
        for i in template_args.__lines:
            template_args.__parsed_yaml_string += i + "\n"

        p = template_args.__parsed_yaml_string
        template_args.__yaml_data = yaml.safe_load(p)
        keys_to_remove = []
        for i in reference_args_and_indents:
            if i.multiple_type == "SINGLE":
                parent_dict, found_index, parent_key_name = find_dict(template_args.__yaml_data, self.__create_placeholder_pair_insert(i), find_by_value=True)
                search_obj = deepcopy(parent_dict[parent_key_name])
                for j in search_obj:
                    if "PLACEHOLDER_SWAGGER_GEN_REAL_ID" in j:
                        if search_obj[j] == str(i.real_unique_id):
                            keys_to_remove.append(j)
                            parent_dict[parent_key_name][get_first_key_in_dict(i.reference_object.__yaml_data)] = unwrap_first_dict(i.reference_object.__yaml_data)
                parent_dict[parent_key_name] = move_dict_key(parent_dict[parent_key_name], get_first_key_in_dict(i.reference_object.__yaml_data), found_index)
            elif i.multiple_type in ["ONE_OR_MORE", "ONE_OR_MORE_LIST"]:
                for j in range(0, len(i.reference_object)):
                    if i.multiple_type == "ONE_OR_MORE_LIST":
                        parent_dict, found_index, parent_key_name = find_dict(template_args.__yaml_data, self.__create_placeholders_pair_insert(i, j), find_by_value=True)
                    else:
                        parent_dict, found_index, parent_key_name = find_dict(template_args.__yaml_data, self.__create_placeholders_pair_insert(i, j), find_by_value=True)
                    search_obj = deepcopy(parent_dict[parent_key_name])
                    for k in search_obj:
                        if isinstance(k, str):
                            if "PLACEHOLDER_SWAGGER_GEN_REAL_ID" in k:
                                if search_obj[k] == f"{i.real_unique_id}_{j}":
                                    keys_to_remove.append(k)
                                    parent_dict[parent_key_name][get_first_key_in_dict(i.reference_object[j].__yaml_data)] = unwrap_first_dict(i.reference_object[j].__yaml_data)
        template_args.__yaml_data = remove_keys_from_dict(template_args.__yaml_data, keys_to_remove)  # remove placeholders


    def __convert_template_args_to_dict(self, args, object):
        for arg in args:
            if arg.is_filled:
                if arg.value:
                    object[arg.key_name] = arg.value
                elif arg.reference_object:
                    if arg.multiple_type == "SINGLE":
                        object[arg.key_name] = {}
                        self.__convert_template_args_to_dict(arg.reference_object.template_args, object[arg.key_name])
                    elif arg.multiple_type in ["ONE_OR_MORE", "ONE_OR_MORE_LIST"]:
                        object[arg.key_name] = []
                        for reference_object in arg.reference_object: # arg.reference object is a list in this case
                            object[arg.key_name].append({})
                            self.__convert_template_args_to_dict(reference_object.template_args, object[arg.key_name][-1])


    def __deepcopy__(self, memodict={}):
        new_object = TemplateArgs(self.template_path)
        new_object.template_args = deepcopy(self.template_args, memo=memodict)
        new_object.args = deepcopy(self.args, memo=memodict)
        new_object.__lines = deepcopy(self.__lines, memo=memodict)
        return new_object


    def __repr__(self):
        template_args_string = ""
        for i, template_arg in enumerate(self.template_args):
            if i == 0:
                template_args_string += "\n" + str(template_arg)
            else:
                template_args_string += "\n," + str(template_arg)

        return f"TemplateArgs<template_path : {self.template_path}, template_args : ({template_args_string})>"


def from_template(template_path : str) -> TemplateArgs:
    template_args = TemplateArgs(template_path)
    template_args.parse_template_data()
    return template_args