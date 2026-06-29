from commitdev.api import get, post

def repos():
    """
    List all repositories connected to your CommitDev account.

    Displays every synchronized repository, including its
    ID, name, and current sync status. Use this command to
    view the repositories available for generating drafts
    and publishing content.
    """
    try:
        repositories = get("/cli/repos/")

        print("\n📦 Repositories\n")

        if not repositories:
            print("No repositories connected\n")
            return

        for repo in repositories:
            # Safely fetch keys matching the response payload template
            print(
                f"ID: {repo.get('id'):<4} | "
                f"Name: {repo.get('name'):<25} | "
                f"Status: {repo.get('status')}"
            )

        print()

    except Exception as e:
        print(f"❌ {e}\n")

def repo(id: int):
    """
    Show detailed information about a connected repository.

    Displays repository statistics including its current
    status, total commits processed, drafts generated,
    and published posts. Useful for monitoring activity
    and adoption for a specific repository.
    """
    try:
        data = get(f"/cli/repos/{id}/")

        print("\n📁 Repository Details\n")

        print(f"ID       : {data.get('id')}")
        print(f"Name     : {data.get('name')}")
        print(f"Status   : {data.get('status')}")
        print(f"Commits  : {data.get('commits', 0)}")
        print(f"Drafts   : {data.get('drafts', 0)}")
        print(f"Posts    : {data.get('posts', 0)}")

        print()

    except Exception as e:
        print(f"❌ {e}\n")


def sync(id: int):
    """
    Synchronize a repository with CommitDev.

    Fetches the latest repository information from GitHub
    and updates CommitDev with any new commits, branches,
    or metadata. Run this command if your repository appears
    out of date or after making significant changes.
    """

    try:

        result = post(f"/cli/repos/{id}/sync/")

        print("\n🔄 Repository Sync\n")

        print(result.get("message"))

        print()

    except Exception as e:

        print(f"❌ {e}")