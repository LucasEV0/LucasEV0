
import os
import json
import urllib.request
import urllib.error
from datetime import date, timedelta

USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GITHUB_TOKEN"]
README_FILE = "README.md"

query = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

payload = json.dumps({
    "query": query,
    "variables": {
        "login": USERNAME
    }
}).encode("utf-8")

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Content-Type": "application/json",
        "User-Agent": "github-streak",
        "Authorization": f"Bearer {TOKEN}"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode("utf-8"))

except urllib.error.HTTPError as error:
    print("Error de GitHub API:")
    print(error.read().decode())
    raise

if "errors" in data:
    print("Error GraphQL:")
    print(json.dumps(data["errors"], indent=2))
    raise SystemExit(1)

user = data.get("data", {}).get("user")

if user is None:
    raise SystemExit(f"No se encontró el usuario: {USERNAME}")

calendar = user["contributionsCollection"]["contributionCalendar"]

days = {}

for week in calendar["weeks"]:
    for contribution_day in week["contributionDays"]:
        day = contribution_day["date"]
        count = contribution_day["contributionCount"]
        days[day] = count

active_days = {
    date.fromisoformat(day)
    for day, count in days.items()
    if count > 0
}

# -------------------------------
# RACHA ACTUAL
# -------------------------------

if not active_days:
    current_streak = 0
    max_streak = 0
    last_activity = None

else:
    today = date.today()

    if today in active_days:
        check_day = today
    elif today - timedelta(days=1) in active_days:
        check_day = today - timedelta(days=1)
    else:
        check_day = None

    current_streak = 0

    if check_day:
        while check_day in active_days:
            current_streak += 1
            check_day -= timedelta(days=1)

    # -------------------------------
    # RACHA MÁXIMA
    # -------------------------------

    sorted_days = sorted(active_days)

    max_streak = 1
    streak = 1

    for i in range(1, len(sorted_days)):
        if sorted_days[i] == sorted_days[i - 1] + timedelta(days=1):
            streak += 1
        else:
            streak = 1

        max_streak = max(max_streak, streak)

    last_activity = max(active_days)

# -------------------------------
# DATOS
# -------------------------------

last_activity_text = (
    last_activity.strftime("%d/%m/%Y")
    if last_activity
    else "Nunca"
)

total_contributions = calendar["totalContributions"]

filled = min(current_streak, 10)
bar = "█" * filled + "░" * (10 - filled)

if current_streak >= 30:
    emoji = "🔥🔥🔥"
elif current_streak >= 14:
    emoji = "🔥🔥"
elif current_streak >= 7:
    emoji = "🔥"
else:
    emoji = "✨"

new_section = f"""<!-- STREAK_START -->
## 🔥 Mi racha

{emoji} **Racha actual:** {current_streak} días

🏆 **Racha máxima:** {max_streak} días

📅 **Última actividad:** {last_activity_text}

📊 **Contribuciones:** {total_contributions}

`{bar}` 🔥
<!-- STREAK_END -->"""

# -------------------------------
# README
# -------------------------------

with open(README_FILE, "r", encoding="utf-8") as file:
    readme = file.read()

start_marker = "<!-- STREAK_START -->"
end_marker = "<!-- STREAK_END -->"

if start_marker not in readme or end_marker not in readme:
    raise SystemExit(
        "No se encontraron STREAK_START y STREAK_END en README.md"
    )

start = readme.index(start_marker)
end = readme.index(end_marker) + len(end_marker)

readme = readme[:start] + new_section + readme[end:]

with open(README_FILE, "w", encoding="utf-8") as file:
    file.write(readme)

print("================================")
print("🔥 Racha actual:", current_streak)
print("🏆 Racha máxima:", max_streak)
print("📅 Última actividad:", last_activity_text)
print("📊 Contribuciones:", total_contributions)
print("================================")
