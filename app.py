import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from supabase import create_client, Client
from datetime import datetime, date, timedelta, timezone

# --- 1. EXECUTIVE CONFIG & THEME ---
st.set_page_config(page_title="TruckParts UG | Executive Portal", page_icon="🚛", layout="wide")

# --- 2. DATABASE CONNECTION ---
# IMPORTANT: Put your actual Supabase URL and KEY here
URL = "https://fasgqlvfmrdtlydelnni.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhc2dxbHZmbXJkdGx5ZGVsbm5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NDYyNzYsImV4cCI6MjA5MDEyMjI3Nn0.gxm--vdmUlxMaGH_r70sMrTxbt-MidtS8Vlse94pkDw"
SECRET_ADMIN_KEY = "UGMASTER2026" 

supabase: Client = create_client(URL, KEY)

# --- 3. ADVANCED EXECUTIVE CSS (Mobile-First) ---
st.markdown("""
<style>
    .stApp { background-color: #0F172A; color: white; }
    [data-testid="stSidebarNav"] { display: none; }
    .nav-text { font-size: 26px !important; font-weight: 900; color: #FFD700; text-align: center; margin-bottom: 30px; }
    
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
        width: 100%;
    }
    
    /* Search Bar Input Styling */
    .stTextInput>div>div>input {
        background-color: white;
        color: black;
        border-radius: 50px;
        height: 50px;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = "Market"
if 'search_query' not in st.session_state: st.session_state.search_query = ""
if 'selected_shop' not in st.session_state: st.session_state.selected_shop = None
if 'cart' not in st.session_state: st.session_state.cart = []
if 'claim_target' not in st.session_state: st.session_state.claim_target = None

# --- 5. UTILITIES ---
def format_ugx(amount):
    return f"UGX {amount:,.0f}"

# --- 6. EXECUTIVE SIDEBAR ---
with st.sidebar:
    st.markdown("<p class='nav-text'>🚛 TRUCKPARTS UG</p>", unsafe_allow_html=True)
    if st.button("🔍  MARKET LOUNGE"): 
        st.session_state.page = "Market"; st.session_state.selected_shop = None; st.session_state.search_query = ""
    st.write("")
    if st.button("🏪  SHOP DIRECTORY"): 
        st.session_state.page = "Directory"
    st.write("")
    if st.button("🛒  MY CART (" + str(len(st.session_state.cart)) + ")"): 
        st.session_state.page = "Cart"
    st.write("")
    if st.button("🛠  VENDOR HUB"): 
        st.session_state.page = "Vendor"
    st.write("---")
    st.caption("Secure Managed Ecosystem v7.0 | Uganda")

# --- PAGE 1: MARKET LOUNGE ---
def render_market():
    if st.session_state.selected_shop:
        render_shop_profile(st.session_state.selected_shop); return

    st.markdown("<h2 style='text-align: center; color: #FFD700;'>Jebale Ko, Driver! 🇺🇬</h2>", unsafe_allow_html=True)
    
    # Google-Style Row
    col_in, col_btn, col_cam = st.columns([3.5, 1, 0.6])
    with col_in:
        query = st.text_input("", value=st.session_state.search_query, placeholder="Search Part No, Brand, or Name...", label_visibility="collapsed")
    with col_btn:
        search_trigger = st.button("🔍 Search")
    with col_cam:
        if st.button("📷"):
            img = st.camera_input("Scan Part", label_visibility="collapsed")
            if img:
                st.session_state.search_query = "1R12-402"; st.rerun()

    # GHOST ADMIN TRIGGER
    if query.strip() == SECRET_ADMIN_KEY:
        render_admin_dashboard(); return

    if query or search_trigger:
        res = supabase.table("parts").select("*, shops(*)").execute()
        results = [i for i in res.data if not i['shops']['is_frozen'] and (query.lower() in i['name'].lower() or query.lower() in str(i['part_number']).lower())]
        
        if results:
            cols = st.columns(2)
            for idx, item in enumerate(results):
                with cols[idx % 2]:
                    st.markdown(f"""<div class='lobby-card'>
                        <h3>{item['name']}</h3><p>{item['brand']} | No: {item['part_number']}<br>📍 {item['shops']['name']}</p>
                        <div class='price-tag'>{format_ugx(item['price_ugx'])}</div>
                    </div>""", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    if c1.button("Details", key=f"d_{item['id']}"): 
                        st.session_state.selected_shop = item['shops']['id']; st.rerun()
                    if c2.button("Add to Cart", key=f"c_{item['id']}"): 
                        st.session_state.cart.append(item); st.toast("Added to Cart!")
        else:
            st.warning("No matches found. Try 'Scania' or 'Hino'.")
    else:
        # CATEGORIES
        st.write("---")
        st.write("### Browse Categories")
        cats = st.columns(4)
        if cats[0].button("⚙️ Engines"): st.session_state.search_query = "Engine"; st.rerun()
        if cats[1].button("🛑 Brakes"): st.session_state.search_query = "Brake"; st.rerun()
        if cats[2].button("🛞 Tyres"): st.session_state.search_query = "Tyre"; st.rerun()
        if cats[3].button("⚡ Electric"): st.session_state.search_query = "Filter"; st.rerun()

# --- PAGE 2: SHOP DIRECTORY (With Maps) ---
def render_directory():
    st.title("Verified Shop Directory")
    shops = supabase.table("shops").select("*").execute().data
    
    # Kampala Map
    m = folium.Map(location=[0.3142, 32.5825], zoom_start=13, tiles="CartoDB dark_matter")
    for s in shops:
        if s['latitude']: folium.Marker([s['latitude'], s['longitude']], popup=s['name']).add_to(m)
    st_folium(m, width=800, height=400)
    
    for s in shops:
        with st.container():
            st.markdown(f"<div class='lobby-card'><h3>{s['name']}</h3><p>📍 {s['location']} | Status: <b>{s['claim_status']}</b></p></div>", unsafe_allow_html=True)
            if s['claim_status'] == "Unclaimed":
                if st.button(f"🔐 Claim Ownership: {s['name']}", key=f"clm_{s['id']}"):
                    st.session_state.claim_target = s['name']; st.session_state.page = "Vendor"; st.rerun()

# --- PAGE 3: VENDOR HUB (Executive Registration) ---
def render_vendor():
    st.title("🛡️ Vendor Hub")
    mode = st.radio("Action", ["Identity Verification (Claim Shop)", "Register New Business"])
    
    if mode == "Register New Business":
        with st.form("exec_reg"):
            st.write("### Executive Business Application")
            c1, c2 = st.columns(2)
            c1.text_input("Legal Business Name")
            c2.text_input("TIN Number (Optional)")
            c1.text_input("Contact Person")
            c2.text_input("Official Email")
            st.file_uploader("Trading License (Optional)")
            if st.form_submit_button("Submit Application"):
                st.success("Application received. We will contact you in 2-5 days.")
    else:
        target = st.session_state.claim_target if st.session_state.claim_target else "Select a shop"
        st.info(f"Target: **{target}**")
        with st.form("kyc"):
            st.selectbox("Role", ["Owner", "Employee"])
            st.text_input("Position")
            st.file_uploader("Upload ID")
            st.camera_input("Selfie Verification")
            st.form_submit_button("Submit for Review")

# --- PAGE 4: GHOST ADMIN ---
def render_admin_dashboard():
    st.title("🛡️ MASTER SYSTEM ADMIN")
    shops = supabase.table("shops").select("*").execute().data
    for s in shops:
        with st.expander(f"Control: {s['name']}"):
            c1, c2 = st.columns(2)
            new_date = c1.date_input("Adjust Expiry", value=datetime.strptime(s['expiry_date'], '%Y-%m-%d').date(), key=f"d_{s['id']}")
            if c1.button("Save Date", key=f"s_{s['id']}"):
                supabase.table("shops").update({"expiry_date": str(new_date)}).eq("id", s['id']).execute(); st.rerun()
            if c2.button("Approve Access", key=f"app_{s['id']}"):
                supabase.table("shops").update({"claim_status": "Verified"}).eq("id", s['id']).execute(); st.rerun()
            if c2.button("Freeze", key=f"frz_{s['id']}"):
                supabase.table("shops").update({"is_frozen": True}).eq("id", s['id']).execute(); st.rerun()

# --- PAGE 5: CART ---
def render_cart():
    st.title("🛒 Your Cart")
    if not st.session_state.cart:
        st.warning("Cart is empty.")
    else:
        total = sum([item['price_ugx'] for item in st.session_state.cart])
        for i, item in enumerate(st.session_state.cart):
            st.write(f"✅ {item['name']} - UGX {item['price_ugx']:,}")
        st.header(f"Total: {format_ugx(total)}")
        st.button("Generate WhatsApp Order")

def render_shop_profile(shop_id):
    shop = supabase.table("shops").select("*").eq("id", shop_id).single().execute().data
    parts = supabase.table("parts").select("*").eq("shop_id", shop_id).execute().data
    st.button("⬅️ Back"); st.title(shop['name'])
    if parts: st.table(pd.DataFrame(parts)[['name', 'part_number', 'price_ugx']])
    st.text_area("Message Vendor..."); st.button("Send Message")

# --- ROUTER ---
if st.session_state.page == "Market": render_market()
elif st.session_state.page == "Directory": render_directory()
elif st.session_state.page == "Vendor": render_vendor()
elif st.session_state.page == "Cart": render_cart()
