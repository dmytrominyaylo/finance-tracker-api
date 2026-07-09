async def test_create_user_success(client):
    response = await client.post("/api/users/", json={
        "email": "testuser@gmail.com",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@gmail.com"
    assert data["isActive"] is True


async def test_create_user_conflict(client):
    await client.post("/api/users/", json={
        "email": "duplicate@gmail.com",
        "password": "password123"
    })
    response = await client.post("/api/users/", json={
        "email": "duplicate@gmail.com",
        "password": "password123"
    })
    assert response.status_code == 409


async def test_create_user_invalid_password(client):
    response = await client.post("/api/users/", json={
        "email": "test2@gmail.com",
        "password": "123"
    })
    assert response.status_code == 422


async def test_login_success(client):
    await client.post("/api/users/", json={
        "email": "loginuser@gmail.com",
        "password": "password123"
    })
    response = await client.post("/api/auth/login?email=loginuser@gmail.com&password=password123")
    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"


async def test_login_invalid_credentials(client):
    response = await client.post("/api/auth/login?email=notexist@gmail.com&password=wrongpassword")
    assert response.status_code == 401
