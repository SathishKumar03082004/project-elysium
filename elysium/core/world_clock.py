
import json
import time

from datetime import datetime, timedelta, timezone
from pathlib import Path


class WorldClock:

    def __init__(
        self,
        simulation_time: datetime,
        time_scale: float = 60,
        paused: bool = False,
        saved_at: datetime | None = None
    ):

        if time_scale <= 0:
            raise ValueError("Time scale must be greater than zero")

        self.simulation_time = simulation_time
        self.time_scale = float(time_scale)
        self.paused = paused

        self.last_monotonic = time.monotonic()
        self.saved_at = saved_at or datetime.now(timezone.utc)

    # --------------------------------------------------
    # LOAD WORLD CLOCK
    # --------------------------------------------------

    @classmethod
    def from_config(cls, config: dict, save_path: Path):

        simulation = config["simulation"]

        save_path.parent.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)

        if save_path.exists():

            with open(save_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            simulation_time = datetime.fromisoformat(
                data["simulation_time"]
            )

            time_scale = float(data["time_scale"])
            paused = bool(data["paused"])

            saved_at = datetime.fromisoformat(data["saved_at"])

            # Offline progression
            if not paused and simulation["allow_offline_progress"]:

                elapsed = max(
                    0,
                    (now - saved_at).total_seconds()
                )

                simulation_time += timedelta(
                    seconds=elapsed * time_scale
                )

            return cls(
                simulation_time=simulation_time,
                time_scale=time_scale,
                paused=paused,
                saved_at=now
            )

        # First world initialization
        start_time = datetime.fromisoformat(
            simulation["start_datetime"]
        )

        return cls(
            simulation_time=start_time,
            time_scale=simulation["time_scale"],
            paused=not simulation["enabled"],
            saved_at=now
        )

    # --------------------------------------------------
    # UPDATE WORLD CLOCK
    # --------------------------------------------------

    def tick(self):

        current_monotonic = time.monotonic()

        elapsed_real = current_monotonic - self.last_monotonic

        if not self.paused:

            elapsed_simulation = elapsed_real * self.time_scale

            self.simulation_time += timedelta(
                seconds=elapsed_simulation
            )

        self.last_monotonic = current_monotonic

        return self.simulation_time

    # --------------------------------------------------
    # PAUSE SIMULATION
    # --------------------------------------------------

    def pause(self):

        if not self.paused:

            self.tick()
            self.paused = True

            print("[CLOCK] Simulation paused.")

    # --------------------------------------------------
    # RESUME SIMULATION
    # --------------------------------------------------

    def resume(self):

        if self.paused:

            self.last_monotonic = time.monotonic()

            self.paused = False

            print("[CLOCK] Simulation resumed.")

    # --------------------------------------------------
    # CHANGE SIMULATION SPEED
    # --------------------------------------------------

    def set_speed(self, new_speed: float):

        if new_speed <= 0:

            raise ValueError(
                "Simulation speed must be greater than zero."
            )

        self.tick()

        self.time_scale = float(new_speed)

        print(
            f"[CLOCK] Simulation speed changed to {new_speed}x."
        )

    # --------------------------------------------------
    # CUSTOM CALENDAR
    # --------------------------------------------------

    def get_calendar(
        self,
        days_per_month=30,
        months_per_year=12
    ):

        self.tick()

        elapsed_days = (
            self.simulation_time.date()
            - datetime(1, 1, 1).date()
        ).days

        absolute_day = elapsed_days + 1

        days_per_year = days_per_month * months_per_year

        year = (absolute_day - 1) // days_per_year + 1

        day_of_year = (absolute_day - 1) % days_per_year

        month = day_of_year // days_per_month + 1

        day = day_of_year % days_per_month + 1

        return {
            "year": year,
            "month": month,
            "day": day,
            "hour": self.simulation_time.hour,
            "minute": self.simulation_time.minute,
            "second": self.simulation_time.second
        }

    # --------------------------------------------------
    # DISPLAY WORLD TIME
    # --------------------------------------------------

    def get_status(
        self,
        days_per_month=30,
        months_per_year=12
    ):

        calendar = self.get_calendar(
            days_per_month,
            months_per_year
        )

        return (
            f"Year {calendar['year']:02d} | "
            f"Month {calendar['month']:02d} | "
            f"Day {calendar['day']:02d} | "
            f"{calendar['hour']:02d}:"
            f"{calendar['minute']:02d}:"
            f"{calendar['second']:02d}"
        )

    # --------------------------------------------------
    # SAVE WORLD CLOCK
    # --------------------------------------------------

    def save(self, save_path: Path):

        self.tick()

        save_path.parent.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)

        data = {
            "simulation_time": self.simulation_time.isoformat(),
            "time_scale": self.time_scale,
            "paused": self.paused,
            "saved_at": now.isoformat()
        }

        temporary_path = save_path.with_suffix(".tmp")

        with open(temporary_path, "w", encoding="utf-8") as file:

            json.dump(data, file, indent=4)

        temporary_path.replace(save_path)

        self.saved_at = now

        print("[CLOCK] World time saved successfully.")
