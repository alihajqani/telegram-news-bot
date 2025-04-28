import json
import pathlib
import sys

# Add the app directory to Python path
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from app.utils import storage_sqlite
from app.utils.storage import _DB as JSON_DB

def migrate():
    print("Initializing SQLite database...")
    storage_sqlite.init_db()
    
    if not JSON_DB.exists():
        print("No JSON storage file found. Nothing to migrate.")
        return
    
    print(f"Loading data from {JSON_DB}...")
    try:
        data = json.loads(JSON_DB.read_text())
    except json.JSONDecodeError:
        print("Error: Invalid JSON file")
        return
    
    print(f"Found {len(data)} entries to migrate")
    
    for url in data:
        # Since old storage only stored URLs, we'll store minimal entries
        storage_sqlite.add_article(
            url=url,
            title="",  # These fields weren't in old storage
            summary="",
            published="",
            tags=[]
        )
    
    print("Migration complete!")
    print(f"Total URLs in new database: {len(storage_sqlite.list_processed_urls())}")

if __name__ == "__main__":
    migrate()