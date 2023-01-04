"""Tests for light entities of hahomematic."""
from __future__ import annotations

from typing import cast

from conftest import get_hm_custom_entity
import helper
import pytest

from hahomematic.const import HmEntityUsage
from hahomematic.custom_platforms.light import (
    CeColorDimmer,
    CeColorTempDimmer,
    CeDimmer,
    CeIpFixedColorLight,
)

TEST_DEVICES: dict[str, str] = {
    "VCU1399816": "HmIP-BDT.json",
    "VCU3747418": "HM-LC-RGBW-WM.json",
    "VCU0000115": "HM-LC-DW-WM.json",
    "VCU3716619": "HmIP-BSL.json",
}


@pytest.mark.asyncio
async def test_cedimmer(
    central_local_factory: helper.CentralUnitLocalFactory,
) -> None:
    """Test CeDimmer."""
    central = await central_local_factory.get_central(TEST_DEVICES)
    assert central
    light: CeDimmer = cast(
        CeDimmer, await get_hm_custom_entity(central, "VCU1399816", 4)
    )
    assert light.usage == HmEntityUsage.CE_PRIMARY

    assert light.brightness == 0
    await light.turn_on()
    assert light.brightness == 255
    await light.turn_on(**{"brightness": 28})
    assert light.brightness == 28
    await light.turn_off()
    assert light.brightness == 0


@pytest.mark.asyncio
async def test_cecolordimmer(
    central_local_factory: helper.CentralUnitLocalFactory,
) -> None:
    """Test CeColorDimmer."""
    central = await central_local_factory.get_central(TEST_DEVICES)
    assert central
    light: CeColorDimmer = cast(
        CeColorDimmer, await get_hm_custom_entity(central, "VCU3747418", 1)
    )
    assert light.usage == HmEntityUsage.CE_PRIMARY

    assert light.brightness == 0
    await light.turn_on()
    assert light.brightness == 255
    await light.turn_on(**{"brightness": 28})
    assert light.brightness == 28
    await light.turn_off()
    assert light.brightness == 0

    assert light.hs_color == (0.0, 0.0)
    await light.turn_on(**{"hs_color": (44.4, 69.3)})
    assert light.hs_color == (45.0, 100)


@pytest.mark.asyncio
async def test_cecolortempdimmer(
    central_local_factory: helper.CentralUnitLocalFactory,
) -> None:
    """Test CeColorTempDimmer."""
    central = await central_local_factory.get_central(TEST_DEVICES)
    assert central
    light: CeColorTempDimmer = cast(
        CeColorTempDimmer, await get_hm_custom_entity(central, "VCU0000115", 1)
    )
    assert light.usage == HmEntityUsage.CE_PRIMARY

    assert light.brightness == 0
    await light.turn_on()
    assert light.brightness == 255
    await light.turn_on(**{"brightness": 28})
    assert light.brightness == 28
    await light.turn_off()
    assert light.brightness == 0

    assert light.color_temp == 500
    await light.turn_on(**{"color_temp": 433})
    assert light.color_temp == 433


@pytest.mark.asyncio
async def test_ceipfixedcolorlight(
    central_local_factory: helper.CentralUnitLocalFactory,
) -> None:
    """Test CeIpFixedColorLight."""
    central = await central_local_factory.get_central(TEST_DEVICES)
    assert central
    light: CeIpFixedColorLight = cast(
        CeIpFixedColorLight, await get_hm_custom_entity(central, "VCU3716619", 8)
    )
    assert light.usage == HmEntityUsage.CE_PRIMARY

    assert light.brightness == 0
    await light.turn_on()
    assert light.brightness == 255
    await light.turn_on(**{"brightness": 28})
    assert light.brightness == 28
    await light.turn_off()
    assert light.brightness == 0

    assert light.color_name == "BLACK"
    await light.turn_on(**{"hs_color": (0, 0)})
    assert light.color_name == "WHITE"
    await light.turn_on(**{"hs_color": (60, 50)})
    assert light.color_name == "YELLOW"
    await light.turn_on(**{"hs_color": (120, 50)})
    assert light.color_name == "GREEN"
    await light.turn_on(**{"hs_color": (180, 50)})
    assert light.color_name == "TURQUOISE"
    await light.turn_on(**{"hs_color": (240, 50)})
    assert light.color_name == "BLUE"
    await light.turn_on(**{"hs_color": (300, 50)})
    assert light.color_name == "PURPLE"
    await light.turn_on(**{"hs_color": (350, 50)})
    assert light.color_name == "RED"
