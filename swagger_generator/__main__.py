import swagger_generator
import copy
import sys
import argparse
import json

"""
WORK IN PROGRESS


from PyInquirer import prompt

def get_normal_input(arg, key_strings):
    if arg.required:
        return input(f"{key_strings}\\{arg.key_name} : Please input '{arg.key_name}' of type '{arg.data_type}' : ")
    else:
        if input(f"{key_strings}\\{arg.key_name} : The argument '{arg.key_name}' is optional do you wan't to fill it ? (y/n) : ").lower() == "y":
            return input(f"{key_strings}\\{arg.key_name} : Please input '{arg.key_name}' of type '{arg.data_type}' : ")


def get_choose_one_input(arg, key_strings):
    if arg.required:
        questions = [
            {
                "type": "list",
                "name": "select_value",
                "message": f"{key_strings}\\{arg.key_name} : Select a value for '{arg.key_name}' of type '{arg.data_type.special_data_type}'",
                "choices": arg.data_type.special_data_arguments
            }
        ]
        answer = prompt(questions)
        return answer["select_value"]
    else:
        if input(f"{key_strings}\\{arg.key_name} : The argument '{arg.key_name}' is optional do you wan't to fill it ? (y/n) : ").lower() == "y":
            questions = [
                {
                    "type": "list",
                    "name": "select_value",
                    "message": f"{key_strings}\\{arg.key_name} : Select a value for '{arg.key_name}' of type '{arg.data_type.special_data_type}'",
                    "choices": arg.data_type.special_data_arguments
                }
            ]
            answer = prompt(questions)
            return answer["select_value"]


def get_choose_any_input(arg, key_strings):
    choices_dict = []
    for i, choice in enumerate(arg.data_type.special_data_arguments):
        choices_dict.append({"name" : choice})

    if arg.required:
        questions = [
            {
                "type": "checkbox",
                "name": "select_value",
                "message": f"{key_strings}\\{arg.key_name} : Select values for '{arg.key_name}' of type '{arg.data_type.special_data_type}'",
                "choices": choices_dict
            }
        ]
        answer = prompt(questions)
        return answer["select_value"]
    else:
        if input(f"{key_strings}\\{arg.key_name} : The argument '{arg.key_name}' is optional do you wan't to fill it ? (y/n) : ").lower() == "y":
            questions = [
                {
                    "type": "checkbox",
                    "name": "select_value",
                    "message": f"{key_strings}\\{arg.key_name} : Select values for '{arg.key_name}' of type '{arg.data_type.special_data_type}'",
                    "choices": choices_dict
                }
            ]
            answer = prompt(questions)
            return answer["select_value"]


def get_input_to_fill_object_arg(arg : swagger_generator.TemplateArg, parent_arg : swagger_generator.TemplateArg = None, key_strings ="root"):
    if arg.multiple_type in ["ONE_OR_MORE", "ONE_OR_MORE_LIST"]:
        ref_copy = copy.deepcopy(arg.reference_object)
        arg.reference_object = []

        while True:
            arg.reference_object.append(copy.deepcopy(ref_copy))
            get_input_to_fill_templates(arg.reference_object[-1], arg, f"{key_strings}\\{arg.key_name}")
            if input(f"{key_strings}\\{arg.key_name} : Add another object with name '{arg.key_name}' ? (y/n) : ").lower() == "n":
                break
        arg.is_filled = True
    elif arg.multiple_type == "SINGLE":
        get_input_to_fill_templates(arg.reference_object, arg, f"{key_strings}\\{arg.key_name}")
        arg.is_filled = True


def get_input_to_fill_templates(args : swagger_generator.TemplateArgs, parent_arg : swagger_generator.TemplateArg = None, key_strings ="root"):
    for argument_index, arg in enumerate(args.template_args):
        if arg.data_type == "STRING":
            arg.fill(get_normal_input(arg, key_strings))
        elif arg.data_type == "INTEGER":
            arg.fill(int(get_normal_input(arg, key_strings)))
        elif arg.data_type == "SCHEMA":
            arg.fill(get_normal_input(arg, key_strings).replace("\\n", "\n").replace("\\t", "  "))
        elif arg.data_type == "CHOOSE_ONE" or arg.data_type == "CHOOSE_ANY" or arg.data_type == "CHOOSE_ANY_LIST":
            if arg.data_type == "CHOOSE_ONE":
                selected_value = get_choose_one_input(arg, key_strings)
            elif arg.data_type == "CHOOSE_ANY" or arg.data_type == "CHOOSE_ANY_LIST":
                selected_value = get_choose_any_input(arg, key_strings)
                if arg.data_type == "CHOOSE_ANY":
                    arg.multiple_type = "ONE_OR_MORE"
                elif arg.data_type == "CHOOSE_ANY_LIST":
                    arg.multiple_type = "ONE_OR_MORE_LIST"

            real_data_type = copy.deepcopy(arg.data_type)
            arg.data_type = swagger_generator.DataType(arg.data_type.special_data_type, arg.data_type.file_name, arg.data_type.line_index)
            if len(selected_value) <= 0:
                raise Exception("At least one option has to be selected")

            if arg.data_type == "OBJECT":
                if real_data_type == "CHOOSE_ONE":
                    arg.reference_template_path = selected_value
                    arg.reference_object = swagger_generator.from_template(arg.reference_template_path)
                    get_input_to_fill_object_arg(arg, parent_arg, key_strings)
                elif real_data_type == "CHOOSE_ANY" or real_data_type == "CHOOSE_ANY_LIST":
                    arg.reference_object = []
                    for i, selected in enumerate(selected_value):
                        arg.reference_object.append(swagger_generator.from_template(selected))
                        get_input_to_fill_templates(arg.reference_object[-1], arg, f"{key_strings}\\{arg.key_name}\\CHOICE_{i}")
                    arg.is_filled = True
            else:
                if real_data_type == "CHOOSE_ANY" or real_data_type == "CHOOSE_ANY_LIST":
                    for i, selection in enumerate(selected_value):
                        if arg.data_type == "STRING":
                            selected_value[i] = selection
                        elif arg.data_type == "INTEGER":
                            selected_value[i] = int(selection)
                        elif arg.data_type == "SCHEMA":
                            selected_value[i] = selection.replace("\\n", "\n").replace("\\t", "  ")
                else:
                    if arg.data_type == "STRING":
                        selected_value = selected_value
                    elif arg.data_type == "INTEGER":
                        selected_value = int(selected_value)
                    elif arg.data_type == "SCHEMA":
                        selected_value = selected_value.replace("\\n", "\n").replace("\\t", "  ")
                arg.fill(selected_value)
        elif arg.data_type == "OBJECT":
            fill_deep_object = arg.required
            if not arg.required:
                if input(f"{key_strings}\\{arg.key_name} : The argument '{arg.key_name}' is optional do you wan't to fill it ? (y/n) : ").lower() == "y":
                    fill_deep_object = True
            if fill_deep_object:
                get_input_to_fill_object_arg(arg, parent_arg, key_strings)
"""

def main():
    if sys.version_info < (3, 7):
        raise Exception("Must be using at least Python 3.7")

    arg_parser = argparse.ArgumentParser()
    group = arg_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build", help="Builds all the swagger documents", action="store_true")
    group.add_argument("--add", help="Work in progress. Dose nothing", action="store_true")
    arg_parser.add_argument("-v", "--verbose", required=False, default=False, help="Shows more information", action="store_true")
    parsed_cmd_args = arg_parser.parse_args()

    build_mode = parsed_cmd_args.build
    add_mode = parsed_cmd_args.add
    verbose = parsed_cmd_args.verbose

    if build_mode:
        swagger_builder = swagger_generator.Builder(verbose)
        swagger_builder.build()
    elif add_mode:
        pass


if __name__ == "__main__":
    main()
