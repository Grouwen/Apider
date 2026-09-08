from dataclasses import dataclass


@dataclass
class LogPointData:
    var_name:str
    type:str
    value:str = ""
    object_id:str = ""