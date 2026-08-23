import typer
from rich.console import Console
from rich.theme import Theme
from commitdev.api import get
from commitdev.pipeline.console import console

app = typer.Typer(help="Manage integrations of socal media")

@app.command("list")
def list_integrations():
    """
    Show the status of your connected publishing integrations.

    Lists every supported publishing platform and indicates
    whether it is connected to your CommitDev account.
    """
    console.print("\n[brand]CommitDev[/brand] [meta]•[/meta] Connected Integrations")
    console.print("[meta]──────────────────────────────────────────────────[/meta]")

    with console.status("[meta]Fetching configuration maps from account profile...[/meta]", spinner="simpleDots"):
        try:
            data = get("/cli/integrations/")
        except Exception as e:
            console.print(f"  [error]✕ Failed to fetch integrations:[/error] [meta]{e}[/meta]\n")
            return

    connected_count = 0

    for platform, details in data.items():
        connected = details.get("connected", False)

        if connected:
            connected_count += 1
            status_indicator = "[success]✓ Connected[/success]"
            bullet = "[success]›[/success]"
        else:
            status_indicator = "[meta]✕ Not Connected[/meta]"
            bullet = "[meta]›[/meta]"

        console.print(
            f"  {bullet} [white]{platform.capitalize():<15}[/white] [meta]───[/meta] {status_indicator}"
        )

    console.print("[meta]──────────────────────────────────────────────────[/meta]")
    
    # Summary line tracking total links active
    console.print(f"Active Channels [meta]›[/meta] [success]{connected_count}[/success] [meta]/ {len(data)} configured[/meta]\n")


@app.command("connect")
def connect_platform(plaform_id:str):
    pass


@app.command("disconnect")
def disconnect_platform(plaform_id:str):
    pass

#Note Adding Two more command Named: commitdev integration list / connect / disconnect