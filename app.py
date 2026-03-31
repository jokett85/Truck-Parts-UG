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
ADMIN_PASS = "Admin@Trucks256"

supabase: Client = create_client(URL, KEY)

def main():
    # --- EXECUTIVE UI (Dark Navy & Gold) ---
    st.markdown("""<style>
        .stApp { background-color: #0F172A; color: white; }
        [data-testid="stSidebar"] { background-color: #1E293B; min-width: 350px !important; }
        [data-testid="stSidebarNav"] { display: none; }
        .nav-text { font-size: 28px !important; font-weight: 800; color: #FFD700; margin-bottom: 25px; }
        .stButton>button { 
            border-radius: 15px; background-color: #FFD700; color: #0F172A; 
            font-weight: 900; font-size: 1.3em; height: 70px; margin-bottom: 15px; border: none; 
        }
        .lobby-card { background: #1E293B; padding: 25px; border-radius: 15px; border-bottom: 5px solid #FFD700; margin-bottom: 20px; }
        .price-tag { color: #FFD700; font-size: 1.8em; font-weight: 900; }
        .category-btn { background: #334155; border-radius: 10px; padding: 10px; text-align: center; }
    </style>""", unsafe_allow_html=True)

    # SESSION STATE MANAGEMENT
    if 'page' not in st.session_state: st.session_state.page = "Market"
    if 'search_val' not in st.session_state: st.session_state.search_val = ""
    if 'selected_shop' not in st.session_state: st.session_state.selected_shop = None
    if 'claim_target' not in st.session_state: st.session_state.claim_target = None

    # --- EXECUTIVE SIDEBAR ---
    with st.sidebar:
        st.markdown("<p class='nav-text'>🚛 TRUCKPARTS UG</p>", unsafe_allow_html=True)
        if st.button("🔍  MARKET LOUNGE", use_container_width=True): 
            st.session_state.page = "Market"; st.session_state.selected_shop = None; st.session_state.search_val = ""
        if st.button("🏪  SHOP DIRECTORY", use_container_width=True): 
            st.session_state.page = "Directory"
        if st.button("🛠  VENDOR HUB", use_container_width=True): 
            st.session_state.page = "Vendor"
        st.write("---")
        st.caption("Secure Managed Ecosystem | v4.0 Final")

    # Routing
    if st.session_state.page == "Market": render_market()
    elif st.session_state.page == "Directory": render_directory()
    elif st.session_state.page == "Vendor": render_vendor()

# --- 1. MARKETPLACE (Search, AI, & Ghost Admin) ---
def render_market():
    if st.session_state.selected_shop:
        render_shop_profile(st.session_state.selected_shop)
        return

    st.markdown("<h1 style='color: #FFD700;'>Jebale Ko, Driver! 🇺🇬</h1>", unsafe_allow_html=True)
    
    # THE REPAIRED SEARCH ROW (Input | Search Button | Camera)
    col_in, col_btn, col_cam = st.columns([3, 1, 0.5])
    with col_in:
        query = st.text_input("", value=st.session_state.search_val, placeholder="Search Part No, Name, or Brand...", label_visibility="collapsed")
    with col_btn:
        do_search = st.button("🔍 Search")
    with col_cam:
        if st.button("📷"):
            img = st.camera_input("Scan Part", label_visibility="collapsed")
            if img:
                st.session_state.search_val = "1R12-402" # AI Match Simulation
                st.rerun()

    # GHOST ADMIN TRIGGER
    if query == SECRET_ADMIN_KEY:
        render_admin_dashboard()
        return

    # SEARCH ENGINE EXECUTION
    final_query = query if query else st.session_state.search_val
    if final_query or do_search:
        res = supabase.table("parts").select("*, shops(*)").execute()
        results = [
            item for item in res.data 
            if not item['shops']['is_frozen'] and
            (final_query.lower() in item['name'].lower() or 
             final_query.lower() in str(item['part_number']).lower() or 
             final_query.lower() in item['brand'].lower())
        ]

        if results:
            st.write(f"### Found {len(results)} Verified Results")
            for item in results:
                with st.container():
                    st.markdown(f"""<div class='lobby-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <div><h3>{item['name']}</h3><p>No: {item['part_number']} | {item['brand']}<br>📍 {item['shops']['name']}</p></div>
                            <div class='price-tag'>UGX {item['price_ugx']:,}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("View Shop Details", key=f"res_{item['id']}"):
                        st.session_state.selected_shop = item['shops']['id']
                        st.rerun()
        else:
            st.warning("No matches found in Uganda database.")
    else:
        # WARM LOBBY CONTENT
        st.write("### Browse Categories")
        cats = st.columns(4)
        if cats[0].button("⚙️ Engine"): st.session_state.search_val = "Engine"; st.rerun()
        if cats[1].button("🛑 Brakes"): st.session_state.search_val = "Brake"; st.rerun()
        if cats[2].button("🛞 Tyres"): st.session_state.search_val = "Tyre"; st.rerun()
        if cats[3].button("⚡ Electric"): st.session_state.search_val = "Filter"; st.rerun()

# --- 2. SHOP DIRECTORY (With Claim Persistence) ---
def render_directory():
    st.title("Executive Shop Directory")
    shops = supabase.table("shops").select("*").execute().data
    for s in shops:
        with st.container():
            st.markdown(f"<div class='lobby-card'><h2>{s['name']}</h2><p>📍 {s['location']} | Status: {s['claim_status']}</p></div>", unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            if c1.button("Open Shop Profile", key=f"dir_{s['id']}"):
                st.session_state.selected_shop = s['id']
                st.session_state.page = "Market"
                st.rerun()
            if s['claim_status'] == "Unclaimed":
                if c2.button(f"🔐 Claim Ownership of {s['name']}", key=f"clm_{s['id']}"):
                    st.session_state.claim_target = s['name']
                    st.session_state.page = "Vendor"
                    st.rerun()

# --- 3. VENDOR HUB (Verification & New Registration) ---
def render_vendor():
    st.title("🛠 Vendor Hub")
    mode = st.radio("Select Action", ["Identity Verification (Claim Shop)", "Register New Business"])
    
    if mode == "Identity Verification (Claim Shop)":
        target = st.session_state.claim_target if st.session_state.claim_target else "Select a shop from the Directory"
        st.info(f"Currently Claiming: **{target}**")
        with st.form("verification_form"):
            role = st.selectbox("My Relationship to Shop", ["Owner", "Authorized Employee"])
            position = st.text_input("My Position (if employee)")
            st.write("---")
            st.file_uploader("Upload National ID/Passport", type=['png', 'jpg', 'pdf'])
            st.file_uploader("Upload Staff ID / Auth Letter", type=['png', 'jpg', 'pdf'])
            st.camera_input("Take Identity Matching Selfie")
            if st.form_submit_button("Submit Documents for Review (2-5 Days)"):
                st.success("Verification documents submitted. Access will be granted after review.")
    else:
        with st.form("new_shop_reg"):
            st.write("### Register a New Shop")
            st.text_input("Business Name")
            st.text_input("WhatsApp Number")
            st.text_input("District / Zone")
            if st.form_submit_button("Request Registration"):
                st.success("Request sent. Admin will contact you.")

# --- 4. GHOST ADMIN (Advanced Dashboard) ---
def render_admin_dashboard():
    st.title("🛡️ MASTER SYSTEM CONTROL")
    shops = supabase.table("shops").select("*").order("name").execute().data
    for s in shops:
        with st.expander(f"Edit: {s['name']} (Trial: {s['expiry_date']})"):
            c1, c2, c3 = st.columns(3)
            with c1:
                new_date = st.date_input("Adjust Expiry", value=datetime.strptime(s['expiry_date'], '%Y-%m-%d').date(), key=f"d_{s['id']}")
                if st.button("Save Date", key=f"s_{s['id']}"):
                    supabase.table("shops").update({"expiry_date": str(new_date)}).eq("id", s['id']).execute()
                    st.rerun()
            with c2:
                if st.button("APPROVE OWNERSHIP", key=f"app_{s['id']}"):
                    supabase.table("shops").update({"claim_status": "Verified"}).eq("id", s['id']).execute()
                    st.success("Access Approved!")
            with c3:
                if s['is_frozen']:
                    if st.button("Activate Shop", key=f"unf_{s['id']}"):
                        supabase.table("shops").update({"is_frozen": False}).eq("id", s['id']).execute(); st.rerun()
                else:
                    if st.button("Freeze/Hide Shop", key=f"frz_{s['id']}"):
                        supabase.table("shops").update({"is_frozen": True}).eq("id", s['id']).execute(); st.rerun()

def render_shop_profile(shop_id):
    shop = supabase.table("shops").select("*").eq("id", shop_id).single().execute().data
    parts = supabase.table("parts").select("*").eq("shop_id", shop_id).execute().data
    st.button("⬅️ Back to Marketplace", on_click=lambda: setattr(st.session_state, 'selected_shop', None))
    st.markdown(f"## {shop['name']}")
    st.write(f"📍 {shop['location']} | 📞 {shop['phone']}")
    st.write("---")
    st.write("### Live Inventory")
    if parts: st.table(pd.DataFrame(parts)[['name', 'part_number', 'brand', 'price_ugx']])
    else: st.info("Inventory upload pending.")
    st.write("---")
    st.write("### 💬 In-App Messaging")
    st.text_area("Message this shop directly...")
    st.button("Send to Shop")

if __name__ == "__main__":
    main()
