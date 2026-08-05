import streamlit as st
import streamlit.components.v1 as components
import requests
import random
import datetime
import base64
import os

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
    payment_info = f"*Payment Method:* {order_data['payment_method']}"
    if order_data['payment_method'] == "Online Payment":
        payment_info += f"\n*Transaction ID / Reference:* `{order_data['transaction_id']}`"

    message_text = (
        f"🛒 *NEW ORDER RECEIVED*\n"
        f"-------------------------------\n"
        f"*Order No:* `{order_data['order_no']}`\n"
        f"*Product:* {order_data['product_name']}\n"
        f"*Quantity:* {order_data['quantity']}\n"
        f"*Total Price:* PKR {order_data['total_price']:,}\n\n"
        f"💳 *PAYMENT INFO*\n"
        f"{payment_info}\n\n"
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

def trigger_side_party_poppers():
    """Fires subtle party popper confetti from the screen sides instead of full balloons."""
    confetti_html = """
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <script>
        var count = 200;
        var defaults = { origin: { y: 0.7 } };

        function fire(particleRatio, opts) {
          confetti(Object.assign({}, defaults, opts, {
            particleCount: Math.floor(count * particleRatio)
          }));
        }

        // Left popper
        fire(0.25, { spread: 26, startVelocity: 55, origin: { x: 0, y: 0.8 } });
        fire(0.2, { spread: 60, origin: { x: 0, y: 0.8 } });
        
        # Right popper
        fire(0.25, { spread: 26, startVelocity: 55, origin: { x: 1, y: 0.8 } });
        fire(0.2, { spread: 60, origin: { x: 1, y: 0.8 } });
    </script>
    """
    components.html(confetti_html, height=0, width=0)

def get_base64_image(image_path):
    """Converts local image to base64 so it can render safely inside HTML components."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
            return f"data:image/webp;base64,{encoded}"
    return None

def render_touch_carousel(image_paths, height=350):
    """Renders a pure touch/swipe horizontal carousel without buttons."""
    img_html_elements = []
    
    for path in image_paths:
        b64_str = get_base64_image(path)
        if b64_str:
            img_html_elements.append(
                f'<div style="min-width: 100%; scroll-snap-align: start; flex-shrink: 0;">'
                f'<img src="{b64_str}" style="width: 100%; height: {height}px; object-fit: cover; border-radius: 10px;">'
                f'</div>'
            )

    if not img_html_elements:
        st.error("Images could not be loaded. Please verify files exist in the 'images/' folder.")
        return

    carousel_html = f"""
    <div style="
        display: flex;
        overflow-x: auto;
        scroll-snap-type: x mandatory;
        gap: 0px;
        border-radius: 10px;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
    ">
        {''.join(img_html_elements)}
    </div>
    <style>
        ::-webkit-scrollbar {{ display: none; }}
    </style>
    """
    components.html(carousel_html, height=height + 10)

# -----------------------------------------------------------------------------
# Main User Interface
# -----------------------------------------------------------------------------
st.title("🛍️ Resins Store Catalog")
st.write("Browse products and place orders instantly.")

# Sidebar Filters & Developer Info
st.sidebar.header("Filter Products")
categories = ["All"] + sorted(list(set(p["category"] for p in PRODUCTS)))
selected_category = st.sidebar.selectbox("Select Category", categories)

st.sidebar.divider()
st.sidebar.caption("**Web Developer:** 0314-4012872")

filtered_products = PRODUCTS if selected_category == "All" else [p for p in PRODUCTS if p["category"] == selected_category]

# Session State
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

cols = st.columns(3)
for idx, product in enumerate(filtered_products):
    col = cols[idx % 3]
    with col:
        # 1. Touch Carousel
        render_touch_carousel(product["images"], height=320)
            
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
        render_touch_carousel(prod["images"], height=280)
            
        st.subheader(prod["name"])
        st.write(f"**Category:** {prod['category']}")
        st.write(f"**Description:** {prod['description']}")
        st.write(f"**Price per item:** PKR {prod['price']:,}/-")
        
        st.divider()
        
        # 1. Quantity Input (Live Total Update)
        quantity = st.number_input(
            "Quantity", 
            min_value=1, 
            max_value=50, 
            value=1, 
            key=f"qty_input_{prod['id']}"
        )
        
        # 2. Total Amount Badge
        total_price = quantity * prod["price"]
        st.info(f"Total Amount: **PKR {total_price:,}/-**")
        
        st.write("### Payment Method")
        payment_method = st.radio(
            "Select Payment Option *",
            ["Online Payment", "COD (Cash on Delivery)"],
            key=f"payment_radio_{prod['id']}"
        )

        if payment_method == "Online Payment":
            st.success(
                " **JazzCash Payment Details**\n\n"
                "• **Account Number:** `0305-8866692`\n\n"
                "• **Account Name:** Rimsha Fatima\n\n"
                "Please send the total amount to the JazzCash account above and enter your transaction ID (TID) below."
            )

        st.divider()
        
        # 3. Customer Information & Checkout Form
        with st.form("checkout_form"):
            transaction_id = ""
            if payment_method == "Online Payment":
                transaction_id = st.text_input("Transaction ID (TID) / Reference Number *")
            
            customer_name = st.text_input("Full Name *")
            customer_phone = st.text_input("Phone Number *")
            customer_address = st.text_area("Delivery Address *")
            customer_notes = st.text_area("Color Customization / Special Instructions (Optional)")
            
            submitted = st.form_submit_button("Submit Order")
            
            if submitted:
                # Validation rules
                missing_fields = []
                if not customer_name.strip():
                    missing_fields.append("Full Name")
                if not customer_phone.strip():
                    missing_fields.append("Phone Number")
                if not customer_address.strip():
                    missing_fields.append("Delivery Address")
                if payment_method == "Online Payment" and not transaction_id.strip():
                    missing_fields.append("Transaction ID (TID)")

                if missing_fields:
                    st.error(f"Please fill in all required fields: {', '.join(missing_fields)}.")
                else:
                    order_data = {
                        "order_no": generate_order_number(),
                        "product_name": prod["name"],
                        "quantity": quantity,
                        "total_price": total_price,
                        "payment_method": payment_method,
                        "transaction_id": transaction_id,
                        "customer_name": customer_name,
                        "customer_phone": customer_phone,
                        "customer_address": customer_address,
                        "customer_notes": customer_notes
                    }
                    
                    with st.spinner("Processing order..."):
                        success, result = send_telegram_order(order_data)
                    
                    if success:
                        st.success(f"🎉 Thank you, {customer_name}! Your order #{order_data['order_no']} has been placed successfully.")
                        trigger_side_party_poppers()
                    else:
                        st.error(f"Failed to deliver order message to Telegram. Error: {result}")

        # Contact Notice with Direct WhatsApp Link at the bottom
        st.markdown(
            "💬 *For further order details, contact on "
            "[+92 305-8866692](https://wa.me/923058866692) through WhatsApp.*"
        )
        
        if st.button("Close"):
            st.session_state.selected_product = None
            st.rerun()

    show_order_modal()

# Footer Developer Information
st.divider()
st.caption("Web Developer: 0314-4012872")
