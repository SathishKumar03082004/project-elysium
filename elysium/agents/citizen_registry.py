
import json

from pathlib import Path

from elysium.agents.citizen import Citizen


class CitizenRegistry:

    def __init__(self, maximum_population: int = 100):

        if maximum_population < 0:
            raise ValueError(
                "Maximum population cannot be negative"
            )

        self.maximum_population = maximum_population

        self.citizens: dict[str, Citizen] = {}

    # --------------------------------------------------
    # REGISTER CITIZEN
    # --------------------------------------------------

    def register(self, citizen: Citizen):

        if citizen.citizen_id in self.citizens:

            raise ValueError(
                f"Citizen {citizen.citizen_id} already exists"
            )

        if len(self.citizens) >= self.maximum_population:

            raise ValueError(
                "Maximum population limit reached"
            )

        self.citizens[citizen.citizen_id] = citizen

    # --------------------------------------------------
    # GET CITIZEN
    # --------------------------------------------------

    def get(self, citizen_id: str) -> Citizen | None:

        return self.citizens.get(citizen_id)

    # --------------------------------------------------
    # GET ALL CITIZENS
    # --------------------------------------------------

    def get_all(self) -> list[Citizen]:

        return list(self.citizens.values())

    # --------------------------------------------------
    # POPULATION COUNT
    # --------------------------------------------------

    @property
    def population(self) -> int:

        return len(self.citizens)

    # --------------------------------------------------
    # SAVE CITIZENS
    # --------------------------------------------------

    def save(self, file_path: Path):

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = {
            "population": self.population,
            "maximum_population": self.maximum_population,
            "citizens": [
                citizen.to_dict()
                for citizen in self.get_all()
            ]
        }

        temporary_path = file_path.with_suffix(".tmp")

        with open(
            temporary_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        temporary_path.replace(file_path)

        print("[CITIZENS] Citizen data saved successfully.")

    # --------------------------------------------------
    # LOAD CITIZENS
    # --------------------------------------------------

    @classmethod
    def load(
        cls,
        file_path: Path,
        maximum_population: int = 100
    ):

        registry = cls(maximum_population)

        if not file_path.exists():

            return registry

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(data.get("citizens"), list):
            raise ValueError("Invalid citizen registry file")

        saved_maximum = data.get(
            "maximum_population",
            maximum_population
        )

        if len(data["citizens"]) > maximum_population:
            raise ValueError(
                "Saved population exceeds configured maximum"
            )

        for citizen_data in data["citizens"]:

            citizen = Citizen.from_dict(citizen_data)

            registry.register(citizen)

        print(
            f"[CITIZENS] Loaded {registry.population} citizens."
        )

        return registry
