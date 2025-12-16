from fastapi import Depends, HTTPException, status
from security import get_current_user


def get_current_user_id(current_user: dict = Depends(get_current_user)):
    """获取当前用户的ID

    数据流动：
    1. 通过get_current_user获取当前用户信息
    2. 提取用户ID
    3. 返回用户ID，供后续接口使用
    """
    return current_user["id"]