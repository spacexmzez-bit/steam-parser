# parser.py
import os
import json
import glob
import re

ACCOUNTS_DIR = "accounts"
OUTPUT_FILE = "data.json"

# Patterns to ignore footer text from the copy-paste
IGNORE_PATTERNS = [
    r"^showing \d+ to \d+ of \d+ entries",
    r"^profile refreshed",
    r"^no data was stored",
    r"^steam$"
]

def should_ignore(line):
    line_lower = line.lower()
    return any(re.search(pat, line_lower) for pat in IGNORE_PATTERNS)

def parse_accounts():
    accounts_data = []

    if not os.path.exists(ACCOUNTS_DIR):
        os.makedirs(ACCOUNTS_DIR)
        print(f"Created '{ACCOUNTS_DIR}' directory. Drop your text files in there.")
        return

    for filepath in glob.glob(os.path.join(ACCOUNTS_DIR, "*.txt")):
        with open(filepath, "r", encoding="utf-8") as f:
            raw_lines = [line.strip() for line in f.readlines() if line.strip()]

        username = ""
        nickname = ""
        games = []

        for line in raw_lines:
            if should_ignore(line):
                continue

            # Header metadata parsing
            if line.lower().startswith("username:"):
                username = line.split(":", 1)[1].strip()
                continue
            if line.lower().startswith("nickname:"):
                nickname = line.split(":", 1)[1].strip()
                continue

            # Tab-delimited row parsing
            columns = [col.strip() for col in line.split("\t") if col.strip()]
            
            if columns:
                game_title = columns[0]
                
                # The provided format has playtime in the 4th column (index 3)
                playtime = columns[3] if len(columns) >= 4 else None

                games.append({
                    "title": game_title,
                    "hours": playtime
                })

        if username:
            accounts_data.append({
                "username": username,
                "nickname": nickname or username,
                "games": games
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(accounts_data, out, indent=2, ensure_ascii=False)

    print(f"Parsed {len(accounts_data)} account(s) and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    parse_accounts()
