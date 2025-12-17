import re
def to_camel(string: str) -> str:
    """将 snake_case 转换为 camelCase（首字母小写）"""
    return re.sub(r'_([a-z])', lambda m: m.group(1).upper(), string)