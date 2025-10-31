import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from src.services.user_service import UserService


@pytest.mark.asyncio
@patch("src.services.user_service.UserRepository", autospec=True)
@patch("src.services.user_service.hash_password", return_value="hashed_pw")
async def test_register_user_success(mock_hash, mock_repo):
    mock_db = AsyncMock()

    # ✅ Async methods must return awaitable values
    mock_repo.get_user_by_email.return_value = None
    mock_repo.get_user_by_phone.return_value = None
    mock_repo.create_user.return_value = AsyncMock()

    result = await UserService.register_user(
        mock_db,
        username="purna",
        email="test@example.com",
        password="1234",
        phone_number="9876543210",
        role="customer"
    )

    assert result["message"] == "User registered successfully"


@pytest.mark.asyncio
@patch("src.services.user_service.UserRepository", autospec=True)
async def test_register_user_duplicate_email(mock_repo):
    mock_db = AsyncMock()
    # ✅ Make it async
    mock_repo.get_user_by_email.return_value = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await UserService.register_user(mock_db, "purna", "test@example.com", "1234", "9876543210", "customer")

    assert exc.value.status_code == 400
    assert "Email already registered" in exc.value.detail


@pytest.mark.asyncio
@patch("src.services.user_service.send_email_otp", new_callable=AsyncMock)
@patch("src.services.user_service.UserRepository", autospec=True)
async def test_send_verification_otp_success(mock_repo, mock_send_email):
    mock_db = AsyncMock()
    mock_repo.get_user_by_email.return_value = AsyncMock()
    mock_repo.store_otp.return_value = AsyncMock()

    result = await UserService.send_verification_otp(mock_db, "test@example.com")

    assert result["message"] == "Verification OTP sent to your email"


@pytest.mark.asyncio
@patch("src.services.user_service.UserRepository", autospec=True)
async def test_send_verification_otp_user_not_found(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_user_by_email.return_value = None

    with pytest.raises(HTTPException) as exc:
        await UserService.send_verification_otp(mock_db, "notfound@example.com")

    assert exc.value.status_code == 404
    assert "User not found" in exc.value.detail


@pytest.mark.asyncio
@patch("src.services.user_service.verify_password", return_value=True)
@patch("src.services.user_service.UserRepository", autospec=True)
async def test_login_with_password_success(mock_repo, mock_verify):
    mock_db = AsyncMock()
    user_mock = AsyncMock()
    user_mock.id = 1
    user_mock.role = "customer"
    user_mock.hashed_password = "hashed_pw"
    mock_repo.get_user_by_email.return_value = user_mock

    result = await UserService.login_with_password(mock_db, "test@example.com", "1234", "customer")

    assert result["message"] == "Login successful"


@pytest.mark.asyncio
@patch("src.services.user_service.verify_password", return_value=False)
@patch("src.services.user_service.UserRepository", autospec=True)
async def test_login_with_password_invalid(mock_repo, mock_verify):
    mock_db = AsyncMock()
    user_mock = AsyncMock()
    user_mock.id = 1
    user_mock.role = "customer"
    user_mock.hashed_password = "wrong"
    mock_repo.get_user_by_email.return_value = user_mock

    with pytest.raises(HTTPException) as exc:
        await UserService.login_with_password(mock_db, "test@example.com", "wrongpw", "customer")

    assert exc.value.status_code == 401
    assert "Invalid password" in exc.value.detail
