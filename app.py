import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date, timedelta, timezone

# --- 1. EXECUTIVE CONFIG & THEME ---
st.set_page_config(page_title="TruckParts UG | Executive Portal", page_icon="🚛", layout="wide")

# --- 2. DATABASE CONNECTION ---
URL = "https://fasgqlvfmrdtlydelnni.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhc2dxbHZmbXJkdGx5ZGVsbm5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NDYyNzYsImV4cCI6MjA5MDEyMjI3Nn0.gxm--vdmUlxMaGH_r70sMrTxbt-MidtS8Vlse94pkDw"
SECRET_ADMIN_KEY = "UGMASTER2026" 
supabase: Client = create_client(URL, KEY)

# --- 3. CUSTOM EXECUTIVE CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0F172A; color: white; }
    [data-testid="stSidebarNav"] { display: none; }
    .nav-text { font-size: 26px !important; font-weight: 800; color: #FFD700; text-align: center; margin-bottom: 30px; }
    .lobby-card { 
        background: #1E293B; padding: 25px; border-radius: 15px; 
        border-left: 6px solid #FFD700; margin-bottom: 20px;
    }
    .price-tag { color: #FFD700; font-size: 1.8em; font-weight: 900; }
    .stButton>button { 
        border-radius: 12px; font-weight: bold; min-height: 60px; 
        background-color: #FFD700; color: #0F172A; border: none; font-size: 1.1em;
    }
    .stTextInput>div>div>input { background-color: #1E293B; color: white; border: 1px solid #475569; }
</style>
""", unsafe_allow_html=True)

# --- 4. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = "Market"
if 'search_query' not in st.session_state: st.session_state.search_query = ""
if 'selected_shop' not in st.session_state: st.session_state.selected_shop = None
if 'claim_target' not in st.session_state: st.session_state.claim_target = None

# --- 5. UTILITIES ---
def format_ugx(amount):
    return f"UGX {amount:,.0f}"

# --- 6. EXECUTIVE SIDEBAR ---
with st.sidebar:
    st.markdown("<p class='nav-text'>🚛 TRUCKPARTS UG</p>", unsafe_allow_html=True)
    if st.button("🔍  MARKET LOUNGE", use_container_width=True): 
        st.session_state.page = "Market"; st.session_state.selected_shop = None; st.session_state.search_query = ""
    st.write("")
    if st.button("🏪  SHOP DIRECTORY", use_container_width=True): 
        st.session_state.page = "Directory"
    st.write("")
    if st.button("🛠  VENDOR HUB", use_container_width=True): 
        st.session_state.page = "Vendor"
    st.write("---")
    st.caption("Secure Managed System v6.0 | Uganda")

# --- PAGE 1: MARKET LOUNGE (Integrated Google-Style Search) ---
def render_market():
    if st.session_state.selected_shop:
        render_shop_profile(st.session_state.selected_shop)
        return

    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Jebale Ko, Driver! 🇺🇬</h2>", unsafe_allow_html=True)
    
    # Google-Style Integrated Search Row
    col_input, col_search, col_cam = st.columns([4, 1, 0.6])
    with col_input:
        query = st.text_input("", value=st.session_state.search_query, placeholder="Search Part Number, Brand, or Name...", label_visibility="collapsed")
    with col_search:
        search_btn = st.button("🔍 Search")
    with col_cam:
        if st.button("📷"):
            img = st.camera_input("Scan Part", label_visibility="collapsed")
            if img:
                st.session_state.search_query = "1R12-402"; st.rerun()

    # GHOST ADMIN TRIGGER
    if query.strip() == SECRET_ADMIN_KEY:
        render_admin_dashboard()
        return

    if query or search_btn:
        res = supabase.table("parts").select("*, shops(*)").execute()
        results = [i for i in res.data if not i['shops']['is_frozen'] and (query.lower() in i['name'].lower() or query.lower() in str(i['part_number']).lower())]
        
        if results:
            for item in results:
                st.markdown(f"""<div class='lobby-card'>
                    <div style='display:flex; justify-content:space-between;'>
                        <div><h3>{item['name']}</h3><p>{item['brand']} | No: {item['part_number']}<br>📍 {item['shops']['name']}</p></div>
                        <div class='price-tag'>{format_ugx(item['price_ugx'])}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
                if st.button("View Shop Details", key=f"res_{item['id']}"):
                    st.session_state.selected_shop = item['shops']['id']; st.rerun()
        else:
            st.warning("No matches found. Try searching for Mercedes, Scania, or a Part Number.")
    else:
        # CATEGORIES LOBBY
        st.write("### Quick Browse")
        c = st.columns(4)
        if c[0].button("⚙️ Engines"): st.session_state.search_query = "Engine"; st.rerun()
        if c[1].button("🛑 Brakes"): st.session_state.search_query = "Brake"; st.rerun()
        if c[2].button("🛞 Tyres"): st.session_state.search_query = "Tyre"; st.rerun()
        if c[3].button("⚡ Electric"): st.session_state.search_query = "Filter"; st.rerun()

# --- PAGE 2: SHOP DIRECTORY (Claiming Persistence) ---
def render_directory():
    st.markdown("## 🏪 Shop Directory")
    res = supabase.table("shops").select("*").execute()
    for s in res.data:
        with st.container():
            st.markdown(f"<div class='lobby-card'><h3>{s['name']}</h3><p>📍 {s['location']} | Status: <b>{s['claim_status']}</b></p></div>", unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            if c1.button("View Shop", key=f"dir_v_{s['id']}"):
                st.session_state.selected_shop = s['id']; st.session_state.page = "Market"; st.rerun()
            if s['claim_status'] == "Unclaimed":
                if c2.button(f"🔐 Claim Ownership: {s['name']}", key=f"clm_{s['id']}"):
                    st.session_state.claim_target = s['name']; st.session_state.page = "Vendor"; st.rerun()

# --- PAGE 3: VENDOR HUB (Registration Updated) ---
def render_vendor():
    st.markdown("## 🛡️ Vendor Onboarding")
    mode = st.radio("Business Action", ["Claim Identity of Listed Shop", "Register a New Enterprise"])
    
    if mode == "Register a New Enterprise":
        st.write("### Business Application Form")
        with st.form("pro_reg"):
            c1, c2 = st.columns(2)
            biz_name = c1.text_input("Legal Business Name")
            tin = c2.text_input("TIN Number (Optional)") # UPDATED: Optional
            district = c1.selectbox("Operating Region", ["Kampala Central", "Kampala Industrial", "Jinja", "Mbale", "Mbarara", "Gulu", "Lira"])
            address = c2.text_input("Physical Address / Plot Number")
            st.write("---")
            c3, c4 = st.columns(2)
            person = c3.text_input("Contact Person (Full Name)")
            email = c4.text_input("Business Email Address")
            phone = c3.text_input("Primary WhatsApp Number")
            st.write("---")
            st.write("##### Official Documentation")
            license_doc = st.file_uploader("Upload Trade License / Incorporation Cert (Optional)", type=['pdf', 'jpg', 'png']) # UPDATED: Optional
            if st.form_submit_button("Submit Registration for Review"):
                st.success("Application Received! Our team will contact you within 2-5 working days.")
    else:
        target = st.session_state.claim_target if st.session_state.claim_target else "Select a shop"
        st.info(f"Currently Claiming: **{target}**")
        with st.form("kyc_claim"):
            role = st.selectbox("My Role", ["Managing Director", "Sales/Parts Manager", "Authorized Employee"])
            position = st.text_input("Current Position")
            st.file_uploader("Upload National ID/Passport")
            st.camera_input("Identity Match Selfie")
            if st.form_submit_button("Submit Identity Claim"):
                st.success("Identity documents submitted for verification.")

# --- PAGE 4: GHOST ADMIN ---
def render_admin_dashboard():
    st.markdown("## 🛡️ MASTER SYSTEM CONTROL")
    shops = supabase.table("shops").select("*").execute().data
    for s in shops:
        with st.expander(f"⚙️ {s['name']} (Status: {s['claim_status']})"):
            c1, c2, c3 = st.columns(3)
            # Trial Adjustment
            new_date = c1.date_input("Expiry", value=datetime.strptime(s['expiry_date'], '%Y-%m-%d').date(), key=f"d_{s['id']}")
            if c1.button("Save Date", key=f"s_{s['id']}"):
                supabase.table("shops").update({"expiry_date": str(new_date)}).eq("id", s['id']).execute(); st.rerun()
            # Visibility
            if s['is_frozen']:
                if c2.button("ACTIVATE", key=f"unf_{s['id']}"):
                    supabase.table("shops").update({"is_frozen": False}).eq("id", s['id']).execute(); st.rerun()
            else:
                if c2.button("FREEZE (HIDE)", key=f"frz_{s['id']}"):
                    supabase.table("shops").update({"is_frozen": True}).eq("id", s['id']).execute(); st.rerun()
            # Approval
            if s['claim_status'] == "Pending Review":
                if c3.button("APPROVE CLAIM", key=f"app_{s['id']}"):
                    supabase.table("shops").update({"claim_status": "Verified"}).eq("id", s['id']).execute(); st.rerun()

def render_shop_profile(shop_id):
    shop = supabase.table("shops").select("*").eq("id", shop_id).single().execute().data
    parts = supabase.table("parts").select("*").eq("shop_id", shop_id).execute().data
    st.button("⬅️ Back to Lounge", on_click=lambda: setattr(st.session_state, 'selected_shop', None))
    st.title(shop['name'])
    st.write(f"📍 {shop['location']} | 📞 {shop['phone']}")
    if parts:
        st.table(pd.DataFrame(parts)[['name', 'part_number', 'brand', 'price_ugx']])
    else:
        st.info("Inventory listing pending verification.")
    st.text_area("💬 Send a message to this vendor...")
    st.button("Send Message")

# --- ROUTER ---
if st.session_state.page == "Market": render_market()
elif st.session_state.page == "Directory": render_directory()
elif st.session_state.page == "Vendor": render_vendor()
