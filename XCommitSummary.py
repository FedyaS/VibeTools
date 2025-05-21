import subprocess
import os
import pyperclip
from datetime import datetime, timedelta

# Get project name from user
project_name = input("Enter project name: ")

# Construct path to project directory
project_path = os.path.join("..", project_name)

# Check if directory exists
if not os.path.isdir(project_path):
    print(f"Error: Directory {project_path} does not exist.")
    exit(1)

# Calculate time 16 hours ago
since_time = (datetime.now() - timedelta(hours=16)).strftime("%Y-%m-%d %H:%M:%S")

# Run git log command
try:
    git_command = [
        "git", 
        "-C", project_path, 
        "log", 
        f'--since={since_time}', 
        "--pretty=%B"
    ]
    result = subprocess.run(git_command, capture_output=True, text=True, check=True)
    commit_messages = result.stdout.strip()
except subprocess.CalledProcessError:
    print("Error: Failed to run git log. Ensure it's a valid git repository.")
    exit(1)

# If no commits, handle empty case
if not commit_messages:
    commit_messages = "No commits found in the last 16 hours."
else:
    # Split commits and format with "-"
    commits = [msg for msg in commit_messages.split('\n\n') if msg.strip()]
    commit_messages = '\n'.join(f"-{msg.strip()}" for msg in commits)

# Get today's date in desired format
today = datetime.now().strftime("%B %dth, %Y")

# Prepend the instruction message with desired output format
prefix = (
    f"Read the commit logs and history and generate an interesting, concise report of what was done today. "
    f"Do not use any complex grammatical structures. Limit it to 200 characters. "
    f"Output in this format:\n"
    f"🚀{project_name} 📅{today}\n"
    "{blank line}"
    f"{{your message}}\n"
    "{blank line}"
    f"🤖 Generated with Grok"
)
full_text = f"{prefix}\n{commit_messages}"

# Copy to clipboard
try:
    pyperclip.copy(full_text)
    print("-------")
    print(full_text)
    print("-------")
    print("Commit messages copied to clipboard!")
except pyperclip.PyperclipException:
    print("Error: Could not copy to clipboard. Ensure pyperclip is configured correctly.")