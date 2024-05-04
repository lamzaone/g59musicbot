import subprocess
import os
import sys

def check_for_updates(on_windows: bool):
    try:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        if subprocess.call(['git', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
            print("[-] Git is not installed or not in the system's PATH.")
            return False

        git_command_base = ['git', '-C', script_dir]

        fetch_result = subprocess.call(git_command_base + ['fetch'])
        if fetch_result != 0:
            print("[-] Git fetch failed")
            return False

        upstream = subprocess.check_output(git_command_base + ['rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'], text=True).strip()
        print(f"[+] Upstream branch: {upstream}")

        ahead_behind_check = subprocess.check_output(git_command_base + ['rev-list', '--count', '--left-right', 'HEAD...@{u}'], text=True).strip()
        left, right = map(int, ahead_behind_check.split())
        if right > 0:
            print(f"[+] {right} updates available.")
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
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        git_command_base = ['git', '-C', script_dir]
        while True:
            confirmation = input("Do you want to update the bot now? (yes/no or y/n): ").lower()
            if confirmation in ['yes', 'y']:
                try:
                    subprocess.call(git_command_base + ['reset', '--hard', 'HEAD'])
                    subprocess.call(git_command_base + ['pull'])
                    print('[+] Successfully updated the bot')

                    # Restart the bot if successfully updated
                    print('[+] Restarting bot...')
                    python_exe = 'python3' if not on_windows else 'python'
                    restart_command = [python_exe, 'main.py', 'updated']
                    subprocess.Popen(restart_command, cwd=script_dir)
                    os._exit(0)  # Ensuring parent process is killed

                except subprocess.CalledProcessError as cpe:
                    print(f'[-] Git command failed: {cpe.output.strip()}')
                except Exception as e:
                    print(f'[-] An error occurred while updating: {e}')
            elif confirmation in ['no', 'n']:
                print('[+] Bot is not updated.')
            else:
                print("Please enter 'yes' or 'no' or 'y' or 'n'.")
    except Exception as e:
        print(f'[-] An error occurred while attempting to update: {e}')