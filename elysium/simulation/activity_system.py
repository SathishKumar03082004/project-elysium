from datetime import timedelta


class ActivitySystem:

    ACTIVITIES = {
        "idle": 1.0,
        "sleep": 8.0,
        "eat": 0.5,
        "work": 4.0,
        "socialize": 1.0,
    }

    def __init__(self):
        self.max_transitions_per_update = 1000

    def can_perform(self, citizen, activity):
        """Check whether a citizen can perform an activity."""

        if citizen.status != "alive":
            return False

        if activity not in self.ACTIVITIES:
            return False

        needs = citizen.needs

        if activity == "eat":
            return needs.hunger >= 10

        if activity == "sleep":
            return needs.energy < 95

        if activity == "work":
            return (
                needs.energy > 15
                and needs.hunger < 90
                and needs.health > 20
            )

        if activity == "socialize":
            return needs.social >= 10

        return True

    def start_activity(
        self,
        citizen,
        activity,
        duration_hours=None
    ):
        """Start or manually assign an activity."""

        activity = activity.lower().strip()

        if activity not in self.ACTIVITIES:
            raise ValueError(
                f"Unknown activity: {activity}"
            )

        if citizen.status != "alive":
            raise ValueError(
                "Cannot assign an activity to a non-living citizen."
            )

        if not self.can_perform(citizen, activity):
            raise ValueError(
                f"{citizen.name} cannot perform {activity} right now."
            )

        duration = (
            self.ACTIVITIES[activity]
            if duration_hours is None
            else duration_hours
        )

        if duration <= 0:
            raise ValueError(
                "Activity duration must be greater than zero."
            )

        citizen.current_activity = activity
        citizen.activity_remaining_hours = float(duration)

    def choose_next_activity(self, citizen, world_time):
        """
        Choose an activity based on needs and world time.

        Priority:
        1. Eat when very hungry.
        2. Sleep when exhausted.
        3. Socialize when isolated.
        4. Work during working hours.
        5. Idle otherwise.
        """

        needs = citizen.needs

        if needs.hunger >= 65 and self.can_perform(citizen, "eat"):
            return "eat"

        if needs.energy <= 30 and self.can_perform(citizen, "sleep"):
            return "sleep"

        if needs.social >= 70 and self.can_perform(citizen, "socialize"):
            return "socialize"

        # Normal working hours: 08:00 to 17:00.
        if (
            8 <= world_time.hour < 17
            and self.can_perform(citizen, "work")
        ):
            return "work"

        # At night, prioritize sleep if energy is not high.
        if (
            world_time.hour >= 22 or world_time.hour < 6
        ) and needs.energy < 90:
            return "sleep"

        return "idle"

    def get_activity_duration(self, activity, world_time):
        """Get the duration of an activity."""

        duration = self.ACTIVITIES[activity]

        # Don't schedule work beyond the normal workday.
        if activity == "work":
            remaining_workday = 17.0 - (
                world_time.hour + world_time.minute / 60.0
            )

            duration = min(duration, remaining_workday)

        # Avoid zero-duration work near the end of the day.
        if duration <= 0:
            return 1.0

        return duration

    def advance(
        self,
        registry,
        elapsed_seconds,
        needs_system,
        start_simulation_time
    ):
        """
        Advance every citizen's activity by elapsed simulation time.

        Activity effects are applied in small segments so citizens
        can automatically switch activities during a long update.
        """

        if elapsed_seconds <= 0:
            return

        remaining_world_hours = elapsed_seconds / 3600.0
        world_time = start_simulation_time

        for citizen in registry.get_all():

            if citizen.status != "alive":
                continue

            remaining = remaining_world_hours
            transitions = 0

            while remaining > 1e-9:

                if transitions >= self.max_transitions_per_update:
                    raise RuntimeError(
                        f"Too many activity transitions for "
                        f"{citizen.citizen_id}"
                    )

                # Start a new activity when the previous one finishes.
                if citizen.activity_remaining_hours <= 1e-9:

                    next_activity = self.choose_next_activity(
                        citizen,
                        world_time
                    )

                    duration = self.get_activity_duration(
                        next_activity,
                        world_time
                    )

                    self.start_activity(
                        citizen,
                        next_activity,
                        duration
                    )

                    transitions += 1

                segment_hours = min(
                    remaining,
                    citizen.activity_remaining_hours
                )

                # Apply Day 4 needs effects.
                needs_system.apply_activity(
                    citizen,
                    citizen.current_activity,
                    segment_hours
                )

                citizen.activity_remaining_hours -= segment_hours
                remaining -= segment_hours

                world_time += timedelta(hours=segment_hours)

    def get_activity_report(self, registry):
        """Return current activity information for all citizens."""

        report = []

        for citizen in registry.get_all():
            report.append({
                "citizen_id": citizen.citizen_id,
                "name": citizen.name,
                "occupation": citizen.occupation,
                "activity": citizen.current_activity,
                "remaining_hours": citizen.activity_remaining_hours,
            })

        return report