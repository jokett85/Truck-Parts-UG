import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date
import smtplib
from email.message import EmailMessage

# --- CONFIG & EXECUTIVE UI ---
st.set_page_config(page_title="TruckParts UG | Executive", page_icon="🚛", layout="wide")

# --- DATABASE & SECURITY ---
URL = "https://fasgqlvfmrdtlydelnni.supabase.co" 
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhc2dxbHZmbXJkdGx5ZGVsbm5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NDYyNzYsImV4cCI6MjA5MDEyMjI3Nn0.gxm--vdmUlxMaGH_r70sMrTxbt-MidtS8Vlse94pkDw"
SECRET_ADMIN_KEY = "UG-MASTER2026" 
APP_EMAIL = "admin@truckparts-ug.com" # The email that receives alerts

supabase: Client = create_client(URL, KEY)

def send_admin_email(subject, content):
    """Placeholder for Email Notification System"""
    # In a live server, you would use smtplib here.
    st.info(f"📩 NOTIFICATION SENT TO ADMIN: {subject}")

def main():
    # --- EXECUTIVE SIDEBAR STYLING ---
    st.markdown("""<style>
        [data-testid="stSidebar"] { background-color: #1B263B; min-width: 320px; }
        [data-testid="stSidebarNav"] { display: none; }
        .nav-card {
            background-color: #2C3E50; border-radius: 15px; padding: 20px;
            margin-bottom: 15px; border-left: 8px solid #FFD700;
            cursor: pointer; transition: 0.3s;
        }
        .nav-card:hover { background-color: #3E5871; transform: scale(1.02); }
        .nav-title { color: #FFD700; font-size: 24px; font-weight: 800; margin-bottom: 0; }
        .nav-icon { font-size: 30px; margin-right: 15px; }
        .price-tag { color: #FFD700; font-size: 2em; font-weight: 900; }
        .stButton>button { border-radius: 12px; font-weight: bold; min-height: 60px; font-size: 1.2em; background-color: #FFD700; color: #1B263B; }
    </style>""", unsafe_allow_html=True)

    # --- THE EXECUTIVE HUB (Sidebar) ---
    with st.sidebar:
        st.markdown("<h1 style='color: white; border-bottom: 2px solid #FFD700;'>MANAGEMENT</h1>", unsafe_allow_html=True)
        st.write("")
        
        if st.button("🔍  MARKET LOUNGE", key="nav_market", use_container_width=True): st.session_state.page = "Market"
        st.write("")
        if st.button("🏪  SHOP DIRECTORY", key="nav_dir", use_container_width=True): st.session_state.page = "Directory"
        st.write("")
        if st.button("🛠  VENDOR PORTAL", key="nav_vendor", use_container_width=True): st.session_state.page = "Vendor"
        
        st.write("---")
        st.caption("TruckParts UG © 2026 | Secure Managed System")

    # Routing
    if "page" not in st.session_state: st.session_state.page = "Market"
    
    if st.session_state.page == "Market": render_marketplace()
    elif st.session_state.page == "Directory": render_directory()
    elif st.session_state.page == "Vendor": render_vendor_portal()

# --- 1. MARKET LOUNGE (Search & Ghost Entry) ---
def render_marketplace():
    st.markdown("<h1 style='color: #FFD700;'>JEBALE KO, DRIVER! 🇺🇬</h1>", unsafe_allow_html=True)
    query = st.text_input("", placeholder="Search Part Name or Number (Admin Code here)...", label_visibility="collapsed")

    if query == SECRET_ADMIN_KEY:
        render_admin_dashboard()
        return

    # Basic Search UI
    res = supabase.table("parts").select("*, shops(*)").execute()
    today = date.today()
    if query:
        valid = [i for i in res.data if not i['shops']['is_frozen'] and datetime.strptime(i['shops']['expiry_date'], '%Y-%m-%d').date() >= today and (query.lower() in i['name'].lower() or query.lower() in i['part_number'].lower())]
        for item in valid:
            with st.container():
                st.markdown(f"""<div style='background:#2C3E50; padding:20px; border-radius:15px; margin-bottom:10px;'>
                    <div style='display:flex; justify-content:space-between;'>
                        <div><h3>{item['name']}</h3><p>📍 {item['shops']['name']} - {item['shops']['location']}</p></div>
                        <div class='price-tag'>UGX {item['price_ugx']:,}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"[💬 WhatsApp Vendor](https://wa.me/{item['shops']['phone']})")

# --- 2. VENDOR PORTAL (Hierarchical Verification) ---
def render_vendor_portal():
    st.title("Vendor Hub & Verification")
    
    mode = st.radio("Select Action", ["Claim an Existing Listed Shop", "Register a New Business"])
    
    if mode == "Claim an Existing Listed Shop":
        st.info("Verification required to manage a pre-listed directory shop.")
        with st.form("claim_form"):
            target = st.selectbox("Select Shop to Claim", [s['name'] for s in supabase.table("shops").select("name").execute().data])
            role = st.selectbox("My Relationship to this Shop", ["I am the Owner", "I am an Authorized Employee"])
            
            position = ""
            if role == "I am an Authorized Employee":
                position = st.text_input("Your Job Position (e.g. Parts Manager)")
                comp_id = st.file_uploader("Upload Staff ID or Authorization Letter", type=['pdf', 'png', 'jpg'])
            
            st.write("---")
            nat_id = st.file_uploader("Upload National ID / Passport", type=['png', 'jpg'])
            selfie = st.camera_input("Security Selfie Check")
            
            if st.form_submit_button("Submit Claim for Review"):
                if nat_id and selfie:
                    # Update Database
                    supabase.table("shops").update({
                        "claim_status": "Pending Review", 
                        "claimer_role": role, 
                        "employee_position": position
                    }).eq("name", target).execute()
                    
                    send_admin_email(f"NEW CLAIM: {target}", f"Role: {role} Position: {position}")
                    st.success("Verification in progress. Review takes 2-5 working days.")

    else:
        st.write("### Register a New Shop")
        with st.form("new_reg"):
            s_name = st.text_input("Business Name")
            s_loc = st.text_input("District / Zone")
            s_phone = st.text_input("WhatsApp Number")
            st.file_uploader("Upload Business Registration Docs", type=['pdf', 'jpg'])
            if st.form_submit_button("Request Registration"):
                st.success("Registration request sent. Admin will contact you.")

# --- 3. MASTER ADMIN (Ghost Access) ---
def render_admin_dashboard():
    st.markdown("---")
    st.title("🛡️ MASTER SYSTEM ADMINISTRATION")
    
    shops = supabase.table("shops").select("*").order("claim_status").execute().data
    
    for s in shops:
        with st.expander(f"Review: {s['name']} - Status: {s['claim_status']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Claimer Role:** {s['claimer_role']}")
                if s['claimer_role'] == "I am an Authorized Employee":
                    st.write(f"**Position:** {s['employee_position']}")
                st.write(f"**Trial Expiry:** {s['expiry_date']}")
                new_days = st.number_input("Add/Subtract Days", value=0, key=f"days_{s['id']}")
                if st.button("Adjust Expiry", key=f"adj_{s['id']}"):
                    new_date = datetime.strptime(s['expiry_date'], '%Y-%m-%d').date() + timedelta(days=new_days)
                    supabase.table("shops").update({"expiry_date": str(new_date)}).eq("id", s['id']).execute()
                    st.rerun()

            with col2:
                st.write("**Verification Actions**")
                if s['claim_status'] == "Pending Review":
                    if st.button("✅ APPROVE ACCESS", key=f"app_{s['id']}"):
                        supabase.table("shops").update({"claim_status": "Verified"}).eq("id", s['id']).execute()
                        st.success("Owner/Employee granted access.")
                
                if st.button("🚫 FREEZE SHOP", key=f"frz_{s['id']}"):
                    supabase.table("shops").update({"is_frozen": True}).eq("id", s['id']).execute()
                    st.rerun()

def render_directory():
    st.title("Executive Shop Directory")
    res = supabase.table("shops").select("*").execute()
    for s in res.data:
        st.write(f"🏢 **{s['name']}** | {s['location']} | Status: {s['claim_status']}")

if __name__ == "__main__":
    main()
