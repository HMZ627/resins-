import streamlit as st
import requests
import random
import datetime

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Resins Store Catalog",
    page_icon="💍",
    layout="wide"
)

# Your Verified Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = "8644129117:AAG3CJ4xJVteiTmwuImnTQz5PXWFvhfqPLs"
TELEGRAM_CHAT_ID = "6359572760"

# Product Inventory
PRODUCTS = [
    {
        "id": 1,
        "name": "Resin Ring",
        "category": "Jewellery",
        "description": "A visualization of beauty and aesthetics, along with the modern requirements of today's jewellery fashion. Colours can be customised.",
        "price": 500,
        "images": [
            "images/SaveClip.App_753224950_17897573046550553_9171311841910070315_n.jpg.webp",
            "images/SaveClip.App_729164572_17897573055550553_1935948774416209706_n.jpg.webp",
            "images/SaveClip.App_753604692_17897573067550553_3868263303187958583_n.jpg.webp"
        ]
    }
]

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def generate_order_number():
    """Generates a unique order ID."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    rand_id = random.randint(100, 999)
    return f"ORD-{timestamp}-{rand_id}"

def send_telegram_order(order_data):
    """Sends background order notifications directly to your Telegram chat."""
    message_text = (
        f"🛒 *NEW ORDER RECEIVED*\n"
        f"-------------------------------\n"
        f"*Order No:* `{order_data['order_no']}`\n"
        f"*Product:* {order_data['product_name']}\n"
        f"*Quantity:* {order_data['quantity']}\n"
        f"*Total Price:* PKR {order_data['total_price']:,}\n\n"
        f"👤 *CUSTOMER DETAILS*\n"
        f"*Name:* {order_data['customer_name']}\n"
        f"*Phone:* {order_data['customer_phone']}\n"
        f"*Address:* {order_data['customer_address']}\n"
        f"*Customization/Notes:* {order_data['customer_notes'] or 'None'}\n"
        f"-------------------------------"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(url, json=payload, timeout=5)
        return res.status_code == 200, res.text
    except Exception as e:
        return False, str(e)

def render_image_slider(product_id, image_paths):
    """Renders a single image frame with Next/Previous slider buttons."""
    key = f"img_idx_{product_id}"
    if key not in st.session_state:
        st.session_state[key] = 0

    current_idx = st.session_state[key]
    
    # Render Current Single Image
    try:
        st.image(image_paths[current_idx], use_container_width=True)
    except Exception:
        st.error(f"Image missing at path: {image_paths[current_idx]}")

    # Render Slider Controls below image if multiple images exist
    if len(image_paths) > 1:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("⬅️ Prev", key=f"prev_{product_id}"):
                st.session_state[key] = (current_idx - 1) % len(image_paths)
                st.rerun()
        with c2:
            st.caption(f"<div style='text-align:center;'>Image {current_idx + 1} of {len(image_paths)}</div>", unsafe_allow_html=True)
        with c3:
            if st.button("Next ➡️", key=f"next_{product_id}"):
                st.session_state[key] = (current_idx + 1) % len(image_paths)
                st.rerun()

# -----------------------------------------------------------------------------
# Main User Interface
# -----------------------------------------------------------------------------
st.title("🛍️ Resins Store Catalog")
st.write("Browse products and place orders instantly.")

# Sidebar Filters
st.sidebar.header("Filter Products")
categories = ["All"] + sorted(list(set(p["category"] for p in PRODUCTS)))
selected_category = st.sidebar.selectbox("Select Category", categories)

filtered_products = PRODUCTS if selected_category == "All" else [p for p in PRODUCTS if p["category"] == selected_category]

# Session State
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

cols = st.columns(3)
for idx, product in enumerate(filtered_products):
    col = cols[idx % 3]
    with col:
        # 1. Image Slider Frame
        render_image_slider(product["id"], product["images"])
            
        # 2. Product Name & Category
        st.subheader(product["name"])
        st.write(f"**Category:** {product['category']}")
        
        # 3. Product Description
        st.write(product["description"])
        
        # 4. Price & Order Button
        st.write(f"**Price:** PKR {product['price']:,}/-")
        if st.button("Order Now", key=f"btn_{product['id']}"):
            st.session_state.selected_product = product

# Order Modal Dialog
if st.session_state.selected_product is not None:
    prod = st.session_state.selected_product
    
    @st.dialog(f"Order: {prod['name']}")
    def show_order_modal():
        render_image_slider(f"modal_{prod['id']}", prod["images"])
            
        st.subheader(prod["name"])
        st.write(f"**Category:** {prod['category']}")
        st.write(f"**Description:** {prod['description']}")
        st.write(f"**Price per item:** PKR {prod['price']:,}/-")
        
        st.divider()
        
        with st.form("checkout_form"):
            quantity = st.number_input("Quantity", min_value=1, max_value=50, value=1)
            total_price = quantity * prod["price"]
            st.info(f"Total Amount: **PKR {total_price:,}/-**")
            
            customer_name = st.text_input("Full Name *")
            customer_phone = st.text_input("Phone Number *")
            customer_address = st.text_area("Delivery Address *")
            customer_notes = st.text_area("Color Customization / Special Instructions (Optional)")
            
            submitted = st.form_submit_button("Submit Order")
            
            if submitted:
                if not customer_name.strip() or not customer_phone.strip() or not customer_address.strip():
                    st.error("Please fill in all required fields marked with *.")
                else:
                    order_data = {
                        "order_no": generate_order_number(),
                        "product_name": prod["name"],
                        "quantity": quantity,
                        "total_price": total_price,
                        "customer_name": customer_name,
                        "customer_phone": customer_phone,
                        "customer_address": customer_address,
                        "customer_notes": customer_notes
                    }
                    
                    with st.spinner("Processing order..."):
                        success, result = send_telegram_order(order_data)
                    
                    if success:
                        st.success(f"🎉 Thank you, {customer_name}! Your order #{order_data['order_no']} has been placed successfully.")
                        st.balloons()
                    else:
                        st.error(f"Failed to deliver order message to Telegram. Error: {result}")

        if st.button("Close"):
            st.session_state.selected_product = None
            st.rerun()

    show_order_modal()
