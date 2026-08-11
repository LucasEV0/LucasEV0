```python
import os
import re
import urllib.request
import datetime
import xml.etree.ElementTree as ET

USERNAME = os.environ["GITHUB_USERNAME"]
README = "README.md"

# GitHub genera un SVG de contribuciones para cada usuario.
url = f"https://github.com/users/{USERNAME}/contributions"

request = urllib.request.Request(
    url,
    headers={"User-Agent": "github-streak-bot"}
)

with urllib.request.urlopen(request) as response:
    html = response.read().decode("utf-8")

# Extraemos las fechas y la cantidad de contribuciones.
pattern = r'<td[^>]*data-date="([^"]+)"[^>]*data-level="([0-4])"'
matches = re.findall(pattern, html)

activity = {}

for date, level in matches:
    activity[date] = int(level)

if not activity:
    print("No se pudieron obtener las contribuciones.")
    exit(1)

# Ordenar fechas
dates = sorted(
    datetime.date.fromisoformat(date)
    for date in activity
)

# Solo cuentan los días con al menos una contribución.
active_days = {
    date for date, level in activity.items()
    if level > 0
}

today = datetime.date.today()

# --------------------------------------------------
# CALCULAR RACHA ACTUAL
# --------------------------------------------------

current_streak = 0
day = today

# Si hoy todavía no hubo actividad, permitimos que
# la racha continúe desde ayer.
if day not in active_days:
    day -= datetime.timedelta(days=1)

while day in active_days:
    current_streak += 1
    day -= datetime.timedelta(days=1)

# --------------------------------------------------
# CALCULAR RACHA MÁXIMA
# --------------------------------------------------

max_streak = 0
streak = 0
previous = None

for date in dates:
    if date not in active_days:
        continue

    if previous is not None and date == previous + datetime.timedelta(days=1):
        streak += 1
    else:
        streak = 1

    max_streak = max(max_streak, streak)
    previous = date

# Última actividad
last_activity = max(active_days) if active_days else None

if last_activity:
    last_activity_text = last_activity.strftime("%d/%m/%Y")
else:
    last_activity_text = "Nunca"

# --------------------------------------------------
# BARRA VISUAL
# --------------------------------------------------

bar_length = 10
filled = min(current_streak, bar_length)

bar = "█" * filled + "░" * (bar_length - filled)

if current_streak >= 30:
    emoji = "🔥🔥🔥"
elif current_streak >= 14:
    emoji = "🔥🔥"
elif current_streak >= 7:
    emoji = "🔥"
else:
    emoji = "✨"

new_section = f"""<!-- STREAK_START -->
{emoji} **Racha actual:** {current_streak} días  
🏆 **Racha máxima:** {max_streak} días  
📅 **Última actividad:** {last_activity_text}

`{bar}` 🔥
<!-- STREAK_END -->"""

# --------------------------------------------------
# ACTUALIZAR README
# --------------------------------------------------

with open(README, "r", encoding="utf-8") as file:
    readme = file.read()

pattern = r"<!-- STREAK_START -->.*?<!-- STREAK_END -->"

if not re.search(pattern, readme, flags=re.DOTALL):
    print("No se encontraron las marcas STREAK_START/STREAK_END.")
    exit(1)

readme = re.sub(
    pattern,
    new_section,
    readme,
    flags=re.DOTALL
)

with open(README, "w", encoding="utf-8") as file:
    file.write(readme)

print(
    f"Racha actual: {current_streak} días | "
    f"Racha máxima: {max_streak} días"
)
```
