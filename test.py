from rich.console import Console

console = Console()

console.print("[bold green][SUCCESS][/bold green] Pipeline initialized.")
console.print(
    "[bold cyan]Pipeline Status:[/bold cyan] Processing 1000 records..."
)
console.print("[red][ERROR][/red] Database connection lost.")
