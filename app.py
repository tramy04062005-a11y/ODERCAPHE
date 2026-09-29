import streamlit as st
import pandas as pd
from PIL import Image
import os

# --- CẤU HÌNH TRANG ---
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
            
            # Tùy chọn cho món ăn/uống
            col_opt1, col_opt2, col_opt3 = st.columns(3)
            with col_opt1:
                size = st.selectbox(f"Size ({item['name']})", ["Nhỏ (S)", "Vừa (M) (+5k)", "Lớn (L) (+10k)"], key=f"size_{item['id']}")
            
            with col_opt2:
                sugar = st.select_slider(f"Đường ({item['name']})", options=["0%", "30%", "50%", "70%", "100%"], value="100%", key=f"sugar_{item['id']}")
                
            with col_opt3:
                ice = st.select_slider(f"Đá ({item['name']})", options=["0%", "30%", "50%", "70%", "100%"], value="100%", key=f"ice_{item['id']}")

            # Số lượng và Nút thêm vào giỏ
            col_qty, col_btn = st.columns([1, 2])
            with col_qty:
                qty = st.number_input("Số lượng", min_value=1, max_value=20, value=1, key=f"qty_{item['id']}")
            
            with col_btn:
                st.write("") # Spacer
                st.write("")
                if st.button(f"🛒 Thêm {item['name']}", key=f"add_{item['id']}"):
                    # Tính giá theo Size
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

# --- CỘT GIỎ HÀNG (BÊN PHẢI) ---
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
        
        # Thao tác dọn giỏ hàng
        if st.button("Xóa tất cả"):
            st.session_state.cart = []
            st.rerun()
            
        st.divider()
        
        # Thông tin thanh toán
        st.subheader("📝 Thông Tin Đặt Hàng")
        customer_name = st.text_input("Họ và Tên*")
        table_num = st.text_input("Số Bàn / Số Phòng*")
        note = st.text_area("Ghi chú thêm (vd: Lấy ít ống hút...)")
        pay_method = st.radio("Hình thức thanh toán", ["Tiền mặt", "Chuyển khoản QR", "Ví MoMo"])
        
        if st.button("🚀 GỬI ĐƠN HÀNG", type="primary", use_container_width=True):
            if not customer_name or not table_num:
                st.error("Vui lòng điền đầy đủ Họ tên và Số bàn!")
            else:
                st.session_state.order_success = True
                
        # Xử lý khi đặt hàng thành công
        if st.session_state.order_success:
            st.balloons()
            st.success("🎉 Đặt hàng thành công! Quán đang chuẩn bị món cho bạn.")
            
            # Hiển thị Tóm tắt hóa đơn
            st.markdown("---")
            st.markdown("### 📜 HÓA ĐƠN XÁC NHẬN")
            st.write(f"**Khách hàng:** {customer_name}")
            st.write(f"**Vị trí:** Bàn {table_num}")
            st.write(f"**Thanh toán:** {pay_method}")
            if note:
                st.write(f"**Ghi chú:** {note}")
                
            # Tạo bảng hiển thị
            df_cart = pd.DataFrame(st.session_state.cart)[['name', 'size', 'qty', 'total_price']]
            df_cart.columns = ['Món', 'Size', 'SL', 'Tổng (VNĐ)']
            st.table(df_cart)
            
            # Nút Đặt đơn mới
            if st.button("Tạo đơn mới"):
                st.session_state.cart = []
                st.session_state.order_success = False
                st.rerun()
