
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Personality:
    curiosity: int = 50
    creativity: int = 50
    sociability: int = 50
    discipline: int = 50
    confidence: int = 50
    empathy: int = 50

    def __post_init__(self):
        for trait, value in asdict(self).items():
            if not 0 <= value <= 100:
                raise ValueError(
                    f"{trait} must be between 0 and 100"
                )


@dataclass
class Needs:
    energy: float = 100.0
    hunger: float = 0.0
    happiness: float = 75.0
    health: float = 100.0
    social: float = 20.0
    comfort: float = 80.0

    def __post_init__(self):
        for need, value in asdict(self).items():
            if not 0 <= value <= 100:
                raise ValueError(
                    f"{need} must be between 0 and 100"
                )


@dataclass
class Citizen:

    citizen_id: str
    name: str
    age: int
    biography: str
    occupation: str

    personality: Personality = field(
        default_factory=Personality
    )

    needs: Needs = field(
        default_factory=Needs
    )

    status: str = "alive"

    created_at_world_time: str = "Year 01 | Month 01 | Day 01"

    current_activity: str = "idle"
    activity_remaining_hours: float = 0.0

    def __post_init__(self):

        if not self.citizen_id:
            raise ValueError("Citizen ID cannot be empty")

        if not self.name.strip():
            raise ValueError("Citizen name cannot be empty")

        if self.age <= 0:
            raise ValueError("Citizen age must be positive")

        if not self.current_activity.strip():
            raise ValueError("Current activity cannot be empty")

        if self.activity_remaining_hours < 0:
            raise ValueError("Activity remaining hours cannot be negative")


    def to_dict(self) -> dict[str, Any]:

        return {
            "citizen_id": self.citizen_id,
            "name": self.name,
            "age": self.age,
            "biography": self.biography,
            "occupation": self.occupation,
            "personality": asdict(self.personality),
            "needs": asdict(self.needs),
            "status": self.status,
            "created_at_world_time": self.created_at_world_time,
            "current_activity": self.current_activity,
            "activity_remaining_hours": self.activity_remaining_hours
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):

        return cls(
            citizen_id=data["citizen_id"],
            name=data["name"],
            age=data["age"],
            biography=data["biography"],
            occupation=data["occupation"],

            personality=Personality(
                **data.get("personality", {})
            ),

            needs=Needs(
                **data.get("needs", {})
            ),

            status=data.get("status", "alive"),

            created_at_world_time=data.get(
                "created_at_world_time",
                "Year 01 | Month 01 | Day 01"
            ),

            current_activity=data.get("current_activity", "idle"),
            activity_remaining_hours=data.get("activity_remaining_hours", 0.0)
        )
