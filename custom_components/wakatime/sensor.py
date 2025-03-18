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
    ICON_ACTIVE_TIME,
    ICON_CATEGORY,
    ICON_CODING,
    ICON_EDITOR,
    ICON_LANGUAGE,
    ICON_OPERATING_SYSTEM,
    ICON_PRODUCTIVITY,
    ICON_PROJECT,
    ICON_STREAK,
    ICON_WEEKLY,
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
    # New sensor types
    SensorEntityDescription(
        key="top_category",
        translation_key="top_category",
        icon=ICON_CATEGORY,
    ),
    SensorEntityDescription(
        key="weekly_average",
        translation_key="weekly_average",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_WEEKLY,
    ),
    SensorEntityDescription(
        key="productivity_level",
        translation_key="productivity_level",
        icon=ICON_PRODUCTIVITY,
    ),
    SensorEntityDescription(
        key="most_active_time",
        translation_key="most_active_time",
        icon=ICON_ACTIVE_TIME,
    ),
    SensorEntityDescription(
        key="current_streak",
        translation_key="current_streak",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="days",
        icon=ICON_STREAK,
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

        # New sensor implementations
        if self.entity_description.key == "top_category":
            if (
                "stats" in self.coordinator.data
                and "data" in self.coordinator.data["stats"]
            ):
                categories = self.coordinator.data["stats"]["data"].get(
                    "categories", []
                )
                if categories:
                    return categories[0].get("name", "Unknown")
            return "Unknown"

        if self.entity_description.key == "weekly_average":
            if (
                "last_7_days" in self.coordinator.data
                and "data" in self.coordinator.data["last_7_days"]
            ):
                days = self.coordinator.data["last_7_days"]["data"]
                if days:
                    total_seconds = sum(
                        day["grand_total"].get("total_seconds", 0)
                        for day in days
                        if "grand_total" in day
                    )
                    return int(total_seconds / 7)  # Average per day
            return 0

        if self.entity_description.key == "productivity_level":
            if (
                "all_time" in self.coordinator.data
                and "data" in self.coordinator.data["all_time"]
            ):
                daily_avg = self.coordinator.data["all_time"]["data"].get(
                    "daily_average", 0
                )
                if daily_avg:
                    # Determine productivity level based on daily average coding time
                    if daily_avg > 14400:  # More than 4 hours
                        return "High"
                    if daily_avg > 7200:  # More than 2 hours
                        return "Medium"
                    return "Low"
            return "Unknown"

        if self.entity_description.key == "most_active_time":
            if (
                "stats" in self.coordinator.data
                and "data" in self.coordinator.data["stats"]
            ):
                best_hour = (
                    self.coordinator.data["stats"]["data"]
                    .get("best_day", {})
                    .get("time", "")
                )
                return best_hour or "Unknown"
            return "Unknown"

        if self.entity_description.key == "current_streak":
            if (
                "all_time" in self.coordinator.data
                and "data" in self.coordinator.data["all_time"]
            ):
                current_streak = self.coordinator.data["all_time"]["data"].get(
                    "current_streak", 0
                )
                return current_streak
            return 0

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

        # Add attributes for the new sensors
        elif self.entity_description.key == "weekly_average":
            if (
                "last_7_days" in self.coordinator.data
                and "data" in self.coordinator.data["last_7_days"]
            ):
                days = self.coordinator.data["last_7_days"]["data"]
                if days:
                    total_seconds = sum(
                        day["grand_total"].get("total_seconds", 0)
                        for day in days
                        if "grand_total" in day
                    )
                    attributes["human_readable_time"] = (
                        f"{int(total_seconds / 7 / 60)} mins"
                    )
                    attributes["days_with_activity"] = len(
                        [
                            day
                            for day in days
                            if day.get("grand_total", {}).get("total_seconds", 0) > 0
                        ]
                    )

        elif self.entity_description.key == "current_streak":
            if (
                "all_time" in self.coordinator.data
                and "data" in self.coordinator.data["all_time"]
            ):
                all_time = self.coordinator.data["all_time"]["data"]
                attributes["best_streak"] = all_time.get("best_streak", 0)
                attributes["best_streak_range"] = all_time.get("best_streak_range", [])

        return attributes
