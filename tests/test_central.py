"""Test the HaHomematic central."""
from __future__ import annotations

from conftest import get_hm_device
import helper
import pytest


@pytest.mark.asyncio
async def test_device_export(
    central_local_factory: helper.CentralUnitLocalFactory,
) -> None:
    """Test device export."""
    assert central_local_factory
    central = await central_local_factory.get_central({"VCU6354483": "HmIP-STHD.json"})
    assert central
    hm_device = get_hm_device(central_unit=central, address="VCU6354483")
    assert hm_device
    await hm_device.export_device_definition()


@pytest.mark.asyncio
async def test_all_parameters(
    central_local_factory: helper.CentralUnitLocalFactory,
) -> None:
    """Test device export."""
    assert central_local_factory
    central = await central_local_factory.get_central({"VCU6354483": "HmIP-STHD.json"})
    assert central
    parameters = central.paramset_descriptions.get_all_readable_parameters()
    assert parameters
    assert len(parameters) == 26
