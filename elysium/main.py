
import argparse
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.settings import ROOT_DIR, load_yaml

from elysium.core.world_clock import WorldClock

from elysium.agents.citizen import Citizen
from elysium.agents.citizen_factory import CitizenFactory
from elysium.agents.citizen_registry import CitizenRegistry


console = Console()


# --------------------------------------------------
# DISPLAY WORLD INFORMATION
# --------------------------------------------------

def display_world(clock, config):

    calendar_config = config["calendar"]

    status = clock.get_status(
        days_per_month=calendar_config["days_per_month"],
        months_per_year=calendar_config["months_per_year"]
    )

    console.print(
        Panel(
            f"[bold cyan]PROJECT ELYSIUM[/bold cyan]\n"
            f"[white]Autonomous AI Civilization[/white]\n\n"
            f"[green]WORLD TIME: {status}[/green]\n"
            f"[yellow]CLOCK SPEED: {clock.time_scale}x[/yellow]\n"
            f"[yellow]STATUS: "
            f"{'PAUSED' if clock.paused else 'RUNNING'}[/yellow]",

            border_style="cyan"
        )
    )


# --------------------------------------------------
# DISPLAY CITIZEN REGISTRY
# --------------------------------------------------

def display_citizens(registry: CitizenRegistry):

    table = Table(
        title="ELYSIUM CITIZEN REGISTRY",
        border_style="cyan"
    )

    table.add_column("Citizen ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Age", justify="right")
    table.add_column("Occupation", style="yellow")
    table.add_column("Status", style="green")

    for citizen in registry.get_all():

        table.add_row(
            citizen.citizen_id,
            citizen.name,
            str(citizen.age),
            citizen.occupation,
            citizen.status
        )

    console.print(table)

    console.print(
        f"[bold green]TOTAL POPULATION: "
        f"{registry.population}[/bold green]"
    )


# --------------------------------------------------
# DISPLAY CITIZEN DETAILS
# --------------------------------------------------

def display_citizen(citizen: Citizen):

    if citizen is None:

        console.print(
            "[bold red]Citizen not found.[/bold red]"
        )

        return

    personality = citizen.personality
    needs = citizen.needs

    details = (
        f"[bold cyan]ID:[/bold cyan] {citizen.citizen_id}\n"
        f"[bold cyan]Name:[/bold cyan] {citizen.name}\n"
        f"[bold cyan]Age:[/bold cyan] {citizen.age}\n"
        f"[bold cyan]Occupation:[/bold cyan] {citizen.occupation}\n"
        f"[bold cyan]Status:[/bold cyan] {citizen.status}\n\n"

        f"[bold yellow]Biography[/bold yellow]\n"
        f"{citizen.biography}\n\n"

        f"[bold yellow]Personality[/bold yellow]\n"
        f"Curiosity: {personality.curiosity}\n"
        f"Creativity: {personality.creativity}\n"
        f"Sociability: {personality.sociability}\n"
        f"Discipline: {personality.discipline}\n"
        f"Confidence: {personality.confidence}\n"
        f"Empathy: {personality.empathy}\n\n"

        f"[bold yellow]Needs[/bold yellow]\n"
        f"Energy: {needs.energy}\n"
        f"Hunger: {needs.hunger}\n"
        f"Happiness: {needs.happiness}\n"
        f"Health: {needs.health}\n\n"

        f"[dim]Created: {citizen.created_at_world_time}[/dim]"
    )

    console.print(
        Panel(
            details,
            title=f"Citizen Profile: {citizen.name}",
            border_style="green"
        )
    )


# --------------------------------------------------
# INITIALIZE CITIZENS
# --------------------------------------------------

def initialize_citizens(clock, config, save_path):

    population_config = config["population"]

    initial_population = population_config["initial_population"]

    maximum_population = population_config["maximum_population"]

    if initial_population > maximum_population:

        raise ValueError(
            "Initial population exceeds maximum population"
        )

    registry = CitizenRegistry.load(
        save_path,
        maximum_population
    )

    # Create the initial population only once.
    if registry.population == 0:

        world_time = clock.get_status(
            config["calendar"]["days_per_month"],
            config["calendar"]["months_per_year"]
        )

        citizens = CitizenFactory.create_initial_population(
            count=initial_population,
            world_time=world_time
        )

        for citizen in citizens:

            registry.register(citizen)

        registry.save(save_path)

        console.print(
            "[bold green]Initial population created successfully.[/bold green]"
        )

    else:

        console.print(
            "[green]Existing citizen population restored.[/green]"
        )

    return registry


# --------------------------------------------------
# INITIALIZE ELYSIUM
# --------------------------------------------------

def initialize_elysium():

    config = load_yaml("simulation.yaml")

    world = config["world"]

    world_clock_path = ROOT_DIR / "data" / "world_clock.json"

    citizen_path = ROOT_DIR / "data" / "citizens.json"

    clock = WorldClock.from_config(
        config,
        world_clock_path
    )

    registry = initialize_citizens(
        clock,
        config,
        citizen_path
    )

    console.print()

    console.print(
        f"[bold cyan]{world['name']}[/bold cyan]"
    )

    console.print(
        f"Version: {world['version']}"
    )

    console.print(
        "[green]WorldClock initialized successfully.[/green]"
    )

    display_world(clock, config)

    display_citizens(registry)

    return (
        clock,
        registry,
        config,
        world_clock_path,
        citizen_path
    )


# --------------------------------------------------
# SAVE WORLD
# --------------------------------------------------

def save_world(clock, registry, world_clock_path, citizen_path):

    clock.save(world_clock_path)

    registry.save(citizen_path)


# --------------------------------------------------
# SIMULATION LOOP
# --------------------------------------------------

def run_simulation():

    parser = argparse.ArgumentParser(
        description="Project Elysium World Simulation"
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Initialize and display the world once"
    )

    parser.add_argument(
        "--pause",
        action="store_true",
        help="Pause the simulation"
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume the simulation"
    )

    parser.add_argument(
        "--speed",
        type=float,
        help="Set simulation speed"
    )

    parser.add_argument(
        "--citizens",
        action="store_true",
        help="Display all citizens"
    )

    parser.add_argument(
        "--citizen",
        type=str,
        help="Display a citizen by ID"
    )

    args = parser.parse_args()

    if args.pause and args.resume:

        parser.error(
            "--pause and --resume cannot be used together"
        )

    (
        clock,
        registry,
        config,
        world_clock_path,
        citizen_path
    ) = initialize_elysium()

    # ----------------------------------------------
    # PAUSE
    # ----------------------------------------------

    if args.pause:

        clock.pause()

        save_world(
            clock,
            registry,
            world_clock_path,
            citizen_path
        )

        display_world(clock, config)

        return

    # ----------------------------------------------
    # RESUME
    # ----------------------------------------------

    if args.resume:

        clock.resume()

        save_world(
            clock,
            registry,
            world_clock_path,
            citizen_path
        )

        display_world(clock, config)

    # ----------------------------------------------
    # SPEED
    # ----------------------------------------------

    if args.speed is not None:

        try:

            clock.set_speed(args.speed)

            clock.resume()

        except ValueError as error:

            console.print(
                f"[bold red]Error: {error}[/bold red]"
            )

            return

        save_world(
            clock,
            registry,
            world_clock_path,
            citizen_path
        )

        display_world(clock, config)

    # ----------------------------------------------
    # DISPLAY CITIZENS
    # ----------------------------------------------

    if args.citizens:

        display_citizens(registry)

        return

    # ----------------------------------------------
    # DISPLAY SINGLE CITIZEN
    # ----------------------------------------------

    if args.citizen:

        citizen = registry.get(args.citizen)

        display_citizen(citizen)

        return

    # ----------------------------------------------
    # INITIALIZATION TEST
    # ----------------------------------------------

    if args.once:

        console.print(
            "[bold green]ELYSIUM INITIALIZATION SUCCESSFUL[/bold green]"
        )

        return

    # ----------------------------------------------
    # SIMULATION LOOP
    # ----------------------------------------------

    autosave_interval = config["simulation"][
        "autosave_interval_seconds"
    ]

    last_save = time.monotonic()

    last_display = time.monotonic()

    console.print()

    console.print(
        "[bold green]ELYSIUM SIMULATION STARTED[/bold green]"
    )

    console.print(
        "[yellow]Press CTRL+C to stop the simulation.[/yellow]"
    )

    try:

        while True:

            clock.tick()

            current_time = time.monotonic()

            # AUTOSAVE
            if (
                config["system"]["autosave_enabled"]
                and current_time - last_save >= autosave_interval
            ):

                save_world(
                    clock,
                    registry,
                    world_clock_path,
                    citizen_path
                )

                last_save = time.monotonic()

            # DISPLAY WORLD STATUS
            if current_time - last_display >= 5:

                status = clock.get_status(
                    config["calendar"]["days_per_month"],
                    config["calendar"]["months_per_year"]
                )

                state = (
                    "PAUSED"
                    if clock.paused
                    else "RUNNING"
                )

                console.print(
                    f"[cyan]ELYSIUM TIME:[/cyan] "
                    f"{status} | "
                    f"POPULATION: {registry.population} | "
                    f"{state} | "
                    f"{clock.time_scale}x"
                )

                last_display = time.monotonic()

            time.sleep(1)

    except KeyboardInterrupt:

        console.print(
            "\n[yellow]Stopping Elysium...[/yellow]"
        )

        save_world(
            clock,
            registry,
            world_clock_path,
            citizen_path
        )

        console.print(
            "[bold green]World and citizen data saved.[/bold green]"
        )

        console.print(
            "[bold cyan]ELYSIUM SHUTDOWN COMPLETE[/bold cyan]"
        )


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":

    run_simulation()
