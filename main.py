"""
REAL ESTATE ERP - ADVANCED SECURE SYSTEM
Streamlit Secrets Integration - Zero User Input - Original Filters Preserved
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
import json
from datetime import datetime
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any

# ============================================
# SYSTEM CONFIGURATION - EXACTLY AS ORIGINAL
# ============================================
st.set_page_config(
    page_title="Real Estate ERP Pro",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS - EXACTLY AS ORIGINAL
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
        margin-bottom: 10px;
    }
    .data-table {
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .filter-card {
        background: #f8fafc;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #4F46E5;
        margin-bottom: 10px;
    }
    .success-box {
        background: #D1FAE5;
        color: #065F46;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #10B981;
        margin: 8px 0;
    }
    .warning-box {
        background: #FEF3C7;
        color: #92400E;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #F59E0B;
        margin: 8px 0;
    }
    .info-box {
        background: #DBEAFE;
        color: #1E40AF;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
        margin: 8px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# STREAMLIT SECRETS LOADER - DEEP SEEK
# ============================================
@st.cache_resource
def load_sheets_from_secrets():
    """Load all Google Sheets URLs from Streamlit Secrets - DEEP SEEK"""
    sheets_config = {}
    
    try:
        # Users Sheet
        if 'sheets.users' in st.secrets:
            users_data = json.loads(st.secrets['sheets.users'])
            sheets_config['users'] = users_data.get('sheet_url', '')
        
        # Properties Sheet
        if 'sheets.properties' in st.secrets:
            props_data = json.loads(st.secrets['sheets.properties'])
            sheets_config['properties'] = props_data.get('sheet_url', '')
        
        # Mother Clients Sheet
        if 'sheets.clients_mother' in st.secrets:
            clients_data = json.loads(st.secrets['sheets.clients_mother'])
            sheets_config['mother_clients'] = clients_data.get('sheet_url', '')
        
        # Transactions Sheet
        if 'sheets.transactions' in st.secrets:
            trans_data = json.loads(st.secrets['sheets.transactions'])
            sheets_config['transactions'] = trans_data.get('sheet_url', '')
        
        # Login Sheet (if separate)
        if 'sheets.login' in st.secrets:
            login_data = json.loads(st.secrets['sheets.login'])
            sheets_config['login'] = login_data.get('sheet_url', '')
        
    except Exception as e:
        # Silent fail - never expose secrets error
        pass
    
    return sheets_config

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
def init_session_state():
    """Initialize session state with activity tracking"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = None
    if 'sheets_urls' not in st.session_state:
        # AUTO-LOAD from secrets on startup
        st.session_state.sheets_urls = load_sheets_from_secrets()
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = []
    if 'sales_uploaded_sheet' not in st.session_state:
        st.session_state.sales_uploaded_sheet = None

init_session_state()

# ============================================
# SECURE SHEET LOADER - NEVER EXPOSE URLS
# ============================================
def load_google_sheet(sheet_type: str, trigger_tracking: bool = True):
    """Load Google Sheet data from pre-configured secrets - NEVER expose URLs"""
    
    url = st.session_state.sheets_urls.get(sheet_type, '')
    
    if not url:
        return pd.DataFrame()
    
    try:
        # Extract sheet ID without logging
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
            r'spreadsheets/d/([a-zA-Z0-9-_]+)/edit'
        ]
        
        sheet_id = None
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                sheet_id = match.group(1)
                break
        
        if not sheet_id:
            return pd.DataFrame()
        
        # Track access (NO URL logging)
        if trigger_tracking and st.session_state.user:
            track_activity("sheet_load", {
                "sheet_type": sheet_type,
                # NO URL, NO ID - just type
            })
        
        # Public export URL
        export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
        
        # Read with error handling
        df = pd.read_excel(export_url)
        df.columns = df.columns.str.strip()
        
        return df
        
    except Exception as e:
        # Silent fail - never expose errors to UI
        return pd.DataFrame()

# ============================================
# ACTIVITY TRACKING - NO SENSITIVE DATA
# ============================================
def track_activity(action: str, details: dict = None):
    """Track user activity - NO sensitive data"""
    if st.session_state.user:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "username": st.session_state.user['username'],
            "role": st.session_state.user['role'],
            "action": action,
            "details": details or {}
        }
        st.session_state.activity_log.append(log_entry)
        if len(st.session_state.activity_log) > 1000:
            st.session_state.activity_log = st.session_state.activity_log[-1000:]

def get_today_activity():
    """Get today's activity from session log"""
    today = datetime.now().date().isoformat()
    return [log for log in st.session_state.activity_log 
            if log['timestamp'].startswith(today)]

# ============================================
# SECURE AUTHENTICATION - FROM SECRETS SHEETS
# ============================================
def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user - ALWAYS from Secrets sheets"""
    
    # Try login sheet first, then users sheet
    users_df = load_google_sheet('login', False)
    if users_df.empty:
        users_df = load_google_sheet('users', False)
    
    if users_df.empty:
        return None
    
    # Dynamic column detection
    username_col = None
    password_col = None
    role_col = None
    name_col = None
    
    for col in users_df.columns:
        col_lower = col.lower()
        if 'username' in col_lower or 'user' in col_lower:
            username_col = col
        if 'password' in col_lower or 'pass' in col_lower:
            password_col = col
        if 'role' in col_lower:
            role_col = col
        if 'full_name' in col_lower or 'name' in col_lower:
            name_col = col
    
    if not username_col or not password_col:
        return None
    
    # Find user
    user_row = users_df[users_df[username_col].astype(str).str.lower() == username.lower()]
    
    if user_row.empty:
        return None
    
    stored_password = str(user_row.iloc[0][password_col]).strip()
    
    if password == stored_password:
        return {
            "username": username,
            "role": user_row.iloc[0][role_col].lower() if role_col else 'sales',
            "full_name": user_row.iloc[0][name_col] if name_col else username,
        }
    
    return None

# ============================================
# ORIGINAL FILTER ENGINE - EXACT COPY, NO CHANGES
# ============================================
def render_original_filters(df):
    """ORIGINAL FILTER ENGINE - DO NOT MODIFY"""
    filtered_df = df.copy()
    
    # --- 1. فلاتر الأرقام (Manual Input بدلاً من Slider) ---
    st.sidebar.subheader("💰 الميزانية والمساحة")
    
    # فلتر السعر
    if "price_total" in df.columns:
        min_p = float(df["price_total"].min())
        max_p = float(df["price_total"].max())
        st.sidebar.write("**السعر الإجمالي**")
        col_p1, col_p2 = st.sidebar.columns(2)
        p_from = col_p1.number_input("من", value=min_p, step=50000.0, key="p_from")
        p_to = col_p2.number_input("إلى", value=max_p, step=50000.0, key="p_to")
        filtered_df = filtered_df[(filtered_df["price_total"] >= p_from) & (filtered_df["price_total"] <= p_to)]
    
    # فلتر المساحة
    if "area_sqm" in df.columns:
        min_a = float(df["area_sqm"].min())
        max_a = float(df["area_sqm"].max())
        st.sidebar.write("**المساحة (م²)**")
        col_a1, col_a2 = st.sidebar.columns(2)
        a_from = col_a1.number_input("من", value=min_a, step=5.0, key="a_from")
        a_to = col_a2.number_input("إلى", value=max_a, step=5.0, key="a_to")
        filtered_df = filtered_df[(filtered_df["area_sqm"] >= a_from) & (filtered_df["area_sqm"] <= a_to)]
    
    # فلتر الأدوار
    if "floor_number" in df.columns:
        st.sidebar.write("**رقم الدور**")
        col_f1, col_f2 = st.sidebar.columns(2)
        f_from = col_f1.number_input("من دور", value=int(df["floor_number"].min()), step=1, key="f_from")
        f_to = col_f2.number_input("إلى دور", value=int(df["floor_number"].max()), step=1, key="f_to")
        filtered_df = filtered_df[(filtered_df["floor_number"] >= f_from) & (filtered_df["floor_number"] <= f_to)]
    
    st.sidebar.divider()
    
    # --- 2. فلاتر الاختيار المتعدد (مع Select All) ---
    def sales_multiselect(column, label):
        nonlocal filtered_df
        if column in df.columns:
            options = sorted([str(x) for x in df[column].dropna().unique().tolist()])
            if options:
                st.sidebar.write(f"**{label}**")
                select_all = st.sidebar.checkbox(f"الكل ({label})", value=True, key=f"all_{column}")
                default_vals = options if select_all else []
                selected = st.sidebar.multiselect(label, options, default=default_vals, key=f"ms_{column}", label_visibility="collapsed")
                filtered_df = filtered_df[filtered_df[column].astype(str).isin(selected)]
    
    sales_multiselect("area", "المنطقة")
    sales_multiselect("unit_type", "نوع الوحدة")
    sales_multiselect("listing_type", "نوع العرض")
    sales_multiselect("rooms", "الغرف")
    sales_multiselect("bathrooms", "الحمامات")
    sales_multiselect("unit_status", "الحالة")
    
    # 3. المرافق
    with st.sidebar.expander("➕ مرافق إضافية"):
        for util in ["electricity", "water", "gas", "elevator", "garage"]:
            sales_multiselect(util, util.capitalize())
    
    return filtered_df

# ============================================
# PROPERTY LINK FINDER - ORIGINAL, NO CHANGES
# ============================================
class PropertyLinkFinder:
    """Property Link Finder - EXACT SAME UI"""
    
    def render_interface(self):
        st.markdown("### Property Link Finder")
        
        df = load_google_sheet('properties')
        
        if df.empty:
            st.warning("No property data available")
            return
        
        link_col = None
        id_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'link' in col_lower or 'url' in col_lower:
                link_col = col
            if 'unit_id' in col_lower or 'id' in col_lower:
                id_col = col
        
        if not id_col:
            st.warning("No ID column found")
            return
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_term = st.text_input(
                "Search by Unit ID",
                placeholder="Enter partial or full Unit ID...",
                key="link_search"
            )
        
        with col2:
            st.write("")
            st.write("")
            search_clicked = st.button("🔍 Search", use_container_width=True)
        
        if search_term or search_clicked:
            mask = df[id_col].astype(str).str.contains(search_term, case=False, na=False)
            results = df[mask]
            
            if not results.empty:
                st.success(f"Found {len(results)} matching properties")
                track_activity("link_finder_search", {"results": len(results)})
                
                for idx, row in results.iterrows():
                    unit_id = row[id_col]
                    link = row[link_col] if link_col else ""
                    
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.write(f"**{unit_id}**")
                    
                    with col2:
                        if link and pd.notna(link) and str(link).strip():
                            st.write(f"🔗 [Open Link]({link})")
                    
                    with col3:
                        if link and pd.notna(link) and str(link).strip():
                            st.code(link, language="text")
                
                buffer = BytesIO()
                results.to_excel(buffer, index=False, engine='openpyxl')
                
                st.download_button(
                    label="📥 Export Search Results (Excel)",
                    data=buffer.getvalue(),
                    file_name=f"property_links_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                st.warning("No matching properties found")

# ============================================
# OWNER DASHBOARD - COMPLETE MONITORING, NO CONFIG
# ============================================
def render_owner_dashboard():
    """Owner Dashboard - Complete Monitoring, NO sheet configuration UI"""
    user = st.session_state.user
    st.markdown(f"<div class='main-header'>Executive Monitoring Dashboard</div>", unsafe_allow_html=True)
    st.markdown(f"**Welcome, {user['full_name']}** | *Owner Access*")
    
    # ============ SESSION SHEETS MONITOR ============
    st.markdown("### 📊 Session Sheets Monitor")
    
    monitor_data = []
    for sheet_type, url in st.session_state.sheets_urls.items():
        if url and sheet_type not in ['users', 'login']:
            # NEVER show full URL - mask completely
            masked_url = "🔒 [Configured in Secrets]" if url else "Not configured"
            
            monitor_data.append({
                "Sheet Name": sheet_type.replace('_', ' ').title(),
                "Type": sheet_type,
                "Status": "✅ Loaded" if url else "❌ Missing",
                "Source": "Streamlit Secrets"
            })
    
    if monitor_data:
        st.dataframe(pd.DataFrame(monitor_data), use_container_width=True)
    else:
        st.warning("No sheets configured in Streamlit Secrets")
    
    # ============ LOGIN ACTIVITY MONITOR ============
    st.markdown("---")
    st.markdown("### 👤 Login Activity Monitor")
    
    today_activity = get_today_activity()
    login_events = [log for log in today_activity if log['action'] in ['login', 'logout']]
    
    if login_events:
        df_logins = pd.DataFrame(login_events)
        display_cols = [c for c in ['timestamp', 'username', 'role', 'action'] if c in df_logins.columns]
        st.dataframe(df_logins[display_cols], use_container_width=True)
    else:
        st.info("No login activity today")
    
    # ============ SHEET ACCESS MONITOR ============
    st.markdown("### 📁 Sheet Access Monitor")
    
    sheet_access = [log for log in today_activity if log['action'] == 'sheet_load']
    
    if sheet_access:
        df_access = pd.DataFrame(sheet_access)
        # Extract sheet_type from details safely
        access_data = []
        for log in sheet_access:
            access_data.append({
                "timestamp": log['timestamp'],
                "username": log['username'],
                "sheet": log.get('details', {}).get('sheet_type', 'unknown')
            })
        st.dataframe(pd.DataFrame(access_data), use_container_width=True)
    else:
        st.info("No sheet access today")
    
    # ============ AUTOMATIC REPORTS ============
    st.markdown("---")
    st.markdown("### 📈 Automatic Reports")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_users = len(set([log['username'] for log in today_activity]))
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Active Users Today", active_users)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        sheets_loaded = len([log for log in today_activity if log['action'] == 'sheet_load'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Sheets Loaded Today", sheets_loaded)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        searches = len([log for log in today_activity if 'search' in log['action'].lower()])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Total Searches", searches)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        exports = len([log for log in today_activity if log['action'] == 'export'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Total Exports", exports)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Most Accessed Sheets
    st.markdown("### 📊 Most Accessed Sheets Today")
    
    sheet_counts = {}
    for log in [l for l in today_activity if l['action'] == 'sheet_load']:
        sheet_type = log.get('details', {}).get('sheet_type', 'unknown')
        sheet_counts[sheet_type] = sheet_counts.get(sheet_type, 0) + 1
    
    if sheet_counts:
        df_counts = pd.DataFrame([
            {"Sheet": k, "Accesses": v} 
            for k, v in sorted(sheet_counts.items(), key=lambda x: x[1], reverse=True)
        ])
        st.dataframe(df_counts, use_container_width=True)
    
    # ============ TRANSACTIONS VIEWER ============
    st.markdown("---")
    st.markdown("### 💰 Transactions Viewer")
    
    if st.button("📥 Load Transactions Data", key="owner_load_trans", use_container_width=True):
        transactions_df = load_google_sheet('transactions')
        
        if not transactions_df.empty:
            st.success(f"Loaded {len(transactions_df)} transactions")
            st.dataframe(transactions_df, use_container_width=True, height=400)
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Transactions", len(transactions_df))
            
            amount_col = None
            for col in transactions_df.columns:
                if 'amount' in col.lower() or 'price' in col.lower():
                    amount_col = col
                    break
            
            if amount_col:
                with col2:
                    total_amount = transactions_df[amount_col].sum()
                    st.metric("Total Amount", f"${total_amount:,.0f}")
                
                with col3:
                    avg_amount = transactions_df[amount_col].mean()
                    st.metric("Average Amount", f"${avg_amount:,.0f}")
            
            track_activity("view_transactions")
        else:
            st.warning("No transactions data available")

# ============================================
# MANAGER DASHBOARD - MOTHER SHEETS ONLY
# ============================================
def render_manager_dashboard():
    """Manager Dashboard - Mother Sheets Only, No Uploads"""
    user = st.session_state.user
    st.markdown("<div class='main-header'>Management Dashboard</div>", unsafe_allow_html=True)
    st.markdown(f"**Welcome, {user['full_name']}** | *Manager Access*")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Properties", "All Clients", "Activity Logs", "Transactions"])
    
    with tab1:
        st.markdown("#### Property Inventory")
        if st.button("📥 Load Properties", key="mgr_load_props"):
            properties_df = load_google_sheet('properties')
            if not properties_df.empty:
                st.success(f"Loaded {len(properties_df)} properties")
                st.dataframe(properties_df, use_container_width=True, height=500)
                track_activity("manager_view_properties")
            else:
                st.info("No property data available")
    
    with tab2:
        st.markdown("#### All Clients")
        if st.button("📥 Load All Clients", key="mgr_load_clients"):
            clients_df = load_google_sheet('mother_clients')
            if not clients_df.empty:
                st.success(f"Loaded {len(clients_df)} clients")
                st.dataframe(clients_df, use_container_width=True, height=500)
                track_activity("manager_view_clients")
            else:
                st.info("No client data available")
    
    with tab3:
        st.markdown("#### Activity Logs")
        if st.button("📥 Load Activity Logs", key="mgr_load_activity"):
            activity_df = load_google_sheet('activity')
            if not activity_df.empty:
                st.success(f"Loaded {len(activity_df)} activity records")
                st.dataframe(activity_df, use_container_width=True, height=500)
                track_activity("manager_view_activity")
            else:
                st.info("No activity logs available")
    
    with tab4:
        st.markdown("#### Transactions")
        if st.button("📥 Load Transactions", key="mgr_load_transactions"):
            transactions_df = load_google_sheet('transactions')
            if not transactions_df.empty:
                st.success(f"Loaded {len(transactions_df)} transactions")
                st.dataframe(transactions_df, use_container_width=True, height=500)
                track_activity("manager_view_transactions")
            else:
                st.info("No transactions available")

# ============================================
# SALES DASHBOARD - UPLOAD OWN CLIENTS SHEET ONLY
# ============================================
def render_sales_dashboard():
    """Sales Dashboard - Upload OWN Clients Sheet Only + Original Filters"""
    user = st.session_state.user
    st.markdown(f"<div class='main-header'>Sales Dashboard</div>", unsafe_allow_html=True)
    st.markdown(f"**Welcome, {user['full_name']}** | *Sales Professional*")
    
    tab1, tab2, tab3 = st.tabs(["Property Search", "My Clients (Upload)", "Property Link Finder"])
    
    with tab1:
        st.markdown("<div class='main-header'>Property Inventory Search</div>", unsafe_allow_html=True)
        
        # LAZY LOADING - Only from Secrets
        if st.button("🔍 Load Property Data", key="sales_load_props", use_container_width=True):
            df = load_google_sheet('properties')
            if not df.empty:
                st.session_state.sales_property_data = df
                track_activity("sales_load_properties")
                st.success(f"Loaded {len(df)} properties")
        
        if 'sales_property_data' in st.session_state:
            # APPLY ORIGINAL FILTERS - EXACT COPY, NO CHANGES
            filtered_df = render_original_filters(st.session_state.sales_property_data)
            
            # Keyword Search
            st.markdown("### 🔍 ابحث عن كلمات مميزة (مثل: بحري، مرخصة، قسط، ناصية)")
            search_query = st.text_input("ادخل الكلمات الدليلية هنا...", placeholder="مثلاً: جراج، عداد كهرباء، الترا سوبر لوكس")
            if search_query:
                mask = pd.Series(False, index=filtered_df.index)
                for col in ["notes", "address"]:
                    if col in filtered_df.columns:
                        mask |= filtered_df[col].astype(str).str.contains(search_query, case=False, na=False)
                filtered_df = filtered_df[mask]
                track_activity("keyword_search")
            
            # Display Results
            st.subheader(f"📈 وجدنا لك {len(filtered_df)} وحدة مطابقة لطلبك")
            st.dataframe(filtered_df, use_container_width=True)
            
            # Export
            if not filtered_df.empty:
                buffer = BytesIO()
                filtered_df.to_excel(buffer, index=False, engine='openpyxl')
                
                if st.download_button(
                    label="📥 تحميل الوحدات المختارة للعميل (Excel)",
                    data=buffer.getvalue(),
                    file_name=f"ابانوب_للعقارات_المفلترة_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                ):
                    track_activity("export", {"rows": len(filtered_df)})
    
    with tab2:
        st.markdown("### 📤 Upload Your Clients Sheet")
        st.markdown("*You can only upload your own assigned clients sheet*")
        
        uploaded_file = st.file_uploader(
            "Choose your clients Excel/CSV file",
            type=['xlsx', 'xls', 'csv'],
            key=f"sales_upload_{user['username']}"
        )
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    clients_df = pd.read_csv(uploaded_file)
                else:
                    clients_df = pd.read_excel(uploaded_file)
                
                clients_df.columns = clients_df.columns.str.strip()
                
                # Store in session state
                st.session_state.sales_uploaded_sheet = clients_df
                track_activity("sales_upload_clients", {"rows": len(clients_df)})
                
                st.success(f"✅ Successfully loaded {len(clients_df)} clients")
                
                # Display clients
                st.markdown("### Your Clients")
                st.dataframe(clients_df, use_container_width=True, height=400)
                
                # Export option
                buffer = BytesIO()
                clients_df.to_excel(buffer, index=False, engine='openpyxl')
                st.download_button(
                    label="📥 Download Your Clients List",
                    data=buffer.getvalue(),
                    file_name=f"my_clients_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
            except Exception as e:
                st.error("❌ Error loading file. Please check the format.")
        
        elif st.session_state.get('sales_uploaded_sheet') is not None:
            # Show previously uploaded data
            st.markdown("### Your Clients (Previously Uploaded)")
            st.dataframe(st.session_state.sales_uploaded_sheet, use_container_width=True, height=400)
    
    with tab3:
        link_finder = PropertyLinkFinder()
        link_finder.render_interface()

# ============================================
# LOGIN PAGE - CLEAN, FROM SECRETS
# ============================================
def render_login_page():
    """Professional login page - AUTO from Secrets"""
    st.markdown("<div class='main-header'>Real Estate ERP System</div>", unsafe_allow_html=True)
    
    # Check if sheets are configured in Secrets
    if not st.session_state.sheets_urls.get('users') and not st.session_state.sheets_urls.get('login'):
        st.error("⚠️ System configuration error. Please contact administrator.")
        st.stop()
    
    st.markdown("### Professional Access Portal")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            login_button = st.form_submit_button("Login", use_container_width=True)
        
        if login_button:
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    track_activity("login")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            else:
                st.error("Username and password are required")

# ============================================
# NAVIGATION - ROLE BASED
# ============================================
def render_navigation():
    """Navigation sidebar - Role based"""
    with st.sidebar:
        user = st.session_state.user
        
        st.markdown(f"### {user['full_name']}")
        st.markdown(f"*{user['role'].title()}*")
        
        st.markdown("---")
        st.markdown("### Navigation")
        
        if user['role'] == 'owner':
            if st.button("🏢 Executive Dashboard", use_container_width=True):
                st.session_state.current_page = "owner"
                st.rerun()
        
        elif user['role'] == 'manager':
            if st.button("👨‍💼 Management Dashboard", use_container_width=True):
                st.session_state.current_page = "manager"
                st.rerun()
        
        elif user['role'] == 'sales':
            if st.button("🔍 Sales Dashboard", use_container_width=True):
                st.session_state.current_page = "sales"
                st.rerun()
        
        st.markdown("---")
        
        if st.button("🚪 Logout", type="primary", use_container_width=True):
            track_activity("logout")
            # Clear session state but KEEP sheets_urls from Secrets
            sheets_backup = st.session_state.sheets_urls.copy()
            for key in list(st.session_state.keys()):
                if key not in ['sheets_urls']:
                    del st.session_state[key]
            st.session_state.sheets_urls = sheets_backup
            st.rerun()

# ============================================
# MAIN APPLICATION
# ============================================
def main():
    """Main application entry point"""
    
    init_session_state()
    
    if st.session_state.user is None:
        render_login_page()
    else:
        render_navigation()
        
        if st.session_state.current_page == "owner":
            render_owner_dashboard()
        elif st.session_state.current_page == "manager":
            render_manager_dashboard()
        elif st.session_state.current_page == "sales":
            render_sales_dashboard()
        else:
            # Default to role dashboard
            if st.session_state.user['role'] == 'owner':
                render_owner_dashboard()
            elif st.session_state.user['role'] == 'manager':
                render_manager_dashboard()
            elif st.session_state.user['role'] == 'sales':
                render_sales_dashboard()

# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    main()
