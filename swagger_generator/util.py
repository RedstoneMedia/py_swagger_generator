import yaml

def read_file_yaml(file_path : str) -> dict:
    with open(file_path, mode="r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def write_file_yaml(file_path : str, data : dict):
    with open(file_path, mode="w", encoding="utf-8") as file:
        file.write(yaml.dump(data, sort_keys=False))


def move_dict_key(input_dict : dict, input_key, to_index):
    if len(input_dict) - 1 <= to_index:
        index = len(input_dict) - 1
    output_dict = {}
    input_dict = input_dict.copy()

    index_before = 0
    for i, key in enumerate(input_dict):
        if key == input_key:
            index_before = i

    if index_before - to_index == 0:
        return output_dict

    for i, key in enumerate(input_dict):
        if i == to_index:
            if index_before - to_index > 0:
                output_dict[input_key] = input_dict[input_key]
                output_dict[key] = input_dict[key]
            else:
                output_dict[key] = input_dict[key]
                output_dict[input_key] = input_dict[input_key]

        else:
            if key != input_key:
                output_dict[key] = input_dict[key]


    return output_dict


def find_dict_with_depth(input_dict : dict, input_key, set_depth : int, current_depth : int = 0, find_by_value=False):
    input_dict = input_dict
    for i, key in enumerate(input_dict):
        if isinstance(input_dict, list):
            key = i

        if current_depth+1 == set_depth and find_by_value:
            if isinstance(input_key, tuple):
                for j, k in enumerate(input_dict[key]):
                    if k == input_key[0] and input_dict[key][k] == input_key[1]:
                        return input_dict, j, key

            elif input_key in input_dict[key]:
                return input_dict, i, key
        if isinstance(input_dict[key], dict):
            if r := find_dict_with_depth(input_dict[key], input_key, set_depth, current_depth + 1, find_by_value):
                return r
        elif isinstance(input_dict[key], list):
            if r := find_dict_with_depth(input_dict[key], input_key, set_depth, current_depth + 1, find_by_value):
                return r

        if current_depth != set_depth and not find_by_value:
            continue
        else:
            if not find_by_value:
                if key == input_key:
                    return input_dict, i


def get_first_key_in_dict(input_dict : dict):
    for i in input_dict:
        return i

def unwrap_first_dict(input_dict : dict):
    for i in input_dict:
        return input_dict[i]

def remove_keys_from_dict(input_dict : dict, remove_keys : list) -> dict:
    output_dict = {}
    for key in input_dict:
        if key in remove_keys:
            continue

        if isinstance(input_dict[key], dict):
            output_dict[key] = remove_keys_from_dict(input_dict[key], remove_keys)
        elif isinstance(input_dict[key], list):
            output_dict[key] = []
            for i in input_dict[key]:
                if isinstance(i, dict):
                    output_dict[key].append(remove_keys_from_dict(i, remove_keys))
                elif not i in remove_keys:
                    output_dict[key].append(i)
        else:
            output_dict[key] = input_dict[key]
    return output_dict

def find_index_in_list(input_list : list, input_item):
    for index, item in enumerate(input_list):
        if input_item == item:
            return index