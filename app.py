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
    page_title="Resins-DreamByR",
    page_icon="❤️",
    layout="wide"
)

# 1. INTRO SPLASH ANIMATION (Injected directly into window.parent.document)
components.html("""
<script>
(function() {
    const parentDoc = window.parent.document;
    
    // Prevent duplicate splash injection on app rerun
    if (parentDoc.getElementById('splash-overlay-container')) return;

    // Inject CSS into top-level document head
    const styleEl = parentDoc.createElement('style');
    styleEl.innerHTML = `
        #splash-overlay-container {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            background: linear-gradient(135deg, #000206 0%, #150012 50%, #000206 100%) !important;
            z-index: 9999999 !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            overflow: hidden !important;
            animation: fadeOutSplash 0.8s ease-in-out forwards !important;
            animation-delay: 3.8s !important;
            pointer-events: all !important;
        }

        .droplet-wrapper {
            position: relative;
            width: 200px;
            height: 200px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .droplet {
            position: absolute;
            width: 45px;
            height: 45px;
            background: radial-gradient(circle at 30% 30%, #FF004B, #6EABF5, #CFE4FF);
            border-radius: 50% 50% 50% 0;
            box-shadow: 0 0 20px rgba(255, 0, 75, 0.8), inset -2px -2px 6px rgba(0,0,0,0.4);
        }

        .droplet-left {
            left: -300px;
            transform: rotate(-45deg);
            animation: mergeLeft 1.2s cubic-bezier(0.6, -0.28, 0.735, 0.045) forwards;
        }

        .droplet-right {
            right: -300px;
            transform: rotate(135deg);
            animation: mergeRight 1.2s cubic-bezier(0.6, -0.28, 0.735, 0.045) forwards;
        }

        .splash-ring {
            position: absolute;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            border: 4px solid #FF004B;
            opacity: 0;
            animation: splashExpand 0.6s ease-out forwards;
            animation-delay: 1.2s;
        }

        .logo-r {
            font-family: 'Playfair Display', 'Georgia', serif;
            font-size: 80px;
            font-weight: 900;
            color: #ffffff;
            text-shadow: 0 0 25px #FF004B, 0 0 50px #6EABF5;
            opacity: 0;
            transform: scale(0.2);
            animation: logoAppear 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            animation-delay: 1.35s;
        }

        .brand-title {
            font-family: 'Poppins', 'Segoe UI', sans-serif;
            font-size: 32px;
            font-weight: 700;
            letter-spacing: 4px;
            color: #ffffff;
            margin-top: 25px;
            opacity: 0;
            transform: translateY(20px);
            animation: titleSlideUp 0.8s ease-out forwards;
            animation-delay: 1.8s;
            text-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
        }

        @keyframes mergeLeft {
            0% { left: -300px; }
            100% { left: calc(50% - 22px); }
        }

        @keyframes mergeRight {
            0% { right: -300px; }
            100% { right: calc(50% - 22px); }
        }

        @keyframes splashExpand {
            0% { width: 10px; height: 10px; opacity: 1; border-width: 8px; }
            100% { width: 180px; height: 180px; opacity: 0; border-width: 1px; }
        }

        @keyframes logoAppear {
            0% { opacity: 0; transform: scale(0.2) rotate(-10deg); }
            100% { opacity: 1; transform: scale(1) rotate(0deg); }
        }

        @keyframes titleSlideUp {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeOutSplash {
            0% { opacity: 1; visibility: visible; }
            100% { opacity: 0; visibility: hidden; }
        }
    `;
    parentDoc.head.appendChild(styleEl);

    // Create Splash Overlay Element
    const splashDiv = parentDoc.createElement('div');
    splashDiv.id = 'splash-overlay-container';
    splashDiv.innerHTML = `
        <div class="droplet-wrapper">
            <div class="droplet droplet-left"></div>
            <div class="droplet droplet-right"></div>
            <div class="splash-ring"></div>
            <div class="logo-r">R</div>
        </div>
        <div class="brand-title">Resins by R</div>
    `;
    parentDoc.body.appendChild(splashDiv);

    // Auto cleanup from DOM after animation completes
    setTimeout(() => {
        if (splashDiv) splashDiv.remove();
    }, 4600);
})();
</script>
""", height=0, width=0)

# 2. RAY COLUMN WEBGL BACKGROUND INJECTION
components.html("""
<script>
(function() {
    const parentDoc = window.parent.document;
    if (parentDoc.getElementById('ray-column-bg-canvas')) return;

    const canvas = parentDoc.createElement('canvas');
    canvas.id = 'ray-column-bg-canvas';
    canvas.style.cssText = 'position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -99999; pointer-events: none; display: block;';
    parentDoc.body.appendChild(canvas);

    const gl = canvas.getContext('webgl', { antialias: false, alpha: false, depth: false });
    if (!gl) return;

    const VERT_SRC = `
        attribute vec2 a_pos;
        void main() { gl_Position = vec4(a_pos, 0.0, 1.0); }
    `;

    const FRAG_SRC = `
        #ifdef GL_FRAGMENT_PRECISION_HIGH
        precision highp float;
        #else
        precision mediump float;
        #endif

        uniform vec2  uRes;
        uniform float uTime;
        uniform vec2  uMouse;
        uniform float uHover;

        const float PI  = 3.14159265;
        const float TAU = 6.28318531;

        float sat(float x){ return clamp(x, 0.0, 1.0); }
        float pw(float x, float e){ return pow(max(x, 1e-5), e); }
        float hash21(vec2 p){ p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 34.56); return fract(p.x * p.y); }
        float vnoise(vec2 p){
          vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
          float a = hash21(i), b = hash21(i + vec2(1.0, 0.0));
          float c = hash21(i + vec2(0.0, 1.0)), d = hash21(i + vec2(1.0, 1.0));
          return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
        }
        float fbm3(vec2 p){ float s = 0.0, a = 0.5; for(int i = 0; i < 3; i++){ s += a * vnoise(p); p = p * 2.07 + vec2(4.1, 2.3); a *= 0.5; } return s; }

        uniform vec3 uBg, uBase, uAccent, uHigh;
        uniform float uRays, uContrast, uSweep, uFall, uAper, uDirection;

        void main(){
          float ar = uRes.x / max(uRes.y, 1.0);
          vec2 uv = gl_FragCoord.xy / uRes;
          vec2 p = (uv - 0.5) * vec2(ar, 1.0);
          float t = uTime * 0.07;

          float dcs = cos(uDirection), dsn = sin(uDirection);
          mat2 drot = mat2(dcs, -dsn, dsn, dcs);
          p = drot * p;
          vec2 src = vec2(0.0, -0.78);
          vec2 d = p - src;
          float r = max(length(d), 1e-3);
          float th = atan(d.x, d.y);

          vec2 mp = drot * ((uMouse - 0.5) * vec2(ar, 1.0));
          vec2 md = mp - src;
          float mr = max(length(md), 1e-3);
          float mth = atan(md.x, md.y);
          float ang = abs(mod(th - mth + PI, TAU) - PI);
          float aw = max(uAper, 0.02);
          float h = sat(uHover);
          float swell = 1.0 + 0.55 * exp(-pw(abs(r - mr) / 0.40, 2.0));
          float open  = h * exp(-pw(ang / aw, 2.0)) * swell;

          float close = h * smoothstep(aw, aw + 0.30, ang);

          float v = fbm3(vec2(th * uRays, r * 0.9 - t * 2.4));
          v += 0.50 * vnoise(vec2(th * uRays * 2.4 + 3.0, r * 1.8 - t * 3.6));
          v = pw(sat(v * 1.10 - 0.31), uContrast);

          v = mix(v, smoothstep(0.08, 0.50, v), 0.60 * sat(open));
          float env = exp(-pw(max(r - 0.30, 0.0) * uFall, 1.5));
          float aen = exp(-pw(abs(th) / max(uSweep, 0.05), 2.0));

          float body = v * env * aen * (1.0 + 0.90 * open) * (1.0 - 0.55 * close);
          float bloom = exp(-pw(max(r - 0.18, 0.0) * uFall * 1.30, 1.7)) * aen * (1.0 + 0.25 * open);
          vec3 col = uBg;
          col += uBase * bloom * 0.90;
          col += mix(uBase, uAccent, sat(body * 1.6)) * body * 2.4;
          col += uHigh * pw(sat(body - 0.38), 2.0) * 1.10;
          gl_FragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
        }
    `;

    function compile(type, src) {
        const sh = gl.createShader(type);
        gl.shaderSource(sh, src);
        gl.compileShader(sh);
        return sh;
    }

    const vs = compile(gl.VERTEX_SHADER, VERT_SRC);
    const fs = compile(gl.FRAGMENT_SHADER, FRAG_SRC);
    const prog = gl.createProgram();
    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);
    gl.useProgram(prog);

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const posLoc = gl.getAttribLocation(prog, "a_pos");
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    const locs = {};
    const u = (name) => {
        if (!(name in locs)) locs[name] = gl.getUniformLocation(prog, name);
        return locs[name];
    };

    let ptr = { x: 0.5, y: 0.5, tx: 0.5, ty: 0.5, on: 0, onTarget: 0 };
    let last = performance.now();
    let clock = 0;

    parentDoc.addEventListener('pointermove', (e) => {
        ptr.tx = e.clientX / window.innerWidth;
        ptr.ty = e.clientY / window.innerHeight;
        ptr.onTarget = 1;
    });

    function render(now) {
        const dt = Math.min(0.05, (now - last) / 1000);
        last = now;

        clock = (clock + dt * 1.0) % 3600;

        const k = 1 - Math.exp(-6 * dt);
        ptr.on += (ptr.onTarget - ptr.on) * k;
        ptr.x += ((ptr.onTarget > 0 ? ptr.tx : 0.5) - ptr.x) * k;
        ptr.y += ((ptr.onTarget > 0 ? ptr.ty : 0.5) - ptr.y) * k;

        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        const bw = Math.max(1, Math.round(window.innerWidth * dpr));
        const bh = Math.max(1, Math.round(window.innerHeight * dpr));

        if (canvas.width !== bw || canvas.height !== bh) {
            canvas.width = bw;
            canvas.height = bh;
        }
        gl.viewport(0, 0, bw, bh);

        gl.uniform2f(u("uRes"), bw, bh);
        gl.uniform1f(u("uTime"), clock);
        gl.uniform2f(u("uMouse"), ptr.x, 1 - ptr.y);
        gl.uniform1f(u("uHover"), Math.min(1, ptr.on) * 2.0);

        // Colors matching your preset:
        gl.uniform3f(u("uBg"), 0.0, 0.008, 0.024);         // #000206
        gl.uniform3f(u("uBase"), 1.0, 0.0, 0.294);        // #FF004B
        gl.uniform3f(u("uAccent"), 0.431, 0.671, 0.961);   // #6EABF5
        gl.uniform3f(u("uHigh"), 0.812, 0.894, 1.0);       // #CFE4FF

        gl.uniform1f(u("uRays"), 4.2);
        gl.uniform1f(u("uContrast"), 1.5);
        gl.uniform1f(u("uSweep"), 0.85);
        gl.uniform1f(u("uFall"), 1.5);
        gl.uniform1f(u("uAper"), 0.05);
        gl.uniform1f(u("uDirection"), 0.0);

        gl.drawArrays(gl.TRIANGLES, 0, 3);
        requestAnimationFrame(render);
    }

    requestAnimationFrame(render);
})();
</script>
""", height=0, width=0)

# 3. GLOBAL CSS STYLING
st.markdown("""
<style>
    #MainMenu,
    footer,
    [data-testid="stStatusWidget"],
    [data-testid="manage-app-button"],
    .stDeployButton,
    [data-testid="stDecoration"],
    [data-testid="stHeaderActionElements"] {
        display: none !important;
        visibility: hidden !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        z-index: 99990 !important;
    }

    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    header[data-testid="stHeader"] button {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        z-index: 99999 !important;
        margin-left: 8px !important;
        margin-top: 4px !important;
    }

    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] svg,
    header[data-testid="stHeader"] button svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
        color: #ffffff !important;
    }

    [data-testid="stAppViewContainer"] {
        background: transparent !important;
    }

    .stApp {
        background: transparent !important;
        color: #ffffff !important;
    }

    div[data-testid="stVerticalBlock"] > div[style*="flex"] {
        background: rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45) !important;
    }

    .stButton > button {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }

    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.6) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 0, 75, 0.4) !important;
    }

    section[data-testid="stSidebar"] {
        background: rgba(0, 2, 6, 0.88) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.15) !important;
    }

    div[role="dialog"] {
        background: rgba(0, 2, 6, 0.94) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 20px !important;
        color: #ffffff !important;
    }

    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }

    div[data-testid="stFeedback"] button {
        transform: scale(1.3);
        margin-right: 8px;
    }

    .scroll-target {
        opacity: 0;
        transform: translateY(40px);
        transition: opacity 0.8s cubic-bezier(0.25, 1, 0.5, 1), transform 0.8s cubic-bezier(0.25, 1, 0.5, 1);
        will-change: opacity, transform;
    }

    .scroll-target.in-view {
        opacity: 1;
        transform: translateY(0px);
    }
</style>
""", unsafe_allow_html=True)

# Intersection Observer for Scroll Effects
components.html("""
<script>
    function setupScrollObserver() {
        const parentDoc = window.parent.document;
        const mainContainer = parentDoc.querySelector('section.main') || parentDoc.querySelector('[data-testid="stMain"]');
        if (!mainContainer) return;

        const selectors = [
            'div[data-testid="stVerticalBlock"] > div',
            'div[data-testid="stMarkdownContainer"]',
            'div[data-testid="column"]',
            'form'
        ];
        
        const elementsToObserve = mainContainer.querySelectorAll(selectors.join(', '));

        const observerOptions = {
            root: null,
            rootMargin: '0px 0px -40px 0px',
            threshold: 0.12
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-view');
                } else {
                    entry.target.classList.remove('in-view');
                }
            });
        }, observerOptions);

        elementsToObserve.forEach(el => {
            if (!el.classList.contains('scroll-target')) {
                el.classList.add('scroll-target');
            }
            observer.observe(el);
        });
    }

    setTimeout(setupScrollObserver, 300);
    setInterval(setupScrollObserver, 1500);
</script>
""", height=0, width=0)

# Discord Webhook Credential
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1548288796200534066/x0AnH1nWfR4O6dt-OV1u5C4iaGLJ13z0GUe8I6WB7LgohPX2XF1Z9Csrrm1IEfNbbba3"

# Product Inventory
PRODUCTS = [
    {
        "id": 1,
        "name": "Resin Ring",
        "category": "Jewellery",
        "description": "A visualization of beauty and aesthetics, along with the modern requirements of today's jewellery fashion. Colours can be customised.",
        "price": 700,
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
# Helper Functions
# -----------------------------------------------------------------------------
def generate_order_number():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    rand_id = random.randint(100, 999)
    return f"ORD-{timestamp}-{rand_id}"

def send_discord_message(content=None, embeds=None, files=None):
    payload = {}
    if content:
        payload["content"] = content
    if embeds:
        payload["embeds"] = embeds

    try:
        if files:
            res = requests.post(DISCORD_WEBHOOK_URL, data={"payload_json": requests.compat.json.dumps(payload)}, files=files, timeout=10)
        else:
            res = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=8)
        
        if res.status_code in [200, 204]:
            return True, "Success"
        else:
            return False, f"Status Code {res.status_code}: {res.text}"
    except Exception as e:
        return False, str(e)

def send_discord_order(order_data, uploaded_files=None):
    add_pic_str = "Yes (+PKR 100)" if order_data.get('add_pictures') else "No"
    
    embed = {
        "title": "🛒 NEW ORDER RECEIVED",
        "color": 16711755,  # Crimson Pink
        "fields": [
            {"name": "Order Number", "value": f"`{order_data['order_no']}`", "inline": True},
            {"name": "Product", "value": order_data['product_name'], "inline": True},
            {"name": "Quantity", "value": str(order_data['quantity']), "inline": True},
            {"name": "Picture Customization", "value": add_pic_str, "inline": True},
            {"name": "Total Price", "value": f"**PKR {order_data['total_price']:,}**", "inline": True},
            {"name": "Transaction ID (TID)", "value": f"`{order_data['transaction_id']}`", "inline": True},
            {"name": "Customer Name", "value": order_data['customer_name'], "inline": True},
            {"name": "Phone Number", "value": order_data['customer_phone'], "inline": True},
            {"name": "Delivery Address", "value": order_data['customer_address'], "inline": False},
            {"name": "Customization Notes", "value": order_data['customer_notes'] or "None", "inline": False}
        ],
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    files_dict = {}
    if uploaded_files:
        for idx, file in enumerate(uploaded_files, 1):
            file.seek(0)
            files_dict[f"file_{idx}"] = (file.name, file.getvalue(), file.type)

    return send_discord_message(embeds=[embed], files=files_dict if files_dict else None)

def trigger_side_party_poppers():
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
                f'<div class="slide{active_class}" style="'
                f'position: absolute; top: 0; left: 0; width: 100%; height: 100%; '
                f'opacity: 0; transition: opacity 1s ease-in-out; pointer-events: none; border-radius: 12px;">'
                f'<img src="{b64_str}" style="width: 100%; height: {height}px; object-fit: cover; border-radius: 12px;">'
                f'</div>'
            )

    if not img_html_elements:
        st.error("Images could not be loaded. Please verify files exist in the 'images/' folder.")
        return

    unique_id = f"carousel_{random.randint(1000, 9999)}"
    
    dots_html = "".join([
        f'<span class="dot{" active" if i == 0 else ""}" data-index="{i}" style="'
        f'height: 10px; width: 10px; margin: 0 4px; background-color: rgba(255, 255, 255, 0.4); '
        f'border-radius: 50%; display: inline-block; cursor: pointer; transition: all 0.3s ease;"></span>'
        for i in range(len(img_html_elements))
    ])

    carousel_html = f"""
    <div id="{unique_id}_container" style="
        position: relative;
        width: 100%;
        height: {height}px;
        border-radius: 12px;
        overflow: hidden;
    ">
        {''.join(img_html_elements)}
        <div style="
            position: absolute;
            bottom: 12px;
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10;
        ">
            {dots_html}
        </div>
    </div>
    <style>
        #{unique_id}_container .slide.active {{
            opacity: 1 !important;
            pointer-events: auto !important;
        }}
        #{unique_id}_container .dot.active {{
            background-color: #ffffff !important;
            transform: scale(1.3);
        }}
    </style>
    <script>
        (function() {{
            const container = document.getElementById('{unique_id}_container');
            if (!container) return;
            const slides = container.getElementsByClassName('slide');
            const dots = container.getElementsByClassName('dot');
            const totalSlides = slides.length;
            let currentIndex = 0;
            let timer = null;

            function showSlide(index) {{
                for (let i = 0; i < totalSlides; i++) {{
                    slides[i].classList.remove('active');
                    if (dots[i]) dots[i].classList.remove('active');
                }}
                currentIndex = index;
                slides[currentIndex].classList.add('active');
                if (dots[currentIndex]) dots[currentIndex].classList.add('active');
            }}

            function nextSlide() {{
                let next = (currentIndex + 1) % totalSlides;
                showSlide(next);
            }}

            function startTimer() {{
                if (totalSlides > 1) {{
                    timer = setInterval(nextSlide, {interval_sec * 1000});
                }}
            }}

            function resetTimer() {{
                if (timer) clearInterval(timer);
                startTimer();
            }}

            for (let i = 0; i < dots.length; i++) {{
                dots[i].addEventListener('click', function() {{
                    showSlide(i);
                    resetTimer();
                }});
            }}

            startTimer();
        }})();
    </script>
    """
    components.html(carousel_html, height=height + 10)

# -----------------------------------------------------------------------------
# Main User Interface
# -----------------------------------------------------------------------------
st.title("Resins-DreamByR")
st.write("Browse products and place orders instantly.")

# Sidebar Filters
st.sidebar.header("Filter Products")
categories = ["All"] + sorted(list(set(p["category"] for p in PRODUCTS)))
selected_category = st.sidebar.selectbox("Select Category", categories)

st.sidebar.divider()
st.sidebar.caption("**Web Developer:** 0314-4012872")

filtered_products = PRODUCTS if selected_category == "All" else [p for p in PRODUCTS if p["category"] == selected_category]

# Session States
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None
if "pending_order" not in st.session_state:
    st.session_state.pending_order = None
if "completed_order_id" not in st.session_state:
    st.session_state.completed_order_id = None

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
            st.session_state.pending_order = None
            st.session_state.completed_order_id = None

# Order Modal Dialog Flow
if st.session_state.selected_product is not None:
    prod = st.session_state.selected_product
    
    @st.dialog(f"Order: {prod['name']}")
    def show_order_modal():
        # STEP 3: Order Completed View
        if st.session_state.completed_order_id:
            st.success("🎉 Order Placed Successfully!")
            st.subheader("Your Order ID")
            st.code(st.session_state.completed_order_id, language="text")
            st.caption(" Please copy or screenshot this Order ID for your tracking reference.")
            trigger_side_party_poppers()
            
            if st.button("Close Window"):
                st.session_state.selected_product = None
                st.session_state.pending_order = None
                st.session_state.completed_order_id = None
                st.rerun()
            return

        # STEP 2: Order Confirmation Dialogue ("Confirm Order?")
        if st.session_state.pending_order is not None:
            order = st.session_state.pending_order
            st.subheader("Confirm Order?")
            st.write("Please review your order details before final submission:")
            
            st.markdown(f"""
            * **Product:** {order['product_name']}
            * **Quantity:** {order['quantity']}
            * **Total Price:** PKR {order['total_price']:,}/-
            * **Transaction ID (TID):** `{order['transaction_id']}`
            * **Customer Name:** {order['customer_name']}
            * **Phone:** {order['customer_phone']}
            * **Address:** {order['customer_address']}
            * **Notes:** {order['customer_notes'] or 'None'}
            """)
            st.divider()

            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if st.button("Confirm", use_container_width=True):
                    with st.spinner("Submitting order to Discord..."):
                        success, result = send_discord_order(
                            order, 
                            uploaded_files=order.get('uploaded_photos')
                        )
                    
                    if success:
                        st.session_state.completed_order_id = order['order_no']
                        st.session_state.pending_order = None
                        st.rerun()
                    else:
                        st.error(f"Failed to submit order to Discord: {result}")
            
            with btn_col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.pending_order = None
                    st.rerun()
            return

        # STEP 1: Initial Order Details & Input Form
        render_auto_sliding_carousel(prod["images"], height=280, interval_sec=4)
            
        st.subheader(prod["name"])
        st.write(f"**Category:** {prod['category']}")
        st.write(f"**Description:** {prod['description']}")
        st.write(f"**Base Price:** PKR {prod['price']:,}/-")
        
        st.divider()
        
        quantity = st.number_input(
            "Quantity", 
            min_value=1, 
            max_value=50, 
            value=1, 
            key=f"qty_input_{prod['id']}"
        )
        
        add_pictures = False
        uploaded_photos = None
        picture_extra_cost = 0

        if prod["category"] == "Resin shields":
            add_pictures = st.checkbox("Add pictures (+ PKR 100/-)", key=f"pic_chk_{prod['id']}")
            if add_pictures:
                picture_extra_cost = 100
                uploaded_photos = st.file_uploader(
                    "➕ Upload pictures (Max 3)", 
                    type=["jpg", "jpeg", "png", "webp"], 
                    accept_multiple_files=True,
                    key=f"shield_pics_{prod['id']}"
                )
                if uploaded_photos and len(uploaded_photos) > 3:
                    st.warning("⚠️ Maximum 3 pictures allowed. Only the first 3 will be processed.")
                    uploaded_photos = uploaded_photos[:3]

        unit_price = prod["price"] + picture_extra_cost
        total_price = quantity * unit_price
        
        st.info(f"Total Amount: **PKR {total_price:,}/-**")
        
        st.write("### Payment Method")
        st.success(
            "**JazzCash Payment Details**\n\n"
            "• **Account Number:** `0305-8866692`\n\n"
            "• **Account Name:** Rimsha Fatima\n\n"
            "Please send the total amount to the JazzCash account above and enter your Transaction ID (TID) below."
        )

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
                if not transaction_id.strip():
                    missing_fields.append("Transaction ID (TID)")
                if not customer_name.strip():
                    missing_fields.append("Full Name")
                if not customer_phone.strip():
                    missing_fields.append("Phone Number")
                if not customer_address.strip():
                    missing_fields.append("Delivery Address")
                if add_pictures and not uploaded_photos:
                    missing_fields.append("Uploaded Pictures (Since 'Add pictures' was checked)")

                if missing_fields:
                    st.error(f"Please fill in all required fields: {', '.join(missing_fields)}.")
                else:
                    st.session_state.pending_order = {
                        "order_no": generate_order_number(),
                        "product_name": prod["name"],
                        "quantity": quantity,
                        "add_pictures": add_pictures,
                        "total_price": total_price,
                        "transaction_id": transaction_id,
                        "customer_name": customer_name,
                        "customer_phone": customer_phone,
                        "customer_address": customer_address,
                        "customer_notes": customer_notes,
                        "uploaded_photos": uploaded_photos
                    }
                    st.rerun()

        st.markdown(
            "*For further order details, contact on "
            "[+92 305-8866692](https://wa.me/923058866692) through WhatsApp.*"
        )
        
        if st.button("Close"):
            st.session_state.selected_product = None
            st.session_state.pending_order = None
            st.session_state.completed_order_id = None
            st.rerun()

    show_order_modal()

# -----------------------------------------------------------------------------
# Bottom Interactive Sections
# -----------------------------------------------------------------------------
st.divider()

st.subheader("Leave a Review")

star_rating_index = st.feedback("stars")

with st.form("client_review_form"):
    review_text = st.text_area("How was your experience:", placeholder="Write your experience with Resins By R...")
    review_submitted = st.form_submit_button("Submit Review")

    if review_submitted:
        if star_rating_index is None:
            st.error("Please click on the stars above to select a star rating!")
        elif not review_text.strip():
            st.error("Please fill in 'How was your experience:' before submitting.")
        else:
            rating_val = star_rating_index + 1
            stars_visual = f"{'★' * rating_val}{'☆' * (5 - rating_val)}"
            
            review_embed = {
                "title": "⭐ NEW CLIENT REVIEW",
                "color": 16766720,  # Gold Color
                "fields": [
                    {"name": "Rating", "value": f"{rating_val} / 5 Stars ({stars_visual})", "inline": False},
                    {"name": "Experience", "value": review_text.strip(), "inline": False}
                ],
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            
            with st.spinner("Submitting review..."):
                ok, err = send_discord_message(embeds=[review_embed])
            if ok:
                st.success("Thank you for submitting your review!")
            else:
                st.error(f"Could not submit review. Error: {err}")

st.divider()

st.markdown(
    '**"Resins by R"** is a brand worth to be trusted and attended, as it opts the '
    '"quality over quantity" fact, making the clients to trust with all their heart. '
    'We do NOT ignore the service demands of our clients, and ensure all the details '
    'are kept in check, building the pure-trust relation with the clients, instead '
    'of just developing a "Buyer-Seller" sense. We do all our best to keep the clients '
    'satisfied and comfortable with our purchases.\n\n'
    'But still, if you think we can serve you better than we are, your opinion is of '
    'great importance for us.\n\n'
    '*(Resins By R)\'s Development team.*'
)

with st.form("client_opinion_form"):
    opinion_text = st.text_area("Your opinion:", placeholder="Share your suggestions or opinion with us...")
    opinion_submitted = st.form_submit_button("Submit Opinion")

    if opinion_submitted:
        if not opinion_text.strip():
            st.error("Please enter your opinion before submitting.")
        else:
            opinion_embed = {
                "title": "💡 NEW CLIENT OPINION",
                "color": 3447003,  # Blue Accent
                "fields": [
                    {"name": "Opinion", "value": opinion_text.strip(), "inline": False}
                ],
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            
            with st.spinner("Submitting opinion..."):
                ok, err = send_discord_message(embeds=[opinion_embed])
            if ok:
                st.success("Thank you for sharing your valuable opinion with us!")
            else:
                st.error(f"Could not submit opinion. Error: {err}")

st.divider()

# Instagram Link Container
st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 12px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FF004B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
            <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
            <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
        </svg>
        <a href="https://www.instagram.com/resin_dreambyrimsha?stkn=NHk5dDlhY2VmM2Q1" target="_blank" style="color: #ffffff; text-decoration: none; font-weight: 600; font-size: 15px;">
            Resins-DreamByR
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption("Web Developer: 0314-4012872")
