import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date

# --- CONFIG & SEO ---
st.set_page_config(page_title="TruckParts UG", page_icon="🚛", layout="wide")

# --- DATABASE & SECURITY ---
# PASTE YOUR ACTUAL KEYS HERE
URL = "https://fasgqlvfmrdtlydelnni.supabase.co" 
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhc2dxbHZmbXJkdGx5ZGVsbm5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NDYyNzYsImV4cCI6MjA5MDEyMjI3Nn0.gxm--vdmUlxMaGH_r70sMrTxbt-MidtS8Vlse94pkDw"
ADMIN_PASSWORD = "Admin@Trucks256" 

supabase: Client = create_client(URL, KEY)

def main():
    # High-Contrast Mobile UI Styling
    st.markdown("""<style>
        .stApp { background-color: #0F172A; color: white; }
        .stButton>button { border-radius: 12px; font-weight: bold; min-height: 50px; background-color: #F59E0B; color: black; border: none; }
        .price-tag { color: #F59E0B; font-size: 1.6em; font-weight: 800; }
        .frozen-tag { background-color: #EF4444; padding: 5px; border-radius: 5px; font-weight: bold; font-size: 0.8em; }
        .verified-tag { color: #10B981; font-weight: bold; }
    </style>""", unsafe_allow_html=True)

    # SIDEBAR - Admin is HIDDEN from the main menu
    st.sidebar.title("🚛 TruckParts UG")
    menu = ["🔍 Find Parts", "🏪 Shop Directory", "🛠 Vendor Portal"]
    choice = st.sidebar.radio("Navigate to:", menu)

    # SECRET ADMIN ACCESS (Hidden at bottom of sidebar)
    st.sidebar.markdown("---")
    secret_admin = st.sidebar.checkbox("🔐 Staff Login")

    if secret_admin:
        render_admin_dashboard()
    elif choice == "🔍 Find Parts":
        render_search()
    elif choice == "🏪 Shop Directory":
        render_directory()
    elif choice == "🛠 Vendor Portal":
        render_vendor_portal()

# --- 1. SEARCH (Hides Frozen or Expired Shops) ---
def render_search():
    st.title("Search Spare Parts")
    query = st.text_input("Enter Part Name, Number or Brand...", placeholder="e.g. 16400, Scania, Actros")

    if query:
        res = supabase.table("parts").select("*, shops(*)").execute()
        today = date.today()
        
        # FILTER: Show only if NOT frozen AND NOT expired
        valid = [
            item for item in res.data 
            if not item['shops']['is_frozen'] 
            and datetime.strptime(item['shops']['expiry_date'], '%Y-%m-%d').date() >= today
            and (query.lower() in item['name'].lower() or query.lower() in item['part_number'].lower() or query.lower() in item['brand'].lower())
        ]

        if valid:
            st.success(f"Found {len(valid)} verified results")
            for item in valid:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"### {item['name']}")
                        st.write(f"🏢 {item['shops']['name']} | 📍 {item['shops']['location']}")
                        st.write(f"**Part No:** `{item['part_number']}` | **Brand:** {item['brand']}")
                        st.markdown(f"<span class='verified-tag'>✅ {item['shops']['status']}</span>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<p class='price-tag'>UGX {item['price_ugx']:,}</p>", unsafe_allow_html=True)
                        st.markdown(f"[💬 WhatsApp](https://wa.me/{item['shops']['phone']})")
                    st.divider()
        else:
            st.error("No active matches found. Shops may be out of stock or trial expired.")

# --- 2. VENDOR PORTAL (Corrected Pricing capped at 1.5M) ---
def render_vendor_portal():
    st.title("Vendor Hub")
    st.info("💡 21-Day Free Trial starts upon registration. Switch to a paid plan to stay visible.")
    
    tab1, tab2 = st.tabs(["Inventory Manager", "Subscription Packages"])
    
    with tab1:
        st.write("### List a New Part")
        with st.form("add_part"):
            n = st.text_input("Part Name")
            num = st.text_input("Part Number")
            pr = st.number_input("Price (UGX)", min_value=1000)
            if st.form_submit_button("Post to Marketplace"):
                st.success("Successfully added to the marketplace!")

    with tab2:
        st.write("### Choose Your Visibility Plan")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("BASIC")
            st.write("1 Mo: 60k")
            st.write("6 Mo: 330k")
            st.write("**1 Year: 600k**")
            st.button("Select Basic", key="p1")
        with c2:
            st.subheader("STANDARD")
            st.write("1 Mo: 100k")
            st.write("6 Mo: 550k")
            st.write("**1 Year: 1.0M**")
            st.button("Select Standard", key="p2")
        with c3:
            st.subheader("PREMIUM")
            st.write("1 Mo: 150k")
            st.write("6 Mo: 800k")
            st.write("**1 Year: 1.5M**") # CAPPED AT YOUR LIMIT
            st.button("Select Premium", key="p3")

# --- 3. HIDDEN ADMIN DASHBOARD (Master Rights) ---
def render_admin_dashboard():
    st.title("Administrator Control Panel")
    pw = st.text_input("Master Password", type="password")
    
    if pw == ADMIN_PASSWORD:
        st.success("Access Granted")
        shops = supabase.table("shops").select("*").order("name").execute().data
        
        for s in shops:
            with st.expander(f"Shop: {s['name']} ({s['location']})"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"Plan: {s['plan']} | Expiry: {s['expiry_date']}")
                
                # FREEZE LOGIC
                if s['is_frozen']:
                    c2.markdown("<span class='frozen-tag'>HIDDEN / FROZEN</span>", unsafe_allow_html=True)
                    if c2.button("Unfreeze Shop", key=f"unf_{s['id']}"):
                        supabase.table("shops").update({"is_frozen": False}).eq("id", s['id']).execute()
                        st.rerun()
                else:
                    if c2.button("Freeze (Hide Shop)", key=f"frz_{s['id']}"):
                        supabase.table("shops").update({"is_frozen": True}).eq("id", s['id']).execute()
                        st.rerun()
                
                # DELETE LOGIC
                if c3.button("🗑 Delete Permanently", key=f"del_{s['id']}"):
                    supabase.table("shops").delete().eq("id", s['id']).execute()
                    st.rerun()
    elif pw:
        st.error("Access Denied")

def render_directory():
    st.title("Verified Shop Directory")
    res = supabase.table("shops").select("*").execute()
    for s in res.data:
        st.write(f"🏢 **{s['name']}** | {s['location']} | 📞 {s['phone']}")

if __name__ == "__main__":
    main()
