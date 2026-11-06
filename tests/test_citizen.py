
import pytest

from elysium.agents.citizen import (
    Citizen,
    Personality,
    Needs
)

from elysium.agents.citizen_factory import CitizenFactory

from elysium.agents.citizen_registry import CitizenRegistry


def create_test_citizen():

    return Citizen(
        citizen_id="CIT-0001",
        name="Arin",
        age=25,
        biography="A curious researcher.",
        occupation="Researcher",
        personality=Personality(),
        needs=Needs()
    )


def test_citizen_creation():

    citizen = create_test_citizen()

    assert citizen.citizen_id == "CIT-0001"
    assert citizen.name == "Arin"
    assert citizen.age == 25
    assert citizen.occupation == "Researcher"
    assert citizen.status == "alive"


def test_personality_validation():

    with pytest.raises(ValueError):

        Personality(curiosity=150)


def test_needs_validation():

    with pytest.raises(ValueError):

        Needs(energy=-10)


def test_initial_population_creation():

    citizens = CitizenFactory.create_initial_population(
        count=10,
        world_time="Year 01 | Month 01 | Day 01"
    )

    assert len(citizens) == 10

    ids = [citizen.citizen_id for citizen in citizens]

    assert len(ids) == len(set(ids))

    assert citizens[0].name == "Arin"


def test_register_citizen():

    registry = CitizenRegistry(maximum_population=10)

    citizen = create_test_citizen()

    registry.register(citizen)

    assert registry.population == 1

    assert registry.get("CIT-0001").name == "Arin"


def test_duplicate_citizen_rejected():

    registry = CitizenRegistry(maximum_population=10)

    registry.register(create_test_citizen())

    with pytest.raises(ValueError):

        registry.register(create_test_citizen())


def test_maximum_population():

    registry = CitizenRegistry(maximum_population=1)

    registry.register(create_test_citizen())

    second_citizen = Citizen(
        citizen_id="CIT-0002",
        name="Mira",
        age=28,
        biography="An engineer.",
        occupation="Engineer"
    )

    with pytest.raises(ValueError):

        registry.register(second_citizen)


def test_citizen_save_and_restore(tmp_path):

    save_path = tmp_path / "citizens.json"

    registry = CitizenRegistry(maximum_population=10)

    registry.register(create_test_citizen())

    registry.save(save_path)

    restored_registry = CitizenRegistry.load(
        save_path,
        maximum_population=10
    )

    assert restored_registry.population == 1

    restored_citizen = restored_registry.get("CIT-0001")

    assert restored_citizen.name == "Arin"

    assert restored_citizen.personality.curiosity == 50

    assert restored_citizen.needs.health == 100
