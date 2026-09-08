from typing import Dict, Any

from langgraph.types import interrupt


def hitl_is_continue(message:str)->bool:
    """
    给出提示，不要加选项
    :param message: 只给提示，不要加选项
    :return: 用户是否继续
    """
    info= {
        "message": message+"\n输入1确认",
    }

    user_input = interrupt(info)

    if user_input == "1":
        return True
    else:
        return False


