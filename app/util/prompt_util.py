from typing import Dict, Any, List
from datetime import date, datetime
from typing import Any
import aiofiles
from langchain_core.prompts import PromptTemplate

from app.common.constants import PROMPT_FILE_PATH

async def load_prompt(prompt_file_name:str,**kwargs):
    async with aiofiles.open(PROMPT_FILE_PATH / prompt_file_name, mode="r", encoding="utf-8") as f:
        prompt_content = await f.read()

    template = PromptTemplate.from_template(prompt_content, template_format="jinja2",)
    return template.format(**kwargs)


async def load_apider_user_message_prompt(user_input:str,history_compress:Dict[str,Any])->str:
    user_message = await load_prompt("apider_user_message.jinja2",
                      user_input=user_input,**history_compress)
    return user_message

async def load_compress_memory_prompt(user_input: str,history_compress: Dict[str,Any],
                                      history: List[dict]) -> str:
    history = make_serializable(history)

    return await load_prompt(
        "compress_memory.jinja2",
        user_input=user_input,
        history_compress=history_compress,
        history=history,
    )

def make_serializable(obj: Any) -> Any:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_serializable(v) for v in obj]
    return obj