import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from supabase import create_client, Client
from datetime import datetime, timezone, timedelta

# --- 1. GLOBAL CONFIG & THEME ---
st.set_page_config(page_title="TruckParts UG | Executive Marketplace", page_icon="🚛", layout="wide")

# --- 2. DATABASE CONNECTION (Ensure these are your actual keys) ---
URL = "https://fasgqlvfmrdtlydelnni.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhc2dxbHZmbXJkdGx5ZGVsbm5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NDYyNzYsImV4cCI6MjA5MDEyMjI3Nn0.gxm--vdmUlxMaGH_r70sMrTxbt-MidtS8Vlse94pkDw"
SECRET_ADMIN_KEY = "UG-MASTER2026" 
supabase: Client = create_client(URL, KEY)

# --- 3. CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0F172A; color: white; }
    .part-card {
        background: #1E293B; border-radius: 15px; padding: 15px;
        border-bottom: 4px solid #F59E0B; margin-bottom: 20px;
    }
    .price-tag { color: #F59E0B; font-size: 1.4em; font-weight: 800; }
    .stButton>button {
        width: 100%; border-radius: 10px; background-color: #F59E0B; color: #000; font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. SESSION STATE ---
if 'cart' not in st.session_state: st.session_state.cart = []
if 'page' not in st.session_state: st.session_state.page = "Catalog"

# --- 5. UTILITIES ---
def format_ugx(amount):
    return f"UGX {amount:,.0f}"

# --- 6. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='color: #F59E0B;'>🚛 TRUCK PARTS UG</h2>", unsafe_allow_html=True)
    if st.button("🔍 MARKET LOUNGE"): st.session_state.page = "Catalog"
    if st.button("🏪 SHOP DIRECTORY"): st.session_state.page = "Directory"
    if st.button("🛒 MY CART (" + str(len(st.session_state.cart)) + ")"): st.session_state.page = "Cart"
    if st.button("🛠 VENDOR HUB"): st.session_state.page = "Vendor"

# --- PAGE 1: CATALOG (THE FIXED FUNCTION) ---
def render_catalog():
    st.title("Market Lounge")
    
    col_s, col_cam = st.columns([5, 1])
    with col_s:
        search_query = st.text_input("", placeholder="Search Part Number or Name...", label_visibility="collapsed")
    with col_cam:
        st.button("📷")
    
    # Secret Admin Entry
    if search_query == SECRET_ADMIN_KEY:
        render_admin()
        return

    # Database Query
    res = supabase.table("parts").select("*, shops(*)").execute()
    
    if res.data:
        df = pd.DataFrame(res.data)
        
        # Apply Search Filter
        if search_query:
            df = df[df['name'].str.contains(search_query, case=False) | df['part_number'].str.contains(search_query, case=False)]

        if not df.empty:
            cols = st.columns(3)
            for idx, row in df.reset_index().iterrows():
                # --- THE FIX FOR THE ERROR ---
                # This line checks if image_url exists. If not, it uses a placeholder.
                img = row.get('image_url') if row.get('image_url') else "https://images.unsplash.com/photo-1580698543091-88c76b323ff1?w=300"
                
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class='part-card'>
                        <img src="{img}" style="width:100%; border-radius:10px; margin-bottom:10px;">
                        <h3>{row['name']}</h3>
                        <p style="color:#94A3B8;">No: {row['part_number']}</p>
                        <p class="price-tag">{format_ugx(row['price_ugx'])}</p>
                        <p style="color:#10B981;">📍 {row['shops']['name']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Add to Cart", key=f"add_{row['id']}"):
                        st.session_state.cart.append(row.to_dict())
                        st.toast("Added to cart!")
    else:
        st.info("No parts found in the database.")

# --- PAGE 2: DIRECTORY ---
def render_directory():
    st.title("Shop Directory")
    shops = supabase.table("shops").select("*").execute().data
    for s in shops:
        with st.container():
            st.markdown(f"<div class='part-card'><h3>{s['name']}</h3><p>📍 {s['location']}</p></div>", unsafe_allow_html=True)

# --- PAGE 3: CART ---
def render_cart():
    st.title("Your Shopping Cart")
    if not st.session_state.cart:
        st.write("Your cart is empty.")
    else:
        for item in st.session_state.cart:
            st.write(f"✅ {item['name']} - {format_ugx(item['price_ugx'])}")
        if st.button("Clear Cart"):
            st.session_state.cart = []
            st.rerun()

# --- PAGE 4: VENDOR ---
def render_vendor():
    st.title("Vendor Hub")
    st.write("Please log in to manage your shop.")

# --- HIDDEN ADMIN ---
def render_admin():
    st.title("🛡️ MASTER ADMIN")
    st.write("System Controls Active")

# --- MAIN ROUTER ---
if st.session_state.page == "Catalog": render_catalog()
elif st.session_state.page == "Directory": render_directory()
elif st.session_state.page == "Cart": render_cart()
elif st.session_state.page == "Vendor": render_vendor()
