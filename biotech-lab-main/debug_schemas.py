#!/usr/bin/env python
"""Debug script to find the schemas import error."""
import sys
import traceback

try:
    print("Step 1: Importing MLService...")
    from nanobio_studio.app.services import MLService
    print("✓ MLService imported successfully")
    
    print("\nStep 2: Creating MLService instance...")
    service = MLService()
    print("✓ MLService instance created successfully")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print(f"\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
