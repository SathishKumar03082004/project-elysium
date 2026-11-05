from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.settings import settings, load_yaml


console = Console()


def initialize_elysium():

    simulation_config = load_yaml("simulation.yaml")

    world = simulation_config["world"]
    simulation = simulation_config["simulation"]
    population = simulation_config["population"]

    console.print()

    console.print(
        Panel(
            "[bold cyan]PROJECT ELYSIUM[/bold cyan]\n"
            "[white]Autonomous AI Civilization[/white]",
            subtitle="Version 0.1.0",
            border_style="cyan"
        )
    )

    table = Table(title="World Configuration")

    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("World Name", world["name"])
    table.add_row("Version", world["version"])
    table.add_row("Operation Mode", world["mode"])
    table.add_row("Simulation Day", str(simulation["start_day"]))
    table.add_row("Start Hour", str(simulation["start_hour"]))
    table.add_row(
        "Initial Population",
        str(population["initial_population"])
    )
    table.add_row(
        "Autonomous Citizens",
        str(simulation_config["citizens"]["autonomous"])
    )

    console.print(table)

    console.print(
        "\n[bold green]ELYSIUM INITIALIZATION SUCCESSFUL[/bold green]"
    )

    console.print(
        "[yellow]Waiting for civilization systems...[/yellow]"
    )


if __name__ == "__main__":

    initialize_elysium()