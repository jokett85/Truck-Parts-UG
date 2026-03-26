import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date, timedelta

# --- CONFIG ---
st.set_page_config(page_title="TruckParts UG | Smart Marketplace", page_icon="🚛", layout="wide")

# --- DATABASE & GHOST SECURITY ---
URL = "https://fasgqlvfmrdtlydelnni.supabase.co" 
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhc2dxbHZmbXJkdGx5ZGVsbm5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NDYyNzYsImV4cCI6MjA5MDEyMjI3Nn0.gxm--vdmUlxMaGH_r70sMrTxbt-MidtS8Vlse94pkDw"
# YOUR SECRET SEARCH KEY (Type this in the search bar to open Admin)
SECRET_ADMIN_KEY = "UG-Admin@2026" 

supabase: Client = create_client(URL, KEY)

def main():
    # --- WARM WELCOMING UI (Redesign) ---
    st.markdown("""<style>
        .stApp { background-color: #0F172A; color: white; }
        .main-card { background-color: #1E293B; padding: 25px; border-radius: 15px; border-left: 5px solid #F59E0B; margin-bottom: 20px; }
        .welcome-text { font-size: 2.2em; font-weight: 800; color: #F59E0B; margin-bottom: 0px; }
        .stButton>button { border-radius: 12px; font-weight: bold; min-height: 55px; background-color: #F59E0B; color: black; transition: 0.3s; }
        .stButton>button:hover { background-color: #FFFFFF; transform: scale(1.02); }
        .price-tag { color: #F59E0B; font-size: 1.8em; font-weight: 900; }
        .category-pill { background-color: #334155; padding: 10px 20px; border-radius: 50px; display: inline-block; margin: 5px; cursor: pointer; border: 1px solid #475569; }
    </style>""", unsafe_allow_html=True)

    # Sidebar (Clean & Minimal)
    st.sidebar.title("🚛 TruckParts UG")
    menu = ["🔍 Marketplace", "🏪 Directory", "🛠 Vendor Hub"]
    choice = st.sidebar.radio("Navigation", menu)

    if choice == "🔍 Marketplace":
        render_marketplace()
    elif choice == "🏪 Directory":
        render_directory()
    elif choice == "🛠 Vendor Hub":
        render_vendor_portal()

# --- 1. THE MARKETPLACE (Warm Lobby & Ghost Admin) ---
def render_marketplace():
    # Welcoming Header
    st.markdown(f"<p class='welcome-text'>Jebale Ko, mukama wange (greetings my boss)! 🇺🇬</p>", unsafe_allow_html=True)
    st.write("Find genuine heavy truck parts from Verified Ugandan Suppliers.")

    # Search Bar (The Secret Gate)
    query = st.text_input("", placeholder="🔍 Search Part Number, Name, or Brand (e.g. 16400, Scania)...")

    # HIDDEN ADMIN TRIGGER
    if query == SECRET_ADMIN_KEY:
        render_admin_dashboard()
        return

    if not query:
        # Welcoming Lobby Cards
        st.write("### Popular Categories")
        cols = st.columns(4)
        categories = [("⚙️ Engines", "Turbo"), ("🛑 Brakes", "Pad"), ("🛞 Tyres", "12.00"), ("⚡ Electrical", "Battery")]
        for i, (cat, q) in enumerate(categories):
            if cols[i].button(cat):
                st.rerun()

        st.markdown("""<div class='main-card'>
            <h4>💡 Pro Tip</h4>
            <p>Always verify the part number with the shop on WhatsApp before making payment.</p>
        </div>""", unsafe_allow_html=True)

    else:
        # SEARCH LOGIC
        res = supabase.table("parts").select("*, shops(*)").execute()
        today = date.today()
        
        valid = [
            item for item in res.data 
            if not item['shops']['is_frozen'] 
            and datetime.strptime(item['shops']['expiry_date'], '%Y-%m-%d').date() >= today
            and (query.lower() in item['name'].lower() or query.lower() in item['part_number'].lower() or query.lower() in item['brand'].lower())
        ]

        if valid:
            for item in valid:
                with st.container():
                    st.markdown(f"""<div class='main-card'>
                        <div style='display: flex; justify-content: space-between;'>
                            <div>
                                <h2 style='margin:0;'>{item['name']}</h2>
                                <p style='color:#94A3B8;'>Part: {item['part_number']} | Brand: {item['brand']}</p>
                                <p>📍 {item['shops']['name']} - {item['shops']['location']}</p>
                            </div>
                            <div style='text-align: right;'>
                                <p class='price-tag'>UGX {item['price_ugx']:,}</p>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    st.markdown(f"[💬 WhatsApp Vendor](https://wa.me/{item['shops']['phone']})")
        else:
            st.error("No parts found. Try searching for a brand like 'Mercedes' or 'Hino'.")

# --- 2. MASTER ADMIN (Fully Powered Dashboard) ---
def render_admin_dashboard():
    st.markdown("---")
    st.title("🛡️ MASTER ADMIN CONTROL")
    st.warning("You are in GHOST MODE. This tab is hidden from all users.")
    
    shops = supabase.table("shops").select("*").order("name").execute().data
    
    # 1. Platform Statistics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Shops", len(shops))
    c2.metric("Revenue Goal", "15M UGX/mo")
    c3.metric("System Health", "ONLINE")

    # 2. Advanced Shop Management
    for s in shops:
        with st.expander(f"⚙️ Manage: {s['name']} ({s['location']})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Current Trial/Plan:**")
                new_plan = st.selectbox("Change Plan", ["Trial", "Basic", "Standard", "Premium"], index=["Trial", "Basic", "Standard", "Premium"].index(s['plan']), key=f"plan_{s['id']}")
                # ADJUST TRIAL DAYS FREELY
                current_expiry = datetime.strptime(s['expiry_date'], '%Y-%m-%d').date()
                new_expiry = st.date_input("Adjust Expiry Date", current_expiry, key=f"date_{s['id']}")
                
                if st.button("Update Access", key=f"upd_{s['id']}"):
                    supabase.table("shops").update({"plan": new_plan, "expiry_date": str(new_expiry)}).eq("id", s['id']).execute()
                    st.success("Access updated!")

            with col2:
                st.write("**Visibility Controls:**")
                if s['is_frozen']:
                    st.error("Shop is currently Hidden")
                    if st.button("ACTIVATE SHOP", key=f"unf_{s['id']}"):
                        supabase.table("shops").update({"is_frozen": False}).eq("id", s['id']).execute()
                        st.rerun()
                else:
                    st.success("Shop is Live")
                    if st.button("FREEZE (HIDE)", key=f"frz_{s['id']}"):
                        supabase.table("shops").update({"is_frozen": True}).eq("id", s['id']).execute()
                        st.rerun()

            with col3:
                st.write("**Critical Actions:**")
                st.text_area("Admin Notes", value=s.get('notes', ''), key=f"note_{s['id']}")
                if st.button("❌ DELETE SHOP", key=f"del_{s['id']}"):
                    supabase.table("shops").delete().eq("id", s['id']).execute()
                    st.rerun()

# --- 3. VENDOR PORTAL (Pricing Logic) ---
def render_vendor_portal():
    st.title("Vendor Hub")
    st.info("Pricing for Uganda Truck Marketplace (Capped at 1.5M/Year)")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("BASIC")
        st.write("1 Mo: 60k | 1 Yr: 600k")
    with c2:
        st.subheader("STANDARD")
        st.write("1 Mo: 100k | 1 Yr: 1.0M")
    with c3:
        st.subheader("PREMIUM")
        st.write("1 Mo: 150k | 1 Yr: 1.5M")

def render_directory():
    st.title("Shop Directory")
    res = supabase.table("shops").select("*").execute()
    for s in res.data:
        st.write(f"🏢 **{s['name']}** | {s['location']} | 📞 {s['phone']}")

if __name__ == "__main__":
    main()
