from swagger_generator import move_dict_key , get_first_key_in_dict, unwrap_first_dict


def insert_route_data_into_document_data_at_end(route_data : dict, document_data : dict):
    try:
        document_data["paths"][get_first_key_in_dict(route_data)]
        try:
            document_data["paths"][get_first_key_in_dict(route_data)][get_first_key_in_dict(unwrap_first_dict(route_data))]
            raise Exception(f"The key at {get_first_key_in_dict(route_data)}/{get_first_key_in_dict(unwrap_first_dict(route_data))} already exists")
        except KeyError:
            document_data["paths"][get_first_key_in_dict(route_data)][get_first_key_in_dict(unwrap_first_dict(route_data))] = unwrap_first_dict(unwrap_first_dict(route_data))
    except KeyError:
        document_data["paths"][get_first_key_in_dict(route_data)] = unwrap_first_dict(route_data)
    return document_data


def insert_route_data_into_document_data_at_start(route_data : dict, document_data : dict):
    return insert_route_data_into_document_data_at_index(route_data, document_data, 0)


def insert_data_into_document_data_at_end(data : dict, document_data : dict):
    try:
        document_data[get_first_key_in_dict(data)]
        raise Exception(f"The key {get_first_key_in_dict(data)} already exists in the document.")
    except KeyError:
        document_data[get_first_key_in_dict(data)] = unwrap_first_dict(data)
        return document_data


def insert_route_data_into_document_data_at_index(route_data : dict, document_data : dict, index : int):
    if len(document_data["paths"]) - 1 <= index:
        index = len(route_data) - 1

    try:
        document_data["paths"][get_first_key_in_dict(route_data)]
        try:
            document_data["paths"][get_first_key_in_dict(route_data)][get_first_key_in_dict(unwrap_first_dict(route_data))]
            raise Exception(f"The key at {get_first_key_in_dict(route_data)}/{get_first_key_in_dict(unwrap_first_dict(route_data))} already exists")
        except KeyError:
            document_data["paths"][get_first_key_in_dict(route_data)][get_first_key_in_dict(unwrap_first_dict(route_data))] = unwrap_first_dict(unwrap_first_dict(route_data))
    except KeyError:
        document_data["paths"][get_first_key_in_dict(route_data)] = unwrap_first_dict(route_data)
        document_data["paths"] = move_dict_key(document_data["paths"], get_first_key_in_dict(route_data), index)
    return document_data