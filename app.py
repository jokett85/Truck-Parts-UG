import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date

# --- CONFIG & MODERN UI ---
st.set_page_config(page_title="TruckParts UG", page_icon="🚛", layout="wide")

# --- DATABASE & GHOST SECURITY ---
URL = "https://fasgqlvfmrdtlydelnni.supabase.co" 
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhc2dxbHZmbXJkdGx5ZGVsbm5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NDYyNzYsImV4cCI6MjA5MDEyMjI3Nn0.gxm--vdmUlxMaGH_r70sMrTxbt-MidtS8Vlse94pkDw"
SECRET_ADMIN_KEY = "UG-MASTER-2026" 

supabase: Client = create_client(URL, KEY)

def main():
    # --- PREMIUM NAVIGATION & BUTTON STYLING ---
    st.markdown("""<style>
        .stApp { background-color: #0F172A; color: white; }
        /* Clean Navigation Sidebar */
        [data-testid="stSidebarNav"] { display: none; } /* Hide default nav */
        .nav-button { 
            width: 100%; padding: 15px; margin-bottom: 10px; border-radius: 10px; 
            background: #1E293B; border-left: 5px solid #F59E0B; text-align: left;
            cursor: pointer; transition: 0.3s;
        }
        .nav-button:hover { background: #334155; }
        .price-tag { color: #F59E0B; font-size: 1.8em; font-weight: 900; }
        .kyc-box { border: 2px dashed #475569; padding: 20px; border-radius: 15px; background: #1E293B; }
    </style>""", unsafe_allow_html=True)

    # --- CUSTOM PREMIUM SIDEBAR ---
    with st.sidebar:
        st.markdown("### 🚛 TruckParts UG")
        st.write("---")
        # Custom Nav Actions
        if st.button("🔍 Market Lounge", use_container_width=True): st.session_state.page = "Market"
        if st.button("🏪 Shop Directory", use_container_width=True): st.session_state.page = "Directory"
        if st.button("🛠 Vendor Portal", use_container_width=True): st.session_state.page = "Vendor"
        st.write("---")
        st.caption("v2.0 Managed Ecosystem | Uganda")

    # Handle Page Routing
    if "page" not in st.session_state: st.session_state.page = "Market"
    
    if st.session_state.page == "Market": render_marketplace()
    elif st.session_state.page == "Directory": render_directory()
    elif st.session_state.page == "Vendor": render_vendor_portal()

# --- 1. MARKETPLACE (Ghost Admin Entry) ---
def render_marketplace():
    st.markdown("## 🇺🇬 Jebale Ko, Driver!")
    query = st.text_input("", placeholder="Search Part Number or Name (Secret Key here for Admin)...")

    if query == SECRET_ADMIN_KEY:
        render_admin_dashboard()
        return

    # Normal Search Logic (Hides Expired/Frozen)
    res = supabase.table("parts").select("*, shops(*)").execute()
    today = date.today()
    
    if query:
        valid = [i for i in res.data if not i['shops']['is_frozen'] and datetime.strptime(i['shops']['expiry_date'], '%Y-%m-%d').date() >= today and (query.lower() in i['name'].lower() or query.lower() in i['part_number'].lower())]
        for item in valid:
            with st.container():
                c1, c2 = st.columns([3, 1])
                c1.write(f"### {item['name']}")
                c1.write(f"🏢 {item['shops']['name']} | 📍 {item['shops']['location']}")
                c2.markdown(f"<p class='price-tag'>UGX {item['price_ugx']:,}</p>", unsafe_allow_html=True)
                st.divider()
    else:
        st.info("Browse the directory or search above to find parts.")

# --- 2. VENDOR PORTAL (Verification & KYC System) ---
def render_vendor_portal():
    st.title("Vendor Hub & Verification")
    
    tab1, tab2 = st.tabs(["Claim/Register Shop", "Manage My Inventory"])
    
    with tab1:
        st.header("Step 1: Identity Verification")
        st.write("To manage a listed shop, you must prove ownership via our KYC system.")
        
        with st.form("kyc_form"):
            target_shop = st.selectbox("Select Your Shop from the List", [s['name'] for s in supabase.table("shops").select("name").execute().data])
            st.write("---")
            st.write("📸 **Upload National ID / Passport**")
            id_doc = st.file_uploader("Upload ID", type=['png', 'jpg', 'jpeg'])
            
            st.write("📸 **Real-Time Selfie**")
            selfie = st.camera_input("Take a Selfie for Identity Match")
            
            email = st.text_input("Contact Email")
            
            if st.form_submit_button("Submit for Review (2-5 Days)"):
                if id_doc and selfie:
                    # Logic to save to Supabase (Simulated here)
                    supabase.table("shops").update({"claim_status": "Pending", "owner_email": email}).eq("name", target_shop).execute()
                    st.success("Documents submitted! Our team will verify your identity within 2-5 working days.")
                else:
                    st.error("Please provide both ID and Selfie.")

    with tab2:
        st.header("Inventory Access")
        st.warning("Access Restricted. Verification Required.")
        st.write("You will receive an email once your shop access is granted.")

# --- 3. GHOST ADMIN DASHBOARD (Master Rights) ---
def render_admin_dashboard():
    st.title("🛡️ MASTER SYSTEM CONTROL")
    st.info("Review Identity Docs, Freeze Shops, Adjust Trials.")
    
    shops = supabase.table("shops").select("*").order("claim_status").execute().data
    
    for s in shops:
        with st.expander(f"Review: {s['name']} (Status: {s['claim_status']})"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"**Plan:** {s['plan']}")
                new_expiry = st.date_input("Adjust Expiry", datetime.strptime(s['expiry_date'], '%Y-%m-%d').date(), key=f"d_{s['id']}")
            
            with c2:
                st.write("**KYC Review**")
                st.write(f"Owner Email: {s['owner_email']}")
                if s['claim_status'] == "Pending":
                    st.warning("⚠️ Pending Identity Match")
                    if st.button("APPROVE OWNERSHIP", key=f"app_{s['id']}"):
                        supabase.table("shops").update({"claim_status": "Verified", "verified_at": str(datetime.now())}).eq("id", s['id']).execute()
                        st.success("Owner Granted Access!")
                
            with col3:
                if st.button("FREEZE SHOP", key=f"frz_{s['id']}"):
                    supabase.table("shops").update({"is_frozen": True}).eq("id", s['id']).execute()
                    st.rerun()

def render_directory():
    st.title("Shop Directory")
    res = supabase.table("shops").select("*").execute()
    for s in res.data:
        st.write(f"🏢 **{s['name']}** | {s['location']} | Status: {s['claim_status']}")

if __name__ == "__main__":
    main()
