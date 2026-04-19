# main.py
# Run this file to start the Incident Response Agent

from rich.console import Console
from rich.panel import Panel
from agent import analyze_incident
from incidents import PAST_INCIDENTS
from memory import save_memory, ensure_bank_exists


console = Console()


def load_past_incidents():
    """Load all past incidents into Hindsight memory at startup."""
    console.print("\n[bold yellow]Loading past incidents into memory...[/bold yellow]")
    for inc in PAST_INCIDENTS:
        memory_text = f"""
Incident: {inc['title']}
Error: {inc['error']}
Root Cause: {inc['cause']}
Resolution: {inc['resolution']}
Time to Resolve: {inc['time_to_resolve']}
Severity: {inc['severity']}
"""
        save_memory(inc['title'], memory_text)
    console.print("[bold green]All past incidents loaded into memory![/bold green]\n")


def main():
    console.print(Panel.fit(
        "[bold red]INCIDENT RESPONSE AGENT[/bold red]\n"
        "[dim]Powered by Hindsight Memory + Groq AI[/dim]",
        border_style="red"
    ))

    # FIX: Create the memory bank first (PUT is idempotent — safe to call every startup)
    ensure_bank_exists()

    # Load past incidents into memory on startup
    load_past_incidents()

    console.print("[bold]Paste your incident below. Type [red]exit[/red] to quit.[/bold]\n")

    while True:
        console.print("[bold cyan]> Describe the incident:[/bold cyan]")
        user_input = input().strip()

        if user_input.lower() == "exit":
            console.print("\n[dim]Agent shutting down. Stay safe![/dim]")
            break

        if not user_input:
            console.print("[yellow]Please describe an incident first.[/yellow]\n")
            continue

        console.print("\n[bold yellow]Analyzing incident...[/bold yellow]")
        result = analyze_incident(user_input)

        console.print(Panel(
            result,
            title="[bold green]AI DIAGNOSIS & FIX PLAN[/bold green]",
            border_style="green"
        ))
        console.print("\n" + "─" * 60 + "\n")


if __name__ == "__main__":
    main()