from commitdev.api import get


def integrations():
    """
    Show the status of your connected publishing integrations.

    Lists every supported publishing platform and indicates
    whether it is connected to your CommitDev account.
    Use this command to verify which channels are available
    for publishing your generated posts.
    """

    try:

        data = get("/cli/integrations/")

        print("\n🔗 Integrations")
        print("─" * 40)

        connected_count = 0

        for platform, details in data.items():

            connected = details.get("connected", False)

            if connected:
                connected_count += 1

            status = (
                "✅ Connected"
                if connected
                else "❌ Not Connected"
            )

            print(
                f"{platform.capitalize():<15} {status}"
            )

        print("─" * 40)
        print(
            f"Connected: {connected_count}/{len(data)}"
        )

        print()

    except Exception as e:

        print("\n❌ Failed to fetch integrations")
        print(f"   {e}\n")