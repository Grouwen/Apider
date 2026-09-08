from pydantic_settings import BaseSettings

from app.util import config_util


class LLMConfig(BaseSettings):
    llm_model: str
    llm_api_key: str
    llm_base_url: str

    model_config = config_util.get_setting_config("MODEL_")

class CompressMemoryLLMConfig(BaseSettings):
    llm_model: str
    llm_api_key: str
    llm_base_url: str

    model_config = config_util.get_setting_config("COMPRESS_MEMORY_MODEL_")

llm_config = LLMConfig()
compress_memory_llm_config = CompressMemoryLLMConfig()