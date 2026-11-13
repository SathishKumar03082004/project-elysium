import argparse
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.settings import ROOT_DIR, load_yaml
from elysium.core.world_clock import WorldClock
from elysium.agents.citizen_factory import CitizenFactory
from elysium.agents.citizen_registry import CitizenRegistry
from elysium.simulation.needs_system import NeedsSystem


console = Console()

WORLD_CLOCK_PATH = ROOT_DIR / "data" / "world_clock.json"
CITIZEN_PATH = ROOT_DIR / "data" / "citizens.json"
NEEDS_STATE_PATH = ROOT_DIR / "data" / "needs_state.json"


def display_world(clock, config):
    table = Table(title="Project Elysium - World Status")

    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("World", config["world"]["name"])
    table.add_row("Version", config["world"]["version"])
    table.add_row("Simulation Time", clock.simulation_time.isoformat())
    table.add_row("Time Scale", f"{clock.time_scale}x")
    table.add_row("Status", "Paused" if clock.paused else "Running")

    console.print(table)


def display_citizens(registry):
    table = Table(title="Elysium Citizens")

    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Age")
    table.add_column("Occupation")
    table.add_column("Status")

    for citizen in registry.get_all():
        table.add_row(
            citizen.citizen_id,
            citizen.name,
            str(citizen.age),
            citizen.occupation,
            citizen.status
        )

    console.print(table)


def display_needs(citizen):
    needs = citizen.needs

    table = Table(title=f"{citizen.name} - Needs")

    table.add_column("Need", style="cyan")
    table.add_column("Value", justify="right")
    table.add_column("Condition")

    need_data = [
        ("Energy", needs.energy, "High is good"),
        ("Hunger", needs.hunger, "High is bad"),
        ("Happiness", needs.happiness, "High is good"),
        ("Health", needs.health, "High is good"),
        ("Social", needs.social, "High is bad"),
        ("Comfort", needs.comfort, "High is good"),
    ]

    for name, value, description in need_data:
        table.add_row(
            name,
            f"{value:.1f}/100",
            description
        )

    console.print(table)


def display_citizen(citizen):
    console.print(
        Panel(
            f"""
[cyan]ID:[/cyan] {citizen.citizen_id}
[cyan]Name:[/cyan] {citizen.name}
[cyan]Age:[/cyan] {citizen.age}
[cyan]Occupation:[/cyan] {citizen.occupation}
[cyan]Status:[/cyan] {citizen.status}

[cyan]Biography:[/cyan]
{citizen.biography}
            """,
            title="Citizen Information"
        )
    )

    display_needs(citizen)


def initialize_citizens(clock, config):
    maximum_population = config["population"]["maximum_population"]

    registry = CitizenRegistry(
        maximum_population=maximum_population
    )

    if CITIZEN_PATH.exists():
        registry = CitizenRegistry.load(
            CITIZEN_PATH,
            maximum_population=maximum_population
        )

    if registry.population == 0:
        initial_count = config["population"]["initial_population"]

        citizens = CitizenFactory.create_initial_population(
            count=initial_count,
            world_time=clock.simulation_time.isoformat()
        )

        for citizen in citizens:
            registry.register(citizen)

        registry.save(CITIZEN_PATH)

    return registry


def save_world(clock, registry, needs_system):
    # Capture time before saving so needs are updated up to that point.
    clock.tick()

    needs_system.advance(
        registry,
        clock.simulation_time
    )

    registry.save(CITIZEN_PATH)
    needs_system.save_state(NEEDS_STATE_PATH)
    clock.save(WORLD_CLOCK_PATH)


def initialize_elysium():
    config = load_yaml("simulation.yaml")

    clock = WorldClock.from_config(
        config,
        WORLD_CLOCK_PATH
    )

    registry = initialize_citizens(clock, config)

    needs_system = NeedsSystem()

    # Restore the previous needs update timestamp.
    needs_system.load_state(
        NEEDS_STATE_PATH,
        clock.simulation_time
    )

    # Apply elapsed simulation time, including offline progress.
    needs_system.advance(
        registry,
        clock.simulation_time
    )

    console.print(
        Panel(
            "[bold green]PROJECT ELYSIUM[/bold green]\n"
            "Autonomous AI Civilization\n"
            "Day 4 - Citizen Needs System",
            title="Initialization"
        )
    )

    display_world(clock, config)
    display_citizens(registry)

    return config, clock, registry, needs_system


def run_simulation():
    parser = argparse.ArgumentParser(
        description="Project Elysium"
    )

    parser.add_argument("--once", action="store_true")
    parser.add_argument("--pause", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--speed", type=float)
    parser.add_argument("--citizens", action="store_true")
    parser.add_argument("--citizen", type=str)
    parser.add_argument(
        "--activity",
        nargs=2,
        metavar=("CITIZEN_ID", "ACTIVITY")
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=1.0
    )

    args = parser.parse_args()

    if args.pause and args.resume:
        parser.error("--pause and --resume cannot be used together.")

    config, clock, registry, needs_system = initialize_elysium()

    if args.pause:
        clock.pause()
        save_world(clock, registry, needs_system)
        console.print("[yellow]World paused.[/yellow]")
        return

    if args.resume:
        clock.resume()
        save_world(clock, registry, needs_system)
        console.print("[green]World resumed.[/green]")

    if args.speed is not None:
        if args.speed <= 0:
            parser.error("--speed must be greater than zero.")

        clock.set_speed(args.speed)
        save_world(clock, registry, needs_system)

        console.print(
            f"[green]Simulation speed set to {args.speed}x.[/green]"
        )

    if args.activity:
        citizen_id, activity = args.activity

        citizen = registry.get(citizen_id)

        if citizen is None:
            console.print(
                f"[red]Citizen {citizen_id} not found.[/red]"
            )
            return

        try:
            needs_system.apply_activity(
                citizen,
                activity,
                args.hours
            )
        except ValueError as error:
            console.print(f"[red]{error}[/red]")
            return

        save_world(clock, registry, needs_system)

        console.print(
            f"[green]{citizen.name} performed {activity} "
            f"for {args.hours} simulation hour(s).[/green]"
        )

        display_needs(citizen)
        return

    if args.citizens:
        display_citizens(registry)
        return

    if args.citizen:
        citizen = registry.get(args.citizen)

        if citizen is None:
            console.print("[red]Citizen not found.[/red]")
            return

        display_citizen(citizen)
        return

    if args.once:
        save_world(clock, registry, needs_system)
        return

    autosave_interval = config["simulation"].get(
        "autosave_interval_seconds",
        10
    )

    last_autosave = time.monotonic()

    console.print(
        "[green]Elysium simulation started. Press Ctrl+C to stop.[/green]"
    )

    try:
        while True:
            clock.tick()

            needs_system.advance(
                registry,
                clock.simulation_time
            )

            if time.monotonic() - last_autosave >= autosave_interval:
                save_world(clock, registry, needs_system)
                last_autosave = time.monotonic()

            time.sleep(0.1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Saving civilization...[/yellow]")

        save_world(clock, registry, needs_system)

        console.print(
            "[bold green]Project Elysium saved successfully.[/bold green]"
        )


if __name__ == "__main__":
    run_simulation()