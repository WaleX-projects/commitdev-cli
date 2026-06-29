import typer

from commitdev.config import (
    save_token,
    clear_token,
    get_token,
)

from commitdev.api import get


import time

from commitdev.api import post

def login():
    """
    Log in to your CommitDev account.

    Opens the device login flow and saves your account
    so you can use CommitDev from the CLI.
    """
    try:
        data = post("/cli/auth/device/start/")
    except Exception as e:
        print(f"❌ Failed to reach the server: {e}")
        return

    device_code = data["device_code"]
    interval = data.get("interval", 5)  # Server tells us how long to wait

    print("\n🔐 Login to CommitDev\n")
    print(f"Visit: {data['verification_uri']}")
    print(f"Code:  {data['user_code']}")
    print("\nWaiting for authorization (Press Ctrl+C to cancel)...\n")

    while True:
        try:
            result = post("/cli/auth/device/poll/", {"device_code": device_code})
            
            if result.get("authenticated"):
                save_token(result)
                print(f"\n✅ Logged in as {result['user']['username']}\n")
                break
                
            # If the backend explicitly tells your CLI to slow down
            if result.get("error") == "slow_down":
                interval += 5  # Add 5 seconds to back off
                
        except Exception:
            # If your server returns a 504 or crashes, don't crash the CLI!
            # Back off slightly and try again on the next tick.
            interval = min(interval + 2, 30) 

        time.sleep(interval)









def logout():
    """
    Log out of your CommitDev account.

    Removes your saved login from this computer.
    """

    clear_token()

    print("✅ Logged out successfully")






def whoami():
    """
    Show information about the currently logged-in user.

    Displays your CommitDev account details.
    """

    auth = get_token()

    if not auth:
        print("❌ Not logged in")
        return

    user = auth["user"]

    print("\n👤 CommitDev User\n")                             

    print(f"Username: {user.get('username', 'N/A')}")                     
    print(f"GitHub ID: {user.get('github_id', 'N/A')}")                   
    

def doctor():
    """
    Check whether the CommitDev CLI is working correctly.

    Verifies your login, API connection, and access token.
    Use this command when troubleshooting issues.
    """
    print("\n🩺 CommitDev Doctor\n")

    auth = get_token()

    if auth:
        print("✅ Authentication")
    else:
        print("❌ Authentication")

    try:

        get("/cli/doctor")

        print("✅ API Connection")

    except Exception as e:

        print("❌ API Connection")
        print(str(e))

    if auth and auth.get("access_token"):
        print("✅ Access Token")
    else:
        print("❌ Access Token")

    print("\nDone.\n")