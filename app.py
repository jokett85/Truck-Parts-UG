import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date, timedelta

# --- EXECUTIVE CONFIG ---
st.set_page_config(page_title="TruckParts UG", page_icon="🚛", layout="wide")

# --- DATABASE CONNECTION ---
URL = "https://fasgqlvfmrdtlydelnni.supabase.co" 
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhc2dxbHZmbXJkdGx5ZGVsbm5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NDYyNzYsImV4cCI6MjA5MDEyMjI3Nn0.gxm--vdmUlxMaGH_r70sMrTxbt-MidtS8Vlse94pkDw"
SECRET_ADMIN_KEY = "UG-MASTER2026" 

supabase: Client = create_client(URL, KEY)

def main():
    # --- ADVANCED CSS FOR GOOGLE-STYLE SEARCH BAR & EXECUTIVE LOBBY ---
    st.markdown("""
        <style>
        .stApp { background-color: #0F172A; color: white; }
        [data-testid="stSidebarNav"] { display: none; }
        
        /* Executive Sidebar */
        .nav-text { font-size: 24px !important; font-weight: 800; color: #FFD700; margin-bottom: 20px; text-align: center; }
        
        /* Integrated Search Bar Container */
        .search-container {
            background-color: white;
            border-radius: 50px;
            padding: 5px 20px;
            display: flex;
            align-items: center;
            border: 1px solid #dfe1e5;
            margin-bottom: 20px;
        }
        
        /* Warm Lobby Cards */
        .category-pill {
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 50px;
            padding: 8px 20px;
            margin: 5px;
            display: inline-block;
            font-weight: 600;
            color: #FFD700;
        }

        .lobby-card { 
            background: #1E293B; 
            padding: 20px; 
            border-radius: 15px; 
            border-left: 5px solid #FFD700; 
            margin-bottom: 15px; 
        }

        /* Buttons */
        .stButton>button { 
            border-radius: 10px; font-weight: bold; height: 3em; 
            background-color: #FFD700; color: #0F172A; border: none; 
        }
        </style>
    """, unsafe_allow_html=True)

    # SESSION STATE
    if 'page' not in st.session_state: st.session_state.page = "Market"
    if 'search_query' not in st.session_state: st.session_state.search_query = ""
    if 'selected_shop' not in st.session_state: st.session_state.selected_shop = None
    if 'claim_target' not in st.session_state: st.session_state.claim_target = None

    # --- EXECUTIVE SIDEBAR ---
    with st.sidebar:
        st.markdown("<p class='nav-text'>🚛 TRUCKPARTS UG</p>", unsafe_allow_html=True)
        if st.button("🔍 Marketplace", use_container_width=True): 
            st.session_state.page = "Market"; st.session_state.selected_shop = None; st.session_state.search_query = ""
        if st.button("🏪 Shop Directory", use_container_width=True): 
            st.session_state.page = "Directory"
        if st.button("🛠 Vendor Hub", use_container_width=True): 
            st.session_state.page = "Vendor"
        st.write("---")
        st.caption("Secure Managed System | v4.5 Executive")

    # Routing
    if st.session_state.page == "Market": render_market()
    elif st.session_state.page == "Directory": render_directory()
    elif st.session_state.page == "Vendor": render_vendor()

# --- 1. MARKETPLACE (Google-Style Integrated Bar) ---
def render_market():
    if st.session_state.selected_shop:
        render_shop_profile(st.session_state.selected_shop)
        return

    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Jebale Ko, Driver! 🇺🇬</h2>", unsafe_allow_html=True)
    st.write("<p style='text-align: center;'>Find genuine heavy truck parts across Uganda.</p>", unsafe_allow_html=True)

    # INTEGRATED SEARCH BAR (Simulated inside columns for layout)
    col_main, col_cam = st.columns([5, 1])
    
    with col_main:
        # The search button is effectively the 'Enter' key or a small button next to it
        query = st.text_input("", value=st.session_state.search_query, placeholder="🔍 Search Part Number, Name, or Brand...", label_visibility="collapsed")
    
    with col_cam:
        if st.button("📷"):
            img = st.camera_input("Scan Part", label_visibility="collapsed")
            if img:
                st.session_state.search_query = "1R12-402"; st.rerun()

    # GHOST ADMIN
    if query == SECRET_ADMIN_KEY:
        render_admin_dashboard()
        return

    # SEARCH EXECUTION
    if query:
        res = supabase.table("parts").select("*, shops(*)").execute()
        results = [i for i in res.data if not i['shops']['is_frozen'] and (query.lower() in i['name'].lower() or query.lower() in str(i['part_number']).lower() or query.lower() in i['brand'].lower())]
        
        if results:
            for item in results:
                with st.container():
                    st.markdown(f"""<div class='lobby-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <div><h3 style='margin:0;'>{item['name']}</h3><p>{item['brand']} | No: {item['part_number']}<br>📍 {item['shops']['name']}</p></div>
                            <div style='color: #FFD700; font-size: 1.5em; font-weight: bold;'>UGX {item['price_ugx']:,}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    if st.button(f"Details & Contact", key=f"p_{item['id']}"):
                        st.session_state.selected_shop = item['shops']['id']; st.rerun()
        else:
            st.warning("No matches found. Try 'Scania' or 'Hino'.")
    else:
        # WARM LOBBY CONTENT
        st.write("---")
        st.write("#### ⚙️ Quick Browse")
        cats = st.columns(4)
        if cats[0].button("Engines"): st.session_state.search_query = "Engine"; st.rerun()
        if cats[1].button("Brakes"): st.session_state.search_query = "Brake"; st.rerun()
        if cats[2].button("Tyres"): st.session_state.search_query = "Tyre"; st.rerun()
        if cats[3].button("Filters"): st.session_state.search_query = "Filter"; st.rerun()

# --- 2. SHOP DIRECTORY (Full Claim Logic Integrated) ---
def render_directory():
    st.markdown("## 🏪 Shop Directory")
    shops = supabase.table("shops").select("*").execute().data
    for s in shops:
        with st.container():
            st.markdown(f"<div class='lobby-card'><h3>{s['name']}</h3><p>📍 {s['location']} | Status: <b>{s['claim_status']}</b></p></div>", unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            if c1.button("View Shop", key=f"v_{s['id']}"):
                st.session_state.selected_shop = s['id']; st.session_state.page = "Market"; st.rerun()
            if s['claim_status'] == "Unclaimed":
                if c2.button(f"🔐 Claim {s['name']}", key=f"clm_{s['id']}"):
                    st.session_state.claim_target = s['name']; st.session_state.page = "Vendor"; st.rerun()

# --- 3. VENDOR HUB (Managed KYC System) ---
def render_vendor():
    st.markdown("## 🛠 Vendor Hub")
    mode = st.radio("Action", ["Claim Identity", "New Registration"])
    
    if mode == "Claim Identity":
        target = st.session_state.claim_target if st.session_state.claim_target else "Select Shop"
        st.info(f"Claiming: **{target}**")
        with st.form("kyc"):
            role = st.selectbox("Role", ["Owner", "Manager/Employee"])
            pos = st.text_input("Job Title")
            st.write("📸 **Verification Documents**")
            st.file_uploader("National ID", type=['png', 'jpg'])
            st.camera_input("Selfie Match")
            if st.form_submit_button("Submit for Review"):
                st.success("Verification in progress (2-5 days).")
    else:
        with st.form("reg"):
            st.text_input("Shop Name"); st.text_input("WhatsApp"); st.form_submit_button("Request Access")

# --- 4. GHOST ADMIN (Hidden Search Trigger) ---
def render_admin_dashboard():
    st.markdown("---")
    st.title("🛡️ MASTER SYSTEM ADMIN")
    shops = supabase.table("shops").select("*").execute().data
    for s in shops:
        with st.expander(f"Control: {s['name']} ({s['expiry_date']})"):
            c1, c2 = st.columns(2)
            new_date = c1.date_input("Adjust Expiry", value=datetime.strptime(s['expiry_date'], '%Y-%m-%d').date(), key=f"d_{s['id']}")
            if c1.button("Update Date", key=f"u_{s['id']}"):
                supabase.table("shops").update({"expiry_date": str(new_date)}).eq("id", s['id']).execute(); st.rerun()
            if c2.button("Approve Access", key=f"a_{s['id']}"):
                supabase.table("shops").update({"claim_status": "Verified"}).eq("id", s['id']).execute(); st.rerun()
            if c2.button("Freeze/Hide", key=f"f_{s['id']}"):
                supabase.table("shops").update({"is_frozen": True}).eq("id", s['id']).execute(); st.rerun()

def render_shop_profile(shop_id):
    shop = supabase.table("shops").select("*").eq("id", shop_id).single().execute().data
    parts = supabase.table("parts").select("*").eq("shop_id", shop_id).execute().data
    st.button("⬅️ Back"); st.title(shop['name'])
    st.write(f"📍 {shop['location']} | 📞 {shop['phone']}")
    if parts: st.table(pd.DataFrame(parts)[['name', 'part_number', 'brand', 'price_ugx']])
    else: st.info("Inventory pending verification.")

if __name__ == "__main__":
    main()
