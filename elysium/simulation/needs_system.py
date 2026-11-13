import json
from datetime import datetime
from pathlib import Path

from elysium.agents.citizen_registry import CitizenRegistry


class NeedsSystem:
    # Passive changes per simulation hour.
    HUNGER_INCREASE = 2.0
    ENERGY_DECREASE = 1.0
    SOCIAL_INCREASE = 1.0

    ACTIVITY_EFFECTS = {
        "idle": {
            "energy": -1.0,
            "hunger": 2.0,
            "happiness": 0.0,
            "social": 1.0,
            "comfort": 0.0,
        },
        "sleep": {
            "energy": 20.0,
            "hunger": 1.0,
            "happiness": 0.2,
            "social": 0.5,
            "comfort": 1.0,
        },
        "eat": {
            "energy": 1.0,
            "hunger": -60.0,
            "happiness": 2.0,
            "social": 0.0,
            "comfort": 2.0,
        },
        "work": {
            "energy": -10.0,
            "hunger": 3.0,
            "happiness": -0.5,
            "social": 1.0,
            "comfort": -0.5,
        },
        "socialize": {
            "energy": -2.0,
            "hunger": 2.0,
            "happiness": 5.0,
            "social": -50.0,
            "comfort": 1.0,
        },
    }

    def __init__(self):
        self.last_update_simulation_time = None

    @staticmethod
    def clamp(value):
        return max(0.0, min(100.0, value))

    def update_citizen(self, citizen, elapsed_hours):
        """Apply passive idle changes over simulation time."""

        if elapsed_hours <= 0:
            return

        needs = citizen.needs

        needs.hunger = self.clamp(
            needs.hunger + self.HUNGER_INCREASE * elapsed_hours
        )

        needs.energy = self.clamp(
            needs.energy - self.ENERGY_DECREASE * elapsed_hours
        )

        needs.social = self.clamp(
            needs.social + self.SOCIAL_INCREASE * elapsed_hours
        )

        # Happiness is affected by unmet needs.
        happiness_change = 0.0

        if needs.hunger >= 80:
            happiness_change -= 1.0

        if needs.energy <= 15:
            happiness_change -= 1.0

        if needs.social >= 80:
            happiness_change -= 0.5

        if needs.comfort <= 20:
            happiness_change -= 0.5

        if (
            needs.hunger < 40
            and needs.energy > 60
            and needs.social < 40
            and needs.comfort > 60
        ):
            happiness_change += 0.2

        needs.happiness = self.clamp(
            needs.happiness + happiness_change * elapsed_hours
        )

        # Health is affected when critical needs remain unmet.
        critical = (
            needs.hunger >= 90
            or needs.energy <= 5
            or needs.comfort <= 5
        )

        if critical:
            needs.health = self.clamp(
                needs.health - 2.0 * elapsed_hours
            )
        elif (
            needs.hunger < 50
            and needs.energy > 50
            and needs.comfort > 40
        ):
            needs.health = self.clamp(
                needs.health + 0.1 * elapsed_hours
            )

    def advance(self, registry, current_simulation_time):
        """
        Update all citizens from the last recorded simulation time.

        This also handles time that passed while the application
        was closed, provided the world clock advanced offline.
        """

        if self.last_update_simulation_time is None:
            self.last_update_simulation_time = current_simulation_time
            return

        elapsed_seconds = (
            current_simulation_time - self.last_update_simulation_time
        ).total_seconds()

        if elapsed_seconds <= 0:
            return

        elapsed_hours = elapsed_seconds / 3600.0

        for citizen in registry.get_all():
            if citizen.status == "alive":
                self.update_citizen(citizen, elapsed_hours)

        self.last_update_simulation_time = current_simulation_time

    def apply_activity(self, citizen, activity, duration_hours):
        """Apply a manually selected activity to one citizen."""

        activity = activity.lower().strip()

        if activity not in self.ACTIVITY_EFFECTS:
            raise ValueError(
                f"Unknown activity: {activity}. "
                f"Available activities: {', '.join(self.ACTIVITY_EFFECTS)}"
            )

        if duration_hours <= 0:
            raise ValueError("Activity duration must be greater than zero.")

        if citizen.status != "alive":
            raise ValueError("Cannot apply an activity to a non-living citizen.")

        effects = self.ACTIVITY_EFFECTS[activity]
        needs = citizen.needs

        for need_name, rate in effects.items():
            current_value = getattr(needs, need_name)
            updated_value = current_value + rate * duration_hours

            setattr(
                needs,
                need_name,
                self.clamp(updated_value)
            )

        # Activities can influence health and happiness indirectly.
        if activity == "sleep" and needs.energy >= 50:
            needs.health = self.clamp(
                needs.health + 0.1 * duration_hours
            )

        if activity == "eat" and needs.hunger < 30:
            needs.happiness = self.clamp(
                needs.happiness + 0.5 * duration_hours
            )

    def save_state(self, file_path):
        """Persist the last needs update time."""

        if self.last_update_simulation_time is None:
            return

        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "last_update_simulation_time":
                self.last_update_simulation_time.isoformat()
        }

        temporary_path = file_path.with_suffix(".tmp")

        with open(temporary_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        temporary_path.replace(file_path)

    def load_state(self, file_path, current_simulation_time):
        """Restore the last needs update time."""

        if file_path is None:
            self.last_update_simulation_time = current_simulation_time
            return

        file_path = Path(file_path)

        if not file_path.exists():
            self.last_update_simulation_time = current_simulation_time
            return

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        saved_time = data.get("last_update_simulation_time")

        if not saved_time:
            self.last_update_simulation_time = current_simulation_time
            return

        self.last_update_simulation_time = datetime.fromisoformat(
            saved_time
        )