"""
Diagnostic script to check training database persistence
"""

import os
import sys
os.chdir('d:\\nano_bio_studio_last\\biotech-lab-main')
sys.path.insert(0, os.getcwd())

print("="*80)
print("TRAINING DATABASE DIAGNOSTIC")
print("="*80)
print(f"\nWorking directory: {os.getcwd()}")
print(f"Database file exists: {os.path.exists('ml_module.db')}")

if os.path.exists('ml_module.db'):
    file_size = os.path.getsize('ml_module.db')
    print(f"Database file size: {file_size} bytes")

# Test SQLAlchemy connection
print("\n" + "-"*80)
print("Testing SQLAlchemy Database Connection...")
print("-"*80)

try:
    from nanobio_studio.app.db.database import get_db, ModelRepository
    from sqlalchemy import text, inspect
    
    db = get_db()
    print(f"✅ Database instance created")
    print(f"   URL: {db.engine.url}")
    
    session = db.get_session()
    print(f"✅ Session created")
    
    # Check schema
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\n✅ Tables in database: {tables}")
    
    # Check trained_models table structure
    if 'trained_models' in tables:
        columns = [col['name'] for col in inspector.get_columns('trained_models')]
        print(f"\n✅ trained_models columns: {columns}")
    
    # Check record count
    result = session.execute(text("SELECT COUNT(*) FROM trained_models"))
    count = result.scalar()
    print(f"\n✅ Records in trained_models: {count}")
    
    if count > 0:
        result = session.execute(text("SELECT id, task_name, model_type, created_at FROM trained_models"))
        rows = result.fetchall()
        print("\n✅ Existing records:")
        for row in rows:
            print(f"   - {row[1]} ({row[2]}) - {row[3]}")
    
    session.close()
    print("\n✅ Session closed successfully")
    
except Exception as e:
    import traceback
    print(f"\n❌ ERROR: {str(e)}")
    print(f"\nTraceback:")
    traceback.print_exc()

# Test if we can write to the database
print("\n" + "-"*80)
print("Testing Database Write Capability...")
print("-"*80)

try:
    from nanobio_studio.app.db.database import get_db, ModelRepository
    from nanobio_studio.app.db.models import TrainedModel
    from datetime import datetime
    import uuid
    
    db = get_db()
    session = db.get_session()
    
    # Create a test record
    test_model = TrainedModel(
        id=str(uuid.uuid4()),
        task_name="test_write_" + str(datetime.now().timestamp()),
        model_type="test_model",
        task_type="predict_test",
        target_variable="test_target",
        created_at=datetime.utcnow(),
        n_training_samples=100,
        n_features=10,
        train_score=0.95,
        validation_score=0.92,
        model_path="/test/path",
        preprocessing_path=None,
        task_config={},
        evaluation_summary={"test": "data"},
        metadata_json={"test": "metadata"},
    )
    
    print(f"✅ Test record created: {test_model.task_name}")
    
    # Try to save it
    model_repo = ModelRepository(session)
    saved = model_repo.create(test_model)
    
    print(f"✅ Test record saved successfully")
    
    # Verify it was saved
    from sqlalchemy import text
    result = session.execute(text(f"SELECT COUNT(*) FROM trained_models WHERE id = '{test_model.id}'"))
    exists = result.scalar() > 0
    
    if exists:
        print(f"✅ Record VERIFIED in database!")
    else:
        print(f"❌ Record NOT found in database after save!")
    
    session.close()
    
except Exception as e:
    import traceback
    print(f"\n❌ ERROR during write test: {str(e)}")
    print(f"\nTraceback:")
    traceback.print_exc()

print("\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80)
