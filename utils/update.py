import subprocess
import os
import sys


# TODO: weird stuff happening when bot updates and restarts (parent process is not killed)

def check_for_updates(on_windows: bool):
    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Ensure Git is installed
        if subprocess.call(['git', '--version']) != 0:
            print("[-] Git is not installed or not in the system's PATH.")
            return

        # Base command for Git with directory context
        git_command_base = ['git', '-C', script_dir]

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
            print(f"[+] {right} updates available. Attempting to update...")
            return True
        else:
            print('[+] Bot is up to date')
            print('[+] Launching bot...')
            return False
    except subprocess.CalledProcessError as cpe:
        print(f'[-] Git command failed: {cpe.output.strip()}')
        return False
    except Exception as e:
        print(f'[-] An error occurred while checking for update: {e}')
        return False


def update(on_windows: bool):
    print('[+] Checking for updates...')
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
