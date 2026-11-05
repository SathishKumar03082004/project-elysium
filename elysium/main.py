
import argparse
import time

from rich.console import Console
from rich.panel import Panel

from config.settings import ROOT_DIR, load_yaml
from elysium.core.world_clock import WorldClock


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
# INITIALIZE ELYSIUM
# --------------------------------------------------

def initialize_elysium():

    config = load_yaml("simulation.yaml")

    world = config["world"]

    save_path = ROOT_DIR / "data" / "world_clock.json"

    clock = WorldClock.from_config(
        config,
        save_path
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

    return clock, config, save_path


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
        help="Initialize and display the clock once"
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

    args = parser.parse_args()

    if args.pause and args.resume:
        parser.error("--pause and --resume cannot be used together")

    clock, config, save_path = initialize_elysium()

    # ----------------------------------------------
    # PAUSE CONTROL
    # ----------------------------------------------

    if args.pause:

        clock.pause()

        clock.save(save_path)

        display_world(clock, config)

        console.print(
            "[yellow]World is paused and saved.[/yellow]"
        )

        return

    # ----------------------------------------------
    # RESUME CONTROL
    # ----------------------------------------------

    if args.resume:

        clock.resume()

        clock.save(save_path)

        display_world(clock, config)

    # ----------------------------------------------
    # SPEED CONTROL
    # ----------------------------------------------

    if args.speed is not None:

        try:

            clock.set_speed(args.speed)

        except ValueError as error:

            console.print(
                f"[bold red]Error: {error}[/bold red]"
            )

            return

        # Changing speed also resumes a paused simulation.
        clock.resume()

        clock.save(save_path)

        display_world(clock, config)

    # ----------------------------------------------
    # INITIALIZATION TEST
    # ----------------------------------------------

    if args.once:

        console.print(
            "[bold green]Clock initialization test completed.[/bold green]"
        )

        return

    # ----------------------------------------------
    # START SIMULATION
    # ----------------------------------------------

    autosave_interval = config["simulation"][
        "autosave_interval_seconds"
    ]

    last_save = time.monotonic()

    last_display = time.monotonic()

    console.print()

    if clock.paused:

        console.print(
            "[bold yellow]ELYSIUM IS PAUSED[/bold yellow]"
        )

    else:

        console.print(
            "[bold green]ELYSIUM SIMULATION STARTED[/bold green]"
        )

    console.print(
        "[yellow]Press CTRL+C to stop the simulation.[/yellow]"
    )

    # ----------------------------------------------
    # MAIN LOOP
    # ----------------------------------------------

    try:

        while True:

            clock.tick()

            current_time = time.monotonic()

            # AUTOSAVE
            if (
                config["system"]["autosave_enabled"]
                and current_time - last_save >= autosave_interval
            ):

                clock.save(save_path)

                last_save = time.monotonic()

            # DISPLAY WORLD TIME
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
                    f"{status} | {state} | "
                    f"{clock.time_scale}x"
                )

                last_display = time.monotonic()

            time.sleep(1)

    except KeyboardInterrupt:

        console.print(
            "\n[yellow]Stopping Elysium...[/yellow]"
        )

        clock.save(save_path)

        console.print(
            "[bold green]World saved successfully.[/bold green]"
        )

        console.print(
            "[bold cyan]ELYSIUM SHUTDOWN COMPLETE[/bold cyan]"
        )


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":

    run_simulation()
