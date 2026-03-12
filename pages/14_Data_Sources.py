"""
Data Sources Documentation Page
Comprehensive guide to finding training data for toxicity prediction models
"""

import streamlit as st

st.set_page_config(
    page_title="Data Sources",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Data Sources & Resources")
st.markdown("Comprehensive guide to finding training data for toxicity prediction and nanoparticle research")

# Navigation
st.sidebar.header("📑 Navigation")
section = st.sidebar.radio(
    "Select Section:",
    [
        "🎯 Quick Start",
        "🔬 Nanoparticle Databases",
        "🧪 Toxicity Datasets",
        "🧬 General Biotech",
        "🔍 Search Keywords",
        "📖 Research Papers",
        "⚡ Pro Tips"
    ]
)

st.divider()

# ==================== QUICK START ====================
if section == "🎯 Quick Start":
    st.header("🎯 Quick Start Guide")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Get Started Today")
        st.markdown("""
        **Top 3 Places to Download Data:**
        
        1. **Kaggle** - Largest AI community with datasets
           - [kaggle.com/datasets](https://www.kaggle.com/datasets)
           - Search: "toxicity prediction"
        
        2. **PubChem** - US NIH chemical database
           - [pubchem.ncbi.nlm.nih.gov](https://pubchem.ncbi.nlm.nih.gov)
           - Free access to millions of compounds
        
        3. **GitHub** - Code & data repositories
           - [github.com](https://github.com)
           - Search: "nanoparticle dataset" or "toxicity data"
        """)
    
    with col2:
        st.subheader("📊 This Week Plan")
        st.markdown("""
        **Action Items:**
        
        ✅ **Day 1-2:** Download from Kaggle
           - Filter by "toxicity" and "bioassay"
           - Look for CSV format
        
        ✅ **Day 3-4:** Explore PubChem API
           - Query nanoparticle properties
           - Export screening data
        
        ✅ **Day 5-7:** Check eNanoMapper
           - Rich nanoparticle database
           - Safety & toxicity data
        """)
    
    st.divider()
    
    st.subheader("💡 File Format Guide")
    st.info("""
    **Preferred Formats:** CSV, Excel, JSON
    
    **What to Look For:**
    - ✅ Training data (features: compound properties, nanoparticle characteristics)
    - ✅ Labels (outcomes: toxicity levels, IC50 values, cell viability %)
    - ✅ Documentation (data dictionary, units, measurement methods)
    - ✅ Sample size (1000+ records for ML)
    """)

# ==================== NANOPARTICLE DATABASES ====================
elif section == "🔬 Nanoparticle Databases":
    st.header("🔬 Nanoparticle & LNP Databases")
    
    databases = [
        {
            "name": "eNanoMapper",
            "url": "https://data.enanomapper.net",
            "description": "Comprehensive European nanoparticle properties database",
            "data_type": "Physicochemical properties, safety data, toxicity",
            "access": "Free",
            "format": "Web interface, API available",
            "size": "50,000+ nanoparticles"
        },
        {
            "name": "ENPRA",
            "url": "https://www.enpra.de",
            "description": "European Nanomaterial Properties Registry",
            "data_type": "Nanoparticle characterization, safety assessment",
            "access": "Free",
            "format": "Database queries, Download",
            "size": "10,000+ entries"
        },
        {
            "name": "NanoHub",
            "url": "https://nanohub.org/resources/nanoparticles",
            "description": "Community resource for nanotech research",
            "data_type": "Simulation results, experimental data",
            "access": "Free",
            "format": "Web portal, Data download",
            "size": "Extensive research collection"
        },
        {
            "name": "PubNano",
            "url": "https://pubnano.org",
            "description": "Nanoparticle properties and safety database",
            "data_type": "Properties, applications, toxicity",
            "access": "Free",
            "format": "Database, Publication data",
            "size": "Published studies database"
        },
        {
            "name": "CEBS",
            "url": "https://cebs.niehs.nih.gov",
            "description": "Chemical Effects in Biological Systems",
            "data_type": "Toxicology, bioassay screening",
            "access": "Free (US NIH)",
            "format": "Database queries, Download",
            "size": "Millions of bioassay records"
        }
    ]
    
    for db in databases:
        with st.expander(f"🔹 {db['name']}"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"**URL:** [{db['url']}]({db['url']})")
                st.markdown(f"**Description:** {db['description']}")
                st.markdown(f"**Data Type:** {db['data_type']}")
            
            with col2:
                st.markdown(f"**Access:** 🟢 {db['access']}")
                st.markdown(f"**Format:** {db['format']}")
                st.markdown(f"**Size:** {db['size']}")

# ==================== TOXICITY DATASETS ====================
elif section == "🧪 Toxicity Datasets":
    st.header("🧪 Toxicity & Chemical Screening Datasets")
    
    st.subheader("🎯 Machine Learning Datasets (Ready-to-use)")
    
    ml_datasets = [
        {
            "name": "Kaggle Toxicity Datasets",
            "url": "https://www.kaggle.com/search?q=toxicity",
            "formats": ["CSV", "Excel", "Parquet"],
            "features": "Multiple toxicity prediction datasets available",
            "cost": "Free"
        },
        {
            "name": "Tox21 Challenge",
            "url": "https://tripod.nih.gov/tox21/challenge/data",
            "formats": ["CSV", "SDF"],
            "features": "21 toxicity endpoints, 7000+ compounds",
            "cost": "Free"
        },
        {
            "name": "SIDER",
            "url": "http://sideeffects.embl.de",
            "formats": ["Download TSV"],
            "features": "Side effects & drug toxicity data",
            "cost": "Free"
        },
        {
            "name": "DrugMatrix",
            "url": "https://www.drugmatrix.org",
            "formats": ["Database queries"],
            "features": "Comprehensive toxicology database",
            "cost": "Free registration"
        }
    ]
    
    for ds in ml_datasets:
        with st.expander(f"📊 {ds['name']}"):
            st.markdown(f"**Link:** [{ds['url']}]({ds['url']})")
            st.markdown(f"**Formats:** {', '.join(ds['formats'])}")
            st.markdown(f"**Features:** {ds['features']}")
            st.markdown(f"**Cost:** {ds['cost']}")
    
    st.divider()
    
    st.subheader("🧬 General Chemical Databases")
    
    chem_databases = [
        {
            "name": "PubChem",
            "url": "https://pubchem.ncbi.nlm.nih.gov",
            "description": "Millions of chemical compounds with bioassay data",
            "access": "Free, API available"
        },
        {
            "name": "ChEMBL",
            "url": "https://www.ebi.ac.uk/chembl",
            "description": "Curated drug discovery database with activity data",
            "access": "Free, REST API"
        },
        {
            "name": "DrugBank",
            "url": "https://www.drugbank.ca",
            "description": "Drug compound information and interactions",
            "access": "Free web access"
        },
        {
            "name": "ZINC",
            "url": "https://zinc.docking.org",
            "description": "Virtual screening database of purchasable compounds",
            "access": "Free downloads"
        }
    ]
    
    for db in chem_databases:
        with st.expander(f"🧪 {db['name']}"):
            st.markdown(f"**URL:** [{db['url']}]({db['url']})")
            st.markdown(f"**Description:** {db['description']}")
            st.markdown(f"**Access:** {db['access']}")

# ==================== GENERAL BIOTECH ====================
elif section == "🧬 General Biotech":
    st.header("🧬 General Biotech Platforms")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Data Repositories")
        st.markdown("""
        **Zenodo**
        - [zenodo.org](https://zenodo.org)
        - Search: "nanoparticle" or "toxicity"
        - Research data & datasets
        
        **GitHub**
        - [github.com](https://github.com)
        - Search: "nanoparticle dataset"
        - Code + data repositories
        
        **Open Data Government**
        - [data.gov](https://www.data.gov)
        - US government datasets
        - NIH, EPA, FDA data
        """)
    
    with col2:
        st.subheader("🔬 Research Communities")
        st.markdown("""
        **ResearchGate**
        - [researchgate.net](https://www.researchgate.net)
        - Connect with researchers
        - Download published datasets
        
        **Google Scholar**
        - [scholar.google.com](https://scholar.google.com)
        - Search: "nanoparticle toxicity"
        - Access supplementary data
        
        **bioRxiv**
        - [biorxiv.org](https://www.biorxiv.org)
        - Preprints with datasets
        - Recent research
        """)

# ==================== SEARCH KEYWORDS ====================
elif section == "🔍 Search Keywords":
    st.header("🔍 Optimized Search Keywords")
    
    st.subheader("🎯 Core Keywords (High Relevance)")
    keywords_core = [
        "toxicity prediction nanoparticles",
        "LNP lipid nanoparticles dataset",
        "nanoparticle safety data",
        "nanotoxicity screening",
        "in vitro toxicity assay",
        "nanomaterial biocompatibility",
        "drug delivery LNP efficacy",
        "nanoparticle physicochemical properties"
    ]
    
    cols = st.columns(2)
    for idx, kw in enumerate(keywords_core):
        with cols[idx % 2]:
            st.code(f'"{kw}"', language=None)
    
    st.divider()
    
    st.subheader("📊 Platform-Specific Keywords")
    
    tabs = st.tabs(["Kaggle", "GitHub", "PubChem", "Google Scholar"])
    
    with tabs[0]:
        st.markdown("""
        ```
        toxicity prediction
        drug discovery dataset
        chemical properties
        SMILES molecules
        bioactivity screening
        protein binding
        cytotoxicity
        nanotoxicity
        ```
        """)
    
    with tabs[1]:
        st.markdown("""
        ```
        nanoparticle dataset
        toxicity prediction model
        LNP data
        drug toxicity
        chemical dataset
        machine learning biomedical
        ```
        """)
    
    with tabs[2]:
        st.markdown("""
        ```
        nanoparticles
        lipid nanoparticles
        toxicity assays
        bioassay results
        screening data
        ```
        """)
    
    with tabs[3]:
        st.markdown("""
        ```
        "nanoparticle toxicity" dataset
        "LNP" "lipid nanoparticles" screening
        "nanotoxicity" prediction
        "in vitro" toxicity assay results
        "drug delivery" efficacy data
        ```
        """)
    
    st.divider()
    
    st.subheader("🧬 Biological Assays Keywords")
    assay_keywords = [
        "MTT assay data",
        "LDH cytotoxicity",
        "apoptosis assay",
        "ROS reactive oxygen species",
        "inflammatory markers",
        "cell viability screening",
        "genotoxicity testing",
        "oxidative stress"
    ]
    
    cols = st.columns(2)
    for idx, kw in enumerate(assay_keywords):
        with cols[idx % 2]:
            st.checkbox(kw, value=True)

# ==================== RESEARCH PAPERS ====================
elif section == "📖 Research Papers":
    st.header("📖 Finding Data in Research Papers")
    
    st.info("""
    Many research papers contain supplementary data with datasets. Here's how to find and extract them:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔗 Paper Database Sources")
        st.markdown("""
        **PubMed Central**
        - [pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov)
        - Search: "nanoparticle toxicity"
        - Free full-text access
        
        **Google Scholar**
        - [scholar.google.com](https://scholar.google.com)
        - Sort by recent/most cited
        - Find supplementary materials
        
        **ResearchGate**
        - [researchgate.net](https://www.researchgate.net)
        - Download PDFs from authors
        - Request datasets directly
        """)
    
    with col2:
        st.subheader("📊 Extracting Data from PDFs")
        st.markdown("""
        **Step-by-Step:**
        
        1. Search for papers + "supplementary data"
        2. Look for data files in:
           - Table S1, S2, etc.
           - Supporting Information
           - Data Availability section
        
        3. Extract from:
           - Excel/CSV in supplements
           - Data repositories (zenodo, figshare)
           - Author's GitHub
        
        4. Tools to use:
           - Tabula (PDF table extraction)
           - Python pandas (data parsing)
        """)
    
    st.divider()
    
    st.subheader("🎯 Recommended Search Combinations")
    search_combos = [
        '"nanoparticle toxicity" dataset filetype:xlsx OR filetype:csv',
        '"LNP screening" "supplementary data"',
        '"in vitro" toxicity assay results data',
        '"machine learning" toxicity prediction dataset',
        '"drug delivery" efficacy "raw data"'
    ]
    
    for combo in search_combos:
        st.code(combo)

# ==================== PRO TIPS ====================
elif section == "⚡ Pro Tips":
    st.header("⚡ Pro Tips for Finding & Using Data")
    
    tips = [
        {
            "title": "🎯 Use Advanced Search Filters",
            "content": """
            - Add date filters: "2022-2026" for recent data
            - Filter by file type: `.csv`, `.xlsx`, `.json`
            - Look for keywords: "raw data", "training set", "supplementary"
            - Sort by: most downloaded, most relevant
            """
        },
        {
            "title": "📂 Organize Your Data",
            "content": """
            - Create folders: raw_data, processed_data, metadata
            - Keep a CSV with: source URL, download date, description
            - Document data cleaning steps
            - Store in version control (git)
            """
        },
        {
            "title": "🔍 Validate Before Using",
            "content": """
            - Check for missing values
            - Verify units and scales
            - Look for outliers
            - Ensure consistent formatting
            - Compare with original source
            """
        },
        {
            "title": "🔗 Use APIs When Available",
            "content": """
            - PubChem REST API: fetch compound data programmatically
            - ChEMBL API: query bioassay results
            - GitHub API: download files automatically
            - Avoid manual downloads when possible
            """
        },
        {
            "title": "📄 Respect Licensing",
            "content": """
            - Check license before using data
            - Prefer: MIT, CC-BY, CC0
            - Credit original sources
            - Follow data usage guidelines
            - Some data requires registration
            """
        },
        {
            "title": "🤝 Contact Researchers",
            "content": """
            - Email authors for raw data
            - Check ResearchGate/Twitter
            - Many researchers share willingly
            - Request through institutions
            - Cite their work in return
            """
        }
    ]
    
    for tip in tips:
        with st.expander(f"💡 {tip['title']}"):
            st.markdown(tip['content'])
    
    st.divider()
    
    st.subheader("🚀 Quick Reference Checklist")
    st.markdown("""
    ✅ **Before Starting:**
    - [ ] Define what data you need (toxicity types, particle sizes, etc.)
    - [ ] Set sample size goal (1000+, 5000+, 10000+)
    - [ ] Identify file formats (CSV, Excel, JSON)
    
    ✅ **During Collection:**
    - [ ] Document sources and dates
    - [ ] Check data quality and completeness
    - [ ] Standardize column names and units
    - [ ] Create metadata files
    
    ✅ **Before Training:**
    - [ ] Handle missing values
    - [ ] Normalize/scale features
    - [ ] Remove duplicates
    - [ ] Verify data splits
    - [ ] Check for bias
    
    ✅ **Documentation:**
    - [ ] Create README with data description
    - [ ] List all sources with URLs
    - [ ] Document preprocessing steps
    - [ ] Include license information
    """)

# Footer
st.divider()
st.markdown("""
---
**💡 Need help?** This page provides links to major data sources for toxicity prediction and nanoparticle research. 
Start with the Quick Start section, then explore specific databases for your research needs.

**Last Updated:** March 12, 2026
""")
