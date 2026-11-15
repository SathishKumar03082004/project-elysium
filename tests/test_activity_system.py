from datetime import datetime

import pytest

from elysium.agents.citizen import Citizen, Needs
from elysium.agents.citizen_registry import CitizenRegistry
from elysium.simulation.activity_system import ActivitySystem
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


def test_low_energy_selects_sleep():
    activity_system = ActivitySystem()
    needs_system = NeedsSystem()

    registry = CitizenRegistry(maximum_population=10)
    citizen = create_citizen()
    citizen.needs.energy = 20

    registry.register(citizen)

    start = datetime(1, 1, 1, 23, 0)

    activity_system.advance(
        registry,
        3600,
        needs_system,
        start
    )

    assert citizen.current_activity == "sleep"
    assert citizen.needs.energy == pytest.approx(40.0)


def test_high_hunger_selects_eating():
    activity_system = ActivitySystem()
    needs_system = NeedsSystem()

    registry = CitizenRegistry(maximum_population=10)
    citizen = create_citizen()
    citizen.needs.hunger = 80

    registry.register(citizen)

    start = datetime(1, 1, 1, 10, 0)

    activity_system.advance(
        registry,
        1800,
        needs_system,
        start
    )

    assert citizen.current_activity == "eat"
    assert citizen.needs.hunger == pytest.approx(20.0)


def test_high_social_need_selects_socializing():
    activity_system = ActivitySystem()
    needs_system = NeedsSystem()

    registry = CitizenRegistry(maximum_population=10)
    citizen = create_citizen()
    citizen.needs.social = 80

    registry.register(citizen)

    start = datetime(1, 1, 1, 20, 0)

    activity_system.advance(
        registry,
        3600,
        needs_system,
        start
    )

    assert citizen.current_activity == "socialize"
    assert citizen.needs.social == pytest.approx(30.0)


def test_work_is_selected_during_working_hours():
    activity_system = ActivitySystem()
    needs_system = NeedsSystem()

    registry = CitizenRegistry(maximum_population=10)
    citizen = create_citizen()

    registry.register(citizen)

    start = datetime(1, 1, 1, 9, 0)

    activity_system.advance(
        registry,
        3600,
        needs_system,
        start
    )

    assert citizen.current_activity == "work"
    assert citizen.activity_remaining_hours == pytest.approx(3.0)


def test_manual_activity_assignment():
    activity_system = ActivitySystem()
    citizen = create_citizen()

    activity_system.start_activity(
        citizen,
        "sleep",
        5
    )

    assert citizen.current_activity == "sleep"
    assert citizen.activity_remaining_hours == 5.0


def test_invalid_activity_rejected():
    activity_system = ActivitySystem()
    citizen = create_citizen()

    with pytest.raises(ValueError):
        activity_system.start_activity(
            citizen,
            "flying",
            2
        )


def test_activity_state_persists():
    citizen = create_citizen()

    citizen.current_activity = "work"
    citizen.activity_remaining_hours = 2.5

    restored = Citizen.from_dict(citizen.to_dict())

    assert restored.current_activity == "work"
    assert restored.activity_remaining_hours == 2.5