import re
def to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase (first letter lowercase)."""
    if not snake_str:
        return snake_str
    parts = snake_str.split('_')
    return parts[0] + ''.join(part.capitalize() for part in parts[1:])
"""
def to_camel(string: str) -> str:
    #将 snake_case 转换为 camelCase（首字母小写)
    return re.sub(r'_([a-z])', lambda m: m.group(1).upper(), string)
"""