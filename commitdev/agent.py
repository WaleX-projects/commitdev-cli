import asyncio
import json
import os
import subprocess
import sys
import tempfile
import websockets
from commitdev.config import get_token

import time


###
# Fallback mechanism if get_token() logic needs refreshing or fails
def fetch_fresh_token():
    try:
        token_data = get_token()
        token = token_data.get('access_token') if isinstance(token_data, dict) else token_data
        if not token:
            raise ValueError("No access token found in token configuration.")
        return token
    except Exception as e:
        print(f"❌ Configuration Error: Could not read local token: {e}")
        sys.exit(1)

def open_in_editor(initial_content):
    """
    Spawns a text editor populated with initial content.
    Blocks execution until the user saves and closes the file.
    """
    editor = os.environ.get('EDITOR', 'nano') 
    
    try:
        with tempfile.NamedTemporaryFile(suffix=".txt", mode='w+', delete=False) as tf:
            tf.write(initial_content)
            tf.flush()
            temp_file_path = tf.name

        print(f"📝 Launching editor ({editor}) for live draft modification...")
        
        # Inside your open_in_editor(initial_content) definition:
        
        if editor == 'code':
            # VS Code doesn't accept a dynamic wrap flag via CLI easily, 
            # but you can use '--wait'
            subprocess.run(['code', '--wait', temp_file_path], check=True)
        elif editor == 'nano':
            # '-$': Disables horizontal scrolling and forces visual soft-wrapping 
            subprocess.run(['nano', '-$', temp_file_path], check=True)
        elif editor == 'vim':
            # '+set wrap': Forces vim to wrap lines visually to fit the screen window boundary
            subprocess.run(['vim', '+set wrap', temp_file_path], check=True)
        else:
            subprocess.run([editor, temp_file_path], check=True)
        
        with open(temp_file_path, 'r') as tf_read:
            updated_content = tf_read.read()

        os.unlink(temp_file_path)
        return updated_content

    except Exception as e:
        print(f"⚠️ Failed to manage editor session safely: {e}")
        return None

async def listen_for_drafts():
    while True:
        token = fetch_fresh_token()
        
        # FIXED: Ensure your routing string is consistent with your consumer setup
        url = f"wss://commitdev.name.ng/ws/drafts/?token={token}"
        
        extra_headers = {
            "Authorization": f"Bearer {token}",
            "Origin": "https://commitdev.name.ng",
            "User-Agent": "CommitDev-Agent/1.0"
        }
        
        print(f"📡 Connecting to background stream...")
        
        try:
            async with websockets.connect(url, additional_headers=extra_headers) as ws:
                print("✅ Securely connected! Listening for live draft saves...")
                
                while True:
                    message = await ws.recv()
                    event_data = json.loads(message)
                    
                    if event_data.get("type") == "send_private_message":
                        payload = event_data.get("payload", {})
                        
                        if payload.get("status") == "draft_saved":
                            
                            post_id = payload.get('post_id')
                            # extract the content from payload 
                            current_content = payload.get('content', '') 
                      
                       

                            # 2. Re-assemble your interactive configuration layout block
                            initial_txt = (
                                f"# ──────────────────────────────────────────────────────────\n"
                                f"# 📝 COMMITDEV EDIT SESSION\n"
                                f"# ──────────────────────────────────────────────────────────\n"
                                f"# Target Post ID: {post_id}\n"
                                f"#\n"
                                f"# Instructions: Lines starting with '#' will be ignored.\n"
                                f"# Save and close this temporary file to finalize and deploy.\n"
                                f"# ──────────────────────────────────────────────────────────\n\n"
                                f"{current_content}\n"
                            )

                            # Run the synchronous editor process in an isolated executor thread
                            loop = asyncio.get_event_loop()
                            edited_result = await loop.run_in_executor(None, open_in_editor, initial_txt)
                            
                            if edited_result:
                                # Strip out the structural instruction lines starting with #
                                clean_body = "\n".join([
                                    line for line in edited_result.splitlines() 
                                    if not line.strip().startswith("#")
                                ]).strip()
                                
                                print("💾 Editor closed. Transmitting payload updates back to server...")
                                
                                # 🚀 SEND BACK TO DJANGO CHANNELS CONSUMER
                                # We package up the draft modifications and send them down the pipe
                                await ws.send(json.dumps({
                                    "action": "update_draft",
                                    "post_id": post_id,
                                    "content": clean_body
                                }))
                                print("🚀 Successfully transmitted to backend pipeline!")

        except websockets.exceptions.InvalidStatus as e:
            if e.response.status_code == 403:
                print("\n❌ Connection Rejected: HTTP 403 Forbidden.")
                break
            else:
                print(f"\n❌ Server returned an unexpected status: HTTP {e.response.status_code}")
                
        except websockets.exceptions.ConnectionClosed as e:
            print(f"\n🔌 Connection lost (Code: {e.code}). Attempting reconnection in 5 seconds...")
            
        except Exception as e:
            print(f"\n💥 An unexpected error occurred: {e}")
            
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(listen_for_drafts())
    except KeyboardInterrupt:
        print("\n👋 Agent gracefully stopped.")




