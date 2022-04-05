"""Philips Air Purifier & Humidifier Switches"""
from __future__ import annotations

import logging
from typing import Any, Callable, List

from aioairctrl import CoAPClient

from homeassistant.components.light import LightEntity
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    CONF_HOST,
    CONF_NAME,
    CONF_ENTITY_CATEGORY,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry

from .philips import Coordinator, PhilipsEntity, model_to_class
from .const import (
    ATTR_LABEL,
    SWITCH_ON,
    SWITCH_OFF,
    CONF_MODEL,
    DATA_KEY_CLIENT,
    DATA_KEY_COORDINATOR,
    DOMAIN,
    PHILIPS_DEVICE_ID,
    LIGHT_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[List[Entity], bool], None]
) -> None:
    _LOGGER.debug("async_setup_entry called for platform switch")

    host = entry.data[CONF_HOST]
    model = entry.data[CONF_MODEL]
    name = entry.data[CONF_NAME]

    data = hass.data[DOMAIN][host]

    client = data[DATA_KEY_CLIENT]
    coordinator = data[DATA_KEY_COORDINATOR]

    model_class = model_to_class.get(model)
    if model_class:
        _LOGGER.debug("working with class: %s", model_class)

        available_lights = model_class.AVAILABLE_LIGHTS

        _LOGGER.debug("result: %s", available_lights)
        lights = []

        for light in LIGHT_TYPES:
            _LOGGER.debug("testing: %s", light)
            if light in available_lights:
                _LOGGER.debug(".. found")
                lights.append(PhilipsLight(client, coordinator, name, model, light))
            else:
                _LOGGER.debug(".. not found in model: %s", model)

        async_add_entities(lights, update_before_add=False)

    else:
        _LOGGER.error("Unsupported model: %s", model)
        return


class PhilipsLight(PhilipsEntity, LightEntity):
    """Define a Philips AirPurifier light."""

    _attr_is_on: bool | None = False

    def __init__(
        self,
        client: CoAPClient,
        coordinator: Coordinator,
        name: str,
        model: str,
        light: str
    ) -> None:
        super().__init__(coordinator)
        self._client = client
        self._model = model
        self._description = LIGHT_TYPES[light]
        self._on = self._description.get(SWITCH_ON)
        self._off = self._description.get(SWITCH_OFF)
        self._attr_device_class = self._description.get(ATTR_DEVICE_CLASS)
        self._attr_icon = self._description.get(ATTR_ICON)
        self._attr_name = f"{name} {self._description[ATTR_LABEL].replace('_', ' ').title()}"
        self._attr_entity_category = self._description.get(CONF_ENTITY_CATEGORY)

        try:
            device_id = self._device_status[PHILIPS_DEVICE_ID]
            self._attr_unique_id = f"{self._model}-{device_id}-{light.lower()}"
        except Exception as e:
            _LOGGER.error("Failed retrieving unique_id: %s", e)
            raise PlatformNotReady
        self._attrs: dict[str, Any] = {}
        self.kind = light


    @property
    def is_on(self) -> bool:
        return self._device_status.get(self.kind) == self._on


    async def async_turn_on(self, **kwargs) -> None:
        _LOGGER.debug("async_turn_on, kind: %s - value: %s", self.kind, self._on)
        await self._client.set_control_value(self.kind, self._on)


    async def async_turn_off(self, **kwargs) -> None:
        _LOGGER.debug("async_turn_off, kind: %s - value: %s", self.kind, self._off)
        await self._client.set_control_value(self.kind, self._off)
