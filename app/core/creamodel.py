from pydantic import BaseModel, create_model
from typing import Dict

def create_pydantic_model(name: str, variable_dict: Dict[str, str]) -> BaseModel:
    fields = {key: (str, ...) for key in variable_dict.values()}
    return create_model(name, **fields, user_id=(str, ...))

def parse_data(model: BaseModel, data_str: str, user_id:str) -> Dict[str, str]:
    data_lines = data_str.split('\n')
    data_dict = {line.split(': ')[0]: line.split(': ')[1] for line in data_lines if ': ' in line}
    data_dict['user_id'] = user_id
    return model(**data_dict).dict()
