"""
Panchayat — Working Prototype
================================
Terminal-based demo of the full game turn workflow.

Run with: python -m bridge.prototype
"""

import os
import sys
import time

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.layout import Layout
from rich import box

from bridge.langgraph_engine import GameState, run_full_turn, run_candidate_reaction
from bridge.ai_prompts import get_candidate_info, get_all_candidate_ids
from data.voter_profiles import VOTER_PROFILES

console = Console()

# ─── Policy Menu ─────────────────────────────────────────────────────────────

POLICY_OPTIONS = [
    {"id": 1, "title": "🌾 Increase MSP by 50% for wheat and rice", "category": "agriculture"},
    {"id": 2, "title": "📱 Free 5G connectivity for all villages", "category": "technology"},
    {"id": 3, "title": "💰 Simplify GST to single 10% slab", "category": "economy"},
    {"id": 4, "title": "🏥 Free healthcare at all Primary Health Centers", "category": "social_welfare"},
    {"id": 5, "title": "🔍 Blockchain transparency for all Panchayat funds", "category": "governance"},
    {"id": 6, "title": "✊ Expand MNREGA to 200 days guaranteed work", "category": "social_welfare"},
    {"id": 7, "title": "🏭 Zero-tax SEZ for startups in every district", "category": "economy"},
    {"id": 8, "title": "📚 Mother tongue education + coding from Class 6", "category": "governance"},
    {"id": 0, "title": "✏️  Enter your own custom policy", "category": "custom"},
]

# ─── Display Functions ───────────────────────────────────────────────────────

def show_welcome():
    """Display the welcome screen."""
    console.clear()
    welcome = """
# 🏛️ PANCHAYAT
## AI-Powered Post-Truth Political Simulator

Welcome to the Panchayat election! You are the **5th candidate** running against 
4 AI opponents, each with a distinct political ideology.

**Your opponents:**
"""
    console.print(Panel(Markdown(welcome), border_style="bold cyan", box=box.DOUBLE))

    # Candidate table
    table = Table(box=box.ROUNDED, border_style="cyan")
    table.add_column("Emoji", justify="center", width=4)
    table.add_column("Name", style="bold")
    table.add_column("Archetype", style="italic")
    table.add_column("Party", style="dim")

    for cid in get_all_candidate_ids():
        info = get_candidate_info(cid)
        table.add_row(info["emoji"], info["name"], info["archetype"], info["party_name"])

    console.print(table)
    console.print()


def show_voter_dashboard(sentiments: dict):
    """Display voter sentiment dashboard."""
    table = Table(title="🗳️ Voter Sentiment Dashboard", box=box.ROUNDED, border_style="yellow")
    table.add_column("Group", width=20)
    table.add_column("Happiness", justify="center", width=12)
    table.add_column("Bar", width=30)
    table.add_column("Mood", justify="center", width=15)

    for vid, vp in VOTER_PROFILES.items():
        happiness = sentiments.get(vid, vp.base_happiness)
        bar_len = int(happiness / 100 * 25)
        bar = "█" * bar_len + "░" * (25 - bar_len)

        if happiness >= 60:
            color = "green"
            mood = "😊 Satisfied"
        elif happiness >= 40:
            color = "yellow"
            mood = "😐 Neutral"
        elif happiness >= 25:
            color = "red"
            mood = "😤 Unhappy"
        else:
            color = "bold red"
            mood = "🔥 Revolt"

        table.add_row(
            f"{vp.emoji} {vp.name_en}",
            f"[{color}]{happiness:.0f}/100[/{color}]",
            f"[{color}]{bar}[/{color}]",
            mood,
        )

    console.print(table)


def show_election_forecast(forecast: dict):
    """Display election forecast."""
    table = Table(title="📊 Election Forecast", box=box.ROUNDED, border_style="magenta")
    table.add_column("Rank", justify="center", width=6)
    table.add_column("Candidate", width=25)
    table.add_column("Vote Share", justify="right", width=12)
    table.add_column("Bar", width=25)

    vote_shares = forecast.get("vote_shares", {})
    for rank, (cid, share) in enumerate(vote_shares.items(), 1):
        bar_len = int(share / 100 * 20)
        bar = "█" * bar_len

        if cid == "player":
            name = "⭐ YOU (Player)"
            color = "bold cyan"
        else:
            try:
                info = get_candidate_info(cid)
                name = f"{info['emoji']} {info['name']}"
            except ValueError:
                name = cid
            color = "white"

        if rank == 1:
            color = "bold green"

        table.add_row(
            f"#{rank}",
            f"[{color}]{name}[/{color}]",
            f"[{color}]{share:.1f}%[/{color}]",
            f"[{color}]{bar}[/{color}]",
        )

    winner = forecast.get("winner", "?")
    margin = forecast.get("margin", 0)
    console.print(table)
    console.print(f"  [dim]Winner: {winner} | Margin: {margin:.1f}%[/dim]\n")


def show_candidate_reactions(reactions: dict):
    """Display candidate reactions."""
    for cid, data in reactions.items():
        color_map = {
            "dharma_rakshak": "orange1",
            "vikas_purush": "dodger_blue1",
            "jan_neta": "red1",
            "mukti_devi": "purple",
        }
        color = color_map.get(cid, "white")

        console.print(Panel(
            f"[italic]{data['reaction']}[/italic]",
            title=f"{data['emoji']} {data['name']} ({data['archetype']})",
            border_style=color,
            width=80,
        ))


def show_sentiment_changes(changes: dict):
    """Display how voter sentiments shifted."""
    console.print("\n[bold yellow]📢 Voter Sentiment Shifts:[/bold yellow]")
    for vid, change in changes.items():
        shift = change["shift"]
        if shift > 0:
            arrow = f"[green]▲ +{shift:.1f}[/green]"
        elif shift < 0:
            arrow = f"[red]▼ {shift:.1f}[/red]"
        else:
            arrow = "[dim]— 0.0[/dim]"

        console.print(
            f"  {change['emoji']} {change['name']}: "
            f"{change['old']:.0f} → {change['new']:.0f} {arrow} "
            f"[dim]{change['narrative']}[/dim]"
        )
    console.print()


# ─── Main Game Loop ──────────────────────────────────────────────────────────

def main():
    """Run the prototype."""
    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        console.print("[bold red]ERROR: GOOGLE_API_KEY not found in .env file![/bold red]")
        console.print("Create a .env file with: GOOGLE_API_KEY=your_key_here")
        sys.exit(1)

    game = GameState()
    show_welcome()

    # Show initial voter dashboard
    show_voter_dashboard(game.voter_sentiments)
    console.print()

    while True:
        # Show policy menu
        console.print(Panel("[bold]Choose your policy move:[/bold]", border_style="cyan"))
        for opt in POLICY_OPTIONS:
            console.print(f"  [{opt['id']}] {opt['title']}")
        console.print()

        # Get player choice
        try:
            choice = console.input("[bold cyan]Your choice (0-8, or 'q' to quit): [/bold cyan]")
        except (EOFError, KeyboardInterrupt):
            break

        if choice.lower() == 'q':
            break

        try:
            choice_num = int(choice)
        except ValueError:
            console.print("[red]Invalid choice. Try again.[/red]")
            continue

        if choice_num == 0:
            player_action = console.input("[bold cyan]Enter your custom policy: [/bold cyan]")
        else:
            selected = [p for p in POLICY_OPTIONS if p["id"] == choice_num]
            if not selected:
                console.print("[red]Invalid choice. Try again.[/red]")
                continue
            player_action = selected[0]["title"]

        console.print(f"\n[bold green]📢 You announced: \"{player_action}\"[/bold green]\n")

        # Run the turn with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("AI candidates are thinking...", total=None)

            # Run full game turn
            result = run_full_turn(player_action, game)

            progress.update(task, description="Done!", completed=True)

        # Display results
        console.print(f"\n[bold]═══ TURN {result['turn']} RESULTS ═══[/bold]\n")

        # 1. Candidate reactions
        console.print("[bold]🎤 Candidate Reactions:[/bold]\n")
        show_candidate_reactions(result["candidate_reactions"])

        # 2. Sentiment changes
        show_sentiment_changes(result["sentiment_changes"])

        # 3. Updated voter dashboard
        show_voter_dashboard(game.voter_sentiments)

        # 4. Election forecast
        console.print()
        show_election_forecast(result["election_forecast"])

        # Separator
        console.print("[dim]─" * 60 + "[/dim]\n")

    # Goodbye
    console.print(Panel(
        "[bold]Thanks for playing Panchayat! 🏛️[/bold]\n"
        f"Turns played: {game.turn_number}",
        border_style="cyan",
    ))


if __name__ == "__main__":
    main()
