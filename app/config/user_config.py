from pathlib import Path

import yaml

class UserConfig:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self._data = self._load_config()

    def _load_config(self) -> dict:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 解析错误: {e}")

    def get(self, key_path: str, default=None):
        """
        通过点号路径获取嵌套配置值
        例如: config.get('database.credentials.username')
        """
        keys = key_path.split('.')
        value = self._data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value