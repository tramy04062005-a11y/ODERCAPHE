import sys
import subprocess

# Tự động cài đặt pymysql nếu server Streamlit Cloud chưa cài
try:
    import pymysql
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql", "cryptography"])
    import pymysql

import streamlit as st
import pandas as pd
from PIL import Image
import os

# --- CẤU HÌNH THÔNG TIN KẾT NỐI MYSQL AIVEN ---
DB_HOST = "mysql-24eda0f5-tramy04062005-899b.k.aivencloud.com"
DB_PORT = 13321
DB_USER = "avnadmin"
DB_PASSWORD = "AVNS_eyALQ_tYt5oQ7pItFnm"
DB_NAME = "defaultdb"

# --- HÀM TẠO KẾT NỐI CƠ SỞ DỮ LIỆU ---
def get_db_connection():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            ssl={'ssl': True},  # Aiven yêu cầu SSL mode = REQUIRED
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10
        )
        return connection
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Cơ sở dữ liệu Aiven MySQL: {e}")
        return None

# --- KHỞI TẠO BẢNG DỮ LIỆU TRÊN MYSQL ---
def init_db():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                # Bảng lưu thông tin chung đơn hàng
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_name VARCHAR(255) NOT NULL,
                    table_num VARCHAR(50) NOT NULL,
                    total_amount INT NOT NULL,
                    payment_method VARCHAR(50) NOT NULL,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                # Bảng lưu chi tiết các món trong đơn hàng
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_details (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id INT NOT NULL,
                    item_name VARCHAR(255) NOT NULL,
                    size VARCHAR(20) NOT NULL,
                    sugar VARCHAR(20) NOT NULL,
                    ice VARCHAR(20) NOT NULL,
                    quantity INT NOT NULL,
                    unit_price INT NOT NULL,
                    total_price INT NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
                );
                """)
            conn.commit()
        except Exception as e:
            st.error(f"Lỗi khởi tạo bảng CSDL: {e}")
        finally:
            conn.close()

# Tự động khởi tạo bảng khi app chạy
init_db()

# --- CẤU HÌNH TRANG STREAMLIT ---
st.set_page_config(
    page_title="CFCU Coffee - App Order",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS TÙY CHỈNH GIAO DIỆN ---
st.markdown("""
<style>
    .main-title {
        color: #3E2723;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #6D4C41;
        color: white;
        border-radius: 8px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #3E2723;
        color: #FFF;
    }
    .card {
        padding: 15px;
        border-radius: 12px;
        background-color: #FFF8E1;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .price-tag {
        color: #D84315;
        font-weight: bold;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# --- DỮ LIỆU MENU ---
MENU = {
    "Cà Phê Truyền Thống": [
        {"id": "c1", "name": "Cà Phê Đen", "price": 25000, "desc": "Đậm đà chuẩn vị gu Việt"},
        {"id": "c2", "name": "Cà Phê Sữa", "price": 29000, "desc": "Hài hòa giữa đắng đậm và ngọt béo"},
        {"id": "c3", "name": "Bạc Xỉu", "price": 32000, "desc": "Nhiều sữa ít cà phê, dễ uống"},
        {"id": "c4", "name": "Cà Phê Muối", "price": 35000, "desc": "Vị mặn nhẹ tôn lên nét béo ngậy"},
    ],
    "Trà & Trà Sữa": [
        {"id": "t1", "name": "Trà Đào Cam Sả", "price": 39000, "desc": "Thanh mát, thơm hương sả tự nhiên"},
        {"id": "t2", "name": "Trà Vải Lài", "price": 39000, "desc": "Ngọt dịu hương hoa lài và vải tươi"},
        {"id": "t3", "name": "Trà Sữa Oolong", "price": 42000, "desc": "Đậm vị trà Oolong kết hợp kem béo"},
    ],
    "Bánh & Đi Kèm": [
        {"id": "b1", "name": "Bánh Croissant", "price": 30000, "desc": "Bánh sừng bò nướng giòn rụm"},
        {"id": "b2", "name": "Bánh Tiramisu", "price": 45000, "desc": "Bánh ngọt thơm vị cà phê và cacao"},
    ]
}

# --- KHỞI TẠO SESSION STATE ---
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'order_success' not in st.session_state:
    st.session_state.order_success = False

# --- HEADER & BANNER ---
col_banner, col_title = st.columns([1, 2])
with col_banner:
    if os.path.exists("CFCU.jpg"):
        image = Image.open("CFCU.jpg")
        st.image(image, use_container_width=True)
    else:
        st.info("📌 Thêm file 'CFCU.jpg' vào cùng thư mục để hiện banner.")

with col_title:
    st.markdown("<h1 class='main-title'>☕ CFCU COFFEE ORDER</h1>", unsafe_allow_html=True)
    st.caption("Thưởng thức hương vị cà phê đậm đà mỗi ngày. Đặt món nhanh chóng & tiện lợi!")

st.divider()

# --- BỐ CỤC CHÍNH (MENU & GIỎ HÀNG) ---
col_menu, col_cart = st.columns([2, 1])

# --- CỘT MENU (BÊN TRÁI) ---
with col_menu:
    st.subheader("📋 Menu Quán")
    
    category = st.radio("Chọn danh mục:", list(MENU.keys()), horizontal=True)
    
    for item in MENU[category]:
        with st.container():
            st.markdown(f"""
            <div class="card">
                <h4>{item['name']}</h4>
                <p style="color: #666; margin-bottom: 5px;">{item['desc']}</p>
                <p class="price-tag">{item['price']:,} VNĐ</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Tùy chọn cho món
            col_opt1, col_opt2, col_opt3 = st.columns(3)
            with col_opt1:
                size = st.selectbox(f"Size ({item['name']})", ["Nhỏ (S)", "Vừa (M) (+5k)", "Lớn (L) (+10k)"], key=f"size_{item['id']}")
            
            with col_opt2:
                sugar = st.select_slider(f"Đường ({item['name']})", options=["0%", "30%", "50%", "70%", "100%"], value="100%", key=f"sugar_{item['id']}")
                
            with col_opt3:
                ice = st.select_slider(f"Đá ({item['name']})", options=["0%", "30%", "50%", "70%", "100%"], value="100%", key=f"ice_{item['id']}")

            col_qty, col_btn = st.columns([1, 2])
            with col_qty:
                qty = st.number_input("Số lượng", min_value=1, max_value=20, value=1, key=f"qty_{item['id']}")
            
            with col_btn:
                st.write("")
                st.write("")
                if st.button(f"🛒 Thêm {item['name']}", key=f"add_{item['id']}"):
                    extra = 0
                    if "M" in size: extra = 5000
                    elif "L" in size: extra = 10000
                    
                    unit_price = item['price'] + extra
                    
                    cart_item = {
                        "id": item['id'],
                        "name": item['name'],
                        "size": size.split()[0],
                        "sugar": sugar,
                        "ice": ice,
                        "qty": qty,
                        "unit_price": unit_price,
                        "total_price": unit_price * qty
                    }
                    st.session_state.cart.append(cart_item)
                    st.toast(f"Đã thêm {qty}x {item['name']} vào giỏ hàng!", icon="✅")
            st.divider()

# --- CỘT GIỎ HÀNG & ĐẶT HÀNG (BÊN PHẢI) ---
with col_cart:
    st.subheader("🛍️ Giỏ Hàng Của Bạn")
    
    if not st.session_state.cart:
        st.info("Giỏ hàng đang trống. Vui lòng chọn món!")
    else:
        total_bill = 0
        for idx, item in enumerate(st.session_state.cart):
            with st.expander(f"{item['qty']}x {item['name']} ({item['size']})", expanded=True):
                st.write(f"- **Đường:** {item['sugar']} | **Đá:** {item['ice']}")
                st.write(f"- **Đơn giá:** {item['unit_price']:,} VNĐ")
                st.write(f"- **Thành tiền:** {item['total_price']:,} VNĐ")
                
                if st.button("🗑️ Xóa", key=f"del_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
            
            total_bill += item['total_price']
            
        st.markdown(f"### **Tổng cộng: :red[{total_bill:,} VNĐ]**")
        
        if st.button("Xóa tất cả"):
            st.session_state.cart = []
            st.rerun()
            
        st.divider()
        
        # Form nhập thông tin khách hàng
        st.subheader("📝 Thông Tin Đặt Hàng")
        customer_name = st.text_input("Họ và Tên*")
        table_num = st.text_input("Số Bàn / Số Phòng*")
        note = st.text_area("Ghi chú thêm (vd: Ít ngọt...)")
        pay_method = st.radio("Hình thức thanh toán", ["Tiền mặt", "Chuyển khoản QR", "Ví MoMo"])
        
        if st.button("🚀 GỬI ĐƠN HÀNG", type="primary", use_container_width=True):
            if not customer_name or not table_num:
                st.error("Vui lòng điền đầy đủ Họ tên và Số bàn!")
            else:
                # --- THAO TÁC LƯU VÀO DATABASE AIVEN MYSQL ---
                conn = get_db_connection()
                if conn:
                    try:
                        with conn.cursor() as cursor:
                            # 1. Chèn đơn hàng mới
                            sql_order = """
                            INSERT INTO orders (customer_name, table_num, total_amount, payment_method, note)
                            VALUES (%s, %s, %s, %s, %s)
                            """
                            cursor.execute(sql_order, (customer_name, table_num, total_bill, pay_method, note))
                            order_id = cursor.lastrowid
                            
                            # 2. Chèn chi tiết món ăn vào order_details
                            sql_detail = """
                            INSERT INTO order_details (order_id, item_name, size, sugar, ice, quantity, unit_price, total_price)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            for cart_item in st.session_state.cart:
                                cursor.execute(sql_detail, (
                                    order_id,
                                    cart_item['name'],
                                    cart_item['size'],
                                    cart_item['sugar'],
                                    cart_item['ice'],
                                    cart_item['qty'],
                                    cart_item['unit_price'],
                                    cart_item['total_price']
                                ))
                        conn.commit()
                        st.session_state.order_success = True
                    except Exception as e:
                        st.error(f"Lỗi khi lưu đơn hàng vào CSDL: {e}")
                    finally:
                        conn.close()

        # Hiển thị kết quả thành công
        if st.session_state.order_success:
            st.balloons()
            st.success("🎉 Đặt hàng thành công! Đơn hàng đã được lưu vào Database Aiven.")
            
            st.markdown("---")
            st.markdown("### 📜 HÓA ĐƠN XÁC NHẬN")
            st.write(f"**Khách hàng:** {customer_name}")
            st.write(f"**Vị trí:** Bàn {table_num}")
            st.write(f"**Thanh toán:** {pay_method}")
            if note:
                st.write(f"**Ghi chú:** {note}")
                
            df_cart = pd.DataFrame(st.session_state.cart)[['name', 'size', 'qty', 'total_price']]
            df_cart.columns = ['Món', 'Size', 'SL', 'Tổng (VNĐ)']
            st.table(df_cart)
            
            if st.button("Tạo đơn mới"):
                st.session_state.cart = []
                st.session_state.order_success = False
                st.rerun()

# --- QUẢN LÝ DÀNH CHO QUÁN (XEM LỊCH SỬ ĐƠN HÀNG) ---
with st.sidebar:
    st.title("⚙️ Quản trị viên")
    show_history = st.checkbox("Hiển thị Lịch sử Đơn hàng")

# Tách riêng phần hiển thị dữ liệu CSDL ra màn hình chính rộng rãi
if show_history:
    st.markdown("---")
    st.subheader("📊 Lịch Sử Đơn Hàng Trên Aiven Database")
    conn = get_db_connection()
    if conn:
        try:
            # Truy vấn lấy dữ liệu đơn hàng
            df_orders = pd.read_sql("""
                SELECT 
                    id AS `Mã Đơn`, 
                    customer_name AS `Tên Khách Hàng`, 
                    table_num AS `Số Bàn`, 
                    total_amount AS `Tổng Tiền (VNĐ)`, 
                    payment_method AS `Thanh Toán`, 
                    note AS `Ghi Chú`, 
                    created_at AS `Thời Gian Tạo` 
                FROM orders 
                ORDER BY created_at DESC
            """, conn)
            
            if df_orders.empty:
                st.info("Chưa có đơn hàng nào trong CSDL Aiven.")
            else:
                # Hiển thị bảng full-width, định dạng chuẩn đẹp
                st.dataframe(
                    df_orders, 
                    use_container_width=True, 
                    hide_index=True
                )
        except Exception as e:
            st.error(f"Lỗi truy vấn dữ liệu từ CSDL: {e}")
        finally:
            conn.close()
