#!/usr/bin/env python
"""Detailed diagnostic for training history persistence"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

print(f"Diagnostic run at: {datetime.now()}")
print(f"Current working directory: {os.getcwd()}\n")

# Check database file details
db_file = "ml_module.db"
if os.path.exists(db_file):
    file_size = os.path.getsize(db_file)
    mod_time = os.path.getmtime(db_file)
    mod_datetime = datetime.fromtimestamp(mod_time)
    print(f"✅ Database file: {db_file}")
    print(f"   Size: {file_size} bytes")
    print(f"   Last modified: {mod_datetime}")
    print(f"   Age: {(datetime.now() - mod_datetime).total_seconds():.1f} seconds ago\n")
else:
    print(f"❌ Database file NOT FOUND: {db_file}\n")
    sys.exit(1)

try:
    from nanobio_studio.app.db.database import get_db
    from sqlalchemy import text, inspect
    
    db = get_db()
    session = db.get_session()
    
    # Get all records with full details
    print("="*70)
    print("TRAINED MODELS TABLE CONTENTS")
    print("="*70)
    
    result = session.execute(text("SELECT COUNT(*) FROM trained_models"))
    count = result.scalar()
    print(f"Total records: {count}\n")
    
    if count > 0:
        result = session.execute(text("""
            SELECT 
                id, 
                task_name, 
                model_type, 
                task_type,
                n_training_samples,
                n_features,
                train_score,
                validation_score,
                created_at
            FROM trained_models 
            ORDER BY created_at DESC
        """))
        
        for i, row in enumerate(result, 1):
            print(f"Record #{i}:")
            print(f"  ID: {row[0]}")
            print(f"  Task: {row[1]}")
            print(f"  Model Type: {row[2]}")
            print(f"  Task Type: {row[3]}")
            print(f"  Samples: {row[4]}")
            print(f"  Features: {row[5]}")
            print(f"  Train R²: {row[6]}")
            print(f"  Valid R²: {row[7]}")
            print(f"  Created: {row[8]}")
            print()
    else:
        print("⚠️  NO RECORDS FOUND IN trained_models TABLE")
    
    session.close()
    
    # Summary
    print("="*70)
    print("ANALYSIS")
    print("="*70)
    if count == 0:
        print("❌ Database file exists but is EMPTY")
        print("   → Training records are NOT being saved to database")
    elif count == 1:
        print("⚠️  Only 1 record found (likely from earlier session)")
        print("   → New training sessions are NOT being saved")
    else:
        print(f"✅ Database has {count} records")
        print("   → Training records ARE being saved")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
