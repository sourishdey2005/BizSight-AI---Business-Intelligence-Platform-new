import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import warnings
import json
import os
import base64
from pathlib import Path
import sqlite3
from hashlib import sha256
import jwt
from functools import wraps
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image as PILImage
import io
import re
import uuid

warnings.filterwarnings('ignore')

# ============================================================
# DATABASE SETUP & AUTHENTICATION
# ============================================================
def init_db():
    """Initialize SQLite database for user authentication and transaction management"""
    conn = sqlite3.connect('bizsight.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Business profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS business_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            business_name TEXT NOT NULL,
            business_type TEXT,
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # User sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Transactions table (Sales & Expenses)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL, -- 'sale' or 'expense'
            amount REAL NOT NULL,
            category TEXT,
            description TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            receipt_image BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_id) REFERENCES business_profiles(id)
        )
    ''')
    
    # Inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            reorder_level INTEGER DEFAULT 10,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_id) REFERENCES business_profiles(id)
        )
    ''')
    
    # Scheduled reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER NOT NULL,
            report_type TEXT NOT NULL, -- 'weekly', 'monthly'
            email TEXT NOT NULL,
            schedule_day INTEGER, -- 0=Monday, 6=Sunday for weekly; 1-31 for monthly
            active BOOLEAN DEFAULT 1,
            last_sent TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_id) REFERENCES business_profiles(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# ============================================================
# AUTHENTICATION FUNCTIONS
# ============================================================
SECRET_KEY = "bizsight_ai_secret_key_2024"

def hash_password(password):
    """Hash password using SHA-256"""
    return sha256(password.encode()).hexdigest()

def generate_token(user_id):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def register_user(username, email, password):
    """Register new user"""
    conn = sqlite3.connect('bizsight.db')
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        return True, "User registered successfully!"
    except sqlite3.IntegrityError:
        return False, "Username or email already exists!"
    finally:
        conn.close()

def login_user(username, password):
    """Authenticate user"""
    conn = sqlite3.connect('bizsight.db')
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    cursor.execute(
        'SELECT id FROM users WHERE (username = ? OR email = ?) AND password_hash = ?',
        (username, username, password_hash)
    )
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        token = generate_token(result[0])
        return True, token, result[0]
    else:
        return False, None, None

def create_business_profile(user_id, business_name, business_type, city):
    """Create business profile for user"""
    conn = sqlite3.connect('bizsight.db')
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO business_profiles (user_id, business_name, business_type, city) VALUES (?, ?, ?, ?)',
        (user_id, business_name, business_type, city)
    )
    business_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return business_id

def get_user_businesses(user_id):
    """Get all business profiles for a user"""
    conn = sqlite3.connect('bizsight.db')
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT id, business_name, business_type, city FROM business_profiles WHERE user_id = ?',
        (user_id,)
    )
    businesses = cursor.fetchall()
    conn.close()
    
    return businesses

def add_transaction(business_id, transaction_type, amount, category, description, receipt_image=None):
    """Add sales or expense transaction"""
    conn = sqlite3.connect('bizsight.db')
    cursor = conn.cursor()
    
    cursor.execute(
        '''INSERT INTO transactions 
        (business_id, transaction_type, amount, category, description, receipt_image) 
        VALUES (?, ?, ?, ?, ?, ?)''',
        (business_id, transaction_type, amount, category, description, receipt_image)
    )
    conn.commit()
    conn.close()

def get_transactions(business_id, start_date=None, end_date=None, transaction_type=None):
    """Get transactions for a business"""
    conn = sqlite3.connect('bizsight.db')
    cursor = conn.cursor()
    
    query = 'SELECT * FROM transactions WHERE business_id = ?'
    params = [business_id]
    
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)
    if transaction_type:
        query += ' AND transaction_type = ?'
        params.append(transaction_type)
    
    query += ' ORDER BY date DESC'
    
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    conn.close()
    
    return transactions

def add_inventory_item(business_id, item_name, quantity, unit_price, reorder_level=10):
    """Add inventory item"""
    conn = sqlite3.connect('bizsight.db')
    cursor = conn.cursor()
    
    cursor.execute(
        '''INSERT INTO inventory 
        (business_id, item_name, quantity, unit_price, reorder_level) 
        VALUES (?, ?, ?, ?, ?)''',
        (business_id, item_name, quantity, unit_price, reorder_level)
    )
    conn.commit()
    conn.close()

def update_inventory(business_id, item_id, quantity_change):
    """Update inventory quantity"""
    conn = sqlite3.connect('bizsight.db')
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE inventory SET quantity = quantity + ?, last_updated = CURRENT_TIMESTAMP WHERE id = ? AND business_id = ?',
        (quantity_change, item_id, business_id)
    )
    conn.commit()
    conn.close()

def get_inventory(business_id):
    """Get inventory items for a business"""
    conn = sqlite3.connect('bizsight.db')
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM inventory WHERE business_id = ? ORDER BY item_name',
        (business_id,)
    )
    inventory = cursor.fetchall()
    conn.close()
    
    return inventory

def get_low_stock_items(business_id):
    """Get items below reorder level"""
    conn = sqlite3.connect('bizsight.db')
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM inventory WHERE business_id = ? AND quantity <= reorder_level',
        (business_id,)
    )
    low_stock = cursor.fetchall()
    conn.close()
    
    return low_stock

def schedule_report(business_id, report_type, email, schedule_day):
    """Schedule automated report"""
    conn = sqlite3.connect('bizsight.db')
    cursor = conn.cursor()
    
    cursor.execute(
        '''INSERT INTO scheduled_reports 
        (business_id, report_type, email, schedule_day) 
        VALUES (?, ?, ?, ?)''',
        (business_id, report_type, email, schedule_day)
    )
    conn.commit()
    conn.close()

def get_scheduled_reports(business_id):
    """Get scheduled reports for a business"""
    conn = sqlite3.connect('bizsight.db')
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM scheduled_reports WHERE business_id = ? AND active = 1',
        (business_id,)
    )
    reports = cursor.fetchall()
    conn.close()
    
    return reports

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
    
    /* Authentication Forms */
    .auth-container {
        max-width: 500px;
        margin: 2rem auto;
        background: white;
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    
    .auth-title {
        text-align: center;
        color: #1E3A8A;
        font-size: 2rem;
        margin-bottom: 1.5rem;
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
    
    /* Transaction Cards */
    .transaction-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #3B82F6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .transaction-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    .transaction-sale {
        border-left-color: #10B981;
    }
    
    .transaction-expense {
        border-left-color: #EF4444;
    }
    
    /* Inventory Alerts */
    .alert-low-stock {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #EF4444;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Business Profile Cards */
    .business-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 2px solid #E5E7EB;
        transition: all 0.3s ease;
    }
    
    .business-card:hover {
        border-color: #3B82F6;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
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
# SESSION STATE INITIALIZATION
# ============================================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_business_id' not in st.session_state:
    st.session_state.current_business_id = None
if 'current_business_name' not in st.session_state:
    st.session_state.current_business_name = None

# For analytics section
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df_raw' not in st.session_state:
    st.session_state.df_raw = None
if 'df' not in st.session_state:
    st.session_state.df = None

# ============================================================
# LOAD AND PROCESS DATA FUNCTION
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

# ============================================================
# AUTHENTICATION PAGE
# ============================================================
def show_auth_page():
    """Display authentication page"""
    st.markdown("<h1 class='main-header'>BizSight AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-header'>Your Business Intelligence Platform</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            st.markdown("<h3 class='auth-title'>Welcome Back</h3>", unsafe_allow_html=True)
            
            username = st.text_input("Username or Email", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", type="primary", key="login_btn"):
                if username and password:
                    success, token, user_id = login_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials!")
                else:
                    st.warning("⚠️ Please fill in all fields")
        
        with tab2:
            st.markdown("<h3 class='auth-title'>Create Account</h3>", unsafe_allow_html=True)
            
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            if st.button("Register", type="primary", key="register_btn"):
                if not all([new_username, new_email, new_password, confirm_password]):
                    st.warning("⚠️ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match!")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters!")
                else:
                    success, message = register_user(new_username, new_email, new_password)
                    if success:
                        st.success(f"✅ {message} Please login to continue.")
                    else:
                        st.error(f"❌ {message}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; margin-top: 2rem;'>
            <p style='color: #6B7280;'>Or try analytics without authentication</p>
            <a href='#analytics-demo' style='
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                margin-top: 1rem;
            '>Try Analytics Demo</a>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# BUSINESS PROFILE MANAGEMENT
# ============================================================
def show_business_setup():
    """Display business profile setup"""
    st.markdown("### 🏢 Business Profile Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        business_name = st.text_input("Business Name *")
        business_type = st.selectbox(
            "Business Type",
            ["Retail", "Restaurant", "Services", "Manufacturing", "E-commerce", "Other"]
        )
    
    with col2:
        city = st.text_input("City")
    
    if st.button("Create Business Profile", type="primary"):
        if business_name:
            business_id = create_business_profile(
                st.session_state.user_id,
                business_name,
                business_type,
                city
            )
            st.session_state.current_business_id = business_id
            st.session_state.current_business_name = business_name
            st.success(f"✅ Business profile '{business_name}' created successfully!")
            st.rerun()
        else:
            st.warning("⚠️ Please enter business name")

def select_business():
    """Allow user to select from existing businesses"""
    businesses = get_user_businesses(st.session_state.user_id)
    
    if businesses:
        business_options = {f"{b[1]} ({b[2]})": b[0] for b in businesses}
        selected = st.selectbox(
            "Select Business",
            options=list(business_options.keys()),
            key="business_selector"
        )
        
        if st.button("Switch to Selected Business", type="primary"):
            st.session_state.current_business_id = business_options[selected]
            st.session_state.current_business_name = selected.split(' (')[0]
            st.success(f"✅ Switched to {selected}")
            st.rerun()
        
        return True
    else:
        return False

# ============================================================
# TRANSACTION MANAGEMENT MODULE
# ============================================================
def show_transaction_management():
    """Display transaction management interface"""
    st.markdown("<h2 class='section-header'>💰 Sales & Expense Management</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Transaction", "📋 View Transactions", "📊 Transaction Analytics"])
    
    with tab1:
        st.markdown("### Add New Transaction")
        
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_type = st.radio(
                "Transaction Type",
                ["Sale", "Expense"],
                horizontal=True
            )
            
            amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                step=10.0,
                format="%.2f"
            )
            
            category = st.text_input("Category (e.g., Rent, Supplies, Food Sales)")
        
        with col2:
            description = st.text_area("Description", height=100)
            
            receipt_file = st.file_uploader(
                "Upload Receipt/Invoice (optional)",
                type=["jpg", "jpeg", "png", "pdf"]
            )
            
            receipt_image = None
            if receipt_file:
                receipt_image = receipt_file.read()
                st.success("✅ Receipt uploaded successfully!")
        
        if st.button("Save Transaction", type="primary"):
            if amount > 0 and category:
                add_transaction(
                    st.session_state.current_business_id,
                    transaction_type.lower(),
                    amount,
                    category,
                    description,
                    receipt_image
                )
                st.success(f"✅ {transaction_type} transaction recorded successfully!")
                st.rerun()
            else:
                st.warning("⚠️ Please fill in amount and category")
    
    with tab2:
        st.markdown("### Transaction History")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now())
        with col3:
            filter_type = st.selectbox("Filter Type", ["All", "Sales", "Expenses"])
        
        transactions = get_transactions(
            st.session_state.current_business_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            filter_type.lower() if filter_type != "All" else None
        )
        
        if transactions:
            df_transactions = pd.DataFrame(
                transactions,
                columns=['ID', 'Business ID', 'Type', 'Amount', 'Category', 'Description', 'Date', 'Receipt', 'Created At']
            )
            
            # Display transactions
            for _, row in df_transactions.iterrows():
                card_class = "transaction-sale" if row['Type'] == 'sale' else "transaction-expense"
                amount_sign = "+" if row['Type'] == 'sale' else "-"
                amount_color = "#10B981" if row['Type'] == 'sale' else "#EF4444"
                
                st.markdown(f"""
                <div class='transaction-card {card_class}'>
                    <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;'>
                        <div>
                            <span style='font-size: 1.2rem; font-weight: 700; color: {amount_color};'>
                                {amount_sign}₹{row['Amount']:,.2f}
                            </span>
                            <span style='margin-left: 1rem; color: #6B7280; font-size: 0.9rem;'>
                                {row['Date']}
                            </span>
                        </div>
                        <span style='background: {amount_color}15; color: {amount_color}; padding: 0.25rem 0.75rem; 
                              border-radius: 12px; font-size: 0.85rem; font-weight: 600;'>
                            {row['Type'].title()}
                        </span>
                    </div>
                    <div style='margin-bottom: 0.5rem;'>
                        <strong>Category:</strong> {row['Category']}
                    </div>
                    <div style='color: #6B7280; margin-bottom: 0.5rem;'>
                        {row['Description'] if row['Description'] else 'No description'}
                    </div>
                    {'<div style="color: #10B981; font-size: 0.9rem;">📎 Receipt attached</div>' if row['Receipt'] else ''}
                </div>
                """, unsafe_allow_html=True)
            
            # Summary statistics
            st.markdown("### Summary")
            total_sales = df_transactions[df_transactions['Type'] == 'sale']['Amount'].sum()
            total_expenses = df_transactions[df_transactions['Type'] == 'expense']['Amount'].sum()
            net_profit = total_sales - total_expenses
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sales", f"₹{total_sales:,.2f}")
            with col2:
                st.metric("Total Expenses", f"₹{total_expenses:,.2f}")
            with col3:
                st.metric("Net Profit", f"₹{net_profit:,.2f}", delta=f"{(net_profit/total_sales*100) if total_sales > 0 else 0:.1f}%")
        else:
            st.info("📭 No transactions found for the selected period.")
    
    with tab3:
        st.markdown("### Transaction Analytics")
        
        transactions = get_transactions(st.session_state.current_business_id)
        
        if transactions:
            df_trans = pd.DataFrame(
                transactions,
                columns=['ID', 'Business ID', 'Type', 'Amount', 'Category', 'Description', 'Date', 'Receipt', 'Created At']
            )
            
            # Category-wise breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Expense Categories")
                expense_data = df_trans[df_trans['Type'] == 'expense'].groupby('Category')['Amount'].sum().reset_index()
                if not expense_data.empty:
                    fig = px.pie(
                        expense_data,
                        values='Amount',
                        names='Category',
                        title='Expense Distribution',
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Sales Categories")
                sales_data = df_trans[df_trans['Type'] == 'sale'].groupby('Category')['Amount'].sum().reset_index()
                if not sales_data.empty:
                    fig = px.bar(
                        sales_data,
                        x='Category',
                        y='Amount',
                        title='Sales by Category',
                        color='Amount',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Daily trend
            df_trans['Date'] = pd.to_datetime(df_trans['Date'])
            daily_trend = df_trans.groupby([df_trans['Date'].dt.date, 'Type'])['Amount'].sum().unstack(fill_value=0).reset_index()
            
            if not daily_trend.empty:
                fig = px.line(
                    daily_trend,
                    x='Date',
                    y=['sale', 'expense'],
                    title='Daily Sales vs Expenses Trend',
                    labels={'value': 'Amount (₹)', 'variable': 'Type'}
                )
                st.plotly_chart(fig, use_container_width=True)

# ============================================================
# INVENTORY MANAGEMENT MODULE
# ============================================================
def show_inventory_management():
    """Display inventory management interface"""
    st.markdown("<h2 class='section-header'>📦 Inventory Management</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Item", "📋 Inventory List", "📊 Inventory Analytics"])
    
    with tab1:
        st.markdown("### Add New Inventory Item")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            item_name = st.text_input("Item Name *")
            quantity = st.number_input("Quantity *", min_value=0, step=1)
        
        with col2:
            unit_price = st.number_input("Unit Price (₹) *", min_value=0.0, step=1.0, format="%.2f")
            reorder_level = st.number_input("Reorder Level", min_value=0, step=1, value=10)
        
        with col3:
            st.info("💡 Reorder level is the minimum quantity before you receive a low stock alert.")
        
        if st.button("Add to Inventory", type="primary"):
            if item_name and quantity >= 0 and unit_price > 0:
                add_inventory_item(
                    st.session_state.current_business_id,
                    item_name,
                    quantity,
                    unit_price,
                    reorder_level
                )
                st.success(f"✅ Item '{item_name}' added to inventory!")
                st.rerun()
            else:
                st.warning("⚠️ Please fill in all required fields")
    
    with tab2:
        st.markdown("### Current Inventory")
        
        inventory = get_inventory(st.session_state.current_business_id)
        
        if inventory:
            df_inventory = pd.DataFrame(
                inventory,
                columns=['ID', 'Business ID', 'Item Name', 'Quantity', 'Unit Price', 'Reorder Level', 'Last Updated']
            )
            
            # Low stock alerts
            low_stock = df_inventory[df_inventory['Quantity'] <= df_inventory['Reorder Level']]
            if not low_stock.empty:
                st.markdown("### ⚠️ Low Stock Alerts")
                for _, item in low_stock.iterrows():
                    st.markdown(f"""
                    <div class='alert-low-stock'>
                        <strong>📦 {item['Item Name']}</strong><br>
                        Current Stock: {item['Quantity']} units (Reorder Level: {item['Reorder Level']})<br>
                        Value: ₹{(item['Quantity'] * item['Unit Price']):,.2f}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Display inventory table
            df_display = df_inventory[['Item Name', 'Quantity', 'Unit Price', 'Reorder Level', 'Last Updated']].copy()
            df_display['Total Value'] = df_display['Quantity'] * df_display['Unit Price']
            df_display['Status'] = df_display.apply(
                lambda x: '⚠️ Low Stock' if x['Quantity'] <= x['Reorder Level'] else '✅ In Stock',
                axis=1
            )
            
            st.dataframe(df_display, use_container_width=True)
            
            # Update inventory
            st.markdown("### Update Inventory")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                item_to_update = st.selectbox(
                    "Select Item",
                    options=df_inventory['Item Name'].tolist(),
                    key="update_item"
                )
            
            with col2:
                item_id = df_inventory[df_inventory['Item Name'] == item_to_update]['ID'].iloc[0]
                quantity_change = st.number_input("Quantity Change", step=1, key="quantity_change")
            
            with col3:
                st.info("💡 Use positive numbers to add stock, negative to remove.")
            
            if st.button("Update Inventory", type="primary"):
                update_inventory(st.session_state.current_business_id, item_id, quantity_change)
                st.success(f"✅ Inventory updated for '{item_to_update}'!")
                st.rerun()
        else:
            st.info("📭 No inventory items found. Add items to get started.")
    
    with tab3:
        st.markdown("### Inventory Analytics")
        
        inventory = get_inventory(st.session_state.current_business_id)
        
        if inventory:
            df_inv = pd.DataFrame(
                inventory,
                columns=['ID', 'Business ID', 'Item Name', 'Quantity', 'Unit Price', 'Reorder Level', 'Last Updated']
            )
            
            df_inv['Total Value'] = df_inv['Quantity'] * df_inv['Unit Price']
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Inventory value by item
                fig = px.bar(
                    df_inv,
                    x='Item Name',
                    y='Total Value',
                    title='Inventory Value by Item',
                    color='Total Value',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Stock levels
                fig = px.bar(
                    df_inv,
                    x='Item Name',
                    y='Quantity',
                    title='Stock Levels',
                    color='Quantity',
                    color_continuous_scale='Blues'
                )
                fig.add_hline(
                    y=df_inv['Reorder Level'].mean(),
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Avg Reorder Level"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Summary metrics
            total_items = len(df_inv)
            total_value = df_inv['Total Value'].sum()
            low_stock_count = len(df_inv[df_inv['Quantity'] <= df_inv['Reorder Level']])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Items", total_items)
            with col2:
                st.metric("Total Inventory Value", f"₹{total_value:,.2f}")
            with col3:
                st.metric("Items Needing Reorder", low_stock_count)

# ============================================================
# REPORT GENERATION MODULE
# ============================================================
def generate_pdf_report(business_name, transactions, inventory, period="Monthly"):
    """Generate PDF report using ReportLab"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    story.append(Paragraph(f"BizSight AI - {period} Business Report", title_style))
    story.append(Paragraph(f"Business: {business_name}", styles['Normal']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    
    if transactions:
        df_trans = pd.DataFrame(
            transactions,
            columns=['ID', 'Business ID', 'Type', 'Amount', 'Category', 'Description', 'Date', 'Receipt', 'Created At']
        )
        
        total_sales = df_trans[df_trans['Type'] == 'sale']['Amount'].sum()
        total_expenses = df_trans[df_trans['Type'] == 'expense']['Amount'].sum()
        net_profit = total_sales - total_expenses
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Sales', f"₹{total_sales:,.2f}"],
            ['Total Expenses', f"₹{total_expenses:,.2f}"],
            ['Net Profit', f"₹{net_profit:,.2f}"],
            ['Profit Margin', f"{(net_profit/total_sales*100) if total_sales > 0 else 0:.1f}%"]
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
    
    # Transaction Summary
    if transactions:
        story.append(Paragraph("Transaction Summary", styles['Heading2']))
        
        trans_data = [['Date', 'Type', 'Category', 'Amount (₹)']]
        for trans in transactions[:20]:  # Limit to 20 for report
            trans_data.append([
                trans[6][:10] if trans[6] else '',
                trans[2].title(),
                trans[4],
                f"{trans[3]:,.2f}"
            ])
        
        trans_table = Table(trans_data)
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT')
        ]))
        
        story.append(trans_table)
        story.append(Spacer(1, 20))
    
    # Inventory Summary
    if inventory:
        story.append(Paragraph("Inventory Summary", styles['Heading2']))
        
        inv_data = [['Item Name', 'Quantity', 'Unit Price (₹)', 'Total Value (₹)', 'Status']]
        for item in inventory:
            status = '⚠️ Low Stock' if item[3] <= item[5] else '✅ OK'
            inv_data.append([
                item[2],
                str(item[3]),
                f"{item[4]:,.2f}",
                f"{item[3] * item[4]:,.2f}",
                status
            ])
        
        inv_table = Table(inv_data)
        inv_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (3, -1), 'RIGHT')
        ]))
        
        story.append(inv_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def show_report_generation():
    """Display report generation interface"""
    st.markdown("<h2 class='section-header'>📊 Report Generation</h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📥 Generate Report", "⏰ Schedule Reports"])
    
    with tab1:
        st.markdown("### Generate Business Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_period = st.selectbox("Report Period", ["Weekly", "Monthly", "Custom Range"])
            
            if report_period == "Custom Range":
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
        
        with col2:
            report_format = st.selectbox("Report Format", ["PDF", "Excel"])
        
        if st.button("Generate Report", type="primary"):
            with st.spinner("Generating report..."):
                # Get data
                transactions = get_transactions(st.session_state.current_business_id)
                inventory = get_inventory(st.session_state.current_business_id)
                
                if report_format == "PDF":
                    pdf_buffer = generate_pdf_report(
                        st.session_state.current_business_name,
                        transactions,
                        inventory,
                        report_period
                    )
                    
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"{st.session_state.current_business_name}_{report_period}_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                    
                    st.success("✅ Report generated successfully!")
                else:
                    # Excel format
                    df_trans = pd.DataFrame(
                        transactions,
                        columns=['ID', 'Business ID', 'Type', 'Amount', 'Category', 'Description', 'Date', 'Receipt', 'Created At']
                    ) if transactions else pd.DataFrame()
                    
                    df_inv = pd.DataFrame(
                        inventory,
                        columns=['ID', 'Business ID', 'Item Name', 'Quantity', 'Unit Price', 'Reorder Level', 'Last Updated']
                    ) if inventory else pd.DataFrame()
                    
                    # Create Excel file
                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        if not df_trans.empty:
                            df_trans.to_excel(writer, sheet_name='Transactions', index=False)
                        if not df_inv.empty:
                            df_inv.to_excel(writer, sheet_name='Inventory', index=False)
                    
                    excel_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=excel_buffer,
                        file_name=f"{st.session_state.current_business_name}_{report_period}_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    st.success("✅ Excel report generated successfully!")
    
    with tab2:
        st.markdown("### Schedule Automated Reports")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            schedule_type = st.selectbox("Report Type", ["Weekly", "Monthly"])
        
        with col2:
            if schedule_type == "Weekly":
                schedule_day = st.selectbox(
                    "Day of Week",
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                )
                day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, 
                          "Friday": 4, "Saturday": 5, "Sunday": 6}
                schedule_day_num = day_map[schedule_day]
            else:
                schedule_day = st.number_input("Day of Month", min_value=1, max_value=31, value=1)
                schedule_day_num = int(schedule_day)
        
        with col3:
            email = st.text_input("Email Address", value=st.session_state.get('user_email', ''))
        
        if st.button("Schedule Report", type="primary"):
            if email and '@' in email:
                schedule_report(
                    st.session_state.current_business_id,
                    schedule_type.lower(),
                    email,
                    schedule_day_num
                )
                st.success(f"✅ {schedule_type} reports scheduled to be sent to {email}!")
            else:
                st.warning("⚠️ Please enter a valid email address")
        
        # Show scheduled reports
        st.markdown("### Current Scheduled Reports")
        scheduled = get_scheduled_reports(st.session_state.current_business_id)
        
        if scheduled:
            for report in scheduled:
                report_type = "Weekly" if report[3] == "weekly" else "Monthly"
                st.info(f"📧 {report_type} reports to {report[4]} (Day: {report[5]})")
        else:
            st.info("📭 No scheduled reports yet.")

# ============================================================
# ANALYTICS MODULE (FROM FIRST CODE)
# ============================================================
def show_analytics_dashboard():
    """Display the analytics dashboard"""
    st.markdown("<h2 class='section-header'>📈 Advanced Business Analytics</h2>", unsafe_allow_html=True)
    
    # Initialize session state for analytics
    if 'analytics_data_loaded' not in st.session_state:
        st.session_state.analytics_data_loaded = False
    if 'analytics_df' not in st.session_state:
        st.session_state.analytics_df = None
    if 'analytics_df_raw' not in st.session_state:
        st.session_state.analytics_df_raw = None
    
    # Sidebar for analytics
    with st.sidebar:
        st.markdown("### 📊 Data Source Selection")
        
        data_source = st.radio(
            "Choose data source:",
            ["Upload your own file", "Use sample data (100K records)", "Use advanced sample dataset (50K records)"],
            index=0,
            help="Select how you want to load data for analysis"
        )
        
        uploaded_file = None
        if data_source == "Upload your own file":
            uploaded_file = st.file_uploader(
                "Upload business dataset",
                type=["csv", "xlsx"],
                help="Upload CSV or Excel file containing business data"
            )
        
        # Load data based on user selection
        df_raw = None
        if data_source == "Upload your own file" and uploaded_file is not None:
            df_raw = load_data(uploaded_file)
            if df_raw is not None and not df_raw.empty:
                st.success("✅ Data loaded successfully!")
        elif data_source == "Use sample data (100K records)":
            df_raw = load_data(sample=True)
            st.success("✅ Sample data with 100,000 records loaded")
        elif data_source == "Use advanced sample dataset (50K records)":
            df_raw = load_data(advanced_sample=True)
            st.success("✅ Advanced sample data with 50,000 records loaded")
        else:
            if not st.session_state.analytics_data_loaded:
                st.info("💡 Please select a data source to begin analytics")
        
        if df_raw is not None and not df_raw.empty:
            # Process data
            df = align_schema(df_raw.copy())
            
            # Calculate monthly_sales
            df["monthly_sales"] = (
                df["avg_daily_footfall"] * df["conversion_rate"] * df["avg_transaction_value"] * 30
            )
            
            # Add derived metrics
            df["sales_per_sqft"] = df["monthly_sales"] / df["store_size_sqft"].replace(0, 1)
            df["sales_per_employee"] = df["monthly_sales"] / df["employee_count"].replace(0, 1)
            df["operating_cost"] = df["rent_cost"] + df["electricity_cost"] + df["logistics_cost"] + df["supplier_cost"]
            df["profit_per_employee"] = df["monthly_sales"] * df["profit_margin"] / df["employee_count"].replace(0, 1)
            df["cost_to_sales_ratio"] = df["operating_cost"] / df["monthly_sales"].replace(0, 1)
            df["roi_per_employee"] = df["employee_efficiency"] / df["avg_employee_salary"].replace(0, 1)
            
            # Model prediction
            if model:
                df["predicted_profit"] = model.predict(df)
            else:
                # Generate synthetic predictions for demonstration
                np.random.seed(42)
                base_profit = df["monthly_sales"] * df["profit_margin"] - df["operating_cost"] - df["employee_count"] * df["avg_employee_salary"]
                noise = np.random.normal(0, 0.1 * abs(base_profit).mean(), len(df))
                df["predicted_profit"] = np.maximum(base_profit + noise, 0)
            
            df["risk_band"] = pd.qcut(df["predicted_profit"], 3, labels=["Low", "Medium", "High"])
            
            # Add advanced scores
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
            
            # Create performance tiers
            if 'predicted_profit' in df.columns and 'monthly_sales' in df.columns and 'employee_efficiency' in df.columns:
                performance_score = (df['predicted_profit'].rank(pct=True) * 0.4 + 
                                   df['monthly_sales'].rank(pct=True) * 0.3 + 
                                   df['employee_efficiency'].rank(pct=True) * 0.3)
                df['performance_tier'] = pd.qcut(performance_score, 5, 
                                                labels=['Poor', 'Below Avg', 'Average', 'Good', 'Excellent'])
            else:
                df['performance_tier'] = 'Average'
            
            # Store in session state
            st.session_state.analytics_data_loaded = True
            st.session_state.analytics_df_raw = df_raw
            st.session_state.analytics_df = df
            
            # Filters
            st.markdown("---")
            st.markdown("### 🔍 Data Filters")
            
            if 'risk_band' in df.columns:
                risk_filter = st.multiselect(
                    "Select Risk Levels",
                    ["Low", "Medium", "High"],
                    default=["Low", "Medium", "High"],
                    key="analytics_risk_filter"
                )
                df = df[df['risk_band'].isin(risk_filter)]
            
            if 'business_type' in df.columns:
                business_types = ["All"] + sorted(df['business_type'].unique().tolist())
                business_filter = st.multiselect(
                    "Select Business Types",
                    business_types,
                    default=["All"],
                    key="analytics_business_filter"
                )
                if business_filter and "All" not in business_filter:
                    df = df[df['business_type'].isin(business_filter)]
            
            # Update the filtered dataframe
            st.session_state.analytics_df = df
    
    # Main analytics content
    if not st.session_state.analytics_data_loaded or st.session_state.analytics_df is None:
        st.markdown("""
        <div class='welcome-message'>
            <h2>Welcome to BizSight AI Analytics! 🚀</h2>
            <p style='font-size: 1.2rem; margin-bottom: 1.5rem;'>
                Advanced Business Intelligence Platform for data-driven decision making
            </p>
            <p style='font-size: 1rem; margin-bottom: 2rem;'>
                To get started, please select a data source from the sidebar.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    df = st.session_state.analytics_df
    
    # Calculate metrics
    avg_profit = df["predicted_profit"].mean()
    avg_sales = df["monthly_sales"].mean()
    risk_percentage = (df["risk_band"] == 'High').mean() * 100 if 'risk_band' in df.columns else 0
    total_records = len(df)
    profit_margin_val = (df['predicted_profit'].sum() / df['monthly_sales'].sum() * 100) if df['monthly_sales'].sum() > 0 else 0
    avg_roi = df['marketing_roi'].mean() if 'marketing_roi' in df.columns else 2.0
    inventory_turnover = (df['monthly_sales'].sum() / df['inventory_level'].sum()) if df['inventory_level'].sum() > 0 else 0
    employee_productivity = df['employee_efficiency'].mean() if 'employee_efficiency' in df.columns else 50000
    
    # Display metrics
    st.markdown("<h2 class='section-header'>Executive Dashboard</h2>", unsafe_allow_html=True)
    
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
    
    # Additional metrics
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
    
    # Data preview
    with st.expander("Dataset Overview", expanded=False):
        tab1, tab2, tab3 = st.tabs(["Data Preview", "Statistics", "Data Quality"])
        
        with tab1:
            st.dataframe(df.head(100), use_container_width=True)
        
        with tab2:
            st.dataframe(df.describe(), use_container_width=True)
        
        with tab3:
            missing_df = pd.DataFrame({
                'Column': df.columns,
                'Missing Values': df.isnull().sum(),
                'Missing %': (df.isnull().sum() / len(df) * 100).round(2)
            })
            st.dataframe(missing_df, use_container_width=True)
    
    # Visualizations
    st.markdown("<h2 class='section-header'>Comprehensive Analytics Dashboard</h2>", unsafe_allow_html=True)
    
    viz_tabs = st.tabs([
        "📊 Sales Analytics", 
        "💰 Profit Analytics", 
        "⚠️ Risk Analytics", 
        "📈 Performance Trends"
    ])
    
    with viz_tabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'business_type' in df.columns:
                sales_by_type = df.groupby('business_type')['monthly_sales'].mean().reset_index()
                fig = px.bar(sales_by_type, x='business_type', y='monthly_sales',
                            title='Average Sales by Business Type',
                            color='monthly_sales',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'city' in df.columns:
                city_sales = df.groupby('city')['monthly_sales'].mean().reset_index().head(10)
                fig = px.bar(city_sales, x='city', y='monthly_sales',
                            title='Top 10 Cities by Sales',
                            color='monthly_sales',
                            color_continuous_scale='Plasma')
                st.plotly_chart(fig, use_container_width=True)
    
    with viz_tabs[1]:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'business_type' in df.columns:
                profit_by_type = df.groupby('business_type')['predicted_profit'].mean().reset_index()
                fig = px.bar(profit_by_type, x='business_type', y='predicted_profit',
                            title='Average Profit by Business Type',
                            color='predicted_profit',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'profit_margin' in df.columns:
                fig = px.histogram(df, x='profit_margin', nbins=30,
                                  title='Profit Margin Distribution',
                                  color_discrete_sequence=[COLOR_PALETTE['primary']])
                st.plotly_chart(fig, use_container_width=True)
    
    with viz_tabs[2]:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'risk_band' in df.columns:
                risk_dist = df['risk_band'].value_counts().reset_index()
                risk_dist.columns = ['Risk Category', 'Count']
                fig = px.pie(risk_dist, values='Count', names='Risk Category',
                            title='Risk Category Distribution',
                            color_discrete_sequence=[COLOR_PALETTE['secondary'], 
                                                    COLOR_PALETTE['warning'], 
                                                    COLOR_PALETTE['danger']])
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if all(col in df.columns for col in ['risk_band', 'predicted_profit']):
                risk_profit = df.groupby('risk_band')['predicted_profit'].mean().reset_index()
                fig = px.bar(risk_profit, x='risk_band', y='predicted_profit',
                            title='Average Profit by Risk Category',
                            color='predicted_profit',
                            color_discrete_map={
                                'Low': COLOR_PALETTE['success'],
                                'Medium': COLOR_PALETTE['warning'],
                                'High': COLOR_PALETTE['danger']
                            })
                st.plotly_chart(fig, use_container_width=True)
    
    with viz_tabs[3]:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'years_of_operation' in df.columns:
                growth_trend = df.groupby('years_of_operation')['monthly_sales'].mean().reset_index()
                fig = px.line(growth_trend, x='years_of_operation', y='monthly_sales',
                             title='Sales Growth by Business Age',
                             markers=True)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if all(col in df.columns for col in ['employee_efficiency', 'predicted_profit']):
                df_sample = df.sample(min(1000, len(df)))
                fig = px.scatter(df_sample, x='employee_efficiency', y='predicted_profit',
                                title='Employee Efficiency vs Profit',
                                trendline='ols')
                st.plotly_chart(fig, use_container_width=True)
    
    # Predictive Simulation
    st.markdown("<h2 class='section-header'>Business Scenario Simulation</h2>", unsafe_allow_html=True)
    
    with st.container():
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        
        with sim_col1:
            st.markdown("#### Sales Parameters")
            marketing_spend = st.slider("Marketing Spend (₹)", 10000, 200000, 50000, 5000, key="sim_marketing")
            avg_footfall = st.slider("Daily Footfall", 50, 1000, 200, 10, key="sim_footfall")
            conversion_rate = st.slider("Conversion Rate", 0.1, 0.5, 0.2, 0.01, key="sim_conversion")
        
        with sim_col2:
            st.markdown("#### Cost Parameters")
            avg_salary = st.number_input("Average Salary (₹)", 15000, 50000, 25000, 1000, key="sim_salary")
            rent_cost = st.number_input("Monthly Rent (₹)", 10000, 100000, 30000, 5000, key="sim_rent")
            inventory_level = st.number_input("Inventory Level", 100, 5000, 1000, 100, key="sim_inventory")
        
        with sim_col3:
            st.markdown("#### Business Profile")
            employee_count = st.slider("Employee Count", 1, 100, 10, 1, key="sim_employees")
            city_tier = st.select_slider("City Tier", options=[1, 2, 3], value=2, key="sim_city_tier")
            discount_pct = st.slider("Discount Percentage", 0, 50, 10, 1, key="sim_discount")
        
        festival_season = st.checkbox("Festival Season", value=False, key="sim_festival")
        
        if st.button("Run Predictive Simulation", type="primary", key="sim_run"):
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
    
    # Data Export
    st.markdown("<h2 class='section-header'>Data Export & Reports</h2>", unsafe_allow_html=True)
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        if st.button("📥 Download Analyzed Data (CSV)", key="export_csv"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Click to download CSV",
                data=csv,
                file_name="business_analysis_results.csv",
                mime="text/csv",
                key="download_csv"
            )
    
    with export_col2:
        if st.button("📊 Generate Executive Summary", key="export_summary"):
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

# ============================================================
# MAIN APPLICATION
# ============================================================
def main_app():
    """Main application after authentication"""
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 1.5rem;'>
            <h2 style='color: #1E3A8A; font-size: 1.5rem; margin-bottom: 0.5rem;'>
                👋 Welcome, {st.session_state.username}!
            </h2>
            <p style='color: #6B7280; font-size: 0.9rem;'>
                Business: {st.session_state.current_business_name or 'Not Selected'}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📱 Navigation")
        
        if st.session_state.current_business_id:
            page = st.radio(
                "Go to",
                ["Dashboard", "Transaction Management", "Inventory Management", 
                 "Advanced Analytics", "Reports", "Settings"],
                label_visibility="collapsed"
            )
        else:
            page = "Business Setup"
        
        st.markdown("---")
        
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content
    if not st.session_state.current_business_id:
        show_business_setup()
        
        st.markdown("### or")
        
        if select_business():
            pass
        else:
            st.info("💡 Create a business profile or select an existing one to get started!")
    
    else:
        if page == "Dashboard":
            show_dashboard()
        elif page == "Transaction Management":
            show_transaction_management()
        elif page == "Inventory Management":
            show_inventory_management()
        elif page == "Advanced Analytics":
            show_analytics_dashboard()
        elif page == "Reports":
            show_report_generation()
        elif page == "Settings":
            show_settings()

def show_dashboard():
    """Display main dashboard"""
    st.markdown("<h1 class='main-header'>BizSight AI Dashboard</h1>", unsafe_allow_html=True)
    
    # Get data
    transactions = get_transactions(st.session_state.current_business_id)
    inventory = get_inventory(st.session_state.current_business_id)
    
    # Calculate metrics
    if transactions:
        df_trans = pd.DataFrame(
            transactions,
            columns=['ID', 'Business ID', 'Type', 'Amount', 'Category', 'Description', 'Date', 'Receipt', 'Created At']
        )
        
        total_sales = df_trans[df_trans['Type'] == 'sale']['Amount'].sum()
        total_expenses = df_trans[df_trans['Type'] == 'expense']['Amount'].sum()
        net_profit = total_sales - total_expenses
        profit_margin = (net_profit / total_sales * 100) if total_sales > 0 else 0
    else:
        total_sales = total_expenses = net_profit = profit_margin = 0
    
    if inventory:
        df_inv = pd.DataFrame(
            inventory,
            columns=['ID', 'Business ID', 'Item Name', 'Quantity', 'Unit Price', 'Reorder Level', 'Last Updated']
        )
        total_inventory_value = (df_inv['Quantity'] * df_inv['Unit Price']).sum()
        low_stock_count = len(df_inv[df_inv['Quantity'] <= df_inv['Reorder Level']])
    else:
        total_inventory_value = 0
        low_stock_count = 0
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card metric-card-primary'>
            <div style='font-size: 2rem; font-weight: 800; color: #1F2937; margin-bottom: 0.5rem;'>
                ₹{total_sales:,.0f}
            </div>
            <div style='font-size: 1rem; color: #6B7280; font-weight: 500;'>
                Total Sales
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card metric-card-secondary'>
            <div style='font-size: 2rem; font-weight: 800; color: #1F2937; margin-bottom: 0.5rem;'>
                ₹{net_profit:,.0f}
            </div>
            <div style='font-size: 1rem; color: #6B7280; font-weight: 500;'>
                Net Profit
            </div>
            <div style='font-size: 0.85rem; color: #10B981; margin-top: 0.5rem;'>
                Margin: {profit_margin:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card metric-card-warning'>
            <div style='font-size: 2rem; font-weight: 800; color: #1F2937; margin-bottom: 0.5rem;'>
                ₹{total_inventory_value:,.0f}
            </div>
            <div style='font-size: 1rem; color: #6B7280; font-weight: 500;'>
                Inventory Value
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card metric-card-danger'>
            <div style='font-size: 2rem; font-weight: 800; color: #1F2937; margin-bottom: 0.5rem;'>
                {low_stock_count}
            </div>
            <div style='font-size: 1rem; color: #6B7280; font-weight: 500;'>
                Items Needing Reorder
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        if transactions:
            st.markdown("### Sales & Expenses Trend")
            df_trans['Date'] = pd.to_datetime(df_trans['Date'])
            daily_data = df_trans.groupby([df_trans['Date'].dt.date, 'Type'])['Amount'].sum().unstack(fill_value=0).reset_index()
            
            if not daily_data.empty:
                fig = px.line(
                    daily_data,
                    x='Date',
                    y=['sale', 'expense'],
                    title='Daily Performance',
                    labels={'value': 'Amount (₹)', 'variable': 'Type'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if inventory:
            st.markdown("### Inventory Status")
            fig = px.pie(
                df_inv,
                values='Quantity',
                names='Item Name',
                title='Inventory Distribution',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent transactions
    st.markdown("### Recent Transactions")
    if transactions:
        df_recent = df_trans.tail(10)[['Date', 'Type', 'Category', 'Amount']]
        df_recent['Date'] = pd.to_datetime(df_recent['Date']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(df_recent, use_container_width=True)
    else:
        st.info("📭 No transactions yet. Start by adding your first transaction!")

def show_settings():
    """Display settings page"""
    st.markdown("<h2 class='section-header'>⚙️ Settings</h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Business Profile", "Account Settings"])
    
    with tab1:
        st.markdown("### Business Information")
        st.info(f"**Business Name:** {st.session_state.current_business_name}")
        st.info(f"**Business ID:** {st.session_state.current_business_id}")
        
        if st.button("Switch Business"):
            st.session_state.current_business_id = None
            st.session_state.current_business_name = None
            st.rerun()
    
    with tab2:
        st.markdown("### Account Information")
        st.info(f"**Username:** {st.session_state.username}")
        st.info(f"**User ID:** {st.session_state.user_id}")
        
        st.markdown("### Export Data")
        if st.button("Export All Data"):
            transactions = get_transactions(st.session_state.current_business_id)
            inventory = get_inventory(st.session_state.current_business_id)
            
            data = {
                'business_name': st.session_state.current_business_name,
                'transactions': transactions,
                'inventory': inventory,
                'exported_at': datetime.now().isoformat()
            }
            
            st.download_button(
                label="📥 Download JSON Data",
                data=json.dumps(data, indent=2),
                file_name=f"{st.session_state.current_business_name}_data_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    """Main application entry point"""
    
    # Check authentication
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        main_app()

# ============================================================
# RUN APPLICATION
# ============================================================
if __name__ == "__main__":
    main()
