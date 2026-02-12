"""
REAL ESTATE ERP - COMPLETED SYSTEM
Targeted Upgrade Only - No Redesign
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
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
    .monitor-table {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION - ADDED ACTIVITY LOG
# ============================================
def init_session_state():
    """Initialize session state with activity tracking"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = None
    if 'sheets_urls' not in st.session_state:
        st.session_state.sheets_urls = {
            "users": st.secrets["google_sheets"]["users_sheet_url"],
            "properties": st.secrets["google_sheets"]["properties_sheet_url"],
            "mother_clients": st.secrets["google_sheets"]["mother_clients_sheet_url"],
            "login": st.secrets["google_sheets"]["login_sheet_url"],
            "transactions": st.secrets["google_sheets"]["transactions_sheet_url"]
        }
    if 'sheets_metadata' not in st.session_state:
        st.session_state.sheets_metadata = {}
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = []
    if 'users_sheet_configured' not in st.session_state:
        st.session_state.users_sheet_configured = True

init_session_state()

# ============================================
# ACTIVITY TRACKING - IN MEMORY ONLY
# ============================================
def track_activity(action: str, details: dict = None):
    """Track user activity in session state only"""
    if st.session_state.user:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "username": st.session_state.user['username'],
            "role": st.session_state.user['role'],
            "action": action,
            "details": details or {}
        }
        st.session_state.activity_log.append(log_entry)
        # Keep last 1000 entries
        if len(st.session_state.activity_log) > 1000:
            st.session_state.activity_log = st.session_state.activity_log[-1000:]

def get_today_activity():
    """Get today's activity from session log"""
    today = datetime.now().date().isoformat()
    return [log for log in st.session_state.activity_log 
            if log['timestamp'].startswith(today)]

# ============================================
# DYNAMIC GOOGLE SHEETS LOADER - LAZY LOADING
# ============================================
def load_google_sheet(url: str, sheet_type: str = None, trigger_tracking: bool = True):
    """Load Google Sheet data - LAZY LOADING, ALWAYS FRESH"""
    if not url:
        return pd.DataFrame()
    
    try:
        # Extract sheet ID
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
        
        # Track sheet access
        if trigger_tracking and st.session_state.user:
            track_activity("sheet_load", {
                "sheet_type": sheet_type,
                "sheet_id": sheet_id[:8] + "...",
                "url_masked": url[:50] + "..."
            })
        
        # Public export URL
        export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
        
        # Read with error handling
        df = pd.read_excel(export_url)
        df.columns = df.columns.str.strip()
        
        return df
        
    except Exception as e:
        return pd.DataFrame()

# ============================================
# USERS SHEET - OWNER ONLY CONFIGURATION
# ============================================
def configure_users_sheet():
    """Users Sheet configuration - OWNER ONLY, SINGLE SETUP"""
    if not st.session_state.users_sheet_configured:
        st.markdown("### 👤 Configure Users Sheet")
        st.info("Users Sheet must be configured before anyone can login")
        
        users_url = st.text_input(
            "Users Registry URL",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            key="users_sheet_setup"
        )
        
        if st.button("✅ Set Users Sheet", use_container_width=True):
            if users_url:
                # Test the sheet
                test_df = load_google_sheet(users_url, "users_test", False)
                if not test_df.empty:
                    st.session_state.sheets_urls['users'] = users_url
                    st.session_state.users_sheet_configured = True
                    track_activity("users_sheet_configured", {"url": users_url[:50] + "..."})
                    st.success("✅ Users Sheet configured successfully!")
                    st.rerun()
                else:
                    st.error("❌ Could not load Users Sheet. Check URL and sharing settings.")
    else:
        st.success("✅ Users Sheet is configured")

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user against Google Sheets users database"""
    if not st.session_state.users_sheet_configured:
        return None
    
    users_df = load_google_sheet(st.session_state.sheets_urls.get('users', ''), "users", False)
    
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
        
        df = load_google_sheet(
            st.session_state.sheets_urls.get('properties', ''), 
            "properties"
        )
        
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
                track_activity("link_finder_search", {"term": search_term, "results": len(results)})
                
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
# OWNER DASHBOARD - مع نشاط اليوم + العقارات + العملاء + الموظفين
# ============================================
def render_owner_dashboard():
    """Owner Dashboard - Complete Monitoring System with Today's Activity"""
    user = st.session_state.user
    st.markdown(f"<div class='main-header'>Executive Monitoring Dashboard</div>", unsafe_allow_html=True)
    st.markdown(f"**Welcome, {user['full_name']}** | *Owner Access*")
    
    # ============ SESSION SHEETS LOADER (مخفي بشكل افتراضي) ============
    with st.expander("📋 Session Sheets Loader", expanded=False):
        st.markdown("### Load Sheets for This Session")
        st.markdown("*All sheets are session-only and cleared on logout*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            properties_url = st.text_input(
                "🏢 Properties Sheet URL",
                value=st.session_state.sheets_urls.get('properties', ''),
                key="owner_properties",
                placeholder="https://docs.google.com/spreadsheets/d/..."
            )
            
            mother_clients_url = st.text_input(
                "👥 Mother Clients Sheet URL",
                value=st.session_state.sheets_urls.get('mother_clients', ''),
                key="owner_clients",
                placeholder="https://docs.google.com/spreadsheets/d/..."
            )
            
        with col2:
            transactions_url = st.text_input(
                "💰 Transactions Sheet URL",
                value=st.session_state.sheets_urls.get('transactions', ''),
                key="owner_transactions",
                placeholder="https://docs.google.com/spreadsheets/d/..."
            )
            
            sales_sheets = st.text_area(
                "👤 Sales Agent Sheets URLs (one per line)",
                value="\n".join(st.session_state.sheets_urls.get('sales_sheets', [])),
                key="owner_sales",
                placeholder="https://docs.google.com/spreadsheets/d/...\nhttps://docs.google.com/spreadsheets/d/..."
            )
        
        if st.button("💾 Load All Sheets", use_container_width=True):
            st.session_state.sheets_urls['properties'] = properties_url
            st.session_state.sheets_urls['mother_clients'] = mother_clients_url
            st.session_state.sheets_urls['transactions'] = transactions_url
            
            if sales_sheets:
                st.session_state.sheets_urls['sales_sheets'] = [
                    url.strip() for url in sales_sheets.split('\n') if url.strip()
                ]
            
            track_activity("sheets_loaded", {
                "properties": bool(properties_url),
                "clients": bool(mother_clients_url),
                "transactions": bool(transactions_url)
            })
            
            st.success("✅ Sheets loaded successfully!")
            st.rerun()
    
    # ============ تبويبات المالك ============
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 نشاط اليوم", 
        "🏢 العقارات", 
        "👥 كل العملاء", 
        "👤 الموظفين",
        "📁 Session Monitor", 
        "💰 Transactions"
    ])
    
    with tab1:
        st.markdown("### 👤 نشاط المستخدمين اليوم")
        st.markdown("*آخر تحديث: يعتمد على نشاط الجلسة الحالية*")
        
        today_activity = get_today_activity()
        
        if today_activity:
            df_today = pd.DataFrame(today_activity)
            
            # فلترة حسب النشاط
            col1, col2 = st.columns(2)
            with col1:
                show_logins = st.checkbox("عرض تسجيلات الدخول", value=True, key="owner_show_logins")
            with col2:
                show_sheets = st.checkbox("عرض تحميل الشيتات", value=True, key="owner_show_sheets")
            
            filtered_df = df_today.copy()
            if not show_logins:
                filtered_df = filtered_df[~filtered_df['action'].isin(['login', 'logout'])]
            if not show_sheets:
                filtered_df = filtered_df[filtered_df['action'] != 'sheet_load']
            
            # عرض الميتريكس
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric("إجمالي المستخدمين النشطين اليوم", len(set([log['username'] for log in today_activity])))
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                logins_count = len([log for log in today_activity if log['action'] == 'login'])
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric("تسجيلات الدخول", logins_count)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col3:
                actions_count = len(today_activity)
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric("إجمالي النشاطات", actions_count)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # عرض الجدول
            st.markdown("#### 📋 سجل النشاطات اليوم")
            st.dataframe(
                filtered_df[['timestamp', 'username', 'role', 'action', 'details']].sort_values('timestamp', ascending=False),
                use_container_width=True,
                height=500
            )
            
            # تصدير
            buffer = BytesIO()
            filtered_df.to_excel(buffer, index=False, engine='openpyxl')
            st.download_button(
                label="📥 تصدير نشاط اليوم (Excel)",
                data=buffer.getvalue(),
                file_name=f"today_activity_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.info("لا يوجد أي نشاط اليوم حتى الآن")
    
    with tab2:
        st.markdown("### 🏢 Property Inventory")
        if st.button("📥 Load Properties", key="owner_load_props"):
            properties_df = load_google_sheet(
                st.session_state.sheets_urls.get('properties', ''), 
                "properties"
            )
            if not properties_df.empty:
                st.session_state.owner_properties_data = properties_df
                st.success(f"Loaded {len(properties_df)} properties")
                track_activity("owner_view_properties")
            else:
                st.info("No property data available")
        
        if 'owner_properties_data' in st.session_state:
            st.dataframe(
                st.session_state.owner_properties_data, 
                use_container_width=True, 
                height=500
            )
            
            # تصدير Excel
            buffer = BytesIO()
            st.session_state.owner_properties_data.to_excel(buffer, index=False, engine='openpyxl')
            st.download_button(
                label="📥 تحميل العقارات (Excel)",
                data=buffer.getvalue(),
                file_name=f"properties_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    with tab3:
        st.markdown("### 👥 All Clients")
        if st.button("📥 Load All Clients", key="owner_load_clients"):
            clients_df = load_google_sheet(
                st.session_state.sheets_urls.get('mother_clients', ''), 
                "mother_clients"
            )
            if not clients_df.empty:
                st.session_state.owner_clients_data = clients_df
                st.success(f"Loaded {len(clients_df)} clients")
                track_activity("owner_view_clients")
            else:
                st.info("No client data available")
        
        if 'owner_clients_data' in st.session_state:
            st.dataframe(
                st.session_state.owner_clients_data, 
                use_container_width=True, 
                height=500
            )
            
            # تصدير Excel
            buffer = BytesIO()
            st.session_state.owner_clients_data.to_excel(buffer, index=False, engine='openpyxl')
            st.download_button(
                label="📥 تحميل العملاء (Excel)",
                data=buffer.getvalue(),
                file_name=f"clients_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    with tab4:
        st.markdown("### 👤 Employees (Users Sheet)")
        if st.button("📥 Load Employees", key="owner_load_users"):
            users_df = load_google_sheet(
                st.session_state.sheets_urls.get('users', ''), 
                "users"
            )
            if not users_df.empty:
                st.session_state.owner_users_data = users_df
                st.success(f"Loaded {len(users_df)} employees")
                track_activity("owner_view_employees")
            else:
                st.info("No employees data available")
        
        if 'owner_users_data' in st.session_state:
            # إخفاء كلمة السر من العرض
            df_display = st.session_state.owner_users_data.copy()
            password_cols = [col for col in df_display.columns if 'pass' in col.lower()]
            for col in password_cols:
                df_display[col] = "••••••••"
            
            st.dataframe(
                df_display, 
                use_container_width=True, 
                height=500
            )
            
            # تصدير Excel (بدون إخفاء كلمة السر)
            buffer = BytesIO()
            st.session_state.owner_users_data.to_excel(buffer, index=False, engine='openpyxl')
            st.download_button(
                label="📥 تحميل الموظفين (Excel)",
                data=buffer.getvalue(),
                file_name=f"employees_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    with tab5:
        st.markdown("### 📊 Session Sheets Monitor")
        
        monitor_data = []
        for sheet_type, url in st.session_state.sheets_urls.items():
            if url and sheet_type != 'users':
                masked_url = url[:30] + "..." if len(url) > 30 else url
                metadata = st.session_state.sheets_metadata.get(sheet_type, {})
                
                monitor_data.append({
                    "Sheet Name": sheet_type.replace('_', ' ').title(),
                    "Type": sheet_type,
                    "Loaded By": metadata.get('loaded_by', 'Owner'),
                    "Load Time": metadata.get('load_time', 'N/A'),
                    "URL": masked_url
                })
        
        if monitor_data:
            st.dataframe(pd.DataFrame(monitor_data), use_container_width=True)
        else:
            st.info("No sheets loaded yet")
        
        st.markdown("### 📁 Sheet Access Monitor")
        sheet_access = [log for log in get_today_activity() if log['action'] == 'sheet_load']
        
        if sheet_access:
            df_access = pd.DataFrame(sheet_access)
            st.dataframe(df_access[['timestamp', 'username', 'details']], use_container_width=True)
        else:
            st.info("No sheet access today")
    
    with tab6:
        st.markdown("### 💰 Transactions Sheet Viewer")
        
        if st.session_state.sheets_urls.get('transactions'):
            if st.button("📥 Load Transactions Data", key="owner_load_transactions"):
                transactions_df = load_google_sheet(
                    st.session_state.sheets_urls['transactions'], 
                    "transactions"
                )
                
                if not transactions_df.empty:
                    st.success(f"Loaded {len(transactions_df)} transactions")
                    st.dataframe(transactions_df, use_container_width=True, height=400)
                    
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
                    
                    track_activity("owner_view_transactions", {"count": len(transactions_df)})
                else:
                    st.warning("Could not load transactions data")
        else:
            st.info("No Transactions Sheet loaded")
# ============================================
# MANAGER DASHBOARD - مع نشاط اليوم
# ============================================
def render_manager_dashboard():
    """Manager Dashboard - View Only + Today's Activity"""
    user = st.session_state.user
    st.markdown("<div class='main-header'>Management Dashboard</div>", unsafe_allow_html=True)
    st.markdown(f"**Welcome, {user['full_name']}** | *Manager Access*")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Properties", "All Clients", "Transactions", "📊 نشاط اليوم"])
    
    with tab1:
        st.markdown("#### Property Inventory")
        if st.button("📥 Load Properties", key="mgr_load_props"):
            properties_df = load_google_sheet(
                st.session_state.sheets_urls.get('properties', ''), 
                "properties"
            )
            if not properties_df.empty:
                st.success(f"Loaded {len(properties_df)} properties")
                st.dataframe(properties_df, use_container_width=True, height=500)
                track_activity("manager_view_properties")
            else:
                st.info("No property data available")
    
    with tab2:
        st.markdown("#### All Clients")
        if st.button("📥 Load All Clients", key="mgr_load_clients"):
            clients_df = load_google_sheet(
                st.session_state.sheets_urls.get('mother_clients', ''), 
                "mother_clients"
            )
            if not clients_df.empty:
                st.success(f"Loaded {len(clients_df)} clients")
                st.dataframe(clients_df, use_container_width=True, height=500)
                track_activity("manager_view_clients")
            else:
                st.info("No client data available")
    
    with tab3:
        st.markdown("#### Transactions")
        if st.button("📥 Load Transactions", key="mgr_load_transactions"):
            transactions_df = load_google_sheet(
                st.session_state.sheets_urls.get('transactions', ''), 
                "transactions"
            )
            if not transactions_df.empty:
                st.success(f"Loaded {len(transactions_df)} transactions")
                st.dataframe(transactions_df, use_container_width=True, height=500)
                track_activity("manager_view_transactions")
            else:
                st.info("No transactions available")
    
    with tab4:
        st.markdown("### 👤 نشاط المستخدمين اليوم")
        st.markdown("*آخر تحديث: يعتمد على نشاط الجلسة الحالية*")
        
        today_activity = get_today_activity()
        
        if today_activity:
            df_today = pd.DataFrame(today_activity)
            
            # فلترة حسب النشاط
            col1, col2 = st.columns(2)
            with col1:
                show_logins = st.checkbox("عرض تسجيلات الدخول", value=True, key="mgr_show_logins")
            with col2:
                show_sheets = st.checkbox("عرض تحميل الشيتات", value=True, key="mgr_show_sheets")
            
            filtered_df = df_today.copy()
            if not show_logins:
                filtered_df = filtered_df[~filtered_df['action'].isin(['login', 'logout'])]
            if not show_sheets:
                filtered_df = filtered_df[filtered_df['action'] != 'sheet_load']
            
            # عرض الميتريكس
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric("إجمالي المستخدمين النشطين اليوم", len(set([log['username'] for log in today_activity])))
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                logins_count = len([log for log in today_activity if log['action'] == 'login'])
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric("تسجيلات الدخول", logins_count)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col3:
                actions_count = len(today_activity)
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.metric("إجمالي النشاطات", actions_count)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # عرض الجدول
            st.markdown("#### 📋 سجل النشاطات اليوم")
            st.dataframe(
                filtered_df[['timestamp', 'username', 'role', 'action', 'details']].sort_values('timestamp', ascending=False),
                use_container_width=True,
                height=500
            )
            
            # تصدير
            buffer = BytesIO()
            filtered_df.to_excel(buffer, index=False, engine='openpyxl')
            st.download_button(
                label="📥 تصدير نشاط اليوم (Excel)",
                data=buffer.getvalue(),
                file_name=f"today_activity_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.info("لا يوجد أي نشاط اليوم حتى الآن")

# ============================================
# SALES DASHBOARD - ORIGINAL FILTERS + LINK FINDER
# ============================================
def render_sales_dashboard():
    """Sales Dashboard - Original Filters + Property Link Finder"""
    user = st.session_state.user
    st.markdown(f"<div class='main-header'>Sales Dashboard</div>", unsafe_allow_html=True)
    st.markdown(f"**Welcome, {user['full_name']}** | *Sales Professional*")
    
    tab1, tab2, tab3 = st.tabs(["Property Search", "My Clients", "Property Link Finder"])
    
    with tab1:
        st.markdown("<div class='main-header'>Property Inventory Search</div>", unsafe_allow_html=True)
        
        # LAZY LOADING - Only load when requested
        if st.button("🔍 Load Property Data", key="sales_load_props", use_container_width=True):
            df = load_google_sheet(
                st.session_state.sheets_urls.get('properties', ''), 
                "properties"
            )
            
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
                track_activity("keyword_search", {"query": search_query})
            
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
        st.markdown("### My Clients")
        
        if st.button("📥 Load My Clients", key="sales_load_clients", use_container_width=True):
            # Try to find sales-specific sheet first
            sales_sheets = st.session_state.sheets_urls.get('sales_sheets', [])
            my_sheet = None
            
            # Simple matching - assume sheet title contains username
            for url in sales_sheets:
                if user['username'].lower() in url.lower():
                    my_sheet = url
                    break
            
            if my_sheet:
                clients_df = load_google_sheet(my_sheet, f"sales_{user['username']}")
            else:
                # Fall back to filtered mother sheet
                mother_df = load_google_sheet(
                    st.session_state.sheets_urls.get('mother_clients', ''), 
                    "mother_clients"
                )
                
                if not mother_df.empty:
                    assigned_col = None
                    for col in mother_df.columns:
                        if 'assigned_to' in col.lower() or 'agent' in col.lower():
                            assigned_col = col
                            break
                    
                    if assigned_col:
                        clients_df = mother_df[mother_df[assigned_col].astype(str).str.contains(
                            user['username'], case=False, na=False
                        )]
            
            if 'clients_df' in locals() and not clients_df.empty:
                st.session_state.sales_clients_data = clients_df
                track_activity("sales_load_clients", {"count": len(clients_df)})
                st.success(f"Loaded {len(clients_df)} clients")
            else:
                st.warning("No clients found for this agent")
        
        if 'sales_clients_data' in st.session_state:
            st.dataframe(st.session_state.sales_clients_data, use_container_width=True, height=400)
    
    with tab3:
        link_finder = PropertyLinkFinder()
        link_finder.render_interface()

# ============================================
# LOGIN PAGE - SIMPLIFIED, NO DEMO
# ============================================
def render_login_page():
    """Professional login page"""
    st.markdown("<div class='main-header'>Real Estate ERP System</div>", unsafe_allow_html=True)
    
    # Users Sheet Configuration - Only visible if not configured
    if not st.session_state.users_sheet_configured:
        configure_users_sheet()
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
                    track_activity("login", {"username": username})
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            else:
                st.error("Username and password are required")

# ============================================
# NAVIGATION - MANAGER/SALES HAVE NO CONFIG
# ============================================
def render_navigation():
    """Navigation sidebar - NO CONFIG for Manager/Sales"""
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
            track_activity("logout", {"username": user['username']})
            # Clear session state
            for key in list(st.session_state.keys()):
                if key not in ['users_sheet_configured', 'activity_log']:
                    del st.session_state[key]
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
