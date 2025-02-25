import sys
from pathlib import Path

# Add web directory to path
sys.path.append(str(Path(__file__).parent))
from app import app
