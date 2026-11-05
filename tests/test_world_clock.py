
from datetime import datetime, timedelta

from elysium.core.world_clock import WorldClock


def test_clock_initialization():

    clock = WorldClock(
        simulation_time=datetime(1, 1, 1, 8, 0),
        time_scale=60
    )

    assert clock.time_scale == 60

    assert clock.simulation_time.hour == 8

    assert clock.paused is False


def test_clock_advances(monkeypatch):

    values = iter([100.0, 102.0])

    monkeypatch.setattr(
        "elysium.core.world_clock.time.monotonic",
        lambda: next(values)
    )

    clock = WorldClock(
        simulation_time=datetime(1, 1, 1, 8, 0),
        time_scale=60
    )

    clock.tick()

    expected = datetime(1, 1, 1, 8, 0) + timedelta(
        seconds=120
    )

    assert clock.simulation_time == expected


def test_pause_prevents_advancement(monkeypatch):

    values = iter([100.0, 101.0, 110.0])

    monkeypatch.setattr(
        "elysium.core.world_clock.time.monotonic",
        lambda: next(values)
    )

    clock = WorldClock(
        simulation_time=datetime(1, 1, 1, 8, 0),
        time_scale=60
    )

    clock.pause()

    paused_time = clock.simulation_time

    clock.tick()

    assert clock.simulation_time == paused_time

    assert clock.paused is True


def test_calendar_progression():

    clock = WorldClock(
        simulation_time=datetime(1, 1, 1, 8, 0),
        time_scale=60
    )

    # Move forward by 30 simulation days
    clock.simulation_time += timedelta(days=30)

    calendar = clock.get_calendar(
        days_per_month=30,
        months_per_year=12
    )

    assert calendar["day"] == 1

    assert calendar["month"] == 2

    assert calendar["year"] == 1


def test_clock_save_and_restore(tmp_path):

    save_path = tmp_path / "world_clock.json"

    config = {
        "simulation": {
            "start_datetime": "0001-01-01T08:00:00",
            "time_scale": 60,
            "enabled": True,
            "allow_offline_progress": True
        }
    }

    clock = WorldClock(
        simulation_time=datetime(1, 1, 1, 12, 0),
        time_scale=60,
        paused=True
    )

    clock.save(save_path)

    restored_clock = WorldClock.from_config(
        config,
        save_path
    )

    assert restored_clock.simulation_time == datetime(
        1, 1, 1, 12, 0
    )

    assert restored_clock.paused is True
