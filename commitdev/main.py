import typer

from commitdev.commands.auth import (
    login,
    logout,
    whoami,
    doctor
)

from commitdev.commands.status import (
    status,
    activity,
    
)

from commitdev.commands.drafts import (
    drafts,
    draft,
    approve,
    regenerate,
    
)

from commitdev.commands.posts import (
    posts,
    post,
)

from commitdev.commands.repos import (
    repos,
    repo,
    sync,
)
from commitdev.commands.setup import setup, uninstall
from commitdev.commands.analytics import analytics
from commitdev.commands.integrations import integrations
from commitdev.commands.publishing import listen_for_drafts
app = typer.Typer()

# Auth
app.command()(login)
app.command()(logout)
app.command()(whoami)
app.command()(doctor)

# Status
app.command()(status)
app.command()(activity)
app.command()(doctor)

# Drafts
app.command()(drafts)
app.command()(draft)
app.command()(approve)
app.command()(regenerate)

# Posts
app.command()(posts)
app.command()(post)

# Repositories
app.command()(repos)
app.command()(repo)
app.command()(sync)

# Analytics
app.command()(analytics)

# Integrations
app.command()(integrations)

#Web socket editing 
app.command()(listen_for_drafts)

app.command()(setup)


app.command()(uninstall)



if __name__ == "__main__":
    app()
    
    
    
    