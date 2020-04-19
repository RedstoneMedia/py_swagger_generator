import swagger_generator
import copy
from PyInquirer import prompt
import sys
import argparse

def get_normal_input(arg, key_strings):
    if arg.required:
        return input(f"{key_strings}\\{arg.key_name} : Please input '{arg.key_name}' of type '{arg.data_type}' : ")
    else:
        if input(f"{key_strings}\\{arg.key_name} : The argument '{arg.key_name}' is optional do you wan't to fill it ? (y/n) : ").lower() == "y":
            return input(f"{key_strings}\\{arg.key_name} : Please input '{arg.key_name}' of type '{arg.data_type}' : ")



def get_input_to_fill_templates(args : swagger_generator.TemplateArgs, parent_arg : swagger_generator.TemplateArg = None, key_strings ="root"):
    for arg in args.template_args:
        if arg.data_type == "STRING":
            arg.fill(get_normal_input(arg, key_strings))
        elif arg.data_type == "INTEGER":
            arg.fill(int(get_normal_input(arg, key_strings)))
        elif arg.data_type == "SCHEMA":
            arg.fill(get_normal_input(arg, key_strings).replace("\\n", "\n").replace("\\t", "  "))
        elif arg.data_type == "OBJECT":
            fill_deep_object = arg.required
            if not arg.required:
                if input(f"{key_strings}\\{arg.key_name} : The argument '{arg.key_name}' is optional do you wan't to fill it ? (y/n) : ").lower() == "y":
                    fill_deep_object = True
            if fill_deep_object:

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


def main():
    if sys.version_info >= (3, 7):
        Exception("Must be using at least Python 3.7")

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--r", required=False, default=False, help="Insert generated under routes", action="store_true")
    arg_parser.add_argument("--verbose", required=False, default=False, help="Shows more information", action="store_true")
    parsed_cmd_args = arg_parser.parse_args()

    insert_at_routes = parsed_cmd_args.r
    verbose = parsed_cmd_args.verbose

    questions = [
        {
            'type': 'input',
            'name': 'swagger_document_file',
            'message': "Which swagger document file do you want to target",
        },
        {
            'type': 'input',
            'name': 'template_path',
            'message': "Where is the template you wan't to use located",
        }
    ]

    answers = {"swagger_document_file" : "task.yaml", "template_path" : "templates/route.yaml"} #prompt(questions)
    document_yaml_path = answers['swagger_document_file']
    args = swagger_generator.from_template(answers['template_path'])

    get_input_to_fill_templates(args)
    if verbose:
        print("Building arguments")
    new_swagger = args.build()
    if verbose:
        print("Reading input document")
    document_data = swagger_generator.util.read_file_yaml(document_yaml_path)
    if insert_at_routes:
        routes = swagger_generator.swagger_info.get_routes_info(document_data).keys()

        questions = [
            {
                'type': 'list',
                'name': 'route',
                'message': 'Choose a route, where the created route should be inserted',
                'choices': routes
            }
        ]
        chosen_route = prompt(questions)["route"]
        if verbose:
            print("Inserting created data into input document")
        document_data = swagger_generator.insert_route_data_into_document_data_at_index(new_swagger, document_data,
                                                                                       swagger_generator.util.find_index_in_list(
                                                                                           routes, chosen_route) + 1)
    else:
        if verbose:
            print("Inserting created data into input document")
        document_data = swagger_generator.insert_data_into_document_data_at_end(new_swagger, document_data)

    if verbose:
        print("Overwriting input document")
    swagger_generator.util.write_file_yaml(document_yaml_path, document_data)
    if verbose:
        print("Done")


if __name__ == "__main__":
    main()
