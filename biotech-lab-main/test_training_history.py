"""
Test script to debug training history issues
"""

import sys
import os

# Set up path and working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print(f"Working directory: {os.getcwd()}")
print(f"Python path[0]: {sys.path[0]}")

# Import database components
from nanobio_studio.app.db.database import get_db, ModelRepository
from sqlalchemy import text

print("\n" + "="*80)
print("TEST: Trying to retrieve training history like Streamlit app does...")
print("="*80 + "\n")

try:
    # Step 1: Get database
    db = get_db()
    print(f"✅ Step 1: Database instance obtained")
    print(f"   URL: {db.engine.url}")
    
    # Step 2: Create session
    session = db.get_session()
    print(f"✅ Step 2: Session created (ID: {id(session)})")
    
    # Step 3: Check raw count
    result = session.execute(text("SELECT COUNT(*) FROM trained_models"))
    row_count = result.scalar()
    print(f"✅ Step 3: Raw row count = {row_count}")
    
    # Step 4: Create repository
    model_repo = ModelRepository(session)
    print(f"✅ Step 4: ModelRepository created")
    
    # Step 5: Get all models
    trained_models = model_repo.get_all()
    print(f"✅ Step 5: Retrieved {len(trained_models)} models")
    
    # Step 6: Detach and close
    session.expunge_all()
    session.close()
    print(f"✅ Step 6: Session closed and objects detached")
    
    # Step 7: Try to access attributes after session close
    print(f"\n✅ Step 7: Accessing model attributes after session close:")
    for i, model in enumerate(trained_models):
        try:
            print(f"\n   Model {i+1}:")
            print(f"     - task_name: {model.task_name}")
            print(f"     - model_type: {model.model_type}")
            print(f"     - n_training_samples: {model.n_training_samples}")
            print(f"     - n_features: {model.n_features}")
            print(f"     - train_score: {model.train_score}")
            print(f"     - validation_score: {model.validation_score}")
            print(f"     - created_at: {model.created_at}")
            print(f"     - target_variable: {model.target_variable}")
            print(f"     - evaluation_summary: {type(model.evaluation_summary).__name__}")
        except Exception as attr_error:
            print(f"     ❌ ERROR accessing attributes: {attr_error}")
    
    print(f"\n✅ SUCCESS: Training history is accessible!")
    
except Exception as e:
    import traceback
    print(f"\n❌ FAILED: {str(e)}")
    print(f"\nFull traceback:")
    traceback.print_exc()

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
