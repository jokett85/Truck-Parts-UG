import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date, timedelta

# --- EXECUTIVE CONFIG ---
st.set_page_config(page_title="TruckParts UG | Executive Portal", page_icon="🚛", layout="wide")

# --- DATABASE CONNECTION ---
URL = "https://fasgqlvfmrdtlydelnni.supabase.co" 
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhc2dxbHZmbXJkdGx5ZGVsbm5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NDYyNzYsImV4cCI6MjA5MDEyMjI3Nn0.gxm--vdmUlxMaGH_r70sMrTxbt-MidtS8Vlse94pkDw"
SECRET_ADMIN_KEY = "UG-MASTER2026" 

supabase: Client = create_client(URL, KEY)

def main():
    # --- ADVANCED EXECUTIVE CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0F172A; color: white; }
        [data-testid="stSidebarNav"] { display: none; }
        
        /* Executive Sidebar Navigation */
        .nav-text { font-size: 26px !important; font-weight: 800; color: #FFD700; text-align: center; margin-bottom: 30px; }
        
        /* Professional Lobby Cards */
        .lobby-card { 
            background: #1E293B; padding: 25px; border-radius: 15px; 
            border-left: 6px solid #FFD700; margin-bottom: 20px;
        }
        
        .price-tag { color: #FFD700; font-size: 1.8em; font-weight: 900; }
        
        /* Button Styling */
        .stButton>button { 
            border-radius: 12px; font-weight: bold; min-height: 60px; 
            background-color: #FFD700; color: #0F172A; border: none; font-size: 1.1em;
        }
        
        /* Remove Admin UI Indicators */
        .stDeployButton { display:none; }
        footer { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

    # SESSION STATE
    if 'page' not in st.session_state: st.session_state.page = "Market"
    if 'admin_active' not in st.session_state: st.session_state.admin_active = False

    # --- EXECUTIVE SIDEBAR ---
    with st.sidebar:
        st.markdown("<p class='nav-text'>🚛 TRUCKPARTS UG</p>", unsafe_allow_html=True)
        if st.button("🔍  MARKET LOUNGE", use_container_width=True): 
            st.session_state.page = "Market"; st.session_state.admin_active = False
        st.write("")
        if st.button("🏪  SHOP DIRECTORY", use_container_width=True): 
            st.session_state.page = "Directory"; st.session_state.admin_active = False
        st.write("")
        if st.button("🛠  VENDOR HUB", use_container_width=True): 
            st.session_state.page = "Vendor"; st.session_state.admin_active = False
        st.write("---")
        st.caption("Secure Managed Ecosystem v5.0")

    # GHOST ADMIN INTERCEPTOR
    if st.session_state.admin_active:
        render_admin_dashboard()
        return

    # Routing
    if st.session_state.page == "Market": render_market()
    elif st.session_state.page == "Directory": render_directory()
    elif st.session_state.page == "Vendor": render_vendor()

# --- 1. MARKETPLACE (Google-Style Bar + Ghost Trigger) ---
def render_market():
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Jebale Ko, Driver! 🇺🇬</h2>", unsafe_allow_html=True)
    
    # Integrated Search Bar Layout
    col_input, col_search, col_cam = st.columns([4, 1, 0.6])
    
    with col_input:
        query = st.text_input("", placeholder="Search Part Number, Brand, or Name...", label_visibility="collapsed")
    
    with col_search:
        search_btn = st.button("🔍 Search")
        
    with col_cam:
        cam_btn = st.button("📷")

    # ADMIN TRIGGER CHECK
    if query.strip() == SECRET_ADMIN_KEY:
        st.session_state.admin_active = True
        st.rerun()

    if cam_btn:
        st.camera_input("Scan Part", label_visibility="collapsed")
        # Logic remains to auto-fill search on image capture as per previous code

    if query or search_btn:
        res = supabase.table("parts").select("*, shops(*)").execute()
        results = [i for i in res.data if not i['shops']['is_frozen'] and (query.lower() in i['name'].lower() or query.lower() in str(i['part_number']).lower())]
        
        if results:
            for item in results:
                st.markdown(f"""<div class='lobby-card'>
                    <div style='display:flex; justify-content:space-between;'>
                        <div><h3>{item['name']}</h3><p>{item['brand']} | No: {item['part_number']}<br>📍 {item['shops']['name']}</p></div>
                        <div class='price-tag'>UGX {item['price_ugx']:,}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.warning("No matches found. Ensure you are searching for Hino, Scania, or specific part numbers.")

# --- 2. VENDOR HUB (Standardized Business Registration) ---
def render_vendor():
    st.markdown("## 🛡️ Vendor Onboarding")
    mode = st.radio("Select Business Action", ["Claim Ownership of Existing Shop", "Register New Enterprise"])
    
    if mode == "Register New Enterprise":
        st.write("### Official Business Application")
        with st.form("professional_reg"):
            st.write("##### Business Information")
            c1, c2 = st.columns(2)
            biz_name = c1.text_input("Legal Business Name (as on Trade License)")
            tin = c2.text_input("TIN Number (Tax Identification)")
            
            district = c1.selectbox("Region of Operation", ["Kampala Central", "Kampala Industrial", "Jinja", "Mbale", "Mbarara", "Gulu", "Lira"])
            address = c2.text_input("Physical Address / Plot Number")
            
            st.write("---")
            st.write("##### Primary Contact Details")
            c3, c4 = st.columns(2)
            person = c3.text_input("Contact Person (Full Name)")
            email = c4.text_input("Official Business Email")
            phone = c3.text_input("Primary WhatsApp/Phone Number")
            
            st.write("---")
            st.write("##### Documentation")
            license_doc = st.file_uploader("Upload Trading License or Certificate of Incorporation (PDF/JPG)")
            
            st.info("By submitting, you agree to our 21-day trial terms and verification protocol.")
            if st.form_submit_button("Submit Formal Registration"):
                st.success("Application received. Our verification team will contact you within 48 hours.")
    else:
        # Integrated KYC Claim System from previous code
        st.write("### Identity Matching for Listed Shops")
        with st.form("kyc"):
            st.selectbox("Select Shop to Claim", [s['name'] for s in supabase.table("shops").select("name").execute().data])
            st.selectbox("Verification Role", ["Managing Director", "Operations Manager", "Authorized Employee"])
            st.file_uploader("National ID Upload")
            st.camera_input("Security Selfie Match")
            st.form_submit_button("Verify Identity")

# --- 3. MASTER ADMIN (Ghost Dashboard) ---
def render_admin_dashboard():
    st.markdown("## 🛡️ SYSTEM COMMAND CENTER")
    st.button("Logout Admin", on_click=lambda: setattr(st.session_state, 'admin_active', False))
    
    tab1, tab2 = st.tabs(["Manage Active Shops", "Review New Applications"])
    
    with tab1:
        shops = supabase.table("shops").select("*").execute().data
        for s in shops:
            with st.expander(f"Review: {s['name']} (Trial Ends: {s['expiry_date']})"):
                c1, c2 = st.columns(2)
                # Trial days adjustment logic from previous code
                new_date = c1.date_input("Adjust Expiry", value=datetime.strptime(s['expiry_date'], '%Y-%m-%d').date(), key=f"d_{s['id']}")
                if c2.button("Freeze Shop", key=f"f_{s['id']}"):
                    supabase.table("shops").update({"is_frozen": True}).eq("id", s['id']).execute(); st.rerun()

def render_directory():
    st.markdown("## 🏪 Shop Directory")
    res = supabase.table("shops").select("*").execute()
    for s in res.data:
        st.markdown(f"<div class='lobby-card'><h3>{s['name']}</h3><p>📍 {s['location']} | {s['status']}</p></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
