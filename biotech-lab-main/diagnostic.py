#!/usr/bin/env python
"""Diagnostic script to check training history persistence"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {__file__}")

# Check database file
db_file = "ml_module.db"
if os.path.exists(db_file):
    file_size = os.path.getsize(db_file)
    print(f"\n✅ Database file EXISTS: {db_file} ({file_size} bytes)")
else:
    print(f"\n❌ Database file NOT FOUND: {db_file}")

# Try to connect and query database
print("\n" + "="*50)
print("Attempting to query database...")
print("="*50)

try:
    from nanobio_studio.app.db.database import get_db
    
    db = get_db()
    print(f"✅ Database instance created")
    print(f"   Engine URL: {db.engine.url}")
    
    session = db.get_session()
    print(f"✅ Session created")
    
    # Check if table exists
    from sqlalchemy import text, inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"✅ Tables in database: {tables}")
    
    if 'trained_models' in tables:
        result = session.execute(text("SELECT COUNT(*) FROM trained_models"))
        count = result.scalar()
        print(f"✅ trained_models table has {count} records")
        
        if count > 0:
            # Show all records
            result = session.execute(text("SELECT id, task_name, model_type, created_at FROM trained_models"))
            for row in result:
                print(f"   - {row}")
        else:
            print("   (No records in trained_models)")
    else:
        print("❌ trained_models table NOT FOUND")
    
    session.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Diagnostic complete")
print("="*50)
