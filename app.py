import streamlit as st
import streamlit.components.v1 as components
import requests
import random
import datetime
import base64
import os

# -----------------------------------------------------------------------------
# Configuration & Global Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Resins Store Catalog",
    page_icon="❤️",
    layout="wide"
)

st.markdown("""
<style>
    #MainMenu, footer, [data-testid="stStatusWidget"], [data-testid="manage-app-button"],
    .stDeployButton, [data-testid="stDecoration"], [data-testid="stHeaderActionElements"] {
        display: none !important;
        visibility: hidden !important;
    }
    header[data-testid="stHeader"] { background: transparent !important; z-index: 99990 !important; }
    [data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"], header[data-testid="stHeader"] button {
        display: flex !important; visibility: visible !important; opacity: 1 !important;
        color: #ffffff !important; background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(8px) !important; border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important; z-index: 99999 !important; margin-left: 8px !important; margin-top: 4px !important;
    }
    [data-testid="stSidebarCollapseButton"] svg, [data-testid="collapsedControl"] svg, header[data-testid="stHeader"] button svg {
        fill: #ffffff !important; stroke: #ffffff !important; color: #ffffff !important;
    }
    [data-testid="stAppViewContainer"] { background: transparent !important; }
    [data-testid="stAppViewContainer"]::before {
        content: ""; position: fixed; top: -50%; left: -50%; width: 200%; height: 200%; z-index: -99999;
        background: linear-gradient(135deg, #1a000d 0%, #5a0022 20%, #990033 40%, #2b021d 60%, #800020 80%, #4a001e 100%);
        animation: diagonalMove 12s linear infinite alternate; pointer-events: none;
    }
    @keyframes diagonalMove { 0% { transform: translate(0, 0); } 100% { transform: translate(-25%, -25%); } }
    .stApp { background: transparent !important; color: #ffffff !important; }
    div[data-testid="stVerticalBlock"] > div[style*="flex"] {
        background: rgba(255, 255, 255, 0.07) !important; backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important; border-radius: 16px !important; padding: 1rem !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }
    .stButton > button {
        background: rgba(255, 255, 255, 0.12) !important; backdrop-filter: blur(10px) !important;
        color: #ffffff !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; border-radius: 12px !important;
        font-weight: 600 !important; transition: all 0.3s ease !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.25) !important; border-color: rgba(255, 255, 255, 0.5) !important;
        transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(233, 30, 99, 0.4) !important;
    }
    section[data-testid="stSidebar"] {
        background: rgba(30, 0, 15, 0.85) !important; backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    div[role="dialog"] {
        background: rgba(35, 2, 20, 0.85) !important; backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important; border-radius: 20px !important; color: #ffffff !important;
    }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.08) !important; border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important; border-radius: 10px !important;
    }
    div[data-testid="stFeedback"] button { transform: scale(1.3); margin-right: 8px; }
    .scroll-target { opacity: 0; transform: translateY(40px); transition: opacity 0.8s cubic-bezier(0.25, 1, 0.5, 1), transform 0.8s cubic-bezier(0.25, 1, 0.5, 1); will-change: opacity, transform; }
    .scroll-target.in-view { opacity: 1; transform: translateY(0px); }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Confidential Discord Webhook Configuration (Loaded via Secrets)
# -----------------------------------------------------------------------------
DISCORD_WEBHOOK_URL = st.secrets.get("DISCORD_WEBHOOK_URL", "")

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
    },
    {
        "id": 2,
        "name": "Black Marble & Gold Dust Resin Clock (Handmade)",
        "category": "Home Decor",
        "description": "Made with love, using the best quality resins and materials, by (ResinsbyR), the handcrafted masterpiece of ours, brings royalty and an attractive look to your wall, enhancing the overall outlook of the room.",
        "price": 5000,
        "images": [
            "images/IMG-20260808-WA0077.jpg",
            "images/IMG-20260808-WA0078.jpg"
        ]
    },
    {
        "id": 3,
        "name": "Resin Shield (6-inches)",
        "category": "Resin shields",
        "description": "Resins shield, made with absolute precision and care, text can be written of your choice. Holds your kind love for your own loved ones.\nAdding picture will cost PKR 100/-",
        "price": 2300,
        "images": [
            "images/shield1.jpg",
            "images/shield2.jpg",
            "images/shield3.jpg"
        ]
    }
]

# -----------------------------------------------------------------------------
# Helper Functions for Discord Integration
# -----------------------------------------------------------------------------
def generate_order_number():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    rand_id = random.randint(100, 999)
    return f"ORD-{timestamp}-{rand_id}"

def send_discord_message(content=None, embed=None, uploaded_files=None):
    if not DISCORD_WEBHOOK_URL:
        return False, "Discord Webhook URL is missing from Streamlit secrets."

    payload = {}
    if content:
        payload["content"] = content
    if embed:
        payload["embeds"] = [embed]

    files_dict = {}
    if uploaded_files:
        for idx, f in enumerate(uploaded_files):
            f.seek(0)
            files_dict[f"file{idx}"] = (f.name, f.getvalue(), f.type)

    try:
        if files_dict:
            res = requests.post(DISCORD_WEBHOOK_URL, data={"payload_json": requests.compat.json.dumps(payload)}, files=files_dict, timeout=10)
        else:
            res = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        
        if res.status_code in [200, 204]:
            return True, "Success"
        else:
            return False, f"Discord HTTP Error: {res.status_code} - {res.text}"
    except Exception as e:
        return False, str(e)

def send_discord_order(order_data, uploaded_files=None):
    add_pic_str = "Yes (+PKR 100/-)" if order_data.get('add_pictures') else "No"
    
    embed = {
        "title": f"🛒 New Order: {order_data['order_no']}",
        "color": 0xE91E63,
        "fields": [
            {"name": "Product", "value": order_data['product_name'], "inline": True},
            {"name": "Quantity", "value": str(order_data['quantity']), "inline": True},
            {"name": "Picture Customization", "value": add_pic_str, "inline": True},
            {"name": "Total Price", "value": f"PKR {order_data['total_price']:,}/-", "inline": True},
            {"name": "Transaction ID (TID)", "value": f"`{order_data['transaction_id']}`", "inline": True},
            {"name": "Customer Name", "value": order_data['customer_name'], "inline": False},
            {"name": "Phone Number", "value": order_data['customer_phone'], "inline": True},
            {"name": "Delivery Address", "value": order_data['customer_address'], "inline": False},
            {"name": "Customization / Notes", "value": order_data['customer_notes'] or "None", "inline": False}
        ],
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    return send_discord_message(embed=embed, uploaded_files=uploaded_files)

def trigger_side_party_poppers():
    confetti_html = """
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <script>
        var count = 200;
        var defaults = { origin: { y: 0.7 } };
        function fire(particleRatio, opts) {
          confetti(Object.assign({}, defaults, opts, { particleCount: Math.floor(count * particleRatio) }));
        }
        fire(0.25, { spread: 26, startVelocity: 55, origin: { x: 0, y: 0.8 } });
        fire(0.2, { spread: 60, origin: { x: 0, y: 0.8 } });
        fire(0.25, { spread: 26, startVelocity: 55, origin: { x: 1, y: 0.8 } });
        fire(0.2, { spread: 60, origin: { x: 1, y: 0.8 } });
    </script>
    """
    components.html(confetti_html, height=0, width=0)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
            return f"data:image/webp;base64,{encoded}"
    return None

def render_auto_sliding_carousel(image_paths, height=350, interval_sec=4):
    img_html_elements = []
    for idx, path in enumerate(image_paths):
        b64_str = get_base64_image(path)
        if b64_str:
            active_class = " active" if idx == 0 else ""
            img_html_elements.append(
                f'<div class="slide{active_class}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; transition: opacity 1s ease-in-out; pointer-events: none; border-radius: 12px;">'
                f'<img src="{b64_str}" style="width: 100%; height: {height}px; object-fit: cover; border-radius: 12px;">'
                f'</div>'
            )

    if not img_html_elements:
        st.error("Images could not be loaded. Please verify files exist in the 'images/' folder.")
        return

    unique_id = f"carousel_{random.randint(1000, 9999)}"
    dots_html = "".join([f'<span class="dot{" active" if i == 0 else ""}" data-index="{i}" style="height: 10px; width: 10px; margin: 0 4px; background-color: rgba(255, 255, 255, 0.4); border-radius: 50%; display: inline-block; cursor: pointer; transition: all 0.3s ease;"></span>' for i in range(len(img_html_elements))])

    carousel_html = f"""
    <div id="{unique_id}_container" style="position: relative; width: 100%; height: {height}px; border-radius: 12px; overflow: hidden;">
        {''.join(img_html_elements)}
        <div style="position: absolute; bottom: 12px; width: 100%; display: flex; justify-content: center; align-items: center; z-index: 10;">
            {dots_html}
        </div>
    </div>
    <script>
        (function() {{
            const container = document.getElementById('{unique_id}_container');
            if (!container) return;
            const slides = container.getElementsByClassName('slide');
            const dots = container.getElementsByClassName('dot');
            let currentIndex = 0;
            function showSlide(index) {{
                for (let i = 0; i < slides.length; i++) {{
                    slides[i].classList.remove('active');
                    if (dots[i]) dots[i].classList.remove('active');
                }}
                currentIndex = index;
                slides[currentIndex].classList.add('active');
                if (dots[currentIndex]) dots[currentIndex].classList.add('active');
            }}
            setInterval(() => {{ showSlide((currentIndex + 1) % slides.length); }}, {interval_sec * 1000});
        }})();
    </script>
    """
    components.html(carousel_html, height=height + 10)

# Initialize Session State Variables for Dialog Management
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

if "pending_order_data" not in st.session_state:
    st.session_state.pending_order_data = None

if "pending_uploaded_files" not in st.session_state:
    st.session_state.pending_uploaded_files = None

# -----------------------------------------------------------------------------
# Dialog Windows
# -----------------------------------------------------------------------------

# Step 2: Order Confirmation Dialog
@st.dialog("Confirm Order?")
def show_confirmation_dialog():
    order_data = st.session_state.pending_order_data
    if not order_data:
        return

    st.write("Please review your order details before submitting:")
    st.markdown(f"""
    * **Product:** {order_data['product_name']}
    * **Quantity:** {order_data['quantity']}
    * **Total Amount:** PKR {order_data['total_price']:,}/-
    * **Transaction ID (TID):** `{order_data['transaction_id']}`
    * **Name:** {order_data['customer_name']}
    * **Phone:** {order_data['customer_phone']}
    * **Address:** {order_data['customer_address']}
    """)
    st.divider()

    col_confirm, col_cancel = st.columns(2)
    with col_confirm:
        if st.button("Confirm", use_container_width=True):
            with st.spinner("Sending order to Discord..."):
                success, result = send_discord_order(order_data, uploaded_files=st.session_state.pending_uploaded_files)
            
            if success:
                st.success(f"🎉 Thank you, {order_data['customer_name']}! Your order #{order_data['order_no']} has been placed successfully.")
                trigger_side_party_poppers()
            else:
                st.error(f"Failed to deliver order to Discord. Error: {result}")
            
            # Reset state
            st.session_state.pending_order_data = None
            st.session_state.pending_uploaded_files = None
            st.session_state.selected_product = None
            st.rerun()

    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.session_state.pending_order_data = None
            st.session_state.pending_uploaded_files = None
            st.rerun()

# Step 1: Product Selection & Order Modal
if st.session_state.selected_product is not None and st.session_state.pending_order_data is None:
    prod = st.session_state.selected_product
    
    @st.dialog(f"Order: {prod['name']}")
    def show_order_modal():
        render_auto_sliding_carousel(prod["images"], height=280, interval_sec=4)
        st.subheader(prod["name"])
        st.write(f"**Category:** {prod['category']}")
        st.write(f"**Description:** {prod['description']}")
        st.write(f"**Base Price:** PKR {prod['price']:,}/-")
        st.divider()
        
        quantity = st.number_input("Quantity", min_value=1, max_value=50, value=1, key=f"qty_input_{prod['id']}")
        
        add_pictures = False
        uploaded_photos = None
        picture_extra_cost = 0

        if prod["category"] == "Resin shields":
            add_pictures = st.checkbox("Add pictures (+ PKR 100/-)", key=f"pic_chk_{prod['id']}")
            if add_pictures:
                picture_extra_cost = 100
                uploaded_photos = st.file_uploader("➕ Upload pictures (Max 3)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key=f"shield_pics_{prod['id']}")
                if uploaded_photos and len(uploaded_photos) > 3:
                    st.warning("⚠️ Maximum 3 pictures allowed. Only the first 3 will be processed.")
                    uploaded_photos = uploaded_photos[:3]

        unit_price = prod["price"] + picture_extra_cost
        total_price = quantity * unit_price
        
        st.info(f"Total Amount: **PKR {total_price:,}/-**")
        st.write("### Payment Method")
        st.success("**JazzCash Payment Details**\n\n• **Account Number:** `0305-8866692`\n\n• **Account Name:** Rimsha Fatima\n\nPlease send the total amount to the JazzCash account above and enter your Transaction ID (TID) below.")
        st.divider()
        
        with st.form("checkout_form"):
            transaction_id = st.text_input("Transaction ID (TID) / Reference Number *")
            customer_name = st.text_input("Full Name *")
            customer_phone = st.text_input("Phone Number *")
            customer_address = st.text_area("Delivery Address *")
            customer_notes = st.text_area("Color Customization / Text Choice / Special Instructions (Optional)")
            
            submitted = st.form_submit_button("Submit Order")
            
            if submitted:
                missing_fields = []
                if not transaction_id.strip(): missing_fields.append("Transaction ID (TID)")
                if not customer_name.strip(): missing_fields.append("Full Name")
                if not customer_phone.strip(): missing_fields.append("Phone Number")
                if not customer_address.strip(): missing_fields.append("Delivery Address")
                if add_pictures and not uploaded_photos: missing_fields.append("Uploaded Pictures")

                if missing_fields:
                    st.error(f"Please fill in all required fields: {', '.join(missing_fields)}.")
                else:
                    st.session_state.pending_order_data = {
                        "order_no": generate_order_number(),
                        "product_name": prod["name"],
                        "quantity": quantity,
                        "add_pictures": add_pictures,
                        "total_price": total_price,
                        "transaction_id": transaction_id,
                        "customer_name": customer_name,
                        "customer_phone": customer_phone,
                        "customer_address": customer_address,
                        "customer_notes": customer_notes
                    }
                    st.session_state.pending_uploaded_files = uploaded_photos
                    st.rerun()

        if st.button("Close"):
            st.session_state.selected_product = None
            st.rerun()

    show_order_modal()

# Display confirmation dialog if an order is pending
if st.session_state.pending_order_data is not None:
    show_confirmation_dialog()

# -----------------------------------------------------------------------------
# Main User Interface
# -----------------------------------------------------------------------------
st.title("Resins By R")
st.write("Browse products and place orders instantly.")

# Sidebar Filters
st.sidebar.header("Filter Products")
categories = ["All"] + sorted(list(set(p["category"] for p in PRODUCTS)))
selected_category = st.sidebar.selectbox("Select Category", categories)
st.sidebar.divider()
st.sidebar.caption("**Web Developer:** 0314-4012872")

filtered_products = PRODUCTS if selected_category == "All" else [p for p in PRODUCTS if p["category"] == selected_category]

cols = st.columns(3)
for idx, product in enumerate(filtered_products):
    col = cols[idx % 3]
    with col:
        render_auto_sliding_carousel(product["images"], height=320, interval_sec=4.5)
        st.subheader(product["name"])
        st.write(f"**Category:** {product['category']}")
        st.write(product["description"])
        st.write(f"**Price:** PKR {product['price']:,}/-")
        if st.button("Order Now", key=f"btn_{product['id']}"):
            st.session_state.selected_product = product
            st.rerun()

# -----------------------------------------------------------------------------
# Reviews & Opinions
# -----------------------------------------------------------------------------
st.divider()
st.subheader("Leave a Review")
star_rating_index = st.feedback("stars")

with st.form("client_review_form"):
    review_text = st.text_area("How was your experience:", placeholder="Write your experience with Resins By R...")
    if st.form_submit_button("Submit Review"):
        if star_rating_index is None or not review_text.strip():
            st.error("Please fill in both the rating and review text.")
        else:
            rating_val = star_rating_index + 1
            embed = {
                "title": "⭐ New Client Review",
                "color": 0xFFD700,
                "fields": [
                    {"name": "Rating", "value": f"{rating_val} / 5 Stars", "inline": True},
                    {"name": "Experience", "value": review_text.strip(), "inline": False}
                ]
            }
            ok, err = send_discord_message(embed=embed)
            if ok:
                st.success("Thank you for submitting your review!")
            else:
                st.error(f"Error: {err}")

st.divider()
with st.form("client_opinion_form"):
    opinion_text = st.text_area("Your opinion:", placeholder="Share your suggestions...")
    if st.form_submit_button("Submit Opinion"):
        if not opinion_text.strip():
            st.error("Please enter your opinion.")
        else:
            embed = {
                "title": "💡 New Client Opinion",
                "color": 0x3498DB,
                "fields": [{"name": "Opinion", "value": opinion_text.strip(), "inline": False}]
            }
            ok, err = send_discord_message(embed=embed)
            if ok:
                st.success("Thank you for sharing your opinion!")
            else:
                st.error(f"Error: {err}")

st.caption("Web Developer: 0314-4012872")
