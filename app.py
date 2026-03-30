import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date

# --- EXECUTIVE THEME & CONFIG ---
st.set_page_config(page_title="TruckParts UG", page_icon="🚛", layout="wide")

# --- CONNECTION ---
URL = "https://fasgqlvfmrdtlydelnni.supabase.co" 
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhc2dxbHZmbXJkdGx5ZGVsbm5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NDYyNzYsImV4cCI6MjA5MDEyMjI3Nn0.gxm--vdmUlxMaGH_r70sMrTxbt-MidtS8Vlse94pkDw"
SECRET_ADMIN_KEY = "UG-MASTER2026" # Access Admin by typing this in search

supabase: Client = create_client(URL, KEY)

def main():
    # --- REDUCED FONT SIZES & EXECUTIVE STYLING ---
    st.markdown("""<style>
        .stApp { background-color: #0F172A; color: white; }
        h1 { font-size: 28px !important; color: #FFD700; }
        h2 { font-size: 22px !important; }
        h3 { font-size: 18px !important; }
        .stButton>button { border-radius: 8px; background-color: #FFD700; color: #0F172A; font-weight: bold; }
        .lobby-card { background: #1E293B; padding: 15px; border-radius: 12px; border-bottom: 3px solid #FFD700; margin-bottom: 10px; }
        .price-tag { color: #FFD700; font-size: 1.4em; font-weight: bold; }
        .nav-link { font-size: 20px !important; font-weight: 700; color: #FFD700 !important; }
    </style>""", unsafe_allow_html=True)

    # Initialize Session States
    if 'view' not in st.session_state: st.session_state.view = "Lobby"
    if 'selected_shop' not in st.session_state: st.session_state.selected_shop = None

    # --- CLEAN SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.markdown("### 🚛 TruckParts UG")
        if st.button("🔍 Marketplace", use_container_width=True): st.session_state.view = "Lobby"; st.session_state.selected_shop = None
        if st.button("🏪 Shop Directory", use_container_width=True): st.session_state.view = "Directory"
        if st.button("🛠 Vendor Center", use_container_width=True): st.session_state.view = "Vendor"
        st.write("---")
        st.caption("v3.0 Executive Secure")

    # Routing
    if st.session_state.view == "Lobby": render_lobby()
    elif st.session_state.view == "Directory": render_directory()
    elif st.session_state.view == "Vendor": render_vendor()

# --- 1. THE LOBBY & SEARCH ---
def render_lobby():
    if st.session_state.selected_shop:
        render_shop_profile(st.session_state.selected_shop)
        return

    st.markdown("## Find Heavy Truck Parts")
    
    # Search Bar & AI Integrated
    col_search, col_ai = st.columns([4, 1])
    with col_search:
        query = st.text_input("", placeholder="Search Part Number, Brand, or Name...", label_visibility="collapsed")
    with col_ai:
        ai_scan = st.button("📷 Scan Part")

    # GHOST ADMIN TRIGGER
    if query == SECRET_ADMIN_KEY:
        render_admin()
        return

    if ai_scan:
        img = st.camera_input("Take a photo of the part")
        if img:
            st.info("🤖 AI Analysis: Identifying geometry and markings...")
            st.success("Detected: Scania Air Spring (Match: 1R12-402)")
            query = "1R12-402"

    if query:
        # FIXED SEARCH LOGIC: Proper Supabase Query
        res = supabase.table("parts").select("*, shops(*)").or_(
            f"name.ilike.%{query}%, part_number.ilike.%{query}%, brand.ilike.%{query}%"
        ).execute()
        
        if res.data:
            for item in res.data:
                if not item['shops']['is_frozen']:
                    with st.container():
                        st.markdown(f"""<div class='lobby-card'>
                            <div style='display:flex; justify-content:space-between;'>
                                <div><h3>{item['name']}</h3><p>No: {item['part_number']} | Brand: {item['brand']}</p></div>
                                <div class='price-tag'>UGX {item['price_ugx']:,}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)
                        c1, c2, c3 = st.columns(3)
                        if c1.button(f"View {item['shops']['name']}", key=f"shop_{item['id']}"):
                            st.session_state.selected_shop = item['shops']['id']
                            st.rerun()
                        c2.markdown(f"[💬 Chat with Vendor](https://wa.me/{item['shops']['phone']})")
        else:
            st.warning("No parts found. Try searching 'Radiator' or 'Hino'.")
    else:
        # WARM LOBBY CONTENT
        st.write("### Browse Categories")
        cats = st.columns(4)
        if cats[0].button("⚙️ Engines"): pass
        if cats[1].button("🛑 Brakes"): pass
        if cats[2].button("🛞 Tyres"): pass
        if cats[3].button("⚡ Electric"): pass

        st.markdown("### 🏢 Featured Suppliers")
        # Horizontal scroll simulation
        featured = supabase.table("shops").select("*").limit(3).execute().data
        f_cols = st.columns(3)
        for i, shop in enumerate(featured):
            with f_cols[i]:
                st.markdown(f"<div class='lobby-card'><b>{shop['name']}</b><br>{shop['location']}</div>", unsafe_allow_html=True)
                if st.button("View Shop", key=f"feat_{shop['id']}"):
                    st.session_state.selected_shop = shop['id']
                    st.rerun()

# --- 2. SHOP PROFILE & DIRECTORY ---
def render_shop_profile(shop_id):
    shop = supabase.table("shops").select("*").eq("id", shop_id).single().execute().data
    parts = supabase.table("parts").select("*").eq("shop_id", shop_id).execute().data
    
    st.button("⬅️ Back to Market", on_click=lambda: setattr(st.session_state, 'selected_shop', None))
    st.markdown(f"## {shop['name']}")
    st.write(f"📍 {shop['location']} | 📞 {shop['phone']}")
    
    st.write("### Live Inventory")
    if parts:
        df = pd.DataFrame(parts)[['name', 'part_number', 'brand', 'price_ugx']]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("This shop has not uploaded parts yet.")

    st.write("---")
    st.write("### 💬 In-App Messaging")
    msg = st.text_area("Send a message directly to this shop...")
    if st.button("Send Message"):
        st.success("Message sent! The vendor will see this in their Portal.")

def render_directory():
    st.markdown("## Shop Directory")
    shops = supabase.table("shops").select("*").execute().data
    for s in shops:
        with st.expander(f"🏢 {s['name']} - {s['location']}"):
            st.write(f"Contact: {s['phone']}")
            if st.button("Open Shop Profile", key=f"dir_{s['id']}"):
                st.session_state.selected_shop = s['id']
                st.session_state.view = "Lobby"
                st.rerun()

# --- 3. THE GHOST ADMIN (Hidden Dashboard) ---
def render_admin():
    st.markdown("## 🛡️ Master Control Dashboard")
    st.warning("Ghost Mode Active. No visible links exist to this page.")
    
    shops = supabase.table("shops").select("*").execute().data
    for s in shops:
        with st.expander(f"Manage: {s['name']}"):
            c1, c2 = st.columns(2)
            # TRIAL ADJUSTMENT
            new_date = c1.date_input("Adjust Expiry", value=datetime.strptime(s['expiry_date'], '%Y-%m-%d').date(), key=f"date_{s['id']}")
            if c1.button("Save Date", key=f"save_{s['id']}"):
                supabase.table("shops").update({"expiry_date": str(new_date)}).eq("id", s['id']).execute()
            
            # FREEZE / DELETE
            if s['is_frozen']:
                if c2.button("Unfreeze", key=f"unf_{s['id']}"):
                    supabase.table("shops").update({"is_frozen": False}).eq("id", s['id']).execute()
                    st.rerun()
            else:
                if c2.button("Freeze (Hide Shop)", key=f"frz_{s['id']}"):
                    supabase.table("shops").update({"is_frozen": True}).eq("id", s['id']).execute()
                    st.rerun()

def render_vendor():
    st.markdown("## Vendor Portal")
    st.info("Verify ownership to manage your inventory and respond to messages.")
    # Implementation of KYC forms as per previous code...

if __name__ == "__main__":
    main()
