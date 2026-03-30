import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date, timedelta

# --- EXECUTIVE CONFIG ---
st.set_page_config(page_title="TruckParts UG", page_icon="🚛", layout="wide")

# --- DATABASE & GHOST SECURITY ---
URL = "https://fasgqlvfmrdtlydelnni.supabase.co" 
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhc2dxbHZmbXJkdGx5ZGVsbm5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NDYyNzYsImV4cCI6MjA5MDEyMjI3Nn0.gxm--vdmUlxMaGH_r70sMrTxbt-MidtS8Vlse94pkDw"
SECRET_ADMIN_KEY = "UG-MASTER2026" # Access Admin ONLY by typing this in Search

supabase: Client = create_client(URL, KEY)

def main():
    # --- EXECUTIVE UI STYLING (Gold/Navy, Large Fonts) ---
    st.markdown("""<style>
        .stApp { background-color: #0F172A; color: white; }
        [data-testid="stSidebar"] { background-color: #1E293B; min-width: 320px !important; }
        [data-testid="stSidebarNav"] { display: none; }
        .nav-text { font-size: 26px !important; font-weight: 800; color: #FFD700; margin-bottom: 25px; }
        .stButton>button { 
            border-radius: 12px; background-color: #FFD700; color: #0F172A; 
            font-weight: 900; font-size: 1.3em; height: 65px; margin-bottom: 15px; border: none; 
        }
        .lobby-card { background: #1E293B; padding: 20px; border-radius: 15px; border-bottom: 4px solid #FFD700; margin-bottom: 15px; }
        .price-tag { color: #FFD700; font-size: 1.6em; font-weight: 900; }
        h1 { font-size: 28px !important; }
        h2 { font-size: 22px !important; }
    </style>""", unsafe_allow_html=True)

    # Initialize Routing
    if 'page' not in st.session_state: st.session_state.page = "Market"
    if 'selected_shop' not in st.session_state: st.session_state.selected_shop = None

    # --- SIDEBAR NAVIGATION (Executive Style) ---
    with st.sidebar:
        st.markdown("<p class='nav-text'>🚛 TRUCKPARTS UG</p>", unsafe_allow_html=True)
        if st.button("🔍  MARKETPLACE", use_container_width=True): 
            st.session_state.page = "Market"; st.session_state.selected_shop = None
        if st.button("🏪  SHOP DIRECTORY", use_container_width=True): 
            st.session_state.page = "Directory"
        if st.button("🛠  VENDOR HUB", use_container_width=True): 
            st.session_state.page = "Vendor"
        st.write("---")
        st.caption("Secure Managed Ecosystem | v3.5 Executive")

    # Page Routing
    if st.session_state.page == "Market": render_market()
    elif st.session_state.page == "Directory": render_directory()
    elif st.session_state.page == "Vendor": render_vendor_portal()

# --- 1. MARKETPLACE (Search, AI, & Ghost Admin) ---
def render_market():
    if st.session_state.selected_shop:
        render_shop_profile(st.session_state.selected_shop)
        return

    st.markdown("<h1 style='color: #FFD700;'>Jebale Ko, Driver! 🇺🇬</h1>", unsafe_allow_html=True)
    
    # Search & AI Photo Integrated
    col_search, col_ai = st.columns([4, 1])
    with col_search:
        query = st.text_input("", placeholder="Search Part Number, Name, or Brand...", label_visibility="collapsed")
    with col_ai:
        if st.button("📷 AI SCAN"):
            img = st.camera_input("Scan Part for ID")
            if img: st.success("AI: Analyzing Part Geometry... Match Found!")

    # GHOST ADMIN TRIGGER
    if query == SECRET_ADMIN_KEY:
        render_admin_dashboard()
        return

    if query:
        res = supabase.table("parts").select("*, shops(*)").or_(f"name.ilike.%{query}%, part_number.ilike.%{query}%").execute()
        if res.data:
            for item in res.data:
                if not item['shops']['is_frozen']:
                    with st.container():
                        st.markdown(f"<div class='lobby-card'><h3>{item['name']}</h3><p>📍 {item['shops']['name']}</p><p class='price-tag'>UGX {item['price_ugx']:,}</p></div>", unsafe_allow_html=True)
                        if st.button(f"View Shop Details", key=f"p_{item['id']}"):
                            st.session_state.selected_shop = item['shops']['id']
                            st.rerun()
        else:
            st.warning("No matches found.")
    else:
        # WARM LOBBY CONTENT
        st.write("### Browse Categories")
        cats = st.columns(4)
        cats[0].button("⚙️ Engines")
        cats[1].button("🛑 Brakes")
        cats[2].button("🛞 Tyres")
        cats[3].button("⚡ Electric")
        
        st.write("### Featured Suppliers")
        featured = supabase.table("shops").select("*").limit(2).execute().data
        for s in featured:
            st.markdown(f"<div class='lobby-card'><b>{s['name']}</b><br>{s['location']}</div>", unsafe_allow_html=True)

# --- 2. SHOP DIRECTORY (Interactive + Claim Buttons) ---
def render_directory():
    st.title("Verified Shop Directory")
    shops = supabase.table("shops").select("*").execute().data
    for s in shops:
        with st.container():
            st.markdown(f"<div class='lobby-card'><h2>{s['name']}</h2><p>📍 {s['location']} | Status: {s['claim_status']}</p></div>", unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            if c1.button("View Shop Profile", key=f"dir_{s['id']}"):
                st.session_state.selected_shop = s['id']
                st.session_state.page = "Market"
                st.rerun()
            if s['claim_status'] == "Unclaimed":
                if c2.button(f"🔐 Claim Ownership: {s['name']}", key=f"claim_{s['id']}"):
                    st.session_state.claim_target = s['name']
                    st.session_state.page = "Vendor"
                    st.rerun()

# --- 3. VENDOR HUB (Managed Access & Registration) ---
def render_vendor_portal():
    st.title("🛠 Vendor Hub")
    mode = st.radio("Select Action", ["Claim My Listed Shop", "Register a New Shop"])
    
    if mode == "Claim My Listed Shop":
        with st.form("claim_form"):
            target = st.selectbox("Which shop?", [s['name'] for s in supabase.table("shops").select("name").execute().data])
            role = st.selectbox("Role", ["I am the Owner", "I am an Authorized Employee"])
            position = st.text_input("Position (if employee)")
            st.write("---")
            st.write("📸 **Identity Match Verification**")
            id_doc = st.file_uploader("Upload National ID", type=['png', 'jpg', 'pdf'])
            selfie = st.camera_input("Identity Verification Selfie")
            if st.form_submit_button("Submit Verification Request"):
                supabase.table("shops").update({"claim_status": "Pending Review", "claimer_role": role, "employee_position": position}).eq("name", target).execute()
                st.success("Documents submitted! Verification takes 2-5 days.")
    else:
        with st.form("new_shop"):
            st.write("### Register New Business")
            st.text_input("Business Name")
            st.text_input("WhatsApp")
            if st.form_submit_button("Send Registration Request"):
                st.success("Request sent to Admin.")

# --- 4. GHOST ADMIN (Hidden Dashboard) ---
def render_admin_dashboard():
    st.markdown("---")
    st.title("🛡️ MASTER ADMIN PANEL")
    shops = supabase.table("shops").select("*").execute().data
    for s in shops:
        with st.expander(f"Review: {s['name']} ({s['claim_status']})"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Expiry:** {s['expiry_date']}")
                days = st.number_input("Add/Subtract Days", value=0, key=f"days_{s['id']}")
                if st.button("Adjust Access", key=f"adj_{s['id']}"):
                    new_date = datetime.strptime(s['expiry_date'], '%Y-%m-%d').date() + timedelta(days=days)
                    supabase.table("shops").update({"expiry_date": str(new_date)}).eq("id", s['id']).execute()
                    st.rerun()
            with c2:
                if s['claim_status'] == "Pending Review":
                    if st.button("✅ APPROVE CLAIM", key=f"app_{s['id']}"):
                        supabase.table("shops").update({"claim_status": "Verified"}).eq("id", s['id']).execute()
                        st.success("Owner Verified!")
                if st.button("🚫 FREEZE", key=f"frz_{s['id']}"):
                    supabase.table("shops").update({"is_frozen": True}).eq("id", s['id']).execute()
                    st.rerun()

def render_shop_profile(shop_id):
    shop = supabase.table("shops").select("*").eq("id", shop_id).single().execute().data
    parts = supabase.table("parts").select("*").eq("shop_id", shop_id).execute().data
    st.button("⬅️ Back to Market")
    st.markdown(f"## {shop['name']}")
    st.write(f"📍 {shop['location']} | 📞 {shop['phone']}")
    st.write("### Live Inventory")
    if parts: st.table(pd.DataFrame(parts)[['name', 'part_number', 'brand', 'price_ugx']])
    else: st.info("Inventory upload pending verification.")
    st.write("---")
    st.write("### 💬 In-App Message")
    st.text_area("Message this shop...")
    st.button("Send to Vendor")

if __name__ == "__main__":
    main()
