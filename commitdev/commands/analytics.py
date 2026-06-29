from commitdev.api import get

def analytics():
    try:
        data = get("/cli/analytics/")

        print("\n📊 CommitDev Analytics")
        print("─" * 40)

        # Print out the global account metrics
        print(f"Posts       : {data.get('posts', 0)}")
        print(f"Impressions : {data.get('impressions', 0)}")
        print(f"Engagement  : {data.get('engagement', 0)}")
        print(f"Followers   : {data.get('followers', 0)}")

        print("\n🏆 Top Repositories")
        print("─" * 40)

        top_repos = data.get("top_repos", [])

        if not top_repos:
            print("No repository data available\n")
            return

        for repo in top_repos:
            repo_name = repo.get('name', '-')
            print(
                f"{repo_name:<25} | "
                f"Posts: {repo.get('posts', 0):<3} | "
                f"Engagement: {repo.get('engagement', 0)}"
            )

        print()

    except Exception as e:
        print(f"❌ {e}\n")
