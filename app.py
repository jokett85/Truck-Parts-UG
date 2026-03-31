import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
from supabase import create_client, Client
from datetime import datetime, timezone, timedelta

# --- GLOBAL CONFIG & THEME ---
st.set_page_config(page_title="TruckParts UG | Executive Marketplace", page_icon="🚛", layout="wide")

# Database Connection
URL = "https://fasgqlvfmrdtlydelnni.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhc2dxbHZmbXJkdGx5ZGVsbm5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NDYyNzYsImV4cCI6MjA5MDEyMjI3Nn0.gxm--vdmUlxMaGH_r70sMrTxbt-MidtS8Vlse94pkDw"
SECRET_ADMIN_KEY = "UG-MASTER2026" 
supabase: Client = create_client(URL, KEY)

# --- CUSTOM CSS (INDUSTRIAL DARK THEME) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #0F172A; color: white; }
    .stApp { background-color: #0F172A; }
    
    /* Executive Cards */
    .part-card {
        background: #1E293B; border-radius: 15px; padding: 15px;
        border-bottom: 4px solid #F59E0B; margin-bottom: 20px; transition: 0.3s;
    }
    .part-card:hover { transform: translateY(-5px); background: #334155; }
    
    /* Branding */
    .brand-orange { color: #F59E0B; font-weight: 900; }
    .price-tag { color: #F59E0B; font-size: 1.6em; font-weight: 800; margin-top: 10px; }
    .stock-green { color: #10B981; font-weight: bold; }
    
    /* Navigation Sidebar */
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #374151; }
    .nav-btn { font-size: 1.2em !important; font-weight: 700 !important; }
    
    /* Buttons */
    .stButton>button {
        width: 100%; border-radius: 10px; height: 3.5em;
        background-color: #F59E0B; color: #000; font-weight: 700; border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'cart' not in st.session_state: st.session_state.cart = []
if 'page' not in st.session_state: st.session_state.page = "Catalog"
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False

# --- UTILITY FUNCTIONS ---
def format_ugx(amount):
    return f"UGX {amount:,.0f}"

def get_uganda_time():
    return datetime.now(timezone(timedelta(hours=3)))

def send_whatsapp(phone, message):
    encoded_msg = requests.utils.quote(message)
    return f"https://wa.me/{phone}?text={encoded_msg}"

# --- PAGE ROUTING ---
with st.sidebar:
    st.markdown("<h2 class='brand-orange'>🚛 TRUCK PARTS UG</h2>", unsafe_allow_html=True)
    st.caption("Genuine Parts | Kampala & Nationwide")
    st.write("---")
    
    if st.button("🔍 MARKET LOUNGE", key="nav_catalog"): st.session_state.page = "Catalog"
    if st.button("🏪 SHOP DIRECTORY", key="nav_dir"): st.session_state.page = "Directory"
    if st.button("🛒 MY CART (" + str(len(st.session_state.cart)) + ")", key="nav_cart"): st.session_state.page = "Cart"
    if st.button("🛠 VENDOR HUB", key="nav_vendor"): st.session_state.page = "Vendor"
    st.write("---")
    
    # Future Placeholder
    st.info("🤖 AI Recognition Coming Soon!")

# --- PAGE 1: CATALOG (MARKET LOUNGE) ---
def render_catalog():
    st.title("Market Lounge")
    
    # Advanced Search Bar (Ghost Admin Hidden Here)
    col_s, col_cam = st.columns([5, 1])
    with col_s:
        search_query = st.text_input("", placeholder="Search Part Number or Name...", label_visibility="collapsed")
    with col_cam:
        if st.button("📷"): st.toast("AI Photo recognition is in development!")
    
    if search_query == SECRET_ADMIN_KEY:
        st.session_state.admin_mode = True
        render_admin()
        return

    # Filters Sidebar
    with st.sidebar:
        st.markdown("### Filters")
        brand = st.selectbox("Truck Brand", ["All Brands", "Scania", "Volvo", "Mercedes Actros", "Hino", "Sinotruk", "Isuzu"])
        category = st.selectbox("Category", ["All", "Engine", "Brakes", "Suspension", "Tyres", "Electrical"])
        condition = st.multiselect("Condition", ["New OEM", "Alternative", "Used Japan Surplus"], default=["New OEM", "Alternative"])

    # Data Retrieval
    res = supabase.table("parts").select("*, shops(*)").execute()
    df = pd.DataFrame(res.data)
    
    if not df.empty:
        # Apply Logic Filters
        if search_query:
            df = df[df['name'].str.contains(search_query, case=False) | df['part_number'].str.contains(search_query, case=False)]
        if brand != "All Brands":
            df = df[df['brand'] == brand]
            
        # Display Grid
        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                st.markdown(f"""
                <div class='part-card'>
                    <img src="{row['image_url']}" style="width:100%; border-radius:10px; margin-bottom:10px;">
                    <h3 style="margin:0;">{row['name']}</h3>
                    <p style="font-size:0.9em; color:#94A3B8;">{row['brand']} | {row['condition']}</p>
                    <p class="stock-green">● {row['stock_status']}</p>
                    <p class="price-tag">{format_ugx(row['price_ugx'])}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Add to Cart", key=f"add_{row['id']}"):
                    st.session_state.cart.append(row.to_dict())
                    st.toast(f"Added {row['name']} to cart!")

# --- PAGE 2: SHOP DIRECTORY & "NEAR ME" ---
def render_directory():
    st.title("Shop Directory")
    
    col_map, col_list = st.columns([2, 1])
    
    # Geolocation "Near Me"
    user_location = st.text_input("Enter your current area (e.g. Kisenyi, Kampala)")
    
    shops_res = supabase.table("shops").select("*").execute()
    shops_df = pd.DataFrame(shops_res.data)
    
    with col_map:
        # Folium Map
        m = folium.Map(location=[0.3142, 32.5825], zoom_start=13, tiles="CartoDB dark_matter")
        for idx, shop in shops_df.iterrows():
            if shop['latitude'] and shop['longitude']:
                folium.Marker(
                    [shop['latitude'], shop['longitude']],
                    popup=shop['name'],
                    tooltip=shop['name'],
                    icon=folium.Icon(color="orange", icon="truck", prefix="fa")
                ).add_to(m)
        st_folium(m, width=700, height=450)

    with col_list:
        st.subheader("Verified Vendors")
        for idx, shop in shops_df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class='part-card'>
                    <h4 style="margin:0;">{shop['name']}</h4>
                    <p style="font-size:0.8em;">📍 {shop['location']}</p>
                    <p style="font-size:0.8em;">⭐ 4.8 (12 Reviews)</p>
                </div>
                """, unsafe_allow_html=True)
                wa_msg = f"Hello {shop['name']}, I found your shop on TruckPartsUG..."
                st.markdown(f"[💬 WhatsApp]({send_whatsapp(shop['phone'], wa_msg)})")

# --- PAGE 3: PERSISTENT CART ---
def render_cart():
    st.title("Your Shopping Cart")
    
    if not st.session_state.cart:
        st.warning("Your cart is empty. Visit the Market Lounge to find parts!")
        return

    cart_df = pd.DataFrame(st.session_state.cart)
    total = cart_df['price_ugx'].sum()
    
    for idx, item in cart_df.iterrows():
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"**{item['name']}** ({item['brand']})")
        c2.write(format_ugx(item['price_ugx']))
        if c3.button("Remove", key=f"rm_{idx}"):
            st.session_state.cart.pop(idx)
            st.rerun()
            
    st.write("---")
    st.header(f"Total: {format_ugx(total)}")
    
    if st.button("Generate WhatsApp Order"):
        order_details = "\\n".join([f"- {i['name']} ({i['brand']})" for i in st.session_state.cart])
        msg = f"Hello TruckPartsUG Admin, I want to order:\\n{order_details}\\nTotal: {format_ugx(total)}"
        st.markdown(f"[🚀 Send Order via WhatsApp]({send_whatsapp('256700000000', msg)})")

# --- PAGE 4: VENDOR & ADMIN (INTEGRATED) ---
def render_vendor():
    st.title("Vendor Hub")
    
    mode = st.radio("Select Action", ["Claim Listed Shop", "Register New Shop", "Post Part Request"])
    
    if mode == "Post Part Request":
        with st.form("request_form"):
            p_desc = st.text_area("What part are you looking for?")
            p_truck = st.text_input("Truck Model/Year")
            p_contact = st.text_input("Your WhatsApp Number")
            if st.form_submit_button("Post Request"):
                st.success("Request posted! Vendors will be notified.")
    else:
        st.info("Log in to manage your inventory, trial dates, and KYC documents.")

def render_admin():
    st.title("🛡️ MASTER SYSTEM ADMINISTRATION")
    st.write("Logged in as: Super Admin (Uganda Time: " + get_uganda_time().strftime('%H:%M') + ")")
    
    shops = supabase.table("shops").select("*").execute().data
    for s in shops:
        with st.expander(f"{s['name']} Control Panel"):
            c1, c2 = st.columns(2)
            c1.write(f"Current Plan: {s['plan']}")
            c1.date_input("Adjust Expiry", key=f"exp_{s['id']}")
            if c2.button("Toggle Verified", key=f"ver_{s['id']}"):
                st.toast(f"Status updated for {s['name']}")

# --- MAIN APP EXECUTION ---
if st.session_state.page == "Catalog": render_catalog()
elif st.session_state.page == "Directory": render_directory()
elif st.session_state.page == "Cart": render_cart()
elif st.session_state.page == "Vendor": render_vendor()

# --- FOOTER ---
st.write("---")
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.8em;">
    <p>Truck Parts UG | Kisekka Market & Industrial Area, Kampala</p>
    <p>Contact: +256 7xx xxx xxx | Email: info@truckpartsug.com</p>
    <p>© 2026 Genuine & Affordable Truck Spare Parts</p>
</div>
""", unsafe_allow_html=True)
