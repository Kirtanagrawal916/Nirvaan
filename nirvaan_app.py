"""
NIRVAAN — AI Satellite Disaster Monitoring Platform
Entry point wrapper supporting both `nirvaan_app.py` and `app.py`
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from app import main

if __name__ == "__main__":
    main()
