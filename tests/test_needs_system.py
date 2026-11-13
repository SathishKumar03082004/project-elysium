from datetime import datetime, timedelta

import pytest

from elysium.agents.citizen import Citizen, Needs
from elysium.agents.citizen_registry import CitizenRegistry
from elysium.simulation.needs_system import NeedsSystem


def create_citizen():
    return Citizen(
        citizen_id="CIT-0001",
        name="Arin",
        age=25,
        biography="A curious researcher.",
        occupation="Researcher",
        needs=Needs()
    )


def test_passive_needs_progression():
    system = NeedsSystem()
    citizen = create_citizen()

    system.update_citizen(citizen, 2.0)

    assert citizen.needs.hunger == pytest.approx(4.0)
    assert citizen.needs.energy == pytest.approx(98.0)
    assert citizen.needs.social == pytest.approx(22.0)


def test_sleep_restores_energy():
    system = NeedsSystem()
    citizen = create_citizen()

    citizen.needs.energy = 40.0

    system.apply_activity(citizen, "sleep", 2.0)

    assert citizen.needs.energy == pytest.approx(80.0)


def test_eating_reduces_hunger():
    system = NeedsSystem()
    citizen = create_citizen()

    citizen.needs.hunger = 80.0

    system.apply_activity(citizen, "eat", 1.0)

    assert citizen.needs.hunger == pytest.approx(20.0)


def test_socializing_reduces_social_need():
    system = NeedsSystem()
    citizen = create_citizen()

    citizen.needs.social = 80.0

    system.apply_activity(citizen, "socialize", 1.0)

    assert citizen.needs.social == pytest.approx(30.0)


def test_needs_never_exceed_100():
    system = NeedsSystem()
    citizen = create_citizen()

    citizen.needs.energy = 95.0

    system.apply_activity(citizen, "sleep", 2.0)

    assert citizen.needs.energy == 100.0


def test_invalid_activity():
    system = NeedsSystem()
    citizen = create_citizen()

    with pytest.raises(ValueError):
        system.apply_activity(citizen, "flying", 1.0)


def test_advance_updates_registry():
    system = NeedsSystem()
    registry = CitizenRegistry(maximum_population=10)
    registry.register(create_citizen())

    start = datetime(1, 1, 1, 8, 0, 0)
    system.load_state(None, start)

    system.advance(
        registry,
        start + timedelta(hours=3)
    )

    citizen = registry.get("CIT-0001")

    assert citizen.needs.hunger == pytest.approx(6.0)
    assert citizen.needs.energy == pytest.approx(97.0)
    assert citizen.needs.social == pytest.approx(23.0)


def test_needs_state_save_and_restore(tmp_path):
    save_path = tmp_path / "needs_state.json"

    system = NeedsSystem()
    start = datetime(1, 1, 1, 8, 0, 0)

    system.load_state(None, start)
    system.save_state(save_path)

    restored_system = NeedsSystem()
    restored_system.load_state(
        save_path,
        start + timedelta(hours=5)
    )

    assert restored_system.last_update_simulation_time == start


def test_offline_progress_is_applied():
    system = NeedsSystem()
    registry = CitizenRegistry(maximum_population=10)
    registry.register(create_citizen())

    start = datetime(1, 1, 1, 8, 0, 0)
    system.load_state(None, start)

    # Simulate the world clock advancing while the app was closed.
    system.advance(
        registry,
        start + timedelta(hours=10)
    )

    citizen = registry.get("CIT-0001")

    assert citizen.needs.hunger == pytest.approx(20.0)
    assert citizen.needs.energy == pytest.approx(90.0)
    assert citizen.needs.social == pytest.approx(30.0)