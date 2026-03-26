import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- DATABASE CONNECTION ---
# Replace these with your actual Supabase URL and Key
URL = "YOUR_SUPABASE_URL" 
KEY = "YOUR_SUPABASE_KEY"
supabase: Client = create_client(URL, KEY)

def main():
    st.set_page_config(page_title="TruckParts UG", layout="wide")
    
    # Custom Styling for Mobile (High Contrast)
    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; 
        background-color: #FF8C00; color: white; font-weight: bold; font-size: 1.2em; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🚛 TruckParts UG")
    st.caption("One-Stop Heavy Truck Spare Parts Marketplace")

    menu = ["🔍 Find Parts", "🏪 Shop Directory", "🛠 Vendor Dashboard"]
    choice = st.sidebar.selectbox("Main Menu", menu)

    if choice == "🔍 Find Parts":
        st.subheader("Search Spare Parts")
        cam_input = st.camera_input("Scan Part (AI Mode)")
        query = st.text_input("Enter Part Name or Number (e.g. 16400)")

        if query:
            res = supabase.table("parts").select("*, shops(name, phone, location)").ilike("part_number", f"%{query}%").execute()
            items = res.data
            if items:
                for item in items:
                    with st.container():
                        st.write(f"### {item['name']}")
                        st.write(f"**No:** {item['part_number']} | **Brand:** {item['brand']}")
                        st.write(f"📍 **Shop:** {item['shops']['name']} ({item['shops']['location']})")
                        st.write(f"## UGX {item['price_ugx']:,}")
                        st.markdown(f"[💬 WhatsApp Vendor](https://wa.me/{item['shops']['phone']})")
                        st.divider()
            else:
                st.warning("No matches found. Try searching 'Radiator' or '16400'.")

    elif choice == "🏪 Shop Directory":
        st.subheader("Verified Shops")
        res = supabase.table("shops").select("*").execute()
        for shop in res.data:
            with st.expander(f"{shop['name']} - {shop['location']}"):
                st.write(f"Status: {shop['status']}")
                st.write(f"Contact: {shop['phone']}")

    elif choice == "🛠 Vendor Dashboard":
        st.subheader("Vendor Management")
        st.warning("30-Day Free Trial: 29 Days Remaining")
        with st.form("add_part"):
            p_name = st.text_input("Part Name")
            p_num = st.text_input("Part Number")
            p_brand = st.selectbox("Brand", ["Hino", "Scania", "Mercedes", "Isuzu"])
            p_price = st.number_input("Price (UGX)", step=1000)
            if st.form_submit_button("List Part Now"):
                data = {"name": p_name, "part_number": p_num, "brand": p_brand, "price_ugx": p_price, "shop_id": 1}
                supabase.table("parts").insert(data).execute()
                st.success("Success! Your part is now live.")

if __name__ == '__main__':
    main()
