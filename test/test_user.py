import pytest
import json


class TestAuthAPI:

    @pytest.mark.asyncio
    async def test_user_register(self, client):
        """测试用户注册"""
        # 准备测试数据
        registration_data = {
          "phone_number": "13800000001",
          "password": "123456789",
          "name": "Alan1",
          "birth": "1990-01-01",
          "gender": "male",
          "bio": "Software Engineer",
          "about": "I love coding and building APIs"
        }

        # 发送注册请求
        response = await client.post("/api/v1/users/register", json=registration_data)

        # 验证响应
        response_data = response.json()
        print(response_data)
        assert response.status_code == 200
        assert response_data["name"] == "Alan1"

    @pytest.mark.asyncio
    async def test_user_register_duplicate(self, client):
        registration_data = {
          "phoneNumber": "13800000001",
          "password": "123456789",
          "name": "Alan1",
          "birth": "1990-01-01",
          "gender": "male",
          "bio": "Software Engineer",
          "about": "I love coding and building APIs"
        }

        # 先注册一次
        await client.post("/api/v1/users/register", json=registration_data)
        # 再注册一次
        response = await client.post("/api/v1/users/register", json=registration_data)

        # 验证响应
        response_data = response.json()
        print(response_data)
        assert response.status_code == 400

    # 用户注册信息格式错误
    @pytest.mark.asyncio
    async def test_user_register_info_error(self, client):
        registration_data = {
            "phoneNumber": "13800000005454545",
            "password": "51561456ergdsfgdsfdg",
            "gender": "tiger"
        }
        response = await client.post("/api/v1/users/register", json=registration_data)
        response_data = response.json()
        print(response_data)

    # 用户登录
    @pytest.mark.asyncio
    def test_user_login_success(self, client):
        """测试用户登录成功"""
        # 预先创建用户
        registration_data = {
          "phone_number": "13800000001",
          "password": "123456789",
        }
        client.post("/api/v1/users/register", json=registration_data)

        # 发送登录请求
        login_data = {
            "phone_number": "13800000001",
            "password": "123456789"
        }
        response = client.post("/api/v1/users/login", json=login_data)

        # 验证响应
        response_data = response.json()
        assert response.status_code == 200
        assert "access_token" in response_data
        assert "token_type" in response_data
        assert response_data["token_type"] == "bearer"

    @pytest.mark.asyncio
    def test_user_login_failure(self, client):
        """测试用户登录失败"""
        # 预先创建用户
        registration_data = {
          "phone_number": "13800000001",
          "password": "123456789"
        }
        client.post("/api/v1/users/register", json=registration_data)
        login_data = {
          "phone_number": "13800000002",
          "password": "12345678231"
        }

        response = client.post("/api/v1/users/login", json=login_data)
        response_data = response.json()
        print(response_data)
        # 验证响应
        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    def test_user_create_order(self, client):
        uer_register_data = {
            "phone_number": "13800000001",
            "password": "1233456789",
        }
        client.post("/api/v1/users/register", json=uer_register_data)
        login_data = {"username": "test_user", "password": "password123"}
        login_response = client.post("/api/login", json=login_data)
        token = login_response.json()["access_token"]

        # 使用token获取用户信息
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/users/me", headers=headers)

        # 验证响应
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["username"] == "test_user"
        assert response_data["email"] == "test@example.com"
