import subprocess
import os
import sys
import discord
import asyncio
import time

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
git_command_base = ['git', '-C', script_dir]

def check_upd(on_windows: bool):
    try:
        print('[+] Checking for updates...')
        # Ensure Git is installed
        if subprocess.call(['git', '--version']) != 0:
            print("[-] Git is not installed or not in the system's PATH.")
            return

        # Fetch latest information from the remote repository
        fetch_result = subprocess.call(git_command_base + ['fetch'])
        if fetch_result != 0:
            print("[-] Git fetch failed")
            return

        # Check if the current branch is behind its upstream
        # This command checks if HEAD has diverged from its upstream
        upstream = subprocess.check_output(git_command_base + ['rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'], text=True).strip()
        print(f"[+] Upstream branch: {upstream}")

        # If the local HEAD is behind the remote branch, it suggests updates are available
        ahead_behind_check = subprocess.check_output(git_command_base + ['rev-list', '--count', '--left-right', 'HEAD...@{u}'], text=True).strip()
        left, right = map(int, ahead_behind_check.split())
        if right > 0:
            print(f"[+] {right} updates available.")
            # fetch the commit messages between the local and remote branches
            commit_messages = subprocess.check_output(git_command_base + ['log', '--pretty=format:%s', f'HEAD..{upstream}'], text=True).strip() 
            print(f"[+] Latest commit messages:\n{commit_messages}")
            return commit_messages # Return them to be displayed in the bot message
        else:
            print('[+] Bot is up to date')
            return False
    except subprocess.CalledProcessError as cpe:
        print(f'[-] Git command failed: {cpe.output.strip()}')
        return False
    except Exception as e:
        print(f'[-] An error occurred while checking for update: {e}')
        return False
    


def update(on_windows: bool):
    
    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        git_command_base = ['git', '-C', script_dir]

        try:
            # Pull the latest changes from the remote repository
            subprocess.call(git_command_base + ['reset', '--hard', 'HEAD'])
            subprocess.call(git_command_base + ['pull'])
            print('[+] Successfully updated the bot')
            print('[+] Restarting bot...')

            # Restarting the bot
            python_exe = 'python3' if not on_windows else 'python'
            restart_command = [python_exe, 'main.py', 'updated']
            # Start the bot as a new process and kill parent process
            subprocess.Popen(restart_command, cwd=script_dir)
            sys.exit(0)

        except subprocess.CalledProcessError as cpe:
            print(f'[-] Git command failed: {cpe.output.strip()}')
        except Exception as e:
            print(f'[-] An error occurred while updating: {e}')
    except Exception as e:
        print(f'[-] An error occurred while attempting to update: {e}')
