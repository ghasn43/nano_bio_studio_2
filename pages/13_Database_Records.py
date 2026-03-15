"""
Database Records Viewer Page
Display all records from ml_module.db in a dedicated page
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path
from components.branding import (
    render_brand_header, render_brand_footer, render_sidebar_branding,
    render_page_title_with_branding, render_research_disclaimer
)

st.set_page_config(
    page_title="Database Records - NanoBio Studio™",
    page_icon="📊",
    layout="wide",
)

# Add branding
render_sidebar_branding()
render_brand_header()
render_page_title_with_branding("📊 Database Records Viewer", 
                                 "View all training records stored in ml_module.db")

# Sidebar controls
st.sidebar.header("⚙️ Database Settings")

# Find database path
@st.cache_data(ttl=60)
def get_db_path():
    """Find the ml_module.db database"""
    current_dir = Path(__file__).parent
    possible_paths = [
        current_dir.parent / "ml_module.db",
        Path("ml_module.db"),
        Path.cwd() / "ml_module.db",
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    return None

db_path = get_db_path()

if not db_path:
    st.error("❌ Database not found. Make sure ml_module.db exists in the project root.")
    st.stop()

st.sidebar.success(f"✅ Database: `{db_path}`")

# Database connection and data loading
@st.cache_data(ttl=30)
def load_data():
    """Load data from database"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get count
        cursor.execute("SELECT COUNT(*) FROM trained_models")
        total_count = cursor.fetchone()[0]
        
        # Get all records and convert to list of dicts for serialization
        cursor.execute("""
            SELECT * FROM trained_models 
            ORDER BY created_at DESC
        """)
        rows = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return total_count, rows
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return 0, []

total_count, rows = load_data()

# Header stats
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📦 Total Records", total_count)
with col2:
    file_size = os.path.getsize(db_path) / 1024
    st.metric("💾 Database Size", f"{file_size:.1f} KB")
with col3:
    st.metric("📁 Last Updated", datetime.fromtimestamp(os.path.getmtime(db_path)).strftime("%Y-%m-%d %H:%M"))

st.divider()

# Display options
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("📋 Records Table")
with col2:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

if rows:
    # Prepare data for display
    records_data = []
    for row in rows:
        row_dict = dict(row)
        
        # Parse JSON fields
        try:
            if row_dict.get('task_config') and isinstance(row_dict['task_config'], str):
                row_dict['task_config'] = json.loads(row_dict['task_config'])
        except:
            pass
        
        try:
            if row_dict.get('evaluation_summary') and isinstance(row_dict['evaluation_summary'], str):
                row_dict['evaluation_summary'] = json.loads(row_dict['evaluation_summary'])
        except:
            pass
        
        try:
            if row_dict.get('metadata_json') and isinstance(row_dict['metadata_json'], str):
                row_dict['metadata_json'] = json.loads(row_dict['metadata_json'])
        except:
            pass
        
        # Parse datetime
        if row_dict.get('created_at') and isinstance(row_dict['created_at'], str):
            try:
                row_dict['created_at'] = datetime.fromisoformat(
                    row_dict['created_at'].replace('Z', '+00:00')
                )
            except:
                pass
        
        records_data.append(row_dict)
    
    # Create display table
    display_data = []
    for i, record in enumerate(records_data, 1):
        display_data.append({
            "No.": i,
            "Task Name": record.get('task_name', 'N/A'),
            "Model Type": record.get('model_type', 'N/A'),
            "Task Type": record.get('task_type', 'N/A'),
            "Train R²": f"{record.get('train_score', 0):.4f}" if record.get('train_score') else "N/A",
            "Valid R²": f"{record.get('validation_score', 0):.4f}" if record.get('validation_score') else "N/A",
            "Samples": record.get('n_training_samples', 'N/A'),
            "Features": record.get('n_features', 'N/A'),
            "Created": record.get('created_at', 'N/A').strftime("%Y-%m-%d %H:%M") if hasattr(record.get('created_at'), 'strftime') else str(record.get('created_at', 'N/A')),
        })
    
    df = pd.DataFrame(display_data)
    st.dataframe(df, width='stretch', height=400, use_container_width=True)
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv,
        file_name=f"ml_training_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    st.divider()
    
    # Detailed view of each record
    st.subheader("📄 Detailed Records")
    
    for i, record in enumerate(records_data, 1):
        task_name = record.get('task_name', 'Unknown')
        model_type = record.get('model_type', 'Unknown')
        created_at = record.get('created_at', 'Unknown')
        
        with st.expander(f"Record {i}: {task_name} ({model_type}) - {created_at}", expanded=False):
            # Basic info
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Basic Information**")
                st.write(f"**ID:** `{record.get('id', 'N/A')}`")
                st.write(f"**Task Name:** {record.get('task_name', 'N/A')}")
                st.write(f"**Model Type:** {record.get('model_type', 'N/A')}")
                st.write(f"**Task Type:** {record.get('task_type', 'N/A')}")
                st.write(f"**Target Variable:** {record.get('target_variable', 'N/A')}")
            
            with col2:
                st.write("**Training Data**")
                st.write(f"**Samples:** {record.get('n_training_samples', 'N/A')}")
                st.write(f"**Features:** {record.get('n_features', 'N/A')}")
                st.write(f"**Train R²:** {record.get('train_score', 'N/A')}")
                st.write(f"**Validation R²:** {record.get('validation_score', 'N/A')}")
            
            # Paths
            st.write("**Paths**")
            st.code(f"Model: {record.get('model_path', 'N/A')}", language=None)
            if record.get('preprocessing_path'):
                st.code(f"Preprocessing: {record.get('preprocessing_path', 'N/A')}", language=None)
            
            # Evaluation summary
            eval_summary = record.get('evaluation_summary')
            if eval_summary and isinstance(eval_summary, dict):
                st.write("**Evaluation Summary**")
                
                if 'train' in eval_summary and eval_summary['train']:
                    st.write("*Training Metrics:*")
                    for key, value in eval_summary['train'].items():
                        if value is not None:
                            if isinstance(value, (int, float)):
                                st.write(f"  • {key}: {value:.4f}")
                            else:
                                st.write(f"  • {key}: {value}")
                
                if 'validation' in eval_summary and eval_summary['validation']:
                    st.write("*Validation Metrics:*")
                    for key, value in eval_summary['validation'].items():
                        if value is not None:
                            if isinstance(value, (int, float)):
                                st.write(f"  • {key}: {value:.4f}")
                            else:
                                st.write(f"  • {key}: {value}")
            
            # Metadata
            metadata = record.get('metadata_json')
            if metadata and isinstance(metadata, dict):
                st.write("**Metadata**")
                st.json(metadata)
            
            # Timestamps
            st.write("**Timestamps**")
            st.write(f"Created: {record.get('created_at', 'N/A')}")

else:
    st.info("📭 No records found in database yet. Train a model to see records here!")
    st.write("Go to **ML Training → Train Models** to train your first model.")
# Add branded footer
render_brand_footer()