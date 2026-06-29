from commitdev.api import get


def posts():
    """
    List your published CommitDev posts.

    Displays a history of published posts, including their
    ID, publishing status, and the platforms where each post
    was successfully delivered.
    """
    try:
        data = get("/cli/posts/")

        print("\n📢 Published Posts History\n")

        if not data:
            print("No published posts found.\n")
            return

        for post in data:
            post_id = post.get('id')
            status = post.get('overall_status', '-').upper()
            platforms = post.get('published_platforms', [])
            
            # Format the platforms array into a comma-separated string
            platform_str = ", ".join(platforms) if platforms else "None"

            print(
                f"ID: {post_id:<4} | "
                f"Status: {status:<6} | "
                f"Platforms: {platform_str}"
            )

        print()

    except Exception as e:
        print(f"❌ {e}\n")



def post(id: int):
    """
    Show the details and performance of a published post.

    Displays the full content of a published post, its
    publishing status, delivery platforms, and engagement
    metrics such as likes, comments, and shares. When a post
    has been published to multiple platforms, a per-platform
    engagement breakdown is also shown.
    """
    try:
        data = get(f"/cli/posts/{id}/")

        print("\n📄 Post Details\n")

        print(f"ID        : {data.get('id')}")
        print(f"Status    : {data.get('overall_status', '-').upper()}")
        
        # Pull and format platform list dynamically
        platforms_list = data.get('platforms', [])
        platform_names = [p.get('provider') for p in platforms_list]
        print(f"Platforms : {', '.join(platform_names) if platform_names else 'None'}")
        
        # Display aggregate performance stats across all accounts
        print(f"Likes     : {data.get('total_likes', 0)}")
        print(f"Comments  : {data.get('total_comments', 0)}")
        print(f"Shares    : {data.get('total_shares', 0)}")

        # Optional: Print out mini-dashboard metrics per network if multiple exist
        if len(platforms_list) > 1:
            print("\n📈 Engagement Breakdown:")
            for p in platforms_list:
                print(f"  • [{p.get('provider')}] → ❤️ {p.get('likes', 0)} | 💬 {p.get('comments', 0)} | 🔁 {p.get('shares', 0)}")

        print("\nContent:\n")
        print(data.get("final_post_content", "No text content found."))
        print()

    except Exception as e:
        print(f"❌ {e}\n")
