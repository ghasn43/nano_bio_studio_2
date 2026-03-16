"""
Workflow Progress Guide - System-driven user direction
Shows where user is in the workflow and what to do next
"""

import streamlit as st

WORKFLOW_STEPS = [
    {
        "number": 1,
        "title": "Disease Selection",
        "description": "Choose disease type and therapeutic drug",
        "page": "pages/00_Disease_Selection.py",
        "required_fields": ["hcc_subtype", "selected_drug"],
        "emoji": "🏥"
    },
    {
        "number": 2,
        "title": "Design Parameters",
        "description": "Review auto-populated design parameters & clinical trials",
        "page": "pages/01_Design_Parameters.py",
        "required_fields": ["hcc_subtype", "selected_drug"],
        "emoji": "📋"
    },
    {
        "number": 3,
        "title": "Design Calibration",
        "description": "Manually tune NP parameters with real-time scoring",
        "page": "pages/02_Design_Calibration.py",
        "required_fields": ["hcc_subtype", "calibration_size", "calibration_charge", "calibration_peg", "calibration_drug_loading"],
        "emoji": "⚙️"
    },
    {
        "number": 5,
        "title": "Trial History",
        "description": "View, compare, and export all your trials",
        "page": "pages/10_Trial_History.py",
        "required_fields": ["trial_id"],
        "emoji": "📊"
    }
]

def get_current_step():
    """Determine which step the user is currently on"""
    # Check if on trial history page
    if 'trial_id' in st.session_state and st.session_state.trial_id and \
       st.session_state.get('calibration_size'):
        return 5
    
    # Check if calibration started
    if 'calibration_size' in st.session_state and st.session_state.calibration_size:
        return 3
    
    # Check if on design parameters
    if 'hcc_subtype' in st.session_state and st.session_state.hcc_subtype and \
       'selected_drug' in st.session_state and st.session_state.selected_drug:
        return 2 if 'move_to_params' not in st.session_state else 3
    
    # Check if disease selected
    if 'hcc_subtype' in st.session_state and st.session_state.hcc_subtype:
        return 1
    
    return 0

def can_proceed_to_step(step_number):
    """Check if user has completed prerequisites for a step"""
    if step_number == 1:
        return True
    elif step_number == 2:
        return 'hcc_subtype' in st.session_state and st.session_state.hcc_subtype and \
               'selected_drug' in st.session_state and st.session_state.selected_drug
    elif step_number == 3:
        return 'hcc_subtype' in st.session_state and st.session_state.hcc_subtype and \
               'selected_drug' in st.session_state and st.session_state.selected_drug
    elif step_number == 5:
        return 'trial_id' in st.session_state and st.session_state.trial_id
    return True

def render_workflow_progress():
    """Render progress indicator showing current position in workflow"""
    current = get_current_step()
    
    st.markdown("""
    <style>
    .workflow-progress {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .step-indicator {
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin: 15px 0;
    }
    .step-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 18px;
    }
    .step-active {
        background: #ffd700;
        color: #333;
    }
    .step-completed {
        background: #4caf50;
        color: white;
    }
    .step-pending {
        background: rgba(255,255,255,0.3);
        color: white;
    }
    .step-line {
        flex: 1;
        height: 3px;
        background: rgba(255,255,255,0.3);
        margin: 0 5px;
    }
    .step-line.active {
        background: #ffd700;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="workflow-progress">', unsafe_allow_html=True)
    st.markdown("### 🗺️ Your Design Workflow", unsafe_allow_html=True)
    
    # Progress bar
    progress_pct = (current / 5) * 100 if current > 0 else 0
    st.progress(progress_pct / 100, text=f"Step {current}/5")
    
    # Step details
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("**Current Status:**")
        if current == 0:
            st.info("👈 Start by selecting a disease")
        elif current == 5:
            st.success("✅ Workflow Complete!")
        else:
            current_step = next((s for s in WORKFLOW_STEPS if s["number"] == current), None)
            if current_step:
                st.info(f"📍 **{current_step['emoji']} Step {current}:** {current_step['title']}")
    
    with col2:
        st.markdown("**Next Actions:**")
        if current == 0:
            st.markdown("1. Go to **Disease Selection**\n2. Choose HCC subtype\n3. Select therapeutic drug")
        elif current == 1:
            st.markdown("1. Click **Continue to Design Parameters**\n2. Review parameter recommendations\n3. View FDA trial data")
        elif current == 2:
            st.markdown("1. Click **Continue to Design Calibration**\n2. Use sliders to tune parameters\n3. Monitor real-time score")
        elif current == 3:
            st.markdown("1. Click **Save to Trial History**\n2. View other designs\n3. Export for analysis")
        elif current == 5:
            st.markdown("✨ You can:\n- Create another trial\n- Compare multiple designs\n- Export results")
    
    with col3:
        st.markdown("**Navigation:**")
        for step in WORKFLOW_STEPS:
            if step["number"] <= current:
                st.success(f"✅ Step {step['number']}")
            else:
                st.write(f"⏳ Step {step['number']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_step_header(step_number):
    """Render header for a specific step"""
    step = next((s for s in WORKFLOW_STEPS if s["number"] == step_number), None)
    if not step:
        return
    
    st.markdown(f"""
    <div class="calibration-card">
        <h2>{step['emoji']} Step {step['number']}: {step['title']}</h2>
        <p>{step['description']}</p>
    </div>
    """, unsafe_allow_html=True)

def render_navigation_buttons(current_step, next_step_page=None, prev_step_page=None):
    """Render Next/Previous navigation buttons with validation"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if prev_step_page:
            if st.button("⬅️ Back", use_container_width=True):
                st.switch_page(prev_step_page)
    
    with col3:
        if next_step_page:
            # Check if current step is complete
            step = next((s for s in WORKFLOW_STEPS if s["number"] == current_step), None)
            if step:
                required_fields = step["required_fields"]
                all_complete = all(
                    field in st.session_state and st.session_state[field] is not None 
                    for field in required_fields
                )
                
                if all_complete:
                    if st.button("Next ➡️", use_container_width=True):
                        st.switch_page(next_step_page)
                else:
                    st.button("Next ➡️", use_container_width=True, disabled=True)
                    st.caption("⚠️ Complete this step first")
            else:
                if st.button("Next ➡️", use_container_width=True):
                    st.switch_page(next_step_page)

def render_quick_start_guide():
    """Render quick start guide for new users"""
    with st.expander("📖 Quick Start Guide - How to Design Your NanoParticle", expanded=False):
        st.markdown("""
        ### 5-Step Nanoparticle Design Workflow
        
        **Step 1: Disease Selection** 🏥
        - Choose hepatocellular carcinoma (HCC) subtype: Small, Medium, or Large
        - Select therapeutic drug: Atezolizumab, Bevacizumab, Sorafenib, or Combination
        - System generates unique Trial ID automatically
        - Time: ~2 minutes
        
        **Step 2: Design Parameters** 📋
        - Review recommended nanoparticle parameters
        - See clinical trial data for your drug
        - Understand why each parameter matters
        - No action needed - just review
        - Time: ~3 minutes
        
        **Step 3: Design Calibration** ⚙️
        - Manually adjust particle size, charge, PEG coating, drug loading
        - Watch real-time optimization score update
        - See parameter analysis and warnings
        - Fine-tune based on your requirements
        - Time: ~5 minutes
        
        **Step 5: Trial History** 📊
        - View all your past designs
        - Compare up to 3 trials side-by-side
        - Export results as JSON or CSV
        - Track your design evolution
        - Time: ~2 minutes
        
        ---
        **💡 Pro Tips:**
        - Each trial gets a unique ID like: `TRIAL-HCC-L-NP65-20260316-00147`
        - You can go back and modify designs
        - Design scores range 0-100 (higher is better)
        - Recommended values are science-backed, but you can experiment
        """)
