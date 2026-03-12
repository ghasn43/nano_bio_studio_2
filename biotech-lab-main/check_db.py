import sqlite3

conn = sqlite3.connect('ml_module.db')
cursor = conn.cursor()

print('=' * 60)
print('Database: ml_module.db')
print('=' * 60)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f'\nTables in ml_module.db:')
for table in tables:
    table_name = table[0]
    print(f'\n  📦 Table: {table_name}')
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]
    print(f'     Records: {count}')
    
    # Show column info
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    if columns:
        print(f'     Columns: {", ".join([col[1] for col in columns])}')
    
    # Show sample data if records exist
    if count > 0 and table_name == 'trained_model':
        cursor.execute(f'SELECT task_name, model_type, train_score, validation_score, created_at FROM {table_name} ORDER BY created_at DESC LIMIT 5')
        rows = cursor.fetchall()
        print(f'     Recent records:')
        for row in rows:
            print(f'       - Task: {row[0]}, Model: {row[1]}, Train R²: {row[2]}, Valid R²: {row[3]}, Created: {row[4]}')

conn.close()
print('\n' + '=' * 60)
