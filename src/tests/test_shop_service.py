import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from src.services.shop_service import ShopService


@pytest.mark.asyncio
@patch("src.services.shop_service.ShopRepository", autospec=True)
async def test_get_shops_for_user_success(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_all_shops.return_value = [
        AsyncMock(
            shop_id=1,
            shop_name="Salon Bliss",
            address="Main Street",
            city="Hyderabad",
            state="Telangana",
            open_time="09:00",
            close_time="18:00",
            is_open=True,
        )
    ]

    result = await ShopService.get_shops_for_user(mock_db)

    assert isinstance(result, list)
    assert result[0]["shop_name"] == "Salon Bliss"
    assert result[0]["is_open"] is True


@pytest.mark.asyncio
@patch("src.services.shop_service.ShopRepository", autospec=True)
async def test_get_shops_for_user_no_shops(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_all_shops.side_effect = HTTPException(status_code=404, detail="No shops found")

    with pytest.raises(HTTPException) as exc:
        await ShopService.get_shops_for_user(mock_db)

    assert exc.value.status_code == 404
    assert "No shops found" in exc.value.detail


@pytest.mark.asyncio
@patch("src.services.shop_service.ShopRepository", autospec=True)
async def test_get_shops_by_owner_success(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_shops_by_owner.return_value = [
        AsyncMock(
            shop_id=1,
            shop_name="Barber Hub",
            address="Market Road",
            city="Vijayawada",
            state="AP",
            open_time="08:00",
            close_time="17:00",
            is_open=True,
        )
    ]

    result = await ShopService.get_shops_by_owner(mock_db, owner_id=101)

    assert len(result) == 1
    assert result[0]["shop_name"] == "Barber Hub"


@pytest.mark.asyncio
@patch("src.services.shop_service.ShopRepository", autospec=True)
async def test_get_available_slots_success(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_available_slots.return_value = [
        AsyncMock(
            slot_id=1,
            barber_id=5,
            barber_name="Ravi",
            slot_time="10:00",
            status="available"
        )
    ]

    result = await ShopService.get_available_slots(mock_db, shop_id=1, date="2025-11-04")

    assert len(result) == 1
    assert result[0]["barber_name"] == "Ravi"
    assert result[0]["status"] == "available"


@pytest.mark.asyncio
@patch("src.services.shop_service.ShopRepository", autospec=True)
async def test_get_available_slots_not_found(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_available_slots.side_effect = HTTPException(status_code=404, detail="No available slots found")

    with pytest.raises(HTTPException) as exc:
        await ShopService.get_available_slots(mock_db, 1, "2025-11-04")

    assert exc.value.status_code == 404
    assert "No available slots found" in exc.value.detail


@pytest.mark.asyncio
@patch("src.services.shop_service.ShopRepository", autospec=True)
async def test_create_shop_if_not_exists_success(mock_repo):
    mock_db = AsyncMock()

    mock_repo.get_user_by_id.return_value = AsyncMock(role="owner")
    mock_repo.get_existing_shop.return_value = None
    mock_repo.create_shop.return_value = AsyncMock(shop_id=123)

    shop_data = AsyncMock(
        shop_name="Gentlemen's Lounge",
        address="Madhapur",
        city="Hyderabad",
        state="TS",
        open_time="09:00",
        close_time="19:00"
    )

    result = await ShopService.create_shop_if_not_exists(mock_db, 1, shop_data)

    assert result["message"] == "Shop created successfully"
    assert "shop_id" in result


@pytest.mark.asyncio
@patch("src.services.shop_service.ShopRepository", autospec=True)
async def test_create_shop_if_not_exists_owner_not_found(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_user_by_id.return_value = None

    shop_data = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await ShopService.create_shop_if_not_exists(mock_db, 99, shop_data)

    assert exc.value.status_code == 404
    assert "Owner not found" in exc.value.detail


@pytest.mark.asyncio
@patch("src.services.shop_service.ShopRepository", autospec=True)
async def test_create_shop_if_not_exists_unauthorized(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_user_by_id.return_value = AsyncMock(role="customer")

    shop_data = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await ShopService.create_shop_if_not_exists(mock_db, 1, shop_data)

    assert exc.value.status_code == 403
    assert "User not authorized" in exc.value.detail


@pytest.mark.asyncio
@patch("src.services.shop_service.ShopRepository", autospec=True)
async def test_create_shop_if_not_exists_duplicate(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_user_by_id.return_value = AsyncMock(role="owner")
    mock_repo.get_existing_shop.return_value = AsyncMock()

    shop_data = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await ShopService.create_shop_if_not_exists(mock_db, 1, shop_data)

    assert exc.value.status_code == 400
    assert "Shop already exists" in exc.value.detail


@pytest.mark.asyncio
@patch("src.services.shop_service.ShopRepository", autospec=True)
async def test_book_slots_success(mock_repo):
    mock_db = AsyncMock()
    slot_mock = AsyncMock(slot_id=1, slot_date="2025-11-04", slot_time="10:00", is_booked=False)
    mock_repo.get_slot_by_id.return_value = slot_mock
    mock_repo.create_booking.return_value = AsyncMock()

    result = await ShopService.book_slots(mock_db, 1, 2, 3, [1])

    assert result["message"] == "1 slots booked successfully"
    assert len(result["booked_slots"]) == 1
    assert result["booked_slots"][0]["status"] == "booked"


@pytest.mark.asyncio
@patch("src.services.shop_service.ShopRepository", autospec=True)
async def test_book_slots_slot_not_found(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_slot_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        await ShopService.book_slots(mock_db, 1, 2, 3, [99])

    assert exc.value.status_code == 404
    assert "Slot 99 not found" in exc.value.detail


@pytest.mark.asyncio
@patch("src.services.shop_service.ShopRepository", autospec=True)
async def test_book_slots_already_booked(mock_repo):
    mock_db = AsyncMock()
    slot_mock = AsyncMock(slot_id=1, is_booked=True)
    mock_repo.get_slot_by_id.return_value = slot_mock

    with pytest.raises(HTTPException) as exc:
        await ShopService.book_slots(mock_db, 1, 2, 3, [1])

    assert exc.value.status_code == 400
    assert "already booked" in exc.value.detail
