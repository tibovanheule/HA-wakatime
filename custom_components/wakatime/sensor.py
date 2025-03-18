"""Sensor platform for Wakatime integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import WakatimeDataUpdateCoordinator
from .const import (
    DOMAIN,
    ICON_CODING,
    ICON_EDITOR,
    ICON_LANGUAGE,
    ICON_OPERATING_SYSTEM,
    ICON_PROJECT,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="daily_total",
        translation_key="daily_total",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL,
        icon=ICON_CODING,
    ),
    SensorEntityDescription(
        key="top_language",
        translation_key="top_language",
        icon=ICON_LANGUAGE,
    ),
    SensorEntityDescription(
        key="top_project",
        translation_key="top_project",
        icon=ICON_PROJECT,
    ),
    SensorEntityDescription(
        key="top_editor",
        translation_key="top_editor",
        icon=ICON_EDITOR,
    ),
    SensorEntityDescription(
        key="top_os",
        translation_key="top_operating_system",
        icon=ICON_OPERATING_SYSTEM,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Wakatime sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        WakatimeSensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in SENSOR_TYPES
    )


class WakatimeSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Wakatime sensor."""

    coordinator: WakatimeDataUpdateCoordinator
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WakatimeDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{DOMAIN}_{entity_description.key}"

        if "user_info" in coordinator.data and "data" in coordinator.data["user_info"]:
            user = coordinator.data["user_info"]["data"]
            self._attr_device_info = {
                "identifiers": {(DOMAIN, user.get("id", ""))},
                "name": user.get("display_name", "Wakatime"),
                "manufacturer": "Wakatime",
                "model": "API",
                "sw_version": user.get("last_heartbeat_at", ""),
            }

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        if self.entity_description.key == "daily_total":
            if (
                "summary" in self.coordinator.data
                and "data" in self.coordinator.data["summary"]
            ):
                for day in self.coordinator.data["summary"]["data"]:
                    if "grand_total" in day:
                        seconds = day["grand_total"].get("total_seconds", 0)
                        return int(seconds)
            return 0

        if self.entity_description.key == "top_language":
            if (
                "stats" in self.coordinator.data
                and "data" in self.coordinator.data["stats"]
            ):
                languages = self.coordinator.data["stats"]["data"].get("languages", [])
                if languages:
                    return languages[0].get("name", "Unknown")
            return "Unknown"

        if self.entity_description.key == "top_project":
            if (
                "stats" in self.coordinator.data
                and "data" in self.coordinator.data["stats"]
            ):
                projects = self.coordinator.data["stats"]["data"].get("projects", [])
                if projects:
                    return projects[0].get("name", "Unknown")
            return "Unknown"

        if self.entity_description.key == "top_editor":
            if (
                "stats" in self.coordinator.data
                and "data" in self.coordinator.data["stats"]
            ):
                editors = self.coordinator.data["stats"]["data"].get("editors", [])
                if editors:
                    return editors[0].get("name", "Unknown")
            return "Unknown"

        if self.entity_description.key == "top_os":
            if (
                "stats" in self.coordinator.data
                and "data" in self.coordinator.data["stats"]
            ):
                operating_systems = self.coordinator.data["stats"]["data"].get(
                    "operating_systems", []
                )
                if operating_systems:
                    return operating_systems[0].get("name", "Unknown")
            return "Unknown"

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return entity specific state attributes."""
        if not self.coordinator.data:
            return None

        attributes = {}

        if self.entity_description.key == "daily_total":
            if (
                "summary" in self.coordinator.data
                and "data" in self.coordinator.data["summary"]
            ):
                for day in self.coordinator.data["summary"]["data"]:
                    if "grand_total" in day:
                        attributes["human_readable_time"] = day["grand_total"].get(
                            "text", "0 mins"
                        )

        elif self.entity_description.key == "top_language":
            if (
                "stats" in self.coordinator.data
                and "data" in self.coordinator.data["stats"]
            ):
                languages = self.coordinator.data["stats"]["data"].get("languages", [])
                if languages and len(languages) > 1:
                    attributes["other_languages"] = [
                        {"name": lang.get("name"), "percent": lang.get("percent")}
                        for lang in languages[1:5]  # Include top 5 languages
                    ]

        elif self.entity_description.key == "top_project":
            if (
                "stats" in self.coordinator.data
                and "data" in self.coordinator.data["stats"]
            ):
                projects = self.coordinator.data["stats"]["data"].get("projects", [])
                if projects and len(projects) > 1:
                    attributes["other_projects"] = [
                        {"name": proj.get("name"), "percent": proj.get("percent")}
                        for proj in projects[1:5]  # Include top 5 projects
                    ]

        return attributes
