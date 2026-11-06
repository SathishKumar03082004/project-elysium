
from elysium.agents.citizen import (
    Citizen,
    Personality,
    Needs
)


class CitizenFactory:

    INITIAL_CITIZENS = [

        {
            "name": "Arin",
            "age": 25,
            "biography": "A curious researcher interested in science and discovery.",
            "occupation": "Researcher",
            "personality": {
                "curiosity": 90,
                "creativity": 80,
                "sociability": 45,
                "discipline": 70,
                "confidence": 75,
                "empathy": 65
            }
        },

        {
            "name": "Mira",
            "age": 28,
            "biography": "An engineer who enjoys designing practical solutions.",
            "occupation": "Engineer",
            "personality": {
                "curiosity": 75,
                "creativity": 85,
                "sociability": 60,
                "discipline": 90,
                "confidence": 80,
                "empathy": 55
            }
        },

        {
            "name": "Kiran",
            "age": 32,
            "biography": "A farmer who values nature and sustainable living.",
            "occupation": "Farmer",
            "personality": {
                "curiosity": 60,
                "creativity": 65,
                "sociability": 75,
                "discipline": 85,
                "confidence": 70,
                "empathy": 80
            }
        },

        {
            "name": "Elena",
            "age": 26,
            "biography": "A teacher who enjoys sharing knowledge.",
            "occupation": "Teacher",
            "personality": {
                "curiosity": 80,
                "creativity": 75,
                "sociability": 90,
                "discipline": 80,
                "confidence": 75,
                "empathy": 95
            }
        },

        {
            "name": "Noah",
            "age": 35,
            "biography": "A builder interested in architecture and construction.",
            "occupation": "Builder",
            "personality": {
                "curiosity": 65,
                "creativity": 70,
                "sociability": 55,
                "discipline": 95,
                "confidence": 85,
                "empathy": 60
            }
        },

        {
            "name": "Sara",
            "age": 30,
            "biography": "A doctor dedicated to improving people's well-being.",
            "occupation": "Doctor",
            "personality": {
                "curiosity": 85,
                "creativity": 65,
                "sociability": 80,
                "discipline": 95,
                "confidence": 85,
                "empathy": 95
            }
        },

        {
            "name": "Dev",
            "age": 23,
            "biography": "An artist who enjoys expressing ideas through creativity.",
            "occupation": "Artist",
            "personality": {
                "curiosity": 80,
                "creativity": 98,
                "sociability": 70,
                "discipline": 55,
                "confidence": 75,
                "empathy": 80
            }
        },

        {
            "name": "Lina",
            "age": 29,
            "biography": "A scientist fascinated by natural phenomena.",
            "occupation": "Scientist",
            "personality": {
                "curiosity": 95,
                "creativity": 85,
                "sociability": 55,
                "discipline": 90,
                "confidence": 80,
                "empathy": 70
            }
        },

        {
            "name": "Omar",
            "age": 34,
            "biography": "A merchant interested in trade and human relationships.",
            "occupation": "Merchant",
            "personality": {
                "curiosity": 70,
                "creativity": 75,
                "sociability": 95,
                "discipline": 80,
                "confidence": 90,
                "empathy": 75
            }
        },

        {
            "name": "Riya",
            "age": 24,
            "biography": "A writer who enjoys stories, history, and culture.",
            "occupation": "Writer",
            "personality": {
                "curiosity": 90,
                "creativity": 95,
                "sociability": 65,
                "discipline": 75,
                "confidence": 70,
                "empathy": 85
            }
        }
    ]

    @classmethod
    def create_initial_population(
        cls,
        count: int,
        world_time: str
    ) -> list[Citizen]:

        if count < 0:
            raise ValueError("Population count cannot be negative")

        if count > len(cls.INITIAL_CITIZENS):
            raise ValueError(
                "Not enough initial citizen profiles defined"
            )

        citizens = []

        for index, profile in enumerate(
            cls.INITIAL_CITIZENS[:count],
            start=1
        ):

            citizen = Citizen(
                citizen_id=f"CIT-{index:04d}",
                name=profile["name"],
                age=profile["age"],
                biography=profile["biography"],
                occupation=profile["occupation"],

                personality=Personality(
                    **profile["personality"]
                ),

                needs=Needs(),

                status="alive",

                created_at_world_time=world_time
            )

            citizens.append(citizen)

        return citizens
