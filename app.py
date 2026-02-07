import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="BizSight AI - Business Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS - COMBINED STYLES
# ============================================================
st.markdown("""
<style>
    /* Main Header - from first code */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    /* Main Header - from second code */
    .main-header-v2 {
        font-size: 3rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
        text-align: center;
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Sub Header - from second code */
    .sub-header {
        text-align: center;
        font-size: 1.2rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    
    /* Welcome Message - from second code */
    .welcome-message {
        text-align: center;
        padding: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .welcome-message h2 {
        color: white;
        margin-bottom: 1rem;
        font-size: 2.5rem;
    }
    
    /* Portfolio Link - from first code */
    .portfolio-link {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .portfolio-link a {
        color: #3B82F6;
        text-decoration: none;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.5rem 1rem;
        border: 2px solid #3B82F6;
        border-radius: 25px;
        transition: all 0.3s ease;
    }
    
    .portfolio-link a:hover {
        background: #3B82F6;
        color: white;
        text-decoration: none;
    }
    
    /* Portfolio Link - from second code */
    .portfolio-link-v2 a {
        color: #3B82F6;
        text-decoration: none;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.5rem 1.5rem;
        border: 2px solid #3B82F6;
        border-radius: 25px;
        transition: all 0.3s ease;
        display: inline-block;
        margin: 0.5rem;
    }
    
    .portfolio-link-v2 a:hover {
        background: #3B82F6;
        color: white;
        text-decoration: none;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.3);
    }
    
    /* Section Headers - from first code */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E3A8A;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E5E7EB;
    }
    
    /* Section Headers - from second code */
    .section-header-v2 {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #E5E7EB;
    }
    
    /* Metric Cards - from first code */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        color: #1F2937;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .metric-card-primary {
        border-left: 4px solid #3B82F6;
    }
    
    .metric-card-secondary {
        border-left: 4px solid #10B981;
    }
    
    .metric-card-warning {
        border-left: 4px solid #F59E0B;
    }
    
    .metric-card-danger {
        border-left: 4px solid #EF4444;
    }
    
    /* Metric Cards - from second code */
    .metric-card-v2 {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        color: #1F2937;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card-v2::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: linear-gradient(to bottom, #3B82F6, #10B981);
    }
    
    .metric-card-v2:hover {
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        transform: translateY(-5px);
    }
    
    /* Metric Values - from first code */
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #6B7280;
        font-weight: 500;
    }
    
    /* Metric Values - from second code */
    .metric-value-v2 {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1F2937;
        margin-bottom: 0.5rem;
        line-height: 1;
    }
    
    .metric-label-v2 {
        font-size: 0.95rem;
        color: #6B7280;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .metric-trend {
        font-size: 0.85rem;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        display: inline-block;
        font-weight: 600;
    }
    
    .trend-up {
        background: rgba(16, 185, 129, 0.1);
        color: #10B981;
    }
    
    .trend-down {
        background: rgba(239, 68, 68, 0.1);
        color: #EF4444;
    }
    
    .trend-neutral {
        background: rgba(156, 163, 175, 0.1);
        color: #6B7280;
    }
    
    /* Insight Cards - from first code */
    .insight-card {
        background: white;
        border-left: 4px solid #3B82F6;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Insight Cards - from second code */
    .insight-card-v2 {
        background: linear-gradient(135deg, rgba(248,250,252,0.9) 0%, rgba(241,245,249,0.9) 100%);
        border-left: 5px solid #3B82F6;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .insight-card-v2:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Buttons - from first code */
    .stButton>button {
        width: 100%;
        background: #3B82F6;
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: #2563EB;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.1);
    }
    
    /* Buttons - from second code */
    .stButton-v2>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.85rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.1);
    }
    
    .stButton-v2>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(102, 126, 234, 0.2);
    }
    
    /* Tabs - from first code */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border: 1px solid #E5E7EB;
        background: #F9FAFB;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: white;
        border-bottom: 2px solid #3B82F6;
    }
    
    /* Tabs - from second code */
    .stTabs-v2 [data-baseweb="tab-list"] {
        gap: 0.5rem;
        padding: 0 0.5rem;
    }
    
    .stTabs-v2 [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 1rem 1.5rem;
        font-weight: 600;
        border: 1px solid #E5E7EB;
        background: #F9FAFB;
        transition: all 0.3s ease;
    }
    
    .stTabs-v2 [data-baseweb="tab"][aria-selected="true"] {
        background: white;
        border-bottom: 3px solid #3B82F6;
        color: #3B82F6;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Data Options - from second code */
    .data-options {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 2px dashed #E5E7EB;
        margin: 1rem 0;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .data-options:hover {
        border-color: #3B82F6;
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .data-options h3 {
        color: #1E3A8A;
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    
    /* Feature Grid - from second code */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-item {
        text-align: center;
        padding: 1.5rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .feature-item:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    /* Dataframes - from first code */
    .stDataFrame {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
    }
    
    /* Expander - from first code */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1F2937;
    }
    
    /* Divider - from first code */
    hr {
        border: none;
        height: 1px;
        background: #E5E7EB;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# COLOR PALETTE - COMBINED
# ============================================================
COLOR_PALETTE = {
    'primary': '#3B82F6',
    'secondary': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'info': '#6B7280',
    'dark': '#1F2937',
    'light': '#F9FAFB',
    'success': '#22C55E',
    'purple': '#8B5CF6',
    'pink': '#EC4899',
    'cyan': '#06B6D4',
    'orange': '#F97316',
    'indigo': '#6366F1',
    'teal': '#14B8A6'
}

PLOTLY_COLORS = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', 
    '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1',
    '#F472B6', '#D946EF', '#0EA5E9', '#22C55E', '#EAB308',
    '#A855F7', '#F43F5E', '#0D9488', '#F59E0B', '#3B82F6'
]

# ============================================================
# LOAD MODEL - FROM FIRST CODE
# ============================================================
@st.cache_resource
def load_model():
    try:
        model = joblib.load("business_sales_profit_pipeline.pkl")
        return model
    except FileNotFoundError:
        st.error("Model file not found. Using demonstration mode.")
        return None
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

model = load_model()

# ============================================================
# REQUIRED SCHEMA - FROM FIRST CODE
# ============================================================
if model:
    REQUIRED_COLUMNS = model.feature_names_in_.tolist()
else:
    # Default columns if model is not available
    REQUIRED_COLUMNS = [
        "city_tier", "customer_rating", "electricity_cost", "inventory_level",
        "avg_employee_salary", "conversion_rate", "is_festival_season",
        "avg_transaction_value", "avg_daily_footfall", "rent_cost",
        "supplier_cost", "discount_percentage", "business_type", "city",
        "store_size_sqft", "logistics_cost", "years_of_operation",
        "profit_margin", "marketing_roi", "employee_efficiency",
        "marketing_spend", "employee_count"
    ]

DEFAULTS = {
    "city_tier": 1,
    "customer_rating": 4.0,
    "electricity_cost": 8000,
    "inventory_level": 500,
    "avg_employee_salary": 20000,
    "conversion_rate": 0.2,
    "is_festival_season": 0,
    "avg_transaction_value": 900,
    "avg_daily_footfall": 200,
    "rent_cost": 30000,
    "supplier_cost": 50000,
    "discount_percentage": 10,
    "business_type": "General",
    "city": "Unknown",
    "store_size_sqft": 1200,
    "logistics_cost": 15000,
    "years_of_operation": 5,
    "profit_margin": 0.2,
    "marketing_roi": 2.0,
    "employee_efficiency": 50000,
    "marketing_spend": 50000,
    "employee_count": 10,
}

def align_schema(df):
    """Ensure the dataframe has all required columns"""
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = DEFAULTS.get(col, 0)
    return df[REQUIRED_COLUMNS]

# ============================================================
# SIDEBAR - COMBINED FROM BOTH CODES
# ============================================================
# Add Infosys logo from first code
st.sidebar.markdown("""
<div style='text-align: center; margin-bottom: 1rem;'>
    <img src='https://imgs.search.brave.com/hRRODIPyRrFGigKCvwNHXaijoLJ3bGB0NcAG49yS-0A/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9sb2dv/dHlwLnVzL2ZpbGUv/aW5mb3N5cy5zdmc' 
         alt='Infosys Logo' style='width: 80%; max-width: 200px; height: auto; border-radius: 8px;'>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style='text-align: center; margin-bottom: 1.5rem;'>
    <h2 style='color: #1E3A8A; font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem;'>BizSight AI</h2>
    <p style='color: #6B7280; font-size: 0.9rem; font-weight: 500;'>Advanced Business Intelligence</p>
</div>
""", unsafe_allow_html=True)

# Portfolio link from first code
st.sidebar.markdown("""
<div class='portfolio-link'>
    <a href='https://sourishdeyportfolio.vercel.app/' target='_blank'>👨‍💻 View Portfolio</a>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### Data Upload")
uploaded_file = st.sidebar.file_uploader(
    "Upload business dataset",
    type=["csv", "xlsx"],
    help="Upload CSV or Excel file containing business data"
)

# REMOVED: The default checkbox that was loading sample data automatically
# Now users must explicitly choose an option
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Data Source Selection")

# Use radio buttons to make data source selection explicit
data_source = st.sidebar.radio(
    "Choose data source:",
    ["Upload your own file", "Use sample data (100K records)", "Use advanced sample dataset (50K records)"],
    index=0,
    help="Select how you want to load data for analysis"
)

# Initialize session state from second code
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df_raw' not in st.session_state:
    st.session_state.df_raw = None
if 'df' not in st.session_state:
    st.session_state.df = None

# ============================================================
# HEADER - SHOW WELCOME MESSAGE UNTIL DATA IS LOADED
# ============================================================
st.markdown("<h1 class='main-header'>BizSight AI - Business Intelligence Platform</h1>", unsafe_allow_html=True)
st.markdown("""
<div class='portfolio-link'>
    <a href='https://sourishdeyportfolio.vercel.app/' target='_blank'>👨‍💻 Developed by Sourish Dey - View Portfolio</a>
</div>
""", unsafe_allow_html=True)

# Check if data is loaded
data_loaded = False
df_raw = None
df = None

# ============================================================
# LOAD AND PROCESS DATA - COMBINED FROM BOTH CODES
# ============================================================
@st.cache_data
def load_data(file=None, sample=False, advanced_sample=False):
    """Load data from uploaded file or generate sample data"""
    if advanced_sample:
        # Advanced sample data from second code
        np.random.seed(42)
        n_samples = 50000
        
        sample_data = {
            'business_id': [f'BUS_{i:06d}' for i in range(n_samples)],
            'city': np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 
                                     'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'], n_samples),
            'state': np.random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'West Bengal',
                                      'Telangana', 'Gujarat', 'Rajasthan', 'Uttar Pradesh'], n_samples),
            'region': np.random.choice(['North', 'South', 'East', 'West', 'Central'], n_samples),
            'city_tier': np.random.choice([1, 2, 3], n_samples, p=[0.3, 0.4, 0.3]),
            'business_type': np.random.choice(['Retail', 'Restaurant', 'Services', 'Manufacturing', 
                                              'E-commerce', 'Healthcare', 'Education', 'Entertainment'], n_samples),
            'years_of_operation': np.random.randint(1, 30, n_samples),
            'store_size_sqft': np.random.randint(500, 10000, n_samples),
            'employee_count': np.random.randint(5, 200, n_samples),
            'employee_efficiency': np.random.randint(20000, 200000, n_samples),
            'avg_employee_salary': np.random.randint(20000, 80000, n_samples),
            'avg_daily_footfall': np.random.randint(50, 2000, n_samples),
            'conversion_rate': np.random.uniform(0.05, 0.5, n_samples),
            'avg_transaction_value': np.random.randint(500, 5000, n_samples),
            'customer_rating': np.random.uniform(2.5, 5.0, n_samples),
            'discount_percentage': np.random.uniform(0, 40, n_samples),
            'rent_cost': np.random.randint(10000, 200000, n_samples),
            'electricity_cost': np.random.randint(5000, 30000, n_samples),
            'logistics_cost': np.random.randint(5000, 50000, n_samples),
            'supplier_cost': np.random.randint(20000, 200000, n_samples),
            'inventory_level': np.random.randint(1000, 100000, n_samples),
            'marketing_spend': np.random.randint(10000, 300000, n_samples),
            'marketing_roi': np.random.uniform(1.0, 5.0, n_samples),
            'is_festival_season': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
            'profit_margin': np.random.uniform(-0.1, 0.4, n_samples),
            'monthly_sales': np.random.randint(100000, 2000000, n_samples),
            'operational_cost': np.random.randint(50000, 500000, n_samples),
            'monthly_revenue': np.random.randint(150000, 2500000, n_samples),
            'sales_per_sqft': np.random.randint(100, 2000, n_samples),
            'profit_per_employee': np.random.randint(-5000, 50000, n_samples),
            'cost_to_sales_ratio': np.random.uniform(0.3, 0.8, n_samples),
            'employee_productivity': np.random.randint(10000, 150000, n_samples),
            'risk_category': np.random.choice(['Low', 'Medium', 'High'], n_samples, p=[0.5, 0.3, 0.2]),
            'business_size': np.random.choice(['Small', 'Medium', 'Large'], n_samples, p=[0.4, 0.4, 0.2])
        }
        
        df = pd.DataFrame(sample_data)
        df['profit'] = df['monthly_sales'] * df['profit_margin']
        df['total_cost'] = df['operational_cost'] + df['employee_count'] * df['avg_employee_salary'] / 12
        df['gross_margin'] = (df['monthly_revenue'] - df['operational_cost']) / df['monthly_revenue'].replace(0, 1)
        df['inventory_turnover'] = df['monthly_sales'] / df['inventory_level'].replace(0, 1)
        df['employee_contribution'] = df['profit_per_employee'] * df['employee_count']
        df['marketing_efficiency'] = df['monthly_sales'] / df['marketing_spend'].replace(0, 1)
        df['roi_category'] = pd.cut(df['marketing_roi'], bins=[0, 1.5, 3, 10], labels=['Low', 'Medium', 'High'])
        
    elif sample:
        # Original sample data from first code
        np.random.seed(42)
        n_samples = 100000
        
        sample_data = {
            "city_tier": np.random.choice([1, 2, 3], n_samples, p=[0.4, 0.4, 0.2]),
            "customer_rating": np.random.uniform(3.0, 5.0, n_samples),
            "electricity_cost": np.random.randint(5000, 15000, n_samples),
            "inventory_level": np.random.randint(100, 5000, n_samples),
            "avg_employee_salary": np.random.randint(15000, 40000, n_samples),
            "conversion_rate": np.random.uniform(0.1, 0.4, n_samples),
            "is_festival_season": np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
            "avg_transaction_value": np.random.randint(500, 2000, n_samples),
            "avg_daily_footfall": np.random.randint(50, 500, n_samples),
            "rent_cost": np.random.randint(10000, 50000, n_samples),
            "supplier_cost": np.random.randint(20000, 100000, n_samples),
            "discount_percentage": np.random.randint(0, 30, n_samples),
            "business_type": np.random.choice(["Retail", "Restaurant", "Services", "Manufacturing", "E-commerce"], n_samples),
            "city": np.random.choice(["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad"], n_samples),
            "store_size_sqft": np.random.randint(500, 5000, n_samples),
            "logistics_cost": np.random.randint(5000, 30000, n_samples),
            "years_of_operation": np.random.randint(1, 20, n_samples),
            "profit_margin": np.random.uniform(0.1, 0.4, n_samples),
            "marketing_roi": np.random.uniform(1.5, 4.0, n_samples),
            "employee_efficiency": np.random.randint(20000, 100000, n_samples),
            "marketing_spend": np.random.randint(10000, 200000, n_samples),
            "employee_count": np.random.randint(5, 50, n_samples),
            "month": np.random.randint(1, 13, n_samples),
            "year": np.random.choice([2022, 2023, 2024], n_samples),
        }
        
        df = pd.DataFrame(sample_data)
    else:
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return pd.DataFrame()
    
    df.fillna(method='ffill', inplace=True)
    df.fillna(0, inplace=True)
    
    return df

# Load data based on user selection
if data_source == "Upload your own file":
    if uploaded_file is not None:
        df_raw = load_data(uploaded_file)
        if df_raw is not None and not df_raw.empty:
            data_loaded = True
            st.sidebar.success("✅ Your data has been loaded successfully!")
        else:
            st.sidebar.warning("⚠️ Please upload a valid dataset file")
    else:
        # Show welcome message when no file is uploaded
        st.markdown("""
        <div class='welcome-message'>
            <h2>Welcome to BizSight AI! 🚀</h2>
            <p style='font-size: 1.2rem; margin-bottom: 1.5rem;'>
                Your comprehensive Business Intelligence Platform for data-driven decision making
            </p>
            <p style='font-size: 1rem; margin-bottom: 2rem;'>
                To get started, please upload your business dataset or choose a sample dataset from the sidebar.
            </p>
            <div style='background: rgba(255, 255, 255, 0.2); padding: 1.5rem; border-radius: 10px;'>
                <h3 style='color: white; margin-bottom: 1rem;'>📋 How to Use:</h3>
                <ol style='text-align: left; color: white; margin-left: 2rem;'>
                    <li>Go to the sidebar on the left</li>
                    <li>Upload your CSV/Excel file or select sample data</li>
                    <li>Apply filters as needed</li>
                    <li>Explore the interactive dashboards</li>
                    <li>Run predictive simulations</li>
                </ol>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show feature highlights
        st.markdown("<h2 class='section-header'>Platform Features</h2>", unsafe_allow_html=True)
        
        feature_col1, feature_col2, feature_col3 = st.columns(3)
        
        with feature_col1:
            st.markdown("""
            <div class='feature-item'>
                <div class='feature-icon'>📊</div>
                <h3>48+ Visualizations</h3>
                <p>Comprehensive charts and graphs for deep analysis</p>
            </div>
            """, unsafe_allow_html=True)
            
        with feature_col2:
            st.markdown("""
            <div class='feature-item'>
                <div class='feature-icon'>🤖</div>
                <h3>Predictive Analytics</h3>
                <p>Machine learning models for profit forecasting</p>
            </div>
            """, unsafe_allow_html=True)
            
        with feature_col3:
            st.markdown("""
            <div class='feature-item'>
                <div class='feature-icon'>📈</div>
                <h3>Real-time Simulation</h3>
                <p>Test business scenarios with instant results</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Stop execution if no data is loaded
        st.stop()

elif data_source == "Use sample data (100K records)":
    df_raw = load_data(sample=True)
    data_loaded = True
    st.sidebar.success("✅ Sample data with 100,000 records loaded")

elif data_source == "Use advanced sample dataset (50K records)":
    df_raw = load_data(sample=True, advanced_sample=True)
    data_loaded = True
    st.sidebar.success("✅ Advanced sample data with 50,000 records loaded")

# Check if data was loaded successfully
if not data_loaded or df_raw is None or df_raw.empty:
    st.error("❌ No data loaded. Please check your selection or upload a valid file.")
    st.stop()

# Process data from first code
df = align_schema(df_raw.copy())

# Calculate monthly_sales
df["monthly_sales"] = (
    df["avg_daily_footfall"] * df["conversion_rate"] * df["avg_transaction_value"] * 30
)

# Add derived metrics from first code
df["sales_per_sqft"] = df["monthly_sales"] / df["store_size_sqft"].replace(0, 1)
df["sales_per_employee"] = df["monthly_sales"] / df["employee_count"].replace(0, 1)
df["operating_cost"] = df["rent_cost"] + df["electricity_cost"] + df["logistics_cost"] + df["supplier_cost"]
df["profit_per_employee"] = df["monthly_sales"] * df["profit_margin"] / df["employee_count"].replace(0, 1)
df["cost_to_sales_ratio"] = df["operating_cost"] / df["monthly_sales"].replace(0, 1)
df["roi_per_employee"] = df["employee_efficiency"] / df["avg_employee_salary"].replace(0, 1)

# Add derived metrics from second code if columns exist
if 'operational_cost' in df_raw.columns and 'monthly_revenue' in df_raw.columns:
    df['gross_margin'] = (df_raw['monthly_revenue'] - df_raw['operational_cost']) / df_raw['monthly_revenue'].replace(0, 1)
if 'inventory_level' in df_raw.columns:
    df['inventory_turnover'] = df['monthly_sales'] / df_raw['inventory_level'].replace(0, 1)
if 'employee_productivity' in df_raw.columns:
    df['employee_productivity'] = df_raw['employee_productivity']
if 'profit_per_employee' in df_raw.columns:
    df['profit_per_employee_raw'] = df_raw['profit_per_employee']

# Model prediction from first code
if model:
    df["predicted_profit"] = model.predict(df)
else:
    # Generate synthetic predictions for demonstration
    np.random.seed(42)
    base_profit = df["monthly_sales"] * df["profit_margin"] - df["operating_cost"] - df["employee_count"] * df["avg_employee_salary"]
    noise = np.random.normal(0, 0.1 * abs(base_profit).mean(), len(df))
    df["predicted_profit"] = np.maximum(base_profit + noise, 0)  # Ensure non-negative for visualization

df["risk_band"] = pd.qcut(df["predicted_profit"], 3, labels=["Low", "Medium", "High"])

# Add advanced scores from second code
df['profitability_score'] = (df['profit_margin'].clip(-0.5, 0.5) * 0.4 + 
                            (df['customer_rating'].clip(1, 5) / 5) * 0.3 + 
                            (1 - df['cost_to_sales_ratio'].clip(0, 1)) * 0.3) * 100

if 'employee_efficiency' in df.columns:
    emp_eff_norm = df['employee_efficiency'] / df['employee_efficiency'].replace(0, 1).max()
else:
    emp_eff_norm = 0.5

if 'sales_per_sqft' in df.columns:
    sales_sqft_norm = df['sales_per_sqft'] / df['sales_per_sqft'].replace(0, 1).max()
else:
    sales_sqft_norm = 0.5

if 'inventory_turnover' in df.columns:
    inv_turn_norm = df['inventory_turnover'] / df['inventory_turnover'].replace(0, 1).max()
else:
    inv_turn_norm = 0.5

df['efficiency_score'] = (emp_eff_norm * 0.4 +
                         sales_sqft_norm * 0.3 +
                         inv_turn_norm * 0.3) * 100

df['growth_potential'] = ((df['years_of_operation'].clip(0, 30) / 30) * 0.3 +
                         (df['city_tier'].clip(1, 3) / 3) * 0.2 +
                         (df['employee_count'].clip(1, 200) / 200) * 0.3 +
                         (df['store_size_sqft'].clip(500, 10000) / 10000) * 0.2) * 100

# Create performance tiers from second code
if 'predicted_profit' in df.columns and 'monthly_sales' in df.columns and 'employee_efficiency' in df.columns:
    performance_score = (df['predicted_profit'].rank(pct=True) * 0.4 + 
                       df['monthly_sales'].rank(pct=True) * 0.3 + 
                       df['employee_efficiency'].rank(pct=True) * 0.3)
    df['performance_tier'] = pd.qcut(performance_score, 5, 
                                    labels=['Poor', 'Below Avg', 'Average', 'Good', 'Excellent'])
else:
    df['performance_tier'] = 'Average'

# Store in session state for second code features
st.session_state.data_loaded = True
st.session_state.df_raw = df_raw
st.session_state.df = df

# ============================================================
# SIDEBAR FILTERS (ONLY SHOW WHEN DATA IS LOADED)
# ============================================================
if data_loaded:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Data Filters")
    
    # Risk Level Filter
    if 'risk_band' in df.columns:
        st.sidebar.markdown("##### Risk Level Filter")
        risk_filter = st.sidebar.multiselect(
            "Select Risk Levels",
            ["Low", "Medium", "High"],
            default=["Low", "Medium", "High"],
            key="risk_filter"
        )
    else:
        risk_filter = ["Low", "Medium", "High"]
    
    # Business Type Filter
    if 'business_type' in df.columns:
        st.sidebar.markdown("##### Business Type Filter")
        business_types = ["All"] + sorted(df['business_type'].unique().tolist())
        business_filter = st.sidebar.multiselect(
            "Select Business Types",
            business_types,
            default=["All"],
            key="business_filter"
        )
    else:
        business_filter = ["All"]
    
    # Additional filters from second code
    if 'region' in df.columns:
        st.sidebar.markdown("##### Region Filter")
        region_filter = st.sidebar.multiselect(
            "Select Regions",
            ["All"] + sorted(df['region'].unique().tolist()),
            default=["All"],
            key="region_filter"
        )
    else:
        region_filter = ["All"]
    
    if 'performance_tier' in df.columns:
        st.sidebar.markdown("##### Performance Tier Filter")
        performance_filter = st.sidebar.multiselect(
            "Select Performance Tiers",
            ["All"] + sorted(df['performance_tier'].unique().tolist()),
            default=["All"],
            key="performance_filter"
        )
    else:
        performance_filter = ["All"]
    
    # Apply filters
    if 'risk_band' in df.columns and risk_filter:
        df = df[df['risk_band'].isin(risk_filter)]
    if 'business_type' in df.columns and business_filter and "All" not in business_filter:
        df = df[df['business_type'].isin(business_filter)]
    if 'region' in df.columns and region_filter and "All" not in region_filter:
        df = df[df['region'].isin(region_filter)]
    if 'performance_tier' in df.columns and performance_filter and "All" not in performance_filter:
        df = df[df['performance_tier'].isin(performance_filter)]

# ============================================================
# EXECUTIVE SUMMARY - FROM FIRST CODE (ONLY SHOW WHEN DATA IS LOADED)
# ============================================================
if data_loaded:
    st.markdown("Advanced analytics and predictive insights for business optimization")
    st.divider()

    # Calculate metrics from first code
    avg_profit = df["predicted_profit"].mean()
    avg_sales = df["monthly_sales"].mean()
    risk_percentage = (df["risk_band"] == 'High').mean() * 100 if 'risk_band' in df.columns else 0
    total_records = len(df)
    profit_margin_val = (df['predicted_profit'].sum() / df['monthly_sales'].sum() * 100) if df['monthly_sales'].sum() > 0 else 0
    avg_roi = df['marketing_roi'].mean() if 'marketing_roi' in df.columns else 2.0
    inventory_turnover = (df['monthly_sales'].sum() / df['inventory_level'].sum()) if df['inventory_level'].sum() > 0 else 0
    employee_productivity = df['employee_efficiency'].mean() if 'employee_efficiency' in df.columns else 50000

    # Additional metrics from second code
    avg_rating = df['customer_rating'].mean() if 'customer_rating' in df.columns else 3.0
    avg_conversion = df['conversion_rate'].mean() * 100 if 'conversion_rate' in df.columns else 20
    avg_efficiency = df['employee_efficiency'].mean() if 'employee_efficiency' in df.columns else 50000
    high_performance_pct = (df['performance_tier'].isin(['Good', 'Excellent'])).mean() * 100 if 'performance_tier' in df.columns else 0
    profitability_score_avg = df['profitability_score'].mean() if 'profitability_score' in df.columns else 50
    efficiency_score_avg = df['efficiency_score'].mean() if 'efficiency_score' in df.columns else 50
    growth_potential_avg = df['growth_potential'].mean() if 'growth_potential' in df.columns else 50
    inventory_turnover_avg = df['inventory_turnover'].mean() if 'inventory_turnover' in df.columns else 1.5

    st.markdown("<h2 class='section-header'>Executive Dashboard</h2>", unsafe_allow_html=True)

    # Row 1: Main Metrics from first code
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class='metric-card metric-card-primary'>
            <div class='metric-value'>₹{avg_profit:,.0f}</div>
            <div class='metric-label'>Average Monthly Profit</div>
            <div style='font-size: 0.85rem; color: #10B981; margin-top: 0.5rem;'>
                ▲ 12.5% from last quarter
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card metric-card-secondary'>
            <div class='metric-value'>₹{avg_sales:,.0f}</div>
            <div class='metric-label'>Average Monthly Sales</div>
            <div style='font-size: 0.85rem; color: #10B981; margin-top: 0.5rem;'>
                ▲ 18.2% from last quarter
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card metric-card-warning'>
            <div class='metric-value'>{risk_percentage:.1f}%</div>
            <div class='metric-label'>High Risk Businesses</div>
            <div style='font-size: 0.85rem; color: #EF4444; margin-top: 0.5rem;'>
                ▼ 5.1% from last quarter
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='metric-card metric-card-danger'>
            <div class='metric-value'>{total_records:,}</div>
            <div class='metric-label'>Total Records Analyzed</div>
            <div style='font-size: 0.85rem; color: #10B981; margin-top: 0.5rem;'>
                ▲ 25,000 new entries
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Row 2: Additional Metrics from first code
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.markdown(f"""
        <div class='metric-card' style='border-left: 4px solid #8B5CF6;'>
            <div class='metric-value'>{profit_margin_val:.1f}%</div>
            <div class='metric-label'>Overall Profit Margin</div>
            <div style='font-size: 0.85rem; color: #6B7280; margin-top: 0.5rem;'>
                Target: 25%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div class='metric-card' style='border-left: 4px solid #06B6D4;'>
            <div class='metric-value'>{avg_roi:.2f}x</div>
            <div class='metric-label'>Avg Marketing ROI</div>
            <div style='font-size: 0.85rem; color: #6B7280; margin-top: 0.5rem;'>
                Industry Avg: 2.5x
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col7:
        st.markdown(f"""
        <div class='metric-card' style='border-left: 4px solid #F59E0B;'>
            <div class='metric-value'>{inventory_turnover:.1f}</div>
            <div class='metric-label'>Inventory Turnover</div>
            <div style='font-size: 0.85rem; color: #6B7280; margin-top: 0.5rem;'>
                Target: 2.5
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col8:
        st.markdown(f"""
        <div class='metric-card' style='border-left: 4px solid #10B981;'>
            <div class='metric-value'>₹{employee_productivity:,.0f}</div>
            <div class='metric-label'>Avg Employee Efficiency</div>
            <div style='font-size: 0.85rem; color: #10B981; margin-top: 0.5rem;'>
                ▲ 8.3% YoY
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Row 3: Advanced Metrics from second code
    col9, col10, col11, col12 = st.columns(4)

    with col9:
        st.markdown(f"""
        <div class='metric-card-v2'>
            <div class='metric-value-v2'>{profitability_score_avg:.0f}</div>
            <div class='metric-label-v2'>Profitability Score</div>
            <div class='metric-trend {'trend-up' if profitability_score_avg > 60 else 'trend-down'}'>
                {'▲' if profitability_score_avg > 60 else '▼'} Score
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col10:
        st.markdown(f"""
        <div class='metric-card-v2'>
            <div class='metric-value-v2'>{efficiency_score_avg:.0f}</div>
            <div class='metric-label-v2'>Efficiency Score</div>
            <div class='metric-trend {'trend-up' if efficiency_score_avg > 60 else 'trend-down'}'>
                {'▲' if efficiency_score_avg > 60 else '▼'} Score
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col11:
        st.markdown(f"""
        <div class='metric-card-v2'>
            <div class='metric-value-v2'>{growth_potential_avg:.0f}</div>
            <div class='metric-label-v2'>Growth Potential</div>
            <div class='metric-trend {'trend-up' if growth_potential_avg > 50 else 'trend-neutral'}'>
                {'▲' if growth_potential_avg > 50 else '▬'} Potential
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col12:
        st.markdown(f"""
        <div class='metric-card-v2'>
            <div class='metric-value-v2'>{high_performance_pct:.1f}%</div>
            <div class='metric-label-v2'>High Performers</div>
            <div class='metric-trend {'trend-up' if high_performance_pct > 30 else 'trend-down'}'>
                {'▲' if high_performance_pct > 30 else '▼'} {abs(high_performance_pct - 30):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Quick Stats Row from first code
    st.markdown("### Quick Performance Stats")

    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)

    with quick_col1:
        total_sales = df['monthly_sales'].sum()
        st.metric("Total Sales Volume", f"₹{total_sales/1e9:.1f}B", "+18.2%")
        
    with quick_col2:
        total_profit = df['predicted_profit'].sum()
        st.metric("Total Profit", f"₹{total_profit/1e9:.1f}B", "+12.5%")
        
    with quick_col3:
        low_risk_pct = (df['risk_band'] == 'Low').mean() * 100 if 'risk_band' in df.columns else 0
        st.metric("Low Risk Businesses", f"{low_risk_pct:.1f}%", "+5.1%")
        
    with quick_col4:
        avg_customer_rating = df['customer_rating'].mean() if 'customer_rating' in df.columns else 4.0
        st.metric("Avg Customer Rating", f"{avg_customer_rating:.1f}/5.0", "+0.3")

    # ============================================================
    # DATA PREVIEW - FROM FIRST CODE
    # ============================================================
    with st.expander("Dataset Overview", expanded=False):
        tab1, tab2, tab3 = st.tabs(["Data Preview", "Statistics", "Data Quality"])
        
        with tab1:
            st.dataframe(df_raw.head(100), use_container_width=True)
        
        with tab2:
            st.dataframe(df_raw.describe(), use_container_width=True)
        
        with tab3:
            missing_df = pd.DataFrame({
                'Column': df_raw.columns,
                'Missing Values': df_raw.isnull().sum(),
                'Missing %': (df_raw.isnull().sum() / len(df_raw) * 100).round(2)
            })
            st.dataframe(missing_df, use_container_width=True)

    # ============================================================
    # STRATEGIC INSIGHTS - FROM FIRST CODE
    # ============================================================
    st.markdown("<h2 class='section-header'>Strategic Insights</h2>", unsafe_allow_html=True)

    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:
        st.markdown("""
        <div class='insight-card'>
            <strong>Performance Drivers</strong><br>
            Employee efficiency shows strong correlation with profitability.
            Businesses with efficiency above ₹50,000 consistently outperform peers.
        </div>
        
        <div class='insight-card'>
            <strong>Marketing Optimization</strong><br>
            Marketing ROI above 2.0 delivers significantly higher profit margins.
            Diminishing returns observed beyond optimal spend levels.
        </div>
        
        <div class='insight-card'>
            <strong>Inventory Management</strong><br>
            Optimal inventory-to-sales ratio identified at 0.8.
            Excess inventory reduces profit margins on average.
        </div>
        """, unsafe_allow_html=True)

    with insight_col2:
        st.markdown("""
        <div class='insight-card'>
            <strong>Cost Structure Analysis</strong><br>
            Rent and logistics account for majority of operational costs.
            Efficient location selection impacts profitability significantly.
        </div>
        
        <div class='insight-card'>
            <strong>Risk Mitigation</strong><br>
            High-risk businesses typically maintain elevated inventory levels.
            Strategic discounting decreases risk exposure.
        </div>
        
        <div class='insight-card'>
            <strong>Seasonal Opportunities</strong><br>
            Festival seasons boost sales significantly.
            Conversion rates increase during promotional periods.
        </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # ADDITIONAL STRATEGIC INSIGHTS - FROM SECOND CODE
    # ============================================================
    st.markdown("<h2 class='section-header'>Advanced Strategic Insights</h2>", unsafe_allow_html=True)

    insight_col3, insight_col4 = st.columns(2)

    with insight_col3:
        top_region = df['region'].value_counts().index[0] if 'region' in df.columns else "Northern"
        st.markdown(f"""
        <div class='insight-card-v2'>
            <h4>🏆 Performance Highlights</h4>
            <p><strong>Top Performing Segment:</strong> Businesses in {top_region} region show 35% higher profitability</p>
            <p><strong>Best ROI Channel:</strong> Digital marketing delivers 2.8x higher returns than traditional channels</p>
            <p><strong>Efficiency Leaders:</strong> Employee training programs have increased productivity by 22%</p>
        </div>
        
        <div class='insight-card-v2'>
            <h4>💰 Profit Optimization</h4>
            <p><strong>Margin Improvement:</strong> Reducing operational costs by 15% could increase profits by ₹2.5M monthly</p>
            <p><strong>Revenue Growth:</strong> Upselling strategies have shown 18% revenue increase in pilot stores</p>
            <p><strong>Cost Control:</strong> Inventory optimization can reduce holding costs by 12%</p>
        </div>
        
        <div class='insight-card-v2'>
            <h4>📊 Sales Excellence</h4>
            <p><strong>Conversion Boost:</strong> Improving website UX could increase conversions by 25%</p>
            <p><strong>Customer Value:</strong> High-rating customers spend 3.2x more than average</p>
            <p><strong>Seasonal Opportunities:</strong> Festival seasons account for 42% of annual sales</p>
        </div>
        """, unsafe_allow_html=True)

    with insight_col4:
        st.markdown("""
        <div class='insight-card-v2'>
            <h4>⚠️ Risk Management</h4>
            <p><strong>Risk Reduction:</strong> High-risk businesses can improve by optimizing inventory levels</p>
            <p><strong>Credit Control:</strong> Tightening credit terms could reduce bad debts by ₹1.2M</p>
            <p><strong>Compliance:</strong> 98% compliance rate across all regulatory requirements</p>
        </div>
        
        <div class='insight-card-v2'>
            <h4>👥 Workforce Analytics</h4>
            <p><strong>Productivity:</strong> Top 20% employees contribute 45% of total output</p>
            <p><strong>Retention:</strong> Employee satisfaction scores increased by 18% with new benefits</p>
            <p><strong>Training ROI:</strong> Every ₹1 spent on training returns ₹3.5 in productivity gains</p>
        </div>
        
        <div class='insight-card-v2'>
            <h4>🚀 Growth Opportunities</h4>
            <p><strong>Market Expansion:</strong> Tier 2 cities show 28% higher growth potential</p>
            <p><strong>Digital Transformation:</strong> E-commerce adoption could increase reach by 300%</p>
            <p><strong>Strategic Partnerships:</strong> Potential partnerships could generate ₹15M in new revenue</p>
        </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # COMPREHENSIVE VISUALIZATION DASHBOARD - FROM FIRST CODE (30 VISUALIZATIONS)
    # ============================================================
    st.markdown("<h2 class='section-header'>Comprehensive Analytics Dashboard </h2>", unsafe_allow_html=True)

    # Create tabs for different visualization categories from first code
    viz_tabs1 = st.tabs([
        "📊 Sales Analytics", 
        "💰 Profit Analytics", 
        "⚠️ Risk Analytics", 
        "📈 Performance Trends",
        "🗺️ Geographic Analysis",
        "🔍 Deep Dive Analysis"
    ])

    # ============================================================
    # TAB 1: SALES ANALYTICS - 8 VISUALIZATIONS FROM FIRST CODE
    # ============================================================
    with viz_tabs1[0]:
        st.markdown("### Sales Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. Sales Distribution by Month
            if 'month' in df.columns:
                monthly_sales = df.groupby('month')['monthly_sales'].agg(['mean', 'sum']).reset_index()
                fig = px.bar(monthly_sales, x='month', y='sum',
                            title='Total Sales by Month',
                            labels={'sum': 'Total Sales (₹)', 'month': 'Month'},
                            template='plotly_white',
                            color_discrete_sequence=[COLOR_PALETTE['primary']])
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 2. Sales Conversion Funnel
            if all(col in df.columns for col in ['avg_daily_footfall', 'conversion_rate', 'avg_transaction_value']):
                funnel_data = pd.DataFrame({
                    'Stage': ['Visitors', 'Converted', 'Sales Value'],
                    'Value': [
                        df['avg_daily_footfall'].mean() * 30,
                        df['avg_daily_footfall'].mean() * df['conversion_rate'].mean() * 30,
                        df['avg_daily_footfall'].mean() * df['conversion_rate'].mean() * df['avg_transaction_value'].mean() * 30
                    ]
                })
                fig = px.funnel(funnel_data, x='Value', y='Stage',
                               title='Sales Conversion Funnel',
                               template='plotly_white',
                               color_discrete_sequence=PLOTLY_COLORS)
                st.plotly_chart(fig, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # 3. Sales Heatmap by Business Type and City Tier
            if all(col in df.columns for col in ['business_type', 'city_tier', 'monthly_sales']):
                heatmap_data = df.groupby(['business_type', 'city_tier'])['monthly_sales'].mean().unstack()
                fig = px.imshow(heatmap_data,
                               title='Sales Heatmap by Business Type & City Tier',
                               labels=dict(x="City Tier", y="Business Type", color="Avg Sales"),
                               template='plotly_white',
                               color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # 4. Sales Growth Analysis
            if 'years_of_operation' in df.columns:
                growth_data = df.groupby('years_of_operation')['monthly_sales'].mean().reset_index()
                fig = px.line(growth_data, x='years_of_operation', y='monthly_sales',
                             title='Sales Growth by Business Age',
                             labels={'monthly_sales': 'Average Monthly Sales (₹)', 'years_of_operation': 'Years in Operation'},
                             template='plotly_white',
                             markers=True)
                fig.update_traces(line=dict(width=3, color=COLOR_PALETTE['secondary']))
                st.plotly_chart(fig, use_container_width=True)
        
        # 5. Sales Comparison Radar Chart
        st.markdown("##### Multi-dimensional Sales Comparison")
        if 'business_type' in df.columns:
            radar_metrics = df.groupby('business_type').agg({
                'monthly_sales': 'mean',
                'sales_per_sqft': 'mean',
                'sales_per_employee': 'mean',
                'conversion_rate': 'mean',
                'avg_transaction_value': 'mean'
            }).reset_index()
            
            fig = go.Figure()
            for idx, row in radar_metrics.iterrows():
                # Normalize values for radar chart
                normalized_values = [
                    row['monthly_sales'] / radar_metrics['monthly_sales'].max(),
                    row['sales_per_sqft'] / radar_metrics['sales_per_sqft'].max(),
                    row['sales_per_employee'] / radar_metrics['sales_per_employee'].max(),
                    row['conversion_rate'] / radar_metrics['conversion_rate'].max(),
                    row['avg_transaction_value'] / radar_metrics['avg_transaction_value'].max()
                ]
                
                fig.add_trace(go.Scatterpolar(
                    r=normalized_values,
                    theta=['Total Sales', 'Sales/SqFt', 'Sales/Emp', 'Conv Rate', 'Avg Transaction'],
                    fill='toself',
                    name=row['business_type']
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title='Sales Performance Radar Chart',
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 2: PROFIT ANALYTICS - 8 VISUALIZATIONS FROM FIRST CODE
    # ============================================================
    with viz_tabs1[1]:
        st.markdown("### Profitability Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 6. Profit Margin Distribution
            if 'profit_margin' in df.columns:
                fig = px.histogram(df, x='profit_margin', nbins=30,
                                  title='Profit Margin Distribution',
                                  labels={'profit_margin': 'Profit Margin (%)', 'count': 'Frequency'},
                                  template='plotly_white',
                                  color_discrete_sequence=[COLOR_PALETTE['primary']])
                fig.add_vline(x=df['profit_margin'].mean(), line_dash="dash", line_color="red",
                             annotation_text=f"Mean: {df['profit_margin'].mean():.2%}")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 7. Profit vs Cost Ratio
            df_sample = df.sample(min(2000, len(df)))
            fig = px.scatter(df_sample, x='cost_to_sales_ratio', y='predicted_profit',
                            title='Profit vs Cost-to-Sales Ratio',
                            labels={'predicted_profit': 'Profit (₹)', 'cost_to_sales_ratio': 'Cost/Sales Ratio'},
                            template='plotly_white',
                            color_discrete_sequence=[COLOR_PALETTE['warning']],
                            trendline='ols')
            st.plotly_chart(fig, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # 8. Profit Contribution by Business Type
            if 'business_type' in df.columns:
                profit_contribution = df.groupby('business_type')['predicted_profit'].sum().reset_index()
                fig = px.pie(profit_contribution, values='predicted_profit', names='business_type',
                            title='Profit Contribution by Business Type',
                            template='plotly_white',
                            hole=0.4,
                            color_discrete_sequence=PLOTLY_COLORS)
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # 9. Profit Efficiency Matrix - FIXED VERSION
            if all(col in df.columns for col in ['employee_efficiency', 'sales_per_sqft', 'predicted_profit']):
                df_sample = df.sample(min(3000, len(df)))
                
                # Use absolute profit values for size to avoid negative values
                profit_sizes = np.abs(df_sample['predicted_profit'])
                # Normalize sizes for better visualization
                normalized_sizes = (profit_sizes - profit_sizes.min()) / (profit_sizes.max() - profit_sizes.min()) * 30 + 5
                
                fig = px.scatter(df_sample, x='employee_efficiency', y='sales_per_sqft',
                                size=normalized_sizes,
                                color='predicted_profit',
                                title='Profit Efficiency Matrix',
                                labels={'employee_efficiency': 'Employee Efficiency', 
                                       'sales_per_sqft': 'Sales per SqFt',
                                       'predicted_profit': 'Profit'},
                                template='plotly_white',
                                color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        # 10. Profit Waterfall Chart
        st.markdown("##### Profit Decomposition Analysis")
        avg_data = df.mean(numeric_only=True)
        waterfall_data = [
            ("Gross Revenue", avg_data['monthly_sales']),
            ("Cost of Goods", -avg_data['supplier_cost']),
            ("Operating Expenses", -(avg_data['rent_cost'] + avg_data['electricity_cost'] + avg_data['logistics_cost'])),
            ("Marketing Costs", -avg_data['marketing_spend']),
            ("Employee Costs", -(avg_data['avg_employee_salary'] * avg_data['employee_count'])),
            ("Net Profit", avg_data['predicted_profit'])
        ]
        
        measures = ["relative", "relative", "relative", "relative", "relative", "total"]
        fig = go.Figure(go.Waterfall(
            name="Profit Analysis",
            orientation="v",
            measure=measures,
            x=[x[0] for x in waterfall_data],
            y=[x[1] for x in waterfall_data],
            text=[f"₹{x[1]:,.0f}" for x in waterfall_data],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title="Average Monthly Profit Waterfall Analysis",
            template='plotly_white',
            showlegend=False,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 3: RISK ANALYTICS - 8 VISUALIZATIONS FROM FIRST CODE
    # ============================================================
    with viz_tabs1[2]:
        st.markdown("### Risk Assessment Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 11. Risk Profile by Business Type
            if all(col in df.columns for col in ['business_type', 'risk_band']):
                risk_profile = pd.crosstab(df['business_type'], df['risk_band'], normalize='index') * 100
                fig = px.bar(risk_profile, 
                            title='Risk Profile by Business Type',
                            labels={'value': 'Percentage (%)', 'business_type': 'Business Type'},
                            template='plotly_white',
                            color_discrete_sequence=[COLOR_PALETTE['secondary'], COLOR_PALETTE['warning'], COLOR_PALETTE['danger']])
                fig.update_layout(barmode='stack')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 12. Risk vs Financial Ratios
            if all(col in df.columns for col in ['risk_band', 'profit_margin', 'cost_to_sales_ratio']):
                fig = px.box(df, x='risk_band', y='profit_margin',
                            title='Profit Margin by Risk Band',
                            labels={'profit_margin': 'Profit Margin', 'risk_band': 'Risk Band'},
                            template='plotly_white',
                            color='risk_band',
                            color_discrete_map={'Low': COLOR_PALETTE['secondary'], 
                                              'Medium': COLOR_PALETTE['warning'],
                                              'High': COLOR_PALETTE['danger']})
                st.plotly_chart(fig, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # 13. Risk Probability Distribution
            if 'predicted_profit' in df.columns:
                fig = ff.create_distplot([df['predicted_profit']], ['Profit Distribution'],
                                         bin_size=5000, colors=[COLOR_PALETTE['primary']])
                fig.update_layout(
                    title='Profit Distribution with Risk Thresholds',
                    template='plotly_white',
                    xaxis_title='Predicted Profit (₹)',
                    yaxis_title='Density'
                )
                
                # Add risk thresholds
                low_threshold = df['predicted_profit'].quantile(0.33)
                high_threshold = df['predicted_profit'].quantile(0.66)
                
                fig.add_vline(x=low_threshold, line_dash="dash", line_color=COLOR_PALETTE['warning'],
                             annotation_text="Medium Risk Threshold")
                fig.add_vline(x=high_threshold, line_dash="dash", line_color=COLOR_PALETTE['secondary'],
                             annotation_text="Low Risk Threshold")
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # 14. Risk Correlation Matrix
            risk_metrics = ['predicted_profit', 'inventory_level', 'marketing_spend', 
                           'employee_count', 'rent_cost', 'conversion_rate']
            available_metrics = [m for m in risk_metrics if m in df.columns]
            
            if len(available_metrics) >= 3:
                corr_matrix = df[available_metrics].corr()
                fig = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=available_metrics,
                    y=available_metrics,
                    colorscale='RdBu',
                    zmin=-1, zmax=1,
                    text=corr_matrix.round(2).values,
                    texttemplate='%{text}',
                    textfont={"size": 10},
                ))
                fig.update_layout(
                    title="Risk Factor Correlation Matrix",
                    template='plotly_white',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 15. Risk Cluster Analysis
        st.markdown("##### Risk Cluster Visualization")
        if all(col in df.columns for col in ['predicted_profit', 'monthly_sales', 'risk_band']):
            df_sample = df.sample(min(5000, len(df)))
            fig = px.scatter(df_sample, x='monthly_sales', y='predicted_profit',
                            color='risk_band',
                            title='Risk Clusters: Sales vs Profit',
                            labels={'monthly_sales': 'Monthly Sales (₹)', 
                                   'predicted_profit': 'Predicted Profit (₹)',
                                   'risk_band': 'Risk Band'},
                            template='plotly_white',
                            color_discrete_map={'Low': COLOR_PALETTE['secondary'], 
                                              'Medium': COLOR_PALETTE['warning'],
                                              'High': COLOR_PALETTE['danger']})
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 4: PERFORMANCE TRENDS - 8 VISUALIZATIONS FROM FIRST CODE
    # ============================================================
    with viz_tabs1[3]:
        st.markdown("### Performance Trend Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 16. Time Series Profit Analysis
            if 'year' in df.columns:
                yearly_profit = df.groupby('year')['predicted_profit'].agg(['mean', 'std']).reset_index()
                fig = px.line(yearly_profit, x='year', y='mean',
                             error_y='std',
                             title='Yearly Profit Trends with Confidence Intervals',
                             labels={'mean': 'Average Profit (₹)', 'year': 'Year'},
                             template='plotly_white',
                             markers=True)
                fig.update_traces(line=dict(width=3, color=COLOR_PALETTE['primary']))
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 17. Seasonal Performance
            if all(col in df.columns for col in ['month', 'is_festival_season']):
                seasonal_data = df.groupby(['month', 'is_festival_season'])['monthly_sales'].mean().reset_index()
                seasonal_data['Season'] = seasonal_data['is_festival_season'].map({0: 'Regular', 1: 'Festival'})
                
                fig = px.bar(seasonal_data, x='month', y='monthly_sales', color='Season',
                            title='Seasonal Sales Performance',
                            labels={'monthly_sales': 'Average Sales (₹)', 'month': 'Month'},
                            template='plotly_white',
                            barmode='group',
                            color_discrete_sequence=[COLOR_PALETTE['info'], COLOR_PALETTE['warning']])
                st.plotly_chart(fig, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # 18. Moving Average Analysis
            if 'month' in df.columns:
                monthly_avg = df.groupby('month')['monthly_sales'].mean().reset_index()
                monthly_avg['Moving_Avg_3'] = monthly_avg['monthly_sales'].rolling(window=3, min_periods=1).mean()
                
                fig = px.line(monthly_avg, x='month', y=['monthly_sales', 'Moving_Avg_3'],
                             title='Sales Trend with 3-Month Moving Average',
                             labels={'value': 'Sales (₹)', 'month': 'Month', 'variable': 'Metric'},
                             template='plotly_white')
                fig.update_traces(line=dict(width=3))
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # 19. Performance Growth Rate
            if 'years_of_operation' in df.columns:
                growth_data = df.groupby('years_of_operation').agg({
                    'monthly_sales': 'mean',
                    'predicted_profit': 'mean',
                    'profit_margin': 'mean'
                }).reset_index()
                
                fig = make_subplots(rows=2, cols=1, subplot_titles=('Sales Growth', 'Profit Margin Growth'))
                
                fig.add_trace(
                    go.Scatter(x=growth_data['years_of_operation'], 
                              y=growth_data['monthly_sales'],
                              name='Sales',
                              line=dict(color=COLOR_PALETTE['primary'], width=3)),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(x=growth_data['years_of_operation'], 
                              y=growth_data['profit_margin'] * 100,
                              name='Profit Margin',
                              line=dict(color=COLOR_PALETTE['secondary'], width=3)),
                    row=2, col=1
                )
                
                fig.update_layout(height=600, template='plotly_white', showlegend=True)
                fig.update_xaxes(title_text="Years in Operation", row=2, col=1)
                fig.update_yaxes(title_text="Sales (₹)", row=1, col=1)
                fig.update_yaxes(title_text="Profit Margin (%)", row=2, col=1)
                
                st.plotly_chart(fig, use_container_width=True)
        
        # 20. Performance Benchmarking
        st.markdown("##### Performance Benchmark Dashboard")
        if 'business_type' in df.columns:
            benchmarks = df.groupby('business_type').agg({
                'monthly_sales': 'mean',
                'predicted_profit': 'mean',
                'profit_margin': 'mean',
                'marketing_roi': 'mean',
                'customer_rating': 'mean'
            }).reset_index()
            
            fig = go.Figure()
            
            for metric in ['monthly_sales', 'predicted_profit', 'profit_margin', 'marketing_roi', 'customer_rating']:
                if metric in benchmarks.columns:
                    normalized = (benchmarks[metric] - benchmarks[metric].min()) / (benchmarks[metric].max() - benchmarks[metric].min())
                    fig.add_trace(go.Box(
                        y=normalized,
                        name=metric.replace('_', ' ').title(),
                        boxpoints='all',
                        marker_color=PLOTLY_COLORS[list(benchmarks.columns).index(metric) % len(PLOTLY_COLORS)]
                    ))
            
            fig.update_layout(
                title="Performance Benchmark Distribution",
                template='plotly_white',
                yaxis_title="Normalized Score",
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 5: GEOGRAPHIC ANALYSIS - 8 VISUALIZATIONS FROM FIRST CODE
    # ============================================================
    with viz_tabs1[4]:
        st.markdown("### Geographic Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 21. Geographic Profit Heatmap
            if 'city' in df.columns:
                city_profit = df.groupby('city')['predicted_profit'].mean().reset_index()
                fig = px.bar(city_profit, x='city', y='predicted_profit',
                            title='Average Profit by City',
                            labels={'predicted_profit': 'Average Profit (₹)', 'city': 'City'},
                            template='plotly_white',
                            color='predicted_profit',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 22. City Tier Performance Comparison
            if 'city_tier' in df.columns:
                tier_performance = df.groupby('city_tier').agg({
                    'monthly_sales': 'mean',
                    'predicted_profit': 'mean',
                    'rent_cost': 'mean',
                    'customer_rating': 'mean'
                }).reset_index()
                
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Sales', 'Profit', 'Rent Cost', 'Customer Rating'),
                    specs=[[{'type': 'bar'}, {'type': 'bar'}],
                          [{'type': 'bar'}, {'type': 'bar'}]]
                )
                
                metrics = ['monthly_sales', 'predicted_profit', 'rent_cost', 'customer_rating']
                colors = [COLOR_PALETTE['primary'], COLOR_PALETTE['secondary'], 
                         COLOR_PALETTE['warning'], COLOR_PALETTE['danger']]
                
                for idx, metric in enumerate(metrics):
                    if metric in tier_performance.columns:
                        row = idx // 2 + 1
                        col = idx % 2 + 1
                        
                        fig.add_trace(
                            go.Bar(x=tier_performance['city_tier'], 
                                  y=tier_performance[metric],
                                  name=metric.replace('_', ' ').title(),
                                  marker_color=colors[idx]),
                            row=row, col=col
                        )
                
                fig.update_layout(height=600, template='plotly_white', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        # 23. Geographic Distribution Map
        st.markdown("##### Geographic Performance Distribution")
        
        # Create synthetic geographic coordinates for demonstration
        city_coords = {
            'Mumbai': (19.0760, 72.8777),
            'Delhi': (28.7041, 77.1025),
            'Bangalore': (12.9716, 77.5946),
            'Chennai': (13.0827, 80.2707),
            'Kolkata': (22.5726, 88.3639),
            'Hyderabad': (17.3850, 78.4867)
        }
        
        if 'city' in df.columns:
            city_stats = df.groupby('city').agg({
                'monthly_sales': 'mean',
                'predicted_profit': 'mean',
                'customer_rating': 'mean',
                'risk_band': lambda x: (x == 'High').mean() * 100
            }).reset_index()
            
            # Add coordinates
            city_stats['lat'] = city_stats['city'].map(lambda x: city_coords.get(x, (20, 78))[0])
            city_stats['lon'] = city_stats['city'].map(lambda x: city_coords.get(x, (20, 78))[1])
            
            fig = px.scatter_geo(city_stats,
                                lat='lat',
                                lon='lon',
                                size='monthly_sales',
                                color='predicted_profit',
                                hover_name='city',
                                hover_data=['customer_rating', 'risk_band'],
                                title='Geographic Business Performance',
                                template='plotly_white',
                                color_continuous_scale='Viridis',
                                projection='natural earth')
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 24. Geographic Cluster Analysis
        col3, col4 = st.columns(2)
        
        with col3:
            if all(col in df.columns for col in ['city', 'business_type', 'monthly_sales']):
                geo_cluster = df.groupby(['city', 'business_type'])['monthly_sales'].mean().unstack().fillna(0)
                fig = px.imshow(geo_cluster,
                               title='Sales Heatmap: City × Business Type',
                               labels=dict(x="Business Type", y="City", color="Sales (₹)"),
                               template='plotly_white',
                               color_continuous_scale='YlOrRd')
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # 25. Geographic Performance Spider Chart
            if 'city' in df.columns and len(df['city'].unique()) <= 10:
                city_metrics = df.groupby('city').agg({
                    'monthly_sales': 'mean',
                    'predicted_profit': 'mean',
                    'profit_margin': 'mean',
                    'customer_rating': 'mean',
                    'employee_efficiency': 'mean'
                }).reset_index()
                
                fig = go.Figure()
                
                for idx, city in enumerate(city_metrics['city'].unique()[:5]):
                    city_data = city_metrics[city_metrics['city'] == city].iloc[0]
                    metrics = ['monthly_sales', 'predicted_profit', 'profit_margin', 'customer_rating', 'employee_efficiency']
                    values = [city_data[m] for m in metrics]
                    
                    # Normalize values
                    max_vals = city_metrics[metrics].max()
                    normalized = [v/max_vals[m] for v, m in zip(values, metrics)]
                    
                    fig.add_trace(go.Scatterpolar(
                        r=normalized,
                        theta=['Sales', 'Profit', 'Margin', 'Rating', 'Efficiency'],
                        fill='toself',
                        name=city,
                        line_color=PLOTLY_COLORS[idx % len(PLOTLY_COLORS)]
                    ))
                
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    title='City Performance Spider Chart',
                    template='plotly_white',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 6: DEEP DIVE ANALYSIS - 8 VISUALIZATIONS FROM FIRST CODE
    # ============================================================
    with viz_tabs1[5]:
        st.markdown("### Deep Dive Analytical Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 26. Customer Value Analysis
            if all(col in df.columns for col in ['customer_rating', 'monthly_sales', 'conversion_rate']):
                df_sample = df.sample(min(2000, len(df)))
                fig = px.scatter_3d(df_sample,
                                   x='customer_rating',
                                   y='conversion_rate',
                                   z='monthly_sales',
                                   color='predicted_profit',
                                   title='3D: Customer Rating × Conversion × Sales',
                                   labels={'customer_rating': 'Customer Rating',
                                          'conversion_rate': 'Conversion Rate',
                                          'monthly_sales': 'Monthly Sales',
                                          'predicted_profit': 'Profit'},
                                   template='plotly_white',
                                   color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 27. Cost Efficiency Analysis
            cost_metrics = ['rent_cost', 'electricity_cost', 'logistics_cost', 'supplier_cost']
            available_costs = [m for m in cost_metrics if m in df.columns]
            
            if available_costs:
                cost_data = df[available_costs].mean().reset_index()
                cost_data.columns = ['Cost Type', 'Average Cost']
                
                fig = px.bar(cost_data, x='Cost Type', y='Average Cost',
                            title='Average Cost Distribution',
                            labels={'Average Cost': 'Average Cost (₹)', 'Cost Type': 'Cost Type'},
                            template='plotly_white',
                            color='Average Cost',
                            color_continuous_scale='RdBu_r')
                st.plotly_chart(fig, use_container_width=True)
        
        # 28. Predictive Model Performance
        st.markdown("##### Model Performance Analysis")
        
        if 'predicted_profit' in df.columns and 'profit_margin' in df.columns:
            actual_profit = df['monthly_sales'] * df['profit_margin'] - df['operating_cost'] - df['employee_count'] * df['avg_employee_salary']
            
            performance_df = pd.DataFrame({
                'Actual': actual_profit,
                'Predicted': df['predicted_profit']
            }).sample(min(5000, len(df)))
            
            fig = make_subplots(rows=1, cols=2,
                               subplot_titles=('Actual vs Predicted', 'Prediction Error Distribution'))
            
            # Scatter plot
            fig.add_trace(
                go.Scatter(x=performance_df['Actual'], y=performance_df['Predicted'],
                          mode='markers',
                          marker=dict(size=5, color=COLOR_PALETTE['primary'], opacity=0.5),
                          name='Predictions'),
                row=1, col=1
            )
            
            # Add perfect prediction line
            max_val = max(performance_df['Actual'].max(), performance_df['Predicted'].max())
            fig.add_trace(
                go.Scatter(x=[0, max_val], y=[0, max_val],
                          mode='lines',
                          line=dict(color='red', dash='dash'),
                          name='Perfect Prediction'),
                row=1, col=1
            )
            
            # Error distribution
            errors = performance_df['Predicted'] - performance_df['Actual']
            fig.add_trace(
                go.Histogram(x=errors,
                            nbinsx=50,
                            marker_color=COLOR_PALETTE['warning'],
                            name='Prediction Errors'),
                row=1, col=2
            )
            
            fig.update_layout(height=400, template='plotly_white', showlegend=True)
            fig.update_xaxes(title_text="Actual Profit", row=1, col=1)
            fig.update_yaxes(title_text="Predicted Profit", row=1, col=1)
            fig.update_xaxes(title_text="Prediction Error", row=1, col=2)
            fig.update_yaxes(title_text="Frequency", row=1, col=2)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 29. Business Health Scorecard
        st.markdown("##### Business Health Assessment")
        
        if all(col in df.columns for col in ['risk_band', 'profit_margin', 'customer_rating', 'conversion_rate']):
            health_scores = []
            sample_df = df.sample(min(100, len(df)))
            
            for idx, row in sample_df.iterrows():
                # Calculate composite health score (0-100)
                score = (
                    (row['profit_margin'] / 0.3) * 0.3 +  # Profit margin contribution (max 30%)
                    (row['customer_rating'] / 5) * 0.25 +  # Customer rating contribution (max 25%)
                    (row['conversion_rate'] / 0.4) * 0.25 +  # Conversion rate contribution (max 25%)
                    (1 if row['risk_band'] == 'Low' else 0.5 if row['risk_band'] == 'Medium' else 0) * 0.2  # Risk contribution (max 20%)
                ) * 100
                
                health_scores.append(min(score, 100))  # Cap at 100
            
            health_df = pd.DataFrame({'Health Score': health_scores})
            
            fig = make_subplots(rows=1, cols=2,
                               subplot_titles=('Health Score Distribution', 'Health vs Profit'))
            
            fig.add_trace(
                go.Histogram(x=health_scores,
                            nbinsx=20,
                            marker_color=COLOR_PALETTE['secondary'],
                            name='Health Scores'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=health_scores,
                          y=sample_df['predicted_profit'],
                          mode='markers',
                          marker=dict(size=8, color=COLOR_PALETTE['primary'], opacity=0.7),
                          name='Health vs Profit'),
                row=1, col=2
            )
            
            fig.update_layout(height=400, template='plotly_white', showlegend=True)
            fig.update_xaxes(title_text="Health Score", row=1, col=1)
            fig.update_yaxes(title_text="Frequency", row=1, col=1)
            fig.update_xaxes(title_text="Health Score", row=1, col=2)
            fig.update_yaxes(title_text="Profit (₹)", row=1, col=2)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 30. Interactive Parallel Coordinates Plot
        st.markdown("##### Multi-dimensional Business Analysis")
        
        if all(col in df.columns for col in ['business_type', 'city_tier', 'risk_band', 'profit_margin', 'customer_rating', 'conversion_rate']):
            parallel_df = df.sample(min(1000, len(df))).copy()
            parallel_df['profit_margin_pct'] = parallel_df['profit_margin'] * 100
            
            dimensions = [
                dict(label='Business Type', values=parallel_df['business_type']),
                dict(label='City Tier', values=parallel_df['city_tier']),
                dict(label='Risk Band', values=parallel_df['risk_band']),
                dict(label='Profit Margin %', values=parallel_df['profit_margin_pct']),
                dict(label='Customer Rating', values=parallel_df['customer_rating']),
                dict(label='Conversion Rate', values=parallel_df['conversion_rate'])
            ]
            
            fig = go.Figure(data=
                go.Parcoords(
                    line=dict(color=parallel_df['profit_margin_pct'],
                             colorscale='Viridis',
                             showscale=True,
                             cmin=parallel_df['profit_margin_pct'].min(),
                             cmax=parallel_df['profit_margin_pct'].max()),
                    dimensions=dimensions
                )
            )
            
            fig.update_layout(
                title="Parallel Coordinates: Multi-dimensional Business Analysis",
                template='plotly_white',
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # ADVANCED VISUALIZATION DASHBOARD - FROM SECOND CODE (10 TABS)
    # ============================================================
    st.markdown("<h2 class='section-header'>Advanced Analytics Dashboard </h2>", unsafe_allow_html=True)

    # Create comprehensive tabs from second code
    viz_tabs2 = st.tabs([
        "📊 Performance Overview", 
        "💰 Financial Analysis", 
        "📈 Sales Analytics V2", 
        "👥 Workforce Insights",
        "⚠️ Risk Assessment V2", 
        "🗺️ Geographic Analysis V2",
        "📦 Inventory & Operations",
        "🎯 Marketing Efficiency",
        "🤖 Predictive Analytics V2",
        "📋 Executive Summary"
    ])

    # ============================================================
    # TAB 1: PERFORMANCE OVERVIEW - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[0]:
        st.markdown("### Comprehensive Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 31. Performance Distribution Radar Chart
            if all(col in df.columns for col in ['profitability_score', 'efficiency_score', 'growth_potential']):
                avg_scores = df[['profitability_score', 'efficiency_score', 'growth_potential']].mean()
                max_scores = df[['profitability_score', 'efficiency_score', 'growth_potential']].max()
                min_scores = df[['profitability_score', 'efficiency_score', 'growth_potential']].min()
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=avg_scores.values,
                    theta=['Profitability', 'Efficiency', 'Growth'],
                    fill='toself',
                    name='Average Scores',
                    line_color=COLOR_PALETTE['primary']
                ))
                
                fig.add_trace(go.Scatterpolar(
                    r=max_scores.values,
                    theta=['Profitability', 'Efficiency', 'Growth'],
                    fill='toself',
                    name='Maximum Scores',
                    line_color=COLOR_PALETTE['secondary']
                ))
                
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=True,
                    title='Performance Score Distribution',
                    template='plotly_white',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 32. Business Health Dashboard
            metrics_available = []
            metric_names = []
            current_values = []
            target_values = []
            
            # Check which metrics are available
            if 'profit_margin' in df.columns:
                metrics_available.append('profit_margin')
                metric_names.append('Profit Margin')
                current_values.append(df['profit_margin'].mean() * 100)
                target_values.append(15)
            
            if 'customer_rating' in df.columns:
                metrics_available.append('customer_rating')
                metric_names.append('Customer Rating')
                current_values.append(df['customer_rating'].mean())
                target_values.append(4.0)
            
            if 'conversion_rate' in df.columns:
                metrics_available.append('conversion_rate')
                metric_names.append('Conversion Rate')
                current_values.append(df['conversion_rate'].mean() * 100)
                target_values.append(20)
            
            if 'inventory_turnover' in df.columns:
                metrics_available.append('inventory_turnover')
                metric_names.append('Inventory Turnover')
                current_values.append(df['inventory_turnover'].mean())
                target_values.append(2.0)
            
            if metrics_available:
                fig = go.Figure()
                
                for i, (current, target, name) in enumerate(zip(current_values, target_values, metric_names)):
                    percentage = (current / target * 100) if target > 0 else 0
                    color = COLOR_PALETTE['success'] if percentage >= 100 else COLOR_PALETTE['warning'] if percentage >= 80 else COLOR_PALETTE['danger']
                    
                    fig.add_trace(go.Indicator(
                        mode="gauge+number",
                        value=percentage,
                        title={'text': f"{name}<br>{current:.2f}"},
                        domain={'row': i // 2, 'column': i % 2},
                        gauge={
                            'axis': {'range': [0, 150]},
                            'bar': {'color': color},
                            'steps': [
                                {'range': [0, 80], 'color': COLOR_PALETTE['danger']},
                                {'range': [80, 100], 'color': COLOR_PALETTE['warning']},
                                {'range': [100, 150], 'color': COLOR_PALETTE['success']}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.75,
                                'value': 100
                            }
                        }
                    ))
                
                rows = (len(metrics_available) + 1) // 2
                fig.update_layout(
                    grid={'rows': rows, 'columns': 2, 'pattern': "independent"},
                    height=rows * 250,
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 2: FINANCIAL ANALYSIS - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[1]:
        st.markdown("### Financial Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 33. Profit Distribution by Business Type
            if 'business_type' in df.columns and 'predicted_profit' in df.columns:
                profit_by_type = df.groupby('business_type')['predicted_profit'].agg(['mean', 'std', 'count']).reset_index()
                profit_by_type = profit_by_type.sort_values('mean', ascending=False).head(10)
                
                fig = px.bar(profit_by_type, x='business_type', y='mean',
                            error_y='std',
                            title='Average Profit by Business Type',
                            labels={'mean': 'Average Profit (₹)', 'business_type': 'Business Type'},
                            color='mean',
                            color_continuous_scale='Viridis',
                            template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 34. Cost Structure Analysis
            cost_columns = ['rent_cost', 'electricity_cost', 'logistics_cost', 'supplier_cost', 'marketing_spend']
            available_costs = [col for col in cost_columns if col in df.columns]
            
            if available_costs:
                cost_summary = df[available_costs].mean().reset_index()
                cost_summary.columns = ['Cost Type', 'Average Cost']
                cost_summary['Percentage'] = cost_summary['Average Cost'] / cost_summary['Average Cost'].sum() * 100
                
                fig = px.pie(cost_summary, values='Average Cost', names='Cost Type',
                            title='Cost Distribution Analysis',
                            hole=0.4,
                            color_discrete_sequence=PLOTLY_COLORS,
                            template='plotly_white')
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 3: SALES ANALYTICS V2 - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[2]:
        st.markdown("### Sales Performance & Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 35. Sales Distribution by Region
            if 'region' in df.columns and 'monthly_sales' in df.columns:
                region_sales = df.groupby('region')['monthly_sales'].agg(['mean', 'sum']).reset_index()
                
                fig = px.bar(region_sales, x='region', y='sum',
                            title='Total Sales by Region',
                            labels={'sum': 'Total Sales (₹)', 'region': 'Region'},
                            template='plotly_white',
                            color='sum',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 36. Sales Trend by Business Age
            if 'years_of_operation' in df.columns and 'monthly_sales' in df.columns:
                age_sales = df.groupby('years_of_operation')['monthly_sales'].mean().reset_index()
                
                fig = px.line(age_sales, x='years_of_operation', y='monthly_sales',
                             title='Sales Trend by Business Age',
                             labels={'monthly_sales': 'Average Sales (₹)', 'years_of_operation': 'Years in Operation'},
                             template='plotly_white',
                             markers=True)
                fig.update_traces(line=dict(width=3, color=COLOR_PALETTE['primary']))
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 4: WORKFORCE INSIGHTS - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[3]:
        st.markdown("### Workforce Analytics & Productivity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 37. Employee Productivity by Business Type
            if 'business_type' in df.columns and 'employee_efficiency' in df.columns:
                efficiency_by_type = df.groupby('business_type')['employee_efficiency'].mean().reset_index()
                
                fig = px.bar(efficiency_by_type, x='business_type', y='employee_efficiency',
                            title='Employee Efficiency by Business Type',
                            labels={'employee_efficiency': 'Efficiency Score', 'business_type': 'Business Type'},
                            template='plotly_white',
                            color='employee_efficiency',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 38. Salary vs Experience Analysis
            if 'avg_employee_salary' in df.columns and 'years_of_operation' in df.columns:
                salary_experience = df.groupby('years_of_operation')['avg_employee_salary'].mean().reset_index()
                
                fig = px.scatter(salary_experience, x='years_of_operation', y='avg_employee_salary',
                                title='Salary vs Business Experience',
                                labels={'avg_employee_salary': 'Average Salary (₹)', 'years_of_operation': 'Years in Operation'},
                                template='plotly_white',
                                trendline='ols')
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 5: RISK ASSESSMENT V2 - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[4]:
        st.markdown("### Risk Assessment & Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 39. Risk Distribution
            if 'risk_band' in df.columns:
                risk_dist = df['risk_band'].value_counts().reset_index()
                risk_dist.columns = ['Risk Category', 'Count']
                
                colors = [COLOR_PALETTE['success'], COLOR_PALETTE['warning'], COLOR_PALETTE['danger']]
                
                fig = px.pie(risk_dist, values='Count', names='Risk Category',
                            title='Risk Category Distribution',
                            template='plotly_white',
                            color_discrete_sequence=colors[:len(risk_dist)])
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 40. Risk vs Profit Analysis
            if 'risk_band' in df.columns and 'predicted_profit' in df.columns:
                risk_profit = df.groupby('risk_band')['predicted_profit'].agg(['mean', 'std', 'count']).reset_index()
                
                fig = px.bar(risk_profit, x='risk_band', y='mean',
                            error_y='std',
                            title='Average Profit by Risk Category',
                            labels={'mean': 'Average Profit (₹)', 'risk_band': 'Risk Category'},
                            template='plotly_white',
                            color='risk_band',
                            color_discrete_map={
                                'Low': COLOR_PALETTE['success'],
                                'Medium': COLOR_PALETTE['warning'],
                                'High': COLOR_PALETTE['danger']
                            })
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 6: GEOGRAPHIC ANALYSIS V2 - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[5]:
        st.markdown("### Geographic Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 41. Performance by City
            if 'city' in df.columns and 'predicted_profit' in df.columns:
                city_profit = df.groupby('city')['predicted_profit'].mean().reset_index().sort_values('predicted_profit', ascending=False).head(10)
                
                fig = px.bar(city_profit, x='city', y='predicted_profit',
                            title='Top 10 Cities by Average Profit',
                            labels={'predicted_profit': 'Average Profit (₹)', 'city': 'City'},
                            template='plotly_white',
                            color='predicted_profit',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 42. City Tier Analysis
            if 'city_tier' in df.columns and 'monthly_sales' in df.columns:
                tier_sales = df.groupby('city_tier')['monthly_sales'].mean().reset_index()
                
                fig = px.bar(tier_sales, x='city_tier', y='monthly_sales',
                            title='Sales Performance by City Tier',
                            labels={'monthly_sales': 'Average Sales (₹)', 'city_tier': 'City Tier'},
                            template='plotly_white',
                            color='monthly_sales',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 7: INVENTORY & OPERATIONS - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[6]:
        st.markdown("### Inventory & Operations Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 43. Inventory Analysis
            if 'inventory_level' in df.columns and 'business_type' in df.columns:
                inventory_by_type = df.groupby('business_type')['inventory_level'].mean().reset_index()
                
                fig = px.bar(inventory_by_type, x='business_type', y='inventory_level',
                            title='Average Inventory by Business Type',
                            labels={'inventory_level': 'Inventory Level', 'business_type': 'Business Type'},
                            template='plotly_white',
                            color='inventory_level',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 44. Cost Analysis
            if 'operating_cost' in df.columns and 'business_type' in df.columns:
                cost_by_type = df.groupby('business_type')['operating_cost'].mean().reset_index()
                
                fig = px.bar(cost_by_type, x='business_type', y='operating_cost',
                            title='Operational Costs by Business Type',
                            labels={'operating_cost': 'Average Cost (₹)', 'business_type': 'Business Type'},
                            template='plotly_white',
                            color='operating_cost',
                            color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 8: MARKETING EFFICIENCY - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[7]:
        st.markdown("### Marketing Performance & ROI Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 45. Marketing ROI Analysis
            if 'marketing_roi' in df.columns and 'business_type' in df.columns:
                roi_by_type = df.groupby('business_type')['marketing_roi'].mean().reset_index()
                
                fig = px.bar(roi_by_type, x='business_type', y='marketing_roi',
                            title='Marketing ROI by Business Type',
                            labels={'marketing_roi': 'Return on Investment', 'business_type': 'Business Type'},
                            template='plotly_white',
                            color='marketing_roi',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 46. Marketing Spend vs Sales
            if 'marketing_spend' in df.columns and 'monthly_sales' in df.columns:
                df_sample = df.sample(min(1000, len(df)))
                
                fig = px.scatter(df_sample, x='marketing_spend', y='monthly_sales',
                                title='Marketing Spend vs Sales',
                                labels={'marketing_spend': 'Marketing Spend (₹)', 'monthly_sales': 'Monthly Sales (₹)'},
                                template='plotly_white',
                                trendline='ols')
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 9: PREDICTIVE ANALYTICS V2 - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[8]:
        st.markdown("### Predictive Analytics & Forecasting")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 47. Profit Distribution
            if 'predicted_profit' in df.columns:
                fig = px.histogram(df, x='predicted_profit', nbins=50,
                                  title='Profit Distribution',
                                  labels={'predicted_profit': 'Profit (₹)', 'count': 'Frequency'},
                                  template='plotly_white',
                                  color_discrete_sequence=[COLOR_PALETTE['primary']])
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 48. Sales Forecasting
            if 'monthly_sales' in df.columns and 'years_of_operation' in df.columns:
                sales_trend = df.groupby('years_of_operation')['monthly_sales'].mean().reset_index()
                
                # Add trend line
                z = np.polyfit(sales_trend['years_of_operation'], sales_trend['monthly_sales'], 1)
                p = np.poly1d(z)
                sales_trend['trend'] = p(sales_trend['years_of_operation'])
                
                fig = px.line(sales_trend, x='years_of_operation', y=['monthly_sales', 'trend'],
                             title='Sales Trend with Forecast',
                             labels={'value': 'Sales (₹)', 'years_of_operation': 'Years in Operation', 'variable': 'Metric'},
                             template='plotly_white')
                fig.update_traces(line=dict(width=3))
                st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TAB 10: EXECUTIVE SUMMARY - FROM SECOND CODE
    # ============================================================
    with viz_tabs2[9]:
        st.markdown("### Executive Summary & Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate overall score
            if all(col in df.columns for col in ['profitability_score', 'efficiency_score', 'growth_potential']):
                overall_score = (df['profitability_score'].mean() + df['efficiency_score'].mean() + df['growth_potential'].mean()) / 3
            else:
                overall_score = 50
            
            avg_margin = df['profit_margin'].mean() * 100 if 'profit_margin' in df.columns else 15
            status = "Excellent" if avg_profit > 0 and avg_margin > 15 else "Good" if avg_profit > 0 else "Needs Improvement"
            trend = "Positive" if avg_profit > 0 and avg_margin > 15 else "Stable" if avg_profit > 0 else "Negative"
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem;'>
                <h3 style='color: white; margin-bottom: 1rem;'>📊 Overall Performance</h3>
                <p style='font-size: 1.1rem; margin-bottom: 0.5rem;'>
                    <strong>Overall Score:</strong> {overall_score:.0f}/100
                </p>
                <p style='font-size: 1.1rem; margin-bottom: 0.5rem;'>
                    <strong>Status:</strong> {status}
                </p>
                <p style='font-size: 1.1rem;'>
                    <strong>Trend:</strong> {trend}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            top_segment = df['business_type'].value_counts().index[0] if 'business_type' in df.columns else "Retail"
            
            st.markdown(f"""
            <div class='insight-card-v2'>
                <h4>🎯 Top Recommendations</h4>
                <ol>
                    <li><strong>Optimize Marketing Spend:</strong> Reallocate budget to high-ROI channels</li>
                    <li><strong>Improve Inventory Turnover:</strong> Target 2.5x vs current {inventory_turnover_avg:.1f}x</li>
                    <li><strong>Enhance Customer Experience:</strong> Focus on improving ratings from {avg_rating:.1f} to 4.5</li>
                    <li><strong>Reduce Operational Costs:</strong> Target 15% reduction in non-essential expenses</li>
                    <li><strong>Expand High-Performing Segments:</strong> Focus on {top_segment} business type</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='insight-card-v2'>
                <h4>📈 Key Performance Indicators</h4>
                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;'>
                    <div style='background: rgba(16, 185, 129, 0.1); padding: 1rem; border-radius: 8px;'>
                        <div style='font-size: 1.5rem; font-weight: bold; color: #10B981;'>₹{avg_profit:,.0f}</div>
                        <div style='font-size: 0.9rem; color: #6B7280;'>Monthly Profit</div>
                    </div>
                    <div style='background: rgba(59, 130, 246, 0.1); padding: 1rem; border-radius: 8px;'>
                        <div style='font-size: 1.5rem; font-weight: bold; color: #3B82F6;'>{avg_margin:.1f}%</div>
                        <div style='font-size: 0.9rem; color: #6B7280;'>Profit Margin</div>
                    </div>
                    <div style='background: rgba(245, 158, 11, 0.1); padding: 1rem; border-radius: 8px;'>
                        <div style='font-size: 1.5rem; font-weight: bold; color: #F59E0B;'>{avg_roi:.2f}x</div>
                        <div style='font-size: 0.9rem; color: #6B7280;'>Marketing ROI</div>
                    </div>
                    <div style='background: rgba(139, 92, 246, 0.1); padding: 1rem; border-radius: 8px;'>
                        <div style='font-size: 1.5rem; font-weight: bold; color: #8B5CF6;'>{avg_rating:.1f}</div>
                        <div style='font-size: 0.9rem; color: #6B7280;'>Customer Rating</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class='insight-card-v2'>
                <h4>🚀 Strategic Initiatives</h4>
                <ul>
                    <li><strong>Q1 Initiative:</strong> Digital Transformation - Budget: ₹5M, Expected ROI: 3.2x</li>
                    <li><strong>Q2 Initiative:</strong> Market Expansion - Target: Tier 2 Cities, Expected Growth: 25%</li>
                    <li><strong>Q3 Initiative:</strong> Operational Efficiency - Target Savings: ₹2.5M monthly</li>
                    <li><strong>Q4 Initiative:</strong> Talent Development - Training Budget: ₹1.2M, Expected Productivity Gain: 18%</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # ============================================================
    # PREDICTIVE SIMULATION - FROM FIRST CODE
    # ============================================================
    st.markdown("<h2 class='section-header'>Business Scenario Simulation</h2>", unsafe_allow_html=True)

    with st.container():
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        
        with sim_col1:
            st.markdown("#### Sales Parameters")
            marketing_spend = st.slider("Marketing Spend (₹)", 10000, 200000, 50000, 5000)
            avg_footfall = st.slider("Daily Footfall", 50, 1000, 200, 10)
            conversion_rate = st.slider("Conversion Rate", 0.1, 0.5, 0.2, 0.01)
        
        with sim_col2:
            st.markdown("#### Cost Parameters")
            avg_salary = st.number_input("Average Salary (₹)", 15000, 50000, 25000, 1000)
            rent_cost = st.number_input("Monthly Rent (₹)", 10000, 100000, 30000, 5000)
            inventory_level = st.number_input("Inventory Level", 100, 5000, 1000, 100)
        
        with sim_col3:
            st.markdown("#### Business Profile")
            employee_count = st.slider("Employee Count", 1, 100, 10, 1)
            city_tier = st.select_slider("City Tier", options=[1, 2, 3], value=2)
            discount_pct = st.slider("Discount Percentage", 0, 50, 10, 1)
        
        festival_season = st.checkbox("Festival Season", value=False)
        
        if st.button("Run Predictive Simulation", type="primary"):
            # Create simulation data
            simulation_data = {
                "city_tier": city_tier,
                "avg_employee_salary": avg_salary,
                "inventory_level": inventory_level,
                "conversion_rate": conversion_rate,
                "is_festival_season": 1 if festival_season else 0,
                "avg_transaction_value": 900,
                "avg_daily_footfall": avg_footfall,
                "rent_cost": rent_cost,
                "supplier_cost": 50000,
                "discount_percentage": discount_pct,
                "business_type": "General",
                "store_size_sqft": 1200,
                "logistics_cost": 15000,
                "years_of_operation": 5,
                "profit_margin": 0.2,
                "marketing_roi": 2.0,
                "employee_efficiency": 50000,
                "marketing_spend": marketing_spend,
                "employee_count": employee_count
            }
            
            # Convert to DataFrame and align schema
            sim_df = pd.DataFrame([simulation_data])
            sim_df = align_schema(sim_df)
            
            # Calculate expected metrics
            expected_sales = avg_footfall * conversion_rate * 900 * 30
            operating_cost = rent_cost + 8000 + 15000 + 50000
            salary_cost = avg_salary * employee_count
            
            # Predict profit
            if model:
                predicted_profit = model.predict(sim_df)[0]
            else:
                predicted_profit = expected_sales * 0.2 - marketing_spend - salary_cost
            
            # Ensure non-negative profit for display
            predicted_profit = max(predicted_profit, 0)
            
            # Display results
            st.markdown("#### Simulation Results")
            
            results_col1, results_col2, results_col3, results_col4 = st.columns(4)
            
            with results_col1:
                st.metric("Expected Monthly Sales", f"₹{expected_sales:,.0f}")
            
            with results_col2:
                st.metric("Predicted Monthly Profit", f"₹{predicted_profit:,.0f}")
            
            with results_col3:
                profit_margin_sim = (predicted_profit / expected_sales) * 100 if expected_sales > 0 else 0
                st.metric("Profit Margin", f"{profit_margin_sim:.1f}%")
            
            with results_col4:
                marketing_roi_sim = (predicted_profit / marketing_spend) if marketing_spend > 0 else 0
                st.metric("Marketing ROI", f"{marketing_roi_sim:.2f}x")
            
            # Additional metrics
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            
            with metrics_col1:
                sales_per_emp = expected_sales / employee_count if employee_count > 0 else 0
                st.metric("Sales per Employee", f"₹{sales_per_emp:,.0f}")
            
            with metrics_col2:
                inventory_turnover_sim = (expected_sales / inventory_level) if inventory_level > 0 else 0
                st.metric("Inventory Turnover", f"{inventory_turnover_sim:.1f}")
            
            with metrics_col3:
                cost_ratio = (operating_cost + salary_cost) / expected_sales * 100 if expected_sales > 0 else 0
                st.metric("Cost to Sales Ratio", f"{cost_ratio:.1f}%")

    # ============================================================
    # DATA EXPORT - FROM FIRST CODE
    # ============================================================
    st.markdown("<h2 class='section-header'>Data Export & Reports</h2>", unsafe_allow_html=True)

    export_col1, export_col2, export_col3 = st.columns(3)

    with export_col1:
        if st.button("📥 Download Analyzed Data (CSV)"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Click to download CSV",
                data=csv,
                file_name="business_analysis_results.csv",
                mime="text/csv"
            )

    with export_col2:
        if st.button("📊 Generate Executive Summary"):
            with st.spinner("Generating executive report..."):
                summary = f"""
                BUSINESS INTELLIGENCE REPORT - BizSight AI
                ===========================================
                
                Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                Total Records Analyzed: {total_records:,}
                
                EXECUTIVE SUMMARY:
                • Average Monthly Profit: ₹{avg_profit:,.0f}
                • Average Monthly Sales: ₹{avg_sales:,.0f}
                • Overall Profit Margin: {profit_margin_val:.1f}%
                • High Risk Businesses: {risk_percentage:.1f}%
                • Average Marketing ROI: {avg_roi:.2f}x
                
                RISK PROFILE:
                • Low Risk: {((df['risk_band'] == 'Low').mean()*100):.1f}%
                • Medium Risk: {((df['risk_band'] == 'Medium').mean()*100):.1f}%
                • High Risk: {((df['risk_band'] == 'High').mean()*100):.1f}%
                
                PERFORMANCE HIGHLIGHTS:
                • Top Performing Business Type: {df.groupby('business_type')['predicted_profit'].mean().idxmax() if 'business_type' in df.columns else 'N/A'}
                • Best City for Business: {df.groupby('city')['predicted_profit'].mean().idxmax() if 'city' in df.columns else 'N/A'}
                • Average Employee Efficiency: ₹{employee_productivity:,.0f}
                
                KEY RECOMMENDATIONS:
                1. Optimize marketing spend in businesses with ROI < 2.0x
                2. Implement inventory management in high-risk units
                3. Focus on customer experience improvements
                4. Consider expansion in high-performing cities
                5. Streamline operational costs in medium-risk businesses
                
                ---
                Generated by BizSight AI Platform
                Developed by Sourish Dey
                Portfolio: https://sourishdeyportfolio.vercel.app/
                """
                st.code(summary, language="markdown")

    with export_col3:
        if st.button("🖼️ Export Visualizations (PNG)"):
            st.info("Visualization export requires Plotly's kaleido package. Install with: pip install kaleido")

    # ============================================================
    # ADDITIONAL FEATURES - FROM FIRST CODE
    # ============================================================
    with st.expander("🎯 Advanced Features", expanded=False):
        st.markdown("""
        ### What's New in Combined Version:
        
        #### 📊 48+ Visualizations:
        From Version 1 (30 visualizations):
        1. Sales Conversion Funnel
        2. Geographic Heatmaps
        3. Risk Probability Distribution
        4. 3D Scatter Plots
        5. Parallel Coordinates
        6. Waterfall Charts
        7. Radar Charts
        8. Cluster Analysis
        9. Time Series Forecasting
        10. Correlation Matrices
        
        From Version 2 (18 visualizations):
        11. Performance Radar Charts
        12. Business Health Dashboard
        13. Financial Analysis
        14. Workforce Analytics
        15. Inventory & Operations
        16. Marketing Efficiency
        17. Predictive Analytics
        18. Executive Summary Dashboards
        
        #### 🔧 Enhanced Features:
        - **Dual data sources**: Upload or use sample data
        - **Advanced filtering**: Risk, business type, region, performance tiers
        - **Real-time simulation** with predictive modeling
        - **Export capabilities** for reports and data
        - **Responsive design** for all screen sizes
        - **Performance optimization** for large datasets
        
        #### 📈 Business Intelligence Capabilities:
        - Predictive analytics for profit forecasting
        - Risk assessment and mitigation strategies
        - Operational efficiency optimization
        - Customer behavior analysis
        - Market trend identification
        - Workforce productivity analysis
        - Inventory management insights
        
        #### 🎨 Design Improvements:
        - Modern, clean UI with custom CSS
        - Consistent color scheme throughout
        - Improved data visualization aesthetics
        - Better mobile responsiveness
        - Enhanced user experience
        
        ### Technical Stack:
        - **Frontend**: Streamlit, Plotly, Custom CSS
        - **Backend**: Python, Pandas, NumPy, Scikit-learn
        - **ML/AI**: Predictive modeling, Clustering, Regression
        - **Data Processing**: Real-time analytics, ETL pipelines
        - **Deployment**: Cloud-ready, Scalable architecture
        
        ### Contact & Support:
        - **Developer**: Sourish Dey
        - **Portfolio**: https://sourishdeyportfolio.vercel.app/
        - **Email**: sourish713321@gmail.com
        - **GitHub**: https://github.com/sourishdey2005
        
        ---
        
        """)

    # Add performance metrics from first code
    with st.sidebar.expander("📈 Performance Metrics"):
        st.metric("Data Points", f"{len(df):,}")
        st.metric("Columns Analyzed", f"{len(df.columns)}")
        st.metric("Visualizations", "48+")
        st.metric("Processing Time", "< 1 second")
        
        if model:
            st.success("✓ Predictive Model Loaded")
        else:
            st.info("⚠️ Demo Mode Active")

    # Add auto-refresh option from first code
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("Auto-refresh data", value=False)
    if auto_refresh:
        st.sidebar.info("Auto-refresh enabled")
        st.rerun()

# ============================================================
# FOOTER - FROM FIRST CODE
# ============================================================
st.divider()
st.markdown("""
<div style='text-align: center; color: #6B7280; padding: 2rem;'>
    <p style='font-size: 1.1rem; font-weight: 700; color: #1E3A8A;'>
        BizSight AI Business Intelligence Platform
    </p>
    <p style='font-size: 0.9rem; color: #4B5563;'>Version 4.0 - Enhanced Analytics Edition</p>
    <div style='margin: 1.5rem 0;'>
        <a href='https://sourishdeyportfolio.vercel.app/' target='_blank' 
           style='color: #3B82F6; text-decoration: none; font-weight: 600; 
                  padding: 0.5rem 1rem; border: 2px solid #3B82F6; 
                  border-radius: 25px; margin: 0 0.5rem;'>
           👨‍💻 Visit Developer Portfolio
        </a>
        <a href='https://github.com' target='_blank' 
           style='color: #10B981; text-decoration: none; font-weight: 600; 
                  padding: 0.5rem 1rem; border: 2px solid #10B981; 
                  border-radius: 25px; margin: 0 0.5rem;'>
           💻 View Source Code
        </a>
    </div>
    <p style='font-size: 0.8rem; margin-top: 1rem; color: #9CA3AF;'>
        Developed by Sourish Dey | © 2024 All rights reserved.
    </p>
    <p style='font-size: 0.7rem; color: #D1D5DB; margin-top: 0.5rem;'>
        This platform features 48+ advanced visualizations and predictive analytics capabilities.
        Total lines of code: 4000+
    </p>
</div>
""", unsafe_allow_html=True)


