#!/usr/bin/env python
"""Simple test to verify database transaction works"""

import os
import sys
import uuid
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

print(f"Test started: {datetime.now()}\n")

try:
    # Get database
    from nanobio_studio.app.db.database import get_db, ModelRepository
    from nanobio_studio.app.db.models import TrainedModel
    from sqlalchemy import text
    
    print("="*70)
    print("TEST 1: Can we write a record to the database?")
    print("="*70)
    
    db = get_db()
    print(f"✅ Database instance obtained")
    print(f"   Engine ID: {id(db.engine)}")
    print(f"   URL: {db.engine.url}\n")
    
    # Create a test record manually
    model_id = str(uuid.uuid4())
    print(f"Creating test record with ID: {model_id}")
    
    session = db.get_session()
    print(f"✅ Session created: {id(session)}\n")
    
    test_model = TrainedModel(
        id=model_id,
        task_name="test_direct_save",
        model_type="test_model",
        task_type="test_type",
        target_variable="test_var",
        created_at=datetime.utcnow(),
        n_training_samples=100,
        n_features=5,
        train_score=0.95,
        validation_score=0.90,
        model_path="/test/path",
        preprocessing_path=None,
        task_config={"test": "config"},
        evaluation_summary={"train": {"r2": 0.95}, "validation": {"r2": 0.90}},
        metadata_json={"test": "metadata"},
    )
    
    print("Test model object created")
    
    # Use repository to save
    repo = ModelRepository(session)
    saved = repo.create(test_model)
    print(f"✅ Model saved via repository\n")
    
    # Verify it exists in this session
    count = session.execute(text(f"SELECT COUNT(*) FROM trained_models WHERE id = '{model_id}'")).scalar()
    print(f"In current session - Record exists: {count > 0}")
    
    session.close()
    print(f"Session closed\n")
    
    # Open new session to verify persistence
    print("="*70)
    print("TEST 2: Does the record persist in a new session?")
    print("="*70)
    
    new_session = db.get_session()
    count = new_session.execute(text(f"SELECT COUNT(*) FROM trained_models WHERE id = '{model_id}'")).scalar()
    new_session.close()
    
    if count > 0:
        print(f"✅ YES - Record persists in new session!")
    else:
        print(f"❌ NO - Record does NOT persist in new session!")
    
    print()
    
    # Check file modification time
    print("="*70)
    print("TEST 3: Was the database file updated?")
    print("="*70)
    
    db_file = "ml_module.db"
    if os.path.exists(db_file):
        mod_time = os.path.getmtime(db_file)
        mod_datetime = datetime.fromtimestamp(mod_time)
        time_diff = (datetime.now() - mod_datetime).total_seconds()
        print(f"Database file modified {time_diff:.1f} seconds ago")
        if time_diff < 5:
            print(f"✅ File was JUST updated (less than 5 seconds ago)")
        elif time_diff < 60:
            print(f"⚠️  File was updated {time_diff:.0f} seconds ago")
        else:
            print(f"❌ File was NOT updated recently (last update was {int(time_diff)} seconds ago)")
    
    print()
    
    # Check total records
    print("="*70)
    print("TEST 4: Total records in database")
    print("="*70)
    
    check_session = db.get_session()
    total = check_session.execute(text("SELECT COUNT(*) FROM trained_models")).scalar()
    check_session.close()
    
    print(f"Total records: {total}")
    
    print("\n" + "="*70)
    if count > 0 and time_diff < 5:
        print("✅ DATABASE SAVE IS WORKING CORRECTLY")
    else:
        print("❌ PROBLEM DETECTED - Database save is not persisting")
    print("="*70)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
