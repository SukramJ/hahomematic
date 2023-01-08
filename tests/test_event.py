"""Tests for switch entities of hahomematic."""
from __future__ import annotations

import asyncio
from typing import cast
from unittest.mock import call

import const
import helper
from helper import get_event
import pytest

from hahomematic.const import HmEntityUsage, HmEventType
from hahomematic.entity import ClickEvent, DeviceErrorEvent, ImpulseEvent

TEST_DEVICES: dict[str, str] = {
    "VCU2128127": "HmIP-BSM.json",
    "VCU0000263": "HM-Sen-EP.json",
}


@pytest.mark.asyncio
async def test_clickevent(
    central_local_factory: helper.CentralUnitLocalFactory,
) -> None:
    """Test ClickEvent."""
    central, mock_client = await central_local_factory.get_central(TEST_DEVICES)
    event: ClickEvent = cast(
        ClickEvent, await get_event(central, "VCU2128127:1", "PRESS_SHORT")
    )
    assert event.usage == HmEntityUsage.EVENT
    assert event.event_type == HmEventType.KEYPRESS
    central.event(const.LOCAL_INTERFACE_ID, "VCU2128127:1", "PRESS_SHORT", True)
    assert central_local_factory.ha_event_mock.call_args_list[-1] == call(
        "homematic.keypress",
        {
            "interface_id": "CentralTest-Local",
            "address": "VCU2128127",
            "value": True,
            "type": "press_short",
            "subtype": 1,
        },
    )


@pytest.mark.asyncio
async def test_impulseevent(
    central_local_factory: helper.CentralUnitLocalFactory,
) -> None:
    """Test ImpulseEvent."""
    central, mock_client = await central_local_factory.get_central(TEST_DEVICES)
    event: ImpulseEvent = cast(
        ImpulseEvent, await get_event(central, "VCU0000263:1", "SEQUENCE_OK")
    )
    assert event.usage == HmEntityUsage.EVENT
    assert event.event_type == HmEventType.IMPULSE
    central.event(const.LOCAL_INTERFACE_ID, "VCU0000263:1", "SEQUENCE_OK", True)
    assert central_local_factory.ha_event_mock.call_args_list[-1] == call(
        "homematic.impulse",
        {
            "interface_id": "CentralTest-Local",
            "address": "VCU0000263",
            "value": True,
            "type": "sequence_ok",
            "subtype": 1,
        },
    )


@pytest.mark.asyncio
async def test_deviceerrorevent(
    central_local_factory: helper.CentralUnitLocalFactory,
) -> None:
    """Test DeviceErrorEvent."""
    central, mock_client = await central_local_factory.get_central(TEST_DEVICES)
    event: DeviceErrorEvent = cast(
        DeviceErrorEvent, await get_event(central, "VCU2128127:0", "ERROR_OVERHEAT")
    )
    assert event.usage == HmEntityUsage.EVENT
    assert event.event_type == HmEventType.DEVICE_ERROR
    central.event(const.LOCAL_INTERFACE_ID, "VCU2128127:0", "ERROR_OVERHEAT", True)
    assert central_local_factory.ha_event_mock.call_args_list[-1] == call(
        "homematic.device_error",
        {
            "interface_id": "CentralTest-Local",
            "address": "VCU2128127",
            "value": True,
            "device_type": "HmIP-BSM",
            "parameter": "ERROR_OVERHEAT",
        },
    )
