import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from src.services.barber_service import BarberService


@pytest.mark.asyncio
@patch("src.services.barber_service.BarberRepository", autospec=True)
async def test_add_barber_success(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_shop_by_id.return_value = AsyncMock(shop_id=1)

    barber_data = AsyncMock(
        barber_name="John",
        start_time="09:00",
        end_time="18:00",
        is_available=True,
        everyday=True
    )

    mock_repo.add_barber.return_value = AsyncMock(barber_id=1)

    result = await BarberService.add_barber(mock_db, shop_id=1, data=barber_data)

    assert result["msg"] == "Barber added successfully"
    assert "barber_id" in result


@pytest.mark.asyncio
@patch("src.services.barber_service.BarberRepository", autospec=True)
async def test_add_barber_shop_not_found(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_shop_by_id.return_value = None

    data = AsyncMock(
        barber_name="John",
        start_time="09:00",
        end_time="18:00",
        is_available=True,
        everyday=True
    )

    with pytest.raises(HTTPException) as exc:
        await BarberService.add_barber(mock_db, 999, data)

    assert exc.value.status_code == 404
    assert "Shop with id 999 not found" in exc.value.detail


@pytest.mark.asyncio
@patch("src.services.barber_service.BarberRepository", autospec=True)
async def test_update_barber_success(mock_repo):
    mock_db = AsyncMock()
    barber_mock = AsyncMock(barber_id=1, shop_id=1)
    shop_mock = AsyncMock(owner_id=10)
    data = AsyncMock(barber_name="Updated Name", start_time=None, end_time=None, is_available=None, everyday=None)

    mock_repo.get_barber_by_id.return_value = barber_mock
    mock_repo.get_shop_by_id.return_value = shop_mock
    mock_repo.update_barber.return_value = barber_mock

    result = await BarberService.update_barber(mock_db, 1, owner_id=10, data=data)

    assert result["msg"] == "Barber updated successfully"
    assert "barber_id" in result


@pytest.mark.asyncio
@patch("src.services.barber_service.BarberRepository", autospec=True)
async def test_update_barber_not_found(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_barber_by_id.return_value = None
    data = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await BarberService.update_barber(mock_db, 1, 10, data)

    assert exc.value.status_code == 404
    assert "Barber not found" in exc.value.detail


@pytest.mark.asyncio
@patch("src.services.barber_service.BarberRepository", autospec=True)
async def test_update_barber_unauthorized(mock_repo):
    mock_db = AsyncMock()
    barber_mock = AsyncMock(shop_id=1)
    shop_mock = AsyncMock(owner_id=5)  # different owner
    data = AsyncMock()

    mock_repo.get_barber_by_id.return_value = barber_mock
    mock_repo.get_shop_by_id.return_value = shop_mock

    with pytest.raises(HTTPException) as exc:
        await BarberService.update_barber(mock_db, 1, owner_id=10, data=data)

    assert exc.value.status_code == 403
    assert "Not authorized to update this barber" in exc.value.detail


@pytest.mark.asyncio
@patch("src.services.barber_service.BarberRepository", autospec=True)
async def test_delete_barber_success(mock_repo):
    mock_db = AsyncMock()
    barber_mock = AsyncMock(barber_id=1, shop_id=1)
    shop_mock = AsyncMock(owner_id=10)

    mock_repo.get_barber_by_id.return_value = barber_mock
    mock_repo.get_shop_by_id.return_value = shop_mock

    result = await BarberService.delete_barber(mock_db, 1, owner_id=10)

    assert result["msg"] == "Barber deleted successfully"


@pytest.mark.asyncio
@patch("src.services.barber_service.BarberRepository", autospec=True)
async def test_delete_barber_not_found(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_barber_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        await BarberService.delete_barber(mock_db, 1, owner_id=10)

    assert exc.value.status_code == 404
    assert "Barber not found" in exc.value.detail


@pytest.mark.asyncio
@patch("src.services.barber_service.BarberRepository", autospec=True)
async def test_delete_barber_unauthorized(mock_repo):
    mock_db = AsyncMock()
    barber_mock = AsyncMock(barber_id=1, shop_id=1)
    shop_mock = AsyncMock(owner_id=5)  # different owner

    mock_repo.get_barber_by_id.return_value = barber_mock
    mock_repo.get_shop_by_id.return_value = shop_mock

    with pytest.raises(HTTPException) as exc:
        await BarberService.delete_barber(mock_db, 1, owner_id=10)

    assert exc.value.status_code == 403
    assert "Not authorized to delete this barber" in exc.value.detail


@pytest.mark.asyncio
@patch("src.services.barber_service.BarberRepository", autospec=True)
async def test_get_available_barbers_success(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_available_barbers.return_value = [AsyncMock(barber_id=1), AsyncMock(barber_id=2)]

    result = await BarberService.get_available_barbers(mock_db, shop_id=1)

    assert isinstance(result, list)
    assert len(result) == 2


@pytest.mark.asyncio
@patch("src.services.barber_service.BarberRepository", autospec=True)
async def test_get_available_barbers_not_found(mock_repo):
    mock_db = AsyncMock()
    mock_repo.get_available_barbers.return_value = []

    with pytest.raises(HTTPException) as exc:
        await BarberService.get_available_barbers(mock_db, 1)

    assert exc.value.status_code == 404
    assert "No available barbers found" in exc.value.detail
