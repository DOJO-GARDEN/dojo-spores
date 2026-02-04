"""
Zapisuje timestamp do STATUS.md jako heartbeat
"""

from datetime import datetime
from pathlib import Path

def run():
    timestamp = datetime.now().isoformat()
    status_file = Path("STATUS.md")
    
    content = f"# STATUS\n\nLast ping: {timestamp}\n"
    
    with open(status_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    return f"Ping: {timestamp}"
