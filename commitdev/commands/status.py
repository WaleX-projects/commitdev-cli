from commitdev.api import get


def status():
    """
    Show the status of your most recent CommitDev deployment.

    Displays the latest repository, commit, overall publishing status,
    commit SHA, and the delivery status for every connected platform.
    Useful for checking whether a post was successfully published,
    is still pending, or failed.
    """
    try:
        # Fetch the updated data from your CLIStatusView endpoint
        data = get("/cli/status/")

        if data.get("status") == "no_posts":
            print("\n📊 No deployment history found for this account.\n")
            return

        print("\n📦 CommitDev Status")
        print("─" * 60)

        # 1. Print core commit details
        sha_suffix = f" ({data.get('commit_sha')})" if data.get('commit_sha') else ""
        print(f"Repository  : {data.get('repository', '-')}{sha_suffix}")
        print(f"Last Commit : {data.get('last_commit', '-')}")
        print(f"Overall     : {data.get('overall_status', '-').upper()}")
        print("─" * 60)
        
        # 2. Loop through and display each individual social media platform
        print("Platform Deliveries:")
        platforms_list = data.get("platforms", [])

        if not platforms_list:
            print("  ➖ No targeted platforms linked to this post.")
        else:
            for p in platforms_list:
                provider = p.get("provider", "-")
                delivery_status = p.get("delivery_status", "-")
                username = p.get("username", "")
                
                # Format username cleanly if it exists
                user_str = f" ({username})" if username else ""
                
                # Match status to custom styling icons
                if delivery_status == "published":
                    icon = "✅"
                elif delivery_status == "failed":
                    icon = "❌"
                else:
                    icon = "⏳" # For "pending" status

                print(f"  {icon} [{provider}]{user_str} ─── Status: {delivery_status}")
                
                # If there's a specific error message, show it underneath
                if p.get("error_message"):
                    print(f"     ↳ Error: {p['error_message']}")

        print("─" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Failed to fetch status")
        print(f"   {e}\n")




def activity():
    """
    Show your recent CommitDev publishing activity.

    Lists recent posts and drafts created from your commits,
    including the repository, commit message, commit SHA,
    overall status, and delivery status for each platform.
    """
    try:
        activities = get("/cli/activity/")

        print("\n📜 Recent Activity")
        print("─" * 60)

        if not activities:
            print("No recent activity\n")
            return

        for act in activities:
            repo = act.get("repository", "-")
            status = act.get("overall_status", "draft").upper()
            commit = act.get("commit_message", "-")
            sha = act.get("commit_sha", "-------")

            # Match overall status to clean terminal colors/indicators
            if status == "POSTED":
                status_tag = f"✅ POSTED"
            elif status == "FAILED":
                status_tag = f"❌ FAILED"
            else:
                status_tag = f"⏳ {status}"

            # 1. Gather all individual platforms targeted for this commit row
            platform_tags = []
            for p in act.get("platforms", []):
                p_provider = p.get("provider", "")
                p_status = p.get("status", "")
                
                # Small micro-indicator icon for individual channels
                p_icon = "✓" if p_status == "published" else "𐄂" if p_status == "failed" else "•"
                platform_tags.append(f"{p_provider}{p_icon}")
            
            platforms_str = f" [{', '.join(platform_tags)}]" if platform_tags else ""

            # 2. Render a clean, legible activity line
            print(f"• [{status_tag}{platforms_str}] {repo} ({sha})")
            print(f"  ↳ {commit.strip()}")
            print("─" * 60)

        print()

    except Exception as e:
        print(f"\n❌ Failed to fetch activity")
        print(f"   {e}\n")





def doctor():
    """
    Diagnose your CommitDev installation.

    Verifies that you are authenticated, GitHub is connected,
    repositories are available, publishing channels are configured,
    access tokens are valid, and your account is ready to publish.
    Run this command whenever something isn't working as expected.
    """
    try:
        data = get("/cli/doctor/")

        print("\n🩺 CommitDev Doctor")
        print("─" * 40)

        # Core Credentials Layout Tracking
        api_status = data["api"]["status"].upper()
        authenticated = "✅ YES" if data["user"]["authenticated"] else "❌ NO"
        github_connected = "✅ CONNECTED" if data["github"]["connected"] else "❌ NOT CONNECTED"

        print(f"API            : ✅ {api_status}")
        print(f"Authenticated  : {authenticated}")
        print(f"User           : {data['user']['username']}")
        print(f"GitHub         : {github_connected}")

        print("\nRepositories")
        print(f"  Total        : {data['repositories']['total']}")
        print(f"  Active       : {data['repositories']['active']}")

        print("\nPosts")
        print(f"  Drafts       : {data['posts']['drafts']}")
        print(f"  Published    : {data['posts']['published']}")

        # New Distribution Integrations Deep Check
        print("\nIntegrations")
        integrations = data["integrations"]
        providers = integrations["connected_providers"]
        
        if not integrations["has_targets"]:
            print("  Status       : ⚠️ NO SOCIAL CHANNELS LINKED (Run web setup)")
        else:
            print(f"  Channels     : ✅ LINKED ({', '.join(providers)})")
            
        if integrations["expired_tokens"] > 0:
            print(f"  Token Health : ❌ {integrations['expired_tokens']} RE-AUTH REQUIRED")
        else:
            print("  Token Health : ✅ ALL TOKENS VALID")

        print("─" * 40)

        # Comprehensive Final Health Evaluation
        if (
            data["user"]["authenticated"]
            and data["github"]["connected"]
            and integrations["has_targets"]
            and integrations["expired_tokens"] == 0
        ):
            print("🎉 Everything looks good. Ready to push code!\n")
        else:
            print("⚠️ Action required. Some validation checks failed.\n")

    except Exception as e:
        print("\n❌ Doctor check failed")
        print(f"   {e}\n")
