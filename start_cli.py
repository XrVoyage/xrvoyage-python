import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from rich.console import Console
from rich.live import Live
from rich.table import Table

# Create a rich console instance
console = Console()

# Create a table to display in the terminal
def create_table() -> Table:
    table = Table(title="Dynamic Table")

    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")
    table.add_column("Status", justify="right", style="green")

    for i in range(1, 11):
        table.add_row(f"{i}", f"Description {i}", "In Progress" if i % 2 == 0 else "Complete")
    
    return table

# Update function for dynamic content
async def update_live_view(live):
    while True:
        live.update(create_table())
        await asyncio.sleep(5)  # Increase the sleep time to 5 seconds

# Interactive Prompt
async def interactive_prompt():
    session = PromptSession()

    while True:
        text = await session.prompt_async("> ")
        console.print(f"You entered: {text}")

# Setup key bindings
bindings = KeyBindings()

@bindings.add("c-c")
def _(event):
    "Exit the application."
    event.app.exit()

# Create the application layout
def create_layout():
    return Layout(
        HSplit(
            [
                Window(FormattedTextControl("Press Ctrl-C to exit."), height=1, style="reverse"),
                Window(FormattedTextControl("Interactive Terminal Application"), height=1),
            ]
        )
    )

# Main function to run the application
async def main():
    layout = create_layout()
    application = Application(
        layout=layout,
        key_bindings=bindings,
        full_screen=True,
    )

    with Live(create_table(), console=console, refresh_per_second=0.2) as live:  # Adjusted refresh rate
        with patch_stdout():
            await asyncio.gather(application.run_async(), interactive_prompt(), update_live_view(live))

# Entry point
if __name__ == "__main__":
    asyncio.run(main())
