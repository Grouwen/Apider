from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from app.config.model_config import compress_memory_llm_config


def init_compress_memory_llm_model()->BaseChatModel:
    compress_memory_llm_model = init_chat_model(
        model=compress_memory_llm_config.llm_model,
        model_provider="openai",
        api_key=compress_memory_llm_config.llm_api_key,
        base_url=compress_memory_llm_config.llm_base_url,
        temperature=0,
        streaming=True
    )
    return compress_memory_llm_model