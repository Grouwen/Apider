from dataclasses import dataclass, field
from typing import List,Dict

from app.domain.logpoint_data import LogPointData
from app.domain.network_request import NetworkRequest
from app.domain.network_response import NetworkResponse
from app.domain.script import Script


@dataclass
class BrowserData:
    request_list:List[NetworkRequest] = field(default_factory=list)
    response_list:List[NetworkResponse] = field(default_factory=list)

    scripts_list:List[Script] = field(default_factory=list)

    logpoint_list:List[dict] = field(default_factory=list)
    console_list:Dict[str,List[LogPointData]] = field(default_factory=dict)

    hook_registry:List[str] = field(default_factory=list)