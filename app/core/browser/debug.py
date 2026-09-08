import re
from typing import Dict, Any, List

from app.common.constants import LOGPOINT_TAG, GENERIC_NOISE_PATTERNS
from app.domain.logpoint_data import LogPointData
from app.domain.browser_data import BrowserData
from playwright.async_api import CDPSession

from app.domain.script import Script

COMPILED_NOISE_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in GENERIC_NOISE_PATTERNS]

class Debug:
    def __init__(self, cdp: CDPSession, data: BrowserData):
        self.cdp = cdp
        self.data = data

        self.cdp.on("Runtime.consoleAPICalled", self._handle_console_api_called)
        self.cdp.on("Debugger.scriptParsed", self._handle_script)


    async def _handle_console_api_called(self, params: dict):
        args = params.get("args",[])
        if not args:
            return
        if not args[0].get("value","") == LOGPOINT_TAG:
            return
        # 根据logpoint_uuid获取对应列表
        logpoint_uuid = args[1]["value"]
        self.data.console_list.setdefault(logpoint_uuid,[])

        # 保存数据
        limit_args = args[2:]
        for key,value in zip(limit_args[::2], limit_args[1::2]):
            # 通用属性
            type = value["type"]
            description = value.get("description")
            logpoint_data = LogPointData(
                var_name=key["value"],
                type=type,
            )
            # type不同属性设置
            if type in ["string","number","boolean"]:
                logpoint_data.value = value["value"]
            elif type in ["undefined","symbol", "bigint", "accessor"]:
                logpoint_data.value = description if description else type
            elif type in ["object", "function"]:
                logpoint_data.object_id = value.get("objectId","")
            else:
                logpoint_data.value = description or type

            self.data.console_list[logpoint_uuid].append(logpoint_data)

    async def _handle_script(self, params: dict):
        if self.is_noise(params):
            return
        scrip = Script.from_dict(params)
        if not scrip.url:
            scrip.url = "动态script，无url"
        self.data.scripts_list.append(scrip)

    def is_noise(self,params:dict)->bool:
        url = params.get("url", "")
        if not url:
            return False
        is_noise = any(pattern.search(url) for pattern in COMPILED_NOISE_PATTERNS)
        return is_noise

    # method
    async def get_scripts_list(self) -> List[Script]:
        """
        获取js的列表
        """
        return self.data.scripts_list

    async def get_script_code_by_id(self, script_id: str) -> List[Dict[str, Any]]:
        """
        根据script_id返回js源码，[{"line":"code"},{"line":"code"}]
        """
        code_with_line = []
        sourcs_dict = await self.cdp.send("Debugger.getScriptSource", {"scriptId": script_id})
        code = sourcs_dict["scriptSource"]
        lines = code.splitlines()
        for i, code in enumerate(lines, start=1):
            code_with_line.append({
                "line": i,
                "code": code
            })
        return code_with_line

    async def set_logpoint(self,logpoint_uuid:str,
                           url:str,
                           line_number:int,column_number:int,
                           condition:str):
        """
        设置logpoint。不暂停程序打印变量
        :param logpoint_uuid: logpoint的uuid
        :param url: js文件的url
        :param line_number: 设置断点行数
        :param column_number: 设置断点列数
        :param condition: 执行的语句
        :return:
        """
        point_data = {
            "url": url,
            "lineNumber": line_number,
            "columnNumber": column_number,
            "condition": f"console.log({condition}),false"
        }
        logpoint = await self.cdp.send("Debugger.setBreakpointByUrl",point_data)
        self.data.logpoint_list.append({
            logpoint_uuid:logpoint
        })

    async def get_logpoint_data_by_uuid(self,logpoint_uuid:str)->List[LogPointData]:
        return self.data.console_list.get(logpoint_uuid,[])

    async def get_object_by_object_id(self,object_id:str)->Dict[str, Any]:
        object_data = await self.cdp.send("Runtime.getProperties", {
            "objectId": object_id,
            "ownProperties": True
        })
        return object_data["result"]