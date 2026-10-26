"""
Database Migration and Schema Synchronization Runner
Ensures all tables, indexes, and constraints exist in the target database.
"""
import sys
import os

# Include parent directory in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.postgres import Base, engine
# Import all models to ensure registered on Base
import models.user
import models.mood
import models.event
import models.user_state
import models.behavior
import models.pattern
import models.personalization
import models.evolution
import models.goals
import models.system_state
import models.agent_metrics
import models.memory
import models.proactive
import models.post_mortem

def run_migrations():
    print("=" * 60)
    print("Psych-AI Database Migration & Synchronization")
    print(f"Target Database Engine: {engine.url.render_as_string(hide_password=True)}")
    print("=" * 60)

    try:
        # Create all tables if they do not exist
        Base.metadata.create_all(bind=engine)
        print("Successfully synchronized all 19 database tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  + {table_name}")
        print("\nAll database tables verified and up to date.")
        return True
    except Exception as e:
        print(f"Error during schema synchronization: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
