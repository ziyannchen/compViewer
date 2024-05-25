# from datetime import datetime
# import json

# def convert_string_to_type(str_value, target_type):
#     if target_type == 'int':
#         return int(str_value)
#     elif target_type == 'float':
#         return float(str_value)
#     elif target_type == 'bool':
#         return str_value.lower() == 'true'
#     elif target_type == 'date':
#         return datetime.strptime(str_value, "%Y-%m-%d")
#     else:
#         return eval(str_value)
#     # elif target_type == 'list':
#     #     return json.loads(str_value)
#     # else:
#     #     raise ValueError(f"Unsupported target type: {target_type}")