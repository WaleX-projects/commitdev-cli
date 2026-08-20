# CommitDev CLI

The CommitDev CLI connects your local Git workflow to CommitDev. It handles
authentication, repository and content workflows, diagnostics, analytics, and
the live draft review pipeline from a terminal.

## Requirements

- Python 3.9 or newer
- A CommitDev account
- Git for repository setup and push integration

## Installation

### Install from source

```bash
git clone https://github.com/WaleX-projects/commitdev-cli.git
cd commitdev-cli
python -m pip install .
```

For local development, install the package in editable mode:

```bash
python -m pip install -e .
```

After installation, verify the CLI is available:

```bash
commitdev --version
commitdev --help
```

## Authentication

Start the device authentication flow and follow the URL and code shown in the
terminal:

```bash
commitdev login
```

Useful account commands:

```bash
commitdev whoami
commitdev doctor
commitdev logout
```

The CLI stores the local authentication profile in `~/.commitdev.json`.

## Commands

### Repositories

```bash
commitdev repo list
commitdev repo show <repository>
commitdev repo sync
```

### Drafts and posts

```bash
commitdev draft list
commitdev draft show <draft>
commitdev draft approve <draft>
commitdev draft regenerate <draft>

commitdev post list
commitdev post show <post>
```

### Integrations and reporting

```bash
commitdev integrations list
commitdev integrations connect
commitdev integrations disconnect

commitdev analytics
commitdev status
commitdev activity
```

Use the command help output for the exact arguments and options supported by
your installed version:

```bash
commitdev <command> --help
```

## Draft review pipeline

Start the live draft listener with:

```bash
commitdev watch
```

When a draft arrives, the interactive pipeline lets you edit content,
regenerate a draft, manage images, publish, or cancel the review.

## Git integration

Run setup from the root of a Git repository:

```bash
commitdev setup
```

Setup installs a local pre-push hook and adds a shell wrapper that watches for
successful pushes whose latest commit message contains `[post]`. Reload your
shell after setup, for example:

```bash
source ~/.bashrc
```

To remove the local CommitDev configuration and shell integration:

```bash
commitdev uninstall
```

## Development

The CLI is a Python package built with setuptools. Its executable entry point
is defined as `commitdev`, which runs `commitdev.main:app`.

Install the project in editable mode while developing, then run commands
directly from the repository:

```bash
python -m pip install -e .
commitdev --help
```