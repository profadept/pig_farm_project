async def test_login_page_loads_when_logged_out(client):
    response = await client.get("/login")

    assert response.status_code == 200


async def test_login_page_redirects_when_logged_in(test_login):
    response = await test_login.get("/login")

    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"


async def test_settings_page_loads(test_login):
    response = await test_login.get("/settings")

    assert response.status_code == 200
