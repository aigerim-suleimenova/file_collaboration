def test_me_includes_full_name(client, user_a, access_token):
    res = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {access_token(user_a)}"})
    assert res.status_code == 200
    assert res.json()["full_name"] == "Aigerim"
