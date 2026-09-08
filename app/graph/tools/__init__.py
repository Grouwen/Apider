import pkgutil
import importlib
import os

# 获取当前包名
current_package = __name__
package_dir = os.path.dirname(__file__)

# walk_packages 会递归遍历所有子包和模块
for importer, module_name, is_pkg in pkgutil.walk_packages([package_dir], prefix=f"{current_package}."):
    importlib.import_module(module_name)