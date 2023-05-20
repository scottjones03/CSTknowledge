import os
import getpass
import platform
from private import USER as user, PASSWORD as password, NOTION_TOKEN as notion_token, SESSION_PATH as session_token, UPLOAD_FOLDER, TEXT_FOLDER, DATABASE_ID
def main():

    if platform.system() == 'Windows':
        print("Please manually add the following lines to your Environment Variables.")
        print(f"USER={user}")
        print(f"PASSWORD={password}")
        print(f"NOTION_TOKEN={notion_token}")
        print(f"SESSION_TOKEN={session_token}")
        print(f"UPLOAD_FOLDER={UPLOAD_FOLDER}")
        print(f"TEXT_FOLDER={TEXT_FOLDER}")
        print(f"DATABASE_ID={DATABASE_ID}")

    else:
        # Determine profile file based on shell
        shell = os.environ.get('SHELL', '')
        if 'bash' in shell:
            profile_file = os.path.expanduser("~/.bash_profile")
        elif 'zsh' in shell:
            profile_file = os.path.expanduser("~/.zshrc")
        else:
            print("Unsupported shell. Please manually add the variables to your shell profile.")
            return

        # Append export commands to profile file
        with open(profile_file, 'a') as file:
            file.write(f"\n# Variables added by setup.py\n")
            file.write(f"export USER='{user}'\n")
            file.write(f"export PASSWORD='{password}'\n")
            file.write(f"export NOTION_TOKEN='{notion_token}'\n")
            file.write(f"export SESSION_TOKEN='{session_token}'\n")
            file.write(f"export UPLOAD_FOLDER='{UPLOAD_FOLDER}'\n")
            file.write(f"export TEXT_FOLDER='{TEXT_FOLDER}'\n")
            file.write(f"export DATABASE_ID='{DATABASE_ID}'\n")

        print("Environment variables have been added to your profile file. Please restart your shell or run `source {profile_file}` for the changes to take effect.")

if __name__ == "__main__":
    main()
