
import argparse
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.settings import ROOT_DIR, load_yaml

from elysium.core.world_clock import WorldClock
from elysium.agents.citizen_factory import CitizenFactory
from elysium.agents.citizen_registry import CitizenRegistry

from elysium.simulation.needs_system import NeedsSystem
from elysium.simulation.activity_system import ActivitySystem


console = Console()

# Persistent data paths
WORLD_CLOCK_PATH = ROOT_DIR / "data" / "world_clock.json"
CITIZEN_PATH = ROOT_DIR / "data" / "citizens.json"
NEEDS_STATE_PATH = ROOT_DIR / "data" / "needs_state.json"


# ---------------------------------------------------------
# DISPLAY FUNCTIONS
# ---------------------------------------------------------

def display_world(clock, config):
    table = Table(title="Project Elysium - World Status")

    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("World", config["world"]["name"])
    table.add_row("Version", config["world"]["version"])
    table.add_row(
        "Simulation Time",
        clock.simulation_time.isoformat()
    )
    table.add_row("Time Scale", f"{clock.time_scale}x")
    table.add_row(
        "Status",
        "Paused" if clock.paused else "Running"
    )

    console.print(table)


def display_citizens(registry):
    table = Table(title="Elysium Citizens")

    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Age")
    table.add_column("Occupation")
    table.add_column("Activity", style="green")
    table.add_column("Status")

    for citizen in registry.get_all():
        table.add_row(
            citizen.citizen_id,
            citizen.name,
            str(citizen.age),
            citizen.occupation,
            citizen.current_activity.capitalize(),
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

[cyan]Current Activity:[/cyan]
{citizen.current_activity.capitalize()}

[cyan]Remaining Activity Hours:[/cyan]
{citizen.activity_remaining_hours:.2f}
            """,
            title="Citizen Information"
        )
    )

    display_needs(citizen)


def display_activities(registry):
    table = Table(title="Citizen Activities")

    table.add_column("Citizen ID", style="cyan")
    table.add_column("Name")
    table.add_column("Occupation")
    table.add_column("Current Activity", style="green")
    table.add_column("Remaining Hours", justify="right")

    for citizen in registry.get_all():
        table.add_row(
            citizen.citizen_id,
            citizen.name,
            citizen.occupation,
            citizen.current_activity.capitalize(),
            f"{citizen.activity_remaining_hours:.2f}"
        )

    console.print(table)


# ---------------------------------------------------------
# CITIZEN INITIALIZATION
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# WORLD ADVANCEMENT
# ---------------------------------------------------------

def advance_world(
    clock,
    registry,
    needs_system,
    activity_system
):
    """
    Advance the world clock and update all citizen activities.

    The activity system receives elapsed simulation seconds,
    not real-world seconds.
    """

    previous_time = needs_system.last_update_simulation_time

    clock.tick()

    if previous_time is None:
        needs_system.last_update_simulation_time = (
            clock.simulation_time
        )
        return

    elapsed_seconds = (
        clock.simulation_time - previous_time
    ).total_seconds()

    if elapsed_seconds > 0:
        activity_system.advance(
            registry,
            elapsed_seconds,
            needs_system,
            previous_time
        )

    needs_system.last_update_simulation_time = (
        clock.simulation_time
    )


# ---------------------------------------------------------
# SAVE WORLD
# ---------------------------------------------------------

def save_world(
    clock,
    registry,
    needs_system,
    activity_system
):
    """Update and persist all world systems."""

    advance_world(
        clock,
        registry,
        needs_system,
        activity_system
    )

    registry.save(CITIZEN_PATH)

    needs_system.save_state(
        NEEDS_STATE_PATH
    )

    clock.save(
        WORLD_CLOCK_PATH
    )

    console.print(
        "[dim]World state saved.[/dim]"
    )


# ---------------------------------------------------------
# INITIALIZE ELYSIUM
# ---------------------------------------------------------

def initialize_elysium():
    config = load_yaml("simulation.yaml")

    clock = WorldClock.from_config(
        config,
        WORLD_CLOCK_PATH
    )

    registry = initialize_citizens(
        clock,
        config
    )

    needs_system = NeedsSystem()
    activity_system = ActivitySystem()

    # Restore the previous needs update timestamp.
    needs_system.load_state(
        NEEDS_STATE_PATH,
        clock.simulation_time
    )

    # Catch up activities during offline simulation time.
    previous_time = needs_system.last_update_simulation_time

    if previous_time is not None:
        elapsed_seconds = (
            clock.simulation_time - previous_time
        ).total_seconds()

        if elapsed_seconds > 0:
            activity_system.advance(
                registry,
                elapsed_seconds,
                needs_system,
                previous_time
            )

    needs_system.last_update_simulation_time = (
        clock.simulation_time
    )

    console.print(
        Panel(
            "[bold green]PROJECT ELYSIUM[/bold green]\n"
            "Autonomous AI Civilization\n"
            "Day 5 - Citizen Activity System",
            title="Initialization"
        )
    )

    display_world(clock, config)
    display_citizens(registry)

    return (
        config,
        clock,
        registry,
        needs_system,
        activity_system
    )


# ---------------------------------------------------------
# MAIN SIMULATION
# ---------------------------------------------------------

def run_simulation():

    parser = argparse.ArgumentParser(
        description="Project Elysium - AI Civilization"
    )

    # World controls
    parser.add_argument(
        "--once",
        action="store_true",
        help="Initialize, update and save once"
    )

    parser.add_argument(
        "--pause",
        action="store_true",
        help="Pause the saved simulation"
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

    # Citizen inspection
    parser.add_argument(
        "--citizens",
        action="store_true",
        help="Display all citizens"
    )

    parser.add_argument(
        "--citizen",
        type=str,
        help="Inspect a citizen by ID"
    )

    # Activity inspection
    parser.add_argument(
        "--activities",
        action="store_true",
        help="Display all citizen activities"
    )

    # Manual activity assignment
    parser.add_argument(
        "--activity",
        nargs=2,
        metavar=("CITIZEN_ID", "ACTIVITY"),
        help="Assign an activity to a citizen"
    )

    parser.add_argument(
        "--hours",
        type=float,
        default=1.0,
        help="Activity duration in simulation hours"
    )

    args = parser.parse_args()

    if args.pause and args.resume:
        parser.error(
            "--pause and --resume cannot be used together."
        )

    if args.hours <= 0:
        parser.error("--hours must be greater than zero.")

    if args.speed is not None and args.speed <= 0:
        parser.error("--speed must be greater than zero.")

    # Initialize all five components.
    (
        config,
        clock,
        registry,
        needs_system,
        activity_system
    ) = initialize_elysium()

    # -----------------------------------------------------
    # PAUSE
    # -----------------------------------------------------

    if args.pause:
        clock.pause()

        save_world(
            clock,
            registry,
            needs_system,
            activity_system
        )

        console.print(
            "[yellow]World paused.[/yellow]"
        )
        return

    # -----------------------------------------------------
    # RESUME
    # -----------------------------------------------------

    if args.resume:
        clock.resume()

        save_world(
            clock,
            registry,
            needs_system,
            activity_system
        )

        console.print(
            "[green]World resumed.[/green]"
        )

    # -----------------------------------------------------
    # SPEED
    # -----------------------------------------------------

    if args.speed is not None:
        clock.set_speed(args.speed)

        save_world(
            clock,
            registry,
            needs_system,
            activity_system
        )

        console.print(
            f"[green]Simulation speed set to "
            f"{args.speed}x.[/green]"
        )

    # -----------------------------------------------------
    # MANUAL ACTIVITY
    # -----------------------------------------------------

    if args.activity:
        citizen_id, activity = args.activity

        citizen = registry.get(citizen_id)

        if citizen is None:
            console.print(
                f"[red]Citizen {citizen_id} not found.[/red]"
            )
            return

        try:
            activity_system.start_activity(
                citizen,
                activity,
                args.hours
            )

            save_world(
                clock,
                registry,
                needs_system,
                activity_system
            )

            console.print(
                f"[green]{citizen.name} started "
                f"{activity} for {args.hours} "
                f"simulation hours.[/green]"
            )

            display_citizen(citizen)

        except ValueError as error:
            console.print(
                f"[red]{error}[/red]"
            )

        return

    # -----------------------------------------------------
    # DISPLAY CITIZENS
    # -----------------------------------------------------

    if args.citizens:
        display_citizens(registry)
        return

    # -----------------------------------------------------
    # DISPLAY ONE CITIZEN
    # -----------------------------------------------------

    if args.citizen:
        citizen = registry.get(args.citizen)

        if citizen is None:
            console.print(
                "[red]Citizen not found.[/red]"
            )
            return

        display_citizen(citizen)
        return

    # -----------------------------------------------------
    # DISPLAY ACTIVITIES
    # -----------------------------------------------------

    if args.activities:
        display_activities(registry)
        return

    # -----------------------------------------------------
    # RUN ONCE
    # -----------------------------------------------------

    if args.once:
        save_world(
            clock,
            registry,
            needs_system,
            activity_system
        )
        return

    # -----------------------------------------------------
    # CONTINUOUS SIMULATION
    # -----------------------------------------------------

    autosave_interval = config["simulation"].get(
        "autosave_interval_seconds",
        10
    )

    last_autosave = time.monotonic()

    console.print(
        "[bold green]Elysium simulation started.[/bold green]"
    )

    console.print(
        "[dim]Press Ctrl+C to save and stop.[/dim]"
    )

    try:
        while True:

            # Advance clock and all citizen activities.
            advance_world(
                clock,
                registry,
                needs_system,
                activity_system
            )

            # Periodic autosave.
            if (
                time.monotonic() - last_autosave
                >= autosave_interval
            ):

                save_world(
                    clock,
                    registry,
                    needs_system,
                    activity_system
                )

                last_autosave = time.monotonic()

            time.sleep(0.1)

    except KeyboardInterrupt:

        console.print(
            "\n[yellow]Saving civilization...[/yellow]"
        )

        save_world(
            clock,
            registry,
            needs_system,
            activity_system
        )

        console.print(
            "[bold green]Project Elysium saved successfully.[/bold green]"
        )


# ---------------------------------------------------------
# APPLICATION ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    run_simulation()
