"""
Navigation Configuration Module
Defines the unified sidebar navigation structure for NanoBio Studio
"""

# Main navigation structure - Only visible when logged in
NAVIGATION_STRUCTURE = {
    
    "🧪 NP Design Workflow": {
        "description": "Design nanoparticles for disease targeting",
        "pages": [
            {
                "name": "1️⃣ Disease Selection",
                "file": "pages/00_Disease_Selection.py",
                "description": "Select cancer type, subtype, and drug"
            },
            {
                "name": "2️⃣ Design Parameters",
                "file": "pages/01_Design_Parameters.py",
                "description": "View auto-populated NP specifications"
            },
            {
                "name": "3️⃣ Design Calibration",
                "file": "pages/02_Design_Calibration.py",
                "description": "Manually tune NP parameters with real-time scoring"
            },
            {
                "name": "4️⃣ AI Co-Designer",
                "file": "pages/9_AI_Co_Designer.py",
                "description": "AI-powered design optimization"
            },
            {
                "name": "5️⃣ Trial History",
                "file": "pages/10_Trial_History.py",
                "description": "View and archive completed trials"
            }
        ]
    },
    
    "📊 Analytics & Visualization": {
        "description": "View data dashboards and analytics",
        "pages": [
            {
                "name": "Data Analytics",
                "file": "pages/17_Data_Analytics.py",
                "description": "Interactive charts and visualizations"
            },
            {
                "name": "External Data Sources",
                "file": "pages/15_External_Data_Sources.py",
                "description": "Data integration from 6 external sources"
            }
        ]
    },
    
    "🤖 Machine Learning": {
        "description": "ML training and model management",
        "pages": [
            {
                "name": "ML Training",
                "file": "pages/12_ML_Training.py",
                "description": "Train ML models on NP design data"
            },
            {
                "name": "Model Management",
                "file": "pages/14_Model_Management.py",
                "description": "Manage ML models and versions"
            }
        ]
    },
    
    "💾 Data Management": {
        "description": "Manage data and records",
        "pages": []
    },
    
    "📚 Learning & Info": {
        "description": "Learn about features and AI Co-Designer",
        "pages": [
            {
                "name": "Tutorial",
                "file": "pages/10_Tutorial.py",
                "description": "Step-by-step user guide"
            },
            {
                "name": "Features Overview",
                "file": "pages/0_Features.py",
                "description": "Overview of all features"
            },
            {
                "name": "About AI Co-Designer",
                "file": "pages/About_AI_Co_Designer.py",
                "description": "How AI Co-Designer works"
            }
        ]
    },
    
    "⚙️ Administration": {
        "description": "Admin tools and settings",
        "pages": [
            {
                "name": "Admin Panel",
                "file": "pages/Admin.py",
                "description": "System administration"
            }
        ]
    }
}

# Get all pages for Streamlit navigation
def get_all_pages():
    """Extract all pages from navigation structure"""
    pages = []
    for category, config in NAVIGATION_STRUCTURE.items():
        if "pages" in config:
            page_list = config["pages"]
            # Handle both string and dict formats
            for page in page_list:
                if isinstance(page, dict):
                    pages.append(page)
    return pages

# Get category for a page
def get_page_category(file_path: str):
    """Find which category a page belongs to"""
    for category, config in NAVIGATION_STRUCTURE.items():
        if "pages" in config:
            for page in config["pages"]:
                if isinstance(page, dict) and page.get("file") == file_path:
                    return category
    return None
