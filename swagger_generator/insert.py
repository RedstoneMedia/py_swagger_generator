from swagger_generator import move_dict_key , get_first_key_in_dict, unwrap_first_dict


def insert_route_data_into_document_data_at_end(route_data : dict, document_data : dict):
    document_data["paths"][get_first_key_in_dict(route_data)] = unwrap_first_dict(route_data)
    return document_data

def insert_route_data_into_document_data_at_start(route_data : dict, document_data : dict):
    return insert_route_data_into_document_data_at_index(route_data, document_data, 0)

def insert_route_data_into_document_data_at_index(route_data : dict, document_data : dict, index : int):
    if len(document_data["paths"]) - 1 <= index:
        index = len(route_data) - 1
    document_data["paths"][get_first_key_in_dict(route_data)] = unwrap_first_dict(route_data)
    document_data["paths"] = move_dict_key(document_data["paths"], get_first_key_in_dict(route_data), index)
    return document_data