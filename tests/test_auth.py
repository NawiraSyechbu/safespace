
from backend.services.auth_service import register_user, login_user


def test_authentication():
    result = register_user(
        username="test_user_safespace",
        email="test_safespace@example.com",
        password="Password123"
    )

    print("Hasil registrasi:", result)

    login_result = login_user(
        email="test_safespace@example.com",
        password="Password123"
    )

    print("Hasil login:", login_result)

    assert login_result["success"] is True


if __name__ == "__main__":
    test_authentication()
