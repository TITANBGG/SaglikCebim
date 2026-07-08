import sys
from pathlib import Path

# Add backend dir to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Initialize DB
from app.core.database import init_db

try:
    init_db()
    print("✓ Database tables created successfully")
except Exception as e:
    print(f"✗ Database initialization failed: {e}")
