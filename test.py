import requests
import sys
import json
import functools
from datetime import datetime

# ===== 配置区 =====
BASE_URL = "http://192.168.12.228:8001/api/v1"  # 修改为你的实际地址
HEADERS = {"Content-Type": "application/json"}

# 测试数据（可按需修改）
TEST_DATA = {
    "user_phone": "13800112233",
    "user_password": "123456789",
    "advisor_phone": "13477438613",
    "advisor_password": "123456789",
}

# 全局状态存储（在一个脚本执行周期内共享）
GLOBAL_STATE = {
    "TOKEN": None,
    "USER_ID": None,
    "ADVISOR_ID": None,
    "ORDER_ID": None,
}

# 已执行成功的测试记录，防止重复执行
EXECUTED_TESTS = set()


def log(msg):
    """统一日志格式"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def print_response(resp: requests.Response):
    """打印响应的详细信息"""
    print("-" * 40)
    print(f"  🟦 状态码: {resp.status_code}")
    # print(f"  🟨 Headers: {dict(resp.headers)}") # 可选打印headers
    try:
        # 尝试解析为JSON并美化输出
        json_data = resp.json()
        print("  🟩 响应体 (JSON):")
        print(json.dumps(json_data, indent=2, ensure_ascii=False))
    except requests.exceptions.JSONDecodeError:
        # 如果不是JSON，则直接打印文本
        print("  🟩 响应体 (Text):")
        print(resp.text)
    print("-" * 40)


# ===== 辅助装饰器：声明测试及其依赖 =====
def depends(*dependencies):
    """装饰器：声明一个测试函数的依赖项"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 检查依赖是否已执行成功
            for dep in dependencies:
                if dep not in EXECUTED_TESTS:
                    log(f"⚠️  检测到依赖 '{dep}' 尚未执行，正在自动执行...")
                    # 查找依赖函数并执行
                    dep_func = ALL_TESTS.get(dep)
                    if dep_func and not dep_func():
                        log(f"❌ 依赖 '{dep}' 执行失败，中断当前测试 '{func.__name__}'")
                        return False
                    log(f"✅ 依赖 '{dep}' 执行成功")

            # 执行当前测试
            result = func(*args, **kwargs)
            if result:
                EXECUTED_TESTS.add(func.__name__)
            return result

        # 保存依赖关系供后续使用
        wrapper.dependencies = dependencies
        return wrapper

    return decorator


# ===== 测试函数定义（带依赖声明）=====

@depends()  # 无依赖
def register_user():
    global GLOBAL_STATE
    url = f"{BASE_URL}/users/register"
    data = {
        "phone_number": TEST_DATA["user_phone"],
        "password": TEST_DATA["user_password"]
    }
    try:
        resp = requests.post(url, json=data, headers=HEADERS)
        log(f"【用户注册】状态码: {resp.status_code}")
        print_response(resp)
        if resp.status_code == 200:
            GLOBAL_STATE["USER_ID"] = resp.json().get("id")
            log(f"✅ 用户注册成功，ID: {GLOBAL_STATE['USER_ID']}")
            return True
        else:
            log(f"❌ 注册失败")
            return False
    except Exception as e:
        log(f"❌ 请求异常: {e}")
        return False


@depends()  # 依赖用户注册
def login_user():
    global GLOBAL_STATE
    url = f"{BASE_URL}/users/login"
    data = {
        "phone_number": TEST_DATA["user_phone"],
        "password": TEST_DATA["user_password"]
    }
    try:
        resp = requests.post(url, json=data, headers=HEADERS)
        log(f"【用户登录】状态码: {resp.status_code}")
        print_response(resp)
        if resp.status_code == 200:
            GLOBAL_STATE["TOKEN"] = resp.json().get("access_token")
            # log(f"🔑 Authorization Header: {GLOBAL_STATE['TOKEN']}")  # 打印前30字符
            log("✅ 登录成功，已获取 Token")
            return True
        else:
            log(f"❌ 登录失败")
            return False
    except Exception as e:
        log(f"❌ 请求异常: {e}")
        return False
@depends()
def login_advisor():
    global GLOBAL_STATE
    url = f"{BASE_URL}/advisors/login"
    data = {
        "phone_number": TEST_DATA["advisor_phone"],
        "password": TEST_DATA["advisor_password"]
    }
    try:
        resp = requests.post(url, json=data, headers=HEADERS)
        log(f"【顾问登录】状态码: {resp.status_code}")
        print_response(resp)
        if resp.status_code == 200:
            GLOBAL_STATE["TOKEN"] = resp.json().get("access_token")
            # log(f"🔑 Authorization Header: {GLOBAL_STATE['TOKEN']}")  # 打印前30字符
            log("✅ 登录成功，已获取 Token")
            return True
        else:
            log(f"❌ 登录失败")
            return False
    except Exception as e:
        log(f"❌ 请求异常: {e}")
        return False

@depends()  # 无依赖
def register_advisor():
    global GLOBAL_STATE
    url = f"{BASE_URL}/advisors/register"
    data = {
        "phone_number": TEST_DATA["advisor_phone"],
        "password": TEST_DATA["advisor_password"]
    }
    try:
        resp = requests.post(url, json=data, headers=HEADERS)
        log(f"【顾问注册】状态码: {resp.status_code}")
        print_response(resp)
        if resp.status_code == 200:
            GLOBAL_STATE["ADVISOR_ID"] = resp.json().get("id")
            log(f"✅ 顾问注册成功，ID: {GLOBAL_STATE['ADVISOR_ID']}")
            return True
        else:
            log(f"❌ 顾问注册失败")
            return False
    except Exception as e:
        log(f"❌ 请求异常: {e}")
        return False


@depends("login_user")
def get_advisor_list():
    url = f"{BASE_URL}/users/active-advisors"
    # 可选：带上Token查看更多信息
    headers = HEADERS.copy()
    if GLOBAL_STATE["TOKEN"]:
        headers["Authorization"] = f"Bearer {GLOBAL_STATE['TOKEN']}"
        # log(f"🔑 Authorization Header: {GLOBAL_STATE['TOKEN']}")  # 打印前30字符

    try:
        resp = requests.get(url, headers=headers)
        log(f"【获取顾问列表】状态码: {resp.status_code}")
        print_response(resp)
        if resp.status_code == 200:
            advisors = resp.json()
            log(f"✅ 获取到 {len(advisors)} 位顾问")
            return True
        else:
            log(f"❌ 获取失败")
            return False
    except Exception as e:
        log(f"❌ 请求异常: {e}")
        return False


@depends("login_user")
def create_order():
    global GLOBAL_STATE
    if not GLOBAL_STATE["TOKEN"] :
        log("❌ 缺少必要状态，请检查依赖是否正确执行")
        return False

    url = f"{BASE_URL}/users/create-order"
    data = {
        "advisorId": 2,
        "orderType": "text_reading",
        "generalSituation": "sdafgdegbgdfgv",
        "specificQuestion": "safffvfvfv",
        "isUrgent": True
    }
    headers = {**HEADERS, "Authorization": f"Bearer {GLOBAL_STATE['TOKEN']}"}
    try:
        resp = requests.post(url, json=data, headers=headers)
        log(f"【创建订单】状态码: {resp.status_code}")
        print_response(resp)
        if resp.status_code == 200:
            GLOBAL_STATE["ORDER_ID"] = resp.json().get("id")
            log(f"✅ 订单创建成功，ID: {GLOBAL_STATE['ORDER_ID']}")
            return True
        else:
            log(f"❌ 创建失败")
            return False
    except Exception as e:
        log(f"❌ 请求异常: {e}")
        return False


@depends("login_advisor")  # 依赖登录和订单创建
def complete_order():
    if not GLOBAL_STATE["TOKEN"] or not GLOBAL_STATE["ORDER_ID"]:
        log("❌顾问未登录 或 未找到代处理订单")
        return False

    url = f"{BASE_URL}/advisors/complete-order/{GLOBAL_STATE['ORDER_ID']}"
    data = {"reply": "abcdefghijklmnopqrstuvwxyz"}
    headers = {**HEADERS, "Authorization": f"Bearer {GLOBAL_STATE['TOKEN']}"}
    try:
        resp = requests.patch(url, json=data, headers=headers)
        log(f"【回复订单】状态码: {resp.status_code}")
        print_response(resp)
        if resp.status_code == 200:
            log("✅ 订单回复成功")
            return True
        else:
            log(f"❌ 回复失败")
            return False
    except Exception as e:
        log(f"❌ 请求异常: {e}")
        return False


# ===== 流程测试 =====
# 1.用户登录——用户创建订单——顾问登录——顾问回复订单
def flow1():
    """完整的用户流程测试"""
    log("=== 开始用户流程测试 ===")
    flow_steps = ["login_user", "create_order", "login_advisor", "complete_order"]

    for test_name in flow_steps:
        func = ALL_TESTS.get(test_name)
        if not func:
            log(f"❌ 未知测试: {test_name}")
            return False
        if not func():
            log(f"❌ 流程中断于步骤: {test_name}")
            return False
    log("✅ 用户流程测试全部通过")
    return True


# ===== 所有测试函数映射表 =====
ALL_TESTS = {
    "register_user": register_user,
    "login_user": login_user,
    "login_advisor": login_advisor,
    "register_advisor": register_advisor,
    "get_advisor_list": get_advisor_list,
    "create_order": create_order,
    "complete_order": complete_order,
}


# ===== 主控逻辑 =====
def run_single_test(test_name):
    """运行单个测试（自动处理依赖）"""
    if test_name not in ALL_TESTS:
        log(f"❌ 未知测试名: {test_name}")
        log("可用测试: " + ", ".join(ALL_TESTS.keys()))
        return False

    log(f"🚀 开始执行测试: {test_name}")
    func = ALL_TESTS[test_name]
    success = func()
    if success:
        log(f"🎉 测试 '{test_name}' 成功完成！")
    else:
        log(f"💥 测试 '{test_name}' 失败！")
    return success


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "flow1":
            flow1()
        elif command in ALL_TESTS:
            run_single_test(command)
        else:
            log(f"❌ 未知命令或测试: {command}")
            print("可用命令:")
            print("  python test.py <test_name>  # 运行单个测试（自动处理依赖）")
            print("  python test.py flow         # 运行完整用户流程")
            print("\n可用测试:")
            for name in ALL_TESTS:
                deps = getattr(ALL_TESTS[name], 'dependencies', ())
                dep_str = f" (依赖: {', '.join(deps)})" if deps else ""
                print(f"  {name}{dep_str}")
    else:
        # 默认行为：显示帮助
        print("用法:")
        print("  py|thon test.py <test_name>  # 运行单个测试（自动处理依赖）")
        print("  python test.py flow         # 运行完整用户流程")
        print("\n可用测试:")
        for name in ALL_TESTS:
            deps = getattr(ALL_TESTS[name], 'dependencies', ())
            dep_str = f" (依赖: {', '.join(deps)})" if deps else ""
            print(f"  {name}{dep_str}")