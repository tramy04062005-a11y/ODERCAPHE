import streamlit as st
import pandas as pd
import pymysql
from PIL import Image
import os


# =========================================================
# CẤU HÌNH STREAMLIT
# =========================================================

st.set_page_config(
    page_title="CFCU Coffee - App Order",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# THÔNG TIN MYSQL AIVEN
# =========================================================

DB_HOST = "mysql-24eda0f5-tramy04062005-899b.k.aivencloud.com"
DB_PORT = 13321
DB_USER = "avnadmin"

# ⚠️ ĐIỀN PASSWORD AIVEN MỚI CỦA BẠN VÀO ĐÂY
DB_PASSWORD = "DIEN_PASSWORD_AIVEN_MOI_VAO_DAY"

DB_NAME = "defaultdb"


# =========================================================
# KẾT NỐI MYSQL
# =========================================================

def get_db_connection():

    try:

        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=15,
            read_timeout=15,
            write_timeout=15,
            ssl={
                "check_hostname": False
            }
        )

        return conn

    except Exception as e:

        st.error(
            "❌ Không thể kết nối MySQL Aiven.\n\n"
            f"{e}"
        )

        return None


# =========================================================
# KHỞI TẠO DATABASE
# =========================================================

def init_db():

    conn = get_db_connection()

    if conn is None:
        return False

    try:

        with conn.cursor() as cursor:

            cursor.execute(
                "SET NAMES utf8mb4"
            )

            # -------------------------------------------------
            # BẢNG ORDERS
            # -------------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (

                    id INT AUTO_INCREMENT PRIMARY KEY,

                    customer_name
                    VARCHAR(255)
                    CHARACTER SET utf8mb4
                    COLLATE utf8mb4_unicode_ci
                    NOT NULL,

                    table_num
                    VARCHAR(50)
                    CHARACTER SET utf8mb4
                    COLLATE utf8mb4_unicode_ci
                    NOT NULL,

                    total_amount INT NOT NULL,

                    payment_method
                    VARCHAR(100)
                    CHARACTER SET utf8mb4
                    COLLATE utf8mb4_unicode_ci
                    NOT NULL,

                    note
                    TEXT
                    CHARACTER SET utf8mb4
                    COLLATE utf8mb4_unicode_ci,

                    created_at
                    TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP

                )
                ENGINE=InnoDB
                DEFAULT CHARSET=utf8mb4
                COLLATE=utf8mb4_unicode_ci
            """)

            # -------------------------------------------------
            # BẢNG ORDER_DETAILS
            # -------------------------------------------------

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_details (

                    id INT AUTO_INCREMENT PRIMARY KEY,

                    order_id INT NOT NULL,

                    item_name
                    VARCHAR(255)
                    CHARACTER SET utf8mb4
                    COLLATE utf8mb4_unicode_ci
                    NOT NULL,

                    size
                    VARCHAR(20)
                    CHARACTER SET utf8mb4
                    COLLATE utf8mb4_unicode_ci
                    NOT NULL,

                    sugar
                    VARCHAR(20)
                    CHARACTER SET utf8mb4
                    COLLATE utf8mb4_unicode_ci
                    NOT NULL,

                    ice
                    VARCHAR(20)
                    CHARACTER SET utf8mb4
                    COLLATE utf8mb4_unicode_ci
                    NOT NULL,

                    quantity INT NOT NULL,

                    unit_price INT NOT NULL,

                    total_price INT NOT NULL,

                    CONSTRAINT fk_order_details_orders
                    FOREIGN KEY (order_id)
                    REFERENCES orders(id)
                    ON DELETE CASCADE

                )
                ENGINE=InnoDB
                DEFAULT CHARSET=utf8mb4
                COLLATE=utf8mb4_unicode_ci
            """)

        conn.commit()

        return True

    except Exception as e:

        conn.rollback()

        st.error(
            "❌ Lỗi khởi tạo bảng MySQL:\n\n"
            f"{e}"
        )

        return False

    finally:

        conn.close()


# =========================================================
# MENU
# =========================================================

MENU = {

    "☕ Cà Phê Truyền Thống": [

        {
            "id": "c1",
            "name": "Cà Phê Đen",
            "price": 25000,
            "desc": "Đậm đà chuẩn vị gu Việt"
        },

        {
            "id": "c2",
            "name": "Cà Phê Sữa",
            "price": 29000,
            "desc": "Hài hòa giữa đắng đậm và ngọt béo"
        },

        {
            "id": "c3",
            "name": "Bạc Xỉu",
            "price": 32000,
            "desc": "Nhiều sữa, ít cà phê, dễ uống"
        },

        {
            "id": "c4",
            "name": "Cà Phê Muối",
            "price": 35000,
            "desc": "Vị mặn nhẹ tôn lên vị béo"
        }
    ],

    "🍹 Trà & Trà Sữa": [

        {
            "id": "t1",
            "name": "Trà Đào Cam Sả",
            "price": 39000,
            "desc": "Thanh mát, thơm hương sả tự nhiên"
        },

        {
            "id": "t2",
            "name": "Trà Vải Lài",
            "price": 39000,
            "desc": "Ngọt dịu, thơm hương hoa lài và vải"
        },

        {
            "id": "t3",
            "name": "Trà Sữa Oolong",
            "price": 42000,
            "desc": "Đậm vị trà Oolong kết hợp vị sữa béo"
        }
    ],

    "🥐 Bánh & Đi Kèm": [

        {
            "id": "b1",
            "name": "Bánh Croissant",
            "price": 30000,
            "desc": "Bánh sừng bò nướng giòn thơm"
        },

        {
            "id": "b2",
            "name": "Bánh Tiramisu",
            "price": 45000,
            "desc": "Bánh ngọt thơm vị cà phê và cacao"
        }
    ]
}


# =========================================================
# SESSION STATE
# =========================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "last_order" not in st.session_state:
    st.session_state.last_order = None


# =========================================================
# DATABASE
# =========================================================

database_ready = init_db()


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        color: #3E2723;
        font-family: Arial, sans-serif;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #795548;
        font-size: 16px;
    }

    .card {
        padding: 15px;
        border-radius: 14px;
        background-color: #FFF8E1;
        box-shadow: 0 3px 8px rgba(0,0,0,0.08);
        margin-bottom: 10px;
        border: 1px solid #EFEBE9;
    }

    .price-tag {
        color: #D84315;
        font-weight: bold;
        font-size: 18px;
    }

    .order-box {
        padding: 20px;
        border-radius: 14px;
        background-color: #FFF8E1;
        border: 1px solid #D7CCC8;
    }

    .stButton > button {
        border-radius: 9px;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🗄️ MYSQL AIVEN")

    if database_ready:

        st.success("🟢 Database đã sẵn sàng")

    else:

        st.error("🔴 Database chưa kết nối")

    st.divider()

    if st.button(
        "🔌 KIỂM TRA KẾT NỐI",
        use_container_width=True
    ):

        test_conn = get_db_connection()

        if test_conn:

            try:

                with test_conn.cursor() as cursor:

                    cursor.execute(
                        """
                        SELECT
                            VERSION() AS version,
                            DATABASE() AS database_name
                        """
                    )

                    result = cursor.fetchone()

                st.success(
                    "✅ KẾT NỐI MYSQL THÀNH CÔNG!"
                )

                st.write(
                    f"**Database:** "
                    f"{result['database_name']}"
                )

                st.write(
                    f"**MySQL:** "
                    f"{result['version']}"
                )

            except Exception as e:

                st.error(
                    f"❌ Lỗi kiểm tra:\n{e}"
                )

            finally:

                test_conn.close()


# =========================================================
# HEADER
# =========================================================

col_banner, col_title = st.columns(
    [1, 2]
)


with col_banner:

    if os.path.exists("CFCU.jpg"):

        st.image(
            Image.open("CFCU.jpg"),
            use_container_width=True
        )

    else:

        st.info(
            "📌 Hãy đặt file CFCU.jpg "
            "cùng thư mục với app.py"
        )


with col_title:

    st.markdown(
        """
        <h1 class="main-title">
            ☕ CFCU COFFEE ORDER
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="subtitle">
            Thưởng thức hương vị cà phê đậm đà mỗi ngày.
            Đặt món nhanh chóng & tiện lợi!
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# =========================================================
# TABS
# =========================================================

tab_order, tab_admin = st.tabs(
    [
        "🛒 ĐẶT MÓN",
        "📊 QUẢN LÝ LỊCH SỬ ĐƠN HÀNG"
    ]
)


# =========================================================
# TAB 1 - ĐẶT MÓN
# =========================================================

with tab_order:

    col_menu, col_cart = st.columns(
        [2, 1]
    )


    # =====================================================
    # MENU
    # =====================================================

    with col_menu:

        st.subheader("📋 MENU QUÁN")

        category = st.radio(
            "Chọn danh mục:",
            list(MENU.keys()),
            horizontal=True
        )

        for item in MENU[category]:

            st.markdown(
                f"""
                <div class="card">

                    <h3>{item['name']}</h3>

                    <p style="color:#666;">
                        {item['desc']}
                    </p>

                    <div class="price-tag">
                        {item['price']:,} VNĐ
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


            # -------------------------------------------------
            # TÙY CHỌN
            # -------------------------------------------------

            col_opt1, col_opt2, col_opt3 = st.columns(3)


            with col_opt1:

                size = st.selectbox(
                    f"Size - {item['name']}",

                    [
                        "S",
                        "M (+5.000)",
                        "L (+10.000)"
                    ],

                    key=f"size_{item['id']}"
                )


            with col_opt2:

                sugar = st.select_slider(
                    f"Đường - {item['name']}",

                    options=[
                        "0%",
                        "30%",
                        "50%",
                        "70%",
                        "100%"
                    ],

                    value="100%",

                    key=f"sugar_{item['id']}"
                )


            with col_opt3:

                ice = st.select_slider(
                    f"Đá - {item['name']}",

                    options=[
                        "0%",
                        "30%",
                        "50%",
                        "70%",
                        "100%"
                    ],

                    value="100%",

                    key=f"ice_{item['id']}"
                )


            col_qty, col_btn = st.columns(
                [1, 2]
            )


            with col_qty:

                qty = st.number_input(
                    "Số lượng",

                    min_value=1,
                    max_value=20,
                    value=1,

                    key=f"qty_{item['id']}"
                )


            with col_btn:

                st.write("")

                if st.button(
                    f"🛒 Thêm {item['name']}",

                    key=f"add_{item['id']}",

                    use_container_width=True
                ):

                    # -----------------------------------------
                    # TÍNH PHỤ THU SIZE
                    # -----------------------------------------

                    if size == "M (+5.000)":

                        extra = 5000
                        clean_size = "M"

                    elif size == "L (+10.000)":

                        extra = 10000
                        clean_size = "L"

                    else:

                        extra = 0
                        clean_size = "S"


                    unit_price = (
                        item["price"] + extra
                    )

                    total_price = (
                        unit_price * qty
                    )


                    # -----------------------------------------
                    # ITEM GIỎ HÀNG
                    # -----------------------------------------

                    cart_item = {

                        "id":
                            item["id"],

                        "name":
                            item["name"],

                        "size":
                            clean_size,

                        "sugar":
                            sugar,

                        "ice":
                            ice,

                        "qty":
                            int(qty),

                        "unit_price":
                            int(unit_price),

                        "total_price":
                            int(total_price)
                    }


                    st.session_state.cart.append(
                        cart_item
                    )


                    st.toast(
                        f"✅ Đã thêm {qty}x {item['name']}"
                    )

            st.divider()


    # =====================================================
    # GIỎ HÀNG
    # =====================================================

    with col_cart:

        st.subheader("🛍️ GIỎ HÀNG")


        if not st.session_state.cart:

            st.info(
                "Giỏ hàng đang trống.\n\n"
                "Vui lòng chọn món!"
            )


        else:

            total_bill = 0

            delete_index = None


            # -------------------------------------------------
            # HIỂN THỊ CART
            # -------------------------------------------------

            for idx, cart_item in enumerate(
                st.session_state.cart
            ):

                with st.expander(
                    f"{cart_item['qty']}x "
                    f"{cart_item['name']} "
                    f"• Size {cart_item['size']}",

                    expanded=True
                ):

                    st.write(
                        f"**Đường:** "
                        f"{cart_item['sugar']}"
                    )

                    st.write(
                        f"**Đá:** "
                        f"{cart_item['ice']}"
                    )

                    st.write(
                        f"**Đơn giá:** "
                        f"{cart_item['unit_price']:,} VNĐ"
                    )

                    st.write(
                        f"**Thành tiền:** "
                        f"{cart_item['total_price']:,} VNĐ"
                    )


                    if st.button(
                        "🗑️ Xóa món",

                        key=f"delete_{idx}",

                        use_container_width=True
                    ):

                        delete_index = idx


                total_bill += int(
                    cart_item["total_price"]
                )


            # -------------------------------------------------
            # XÓA MÓN
            # -------------------------------------------------

            if delete_index is not None:

                st.session_state.cart.pop(
                    delete_index
                )

                st.rerun()


            # -------------------------------------------------
            # TỔNG TIỀN
            # -------------------------------------------------

            st.markdown(
                f"""
                ### 💰 Tổng cộng

                ## :red[{total_bill:,} VNĐ]
                """
            )


            if st.button(
                "🗑️ XÓA TẤT CẢ MÓN",

                use_container_width=True
            ):

                st.session_state.cart = []

                st.rerun()


            st.divider()


            # =================================================
            # THÔNG TIN ĐẶT HÀNG
            # =================================================

            st.subheader(
                "📝 THÔNG TIN ĐẶT HÀNG"
            )


            customer_name = st.text_input(
                "Họ và Tên *",

                key="customer_name"
            )


            table_num = st.text_input(
                "Số Bàn / Số Phòng *",

                key="table_num"
            )


            note = st.text_area(
                "Ghi chú",

                placeholder=(
                    "Ví dụ: ít ngọt, không đá, "
                    "thêm ống hút..."
                ),

                key="order_note"
            )


            pay_method = st.radio(
                "💳 Hình thức thanh toán",

                [
                    "Tiền mặt",
                    "Chuyển khoản QR",
                    "Ví MoMo"
                ],

                key="payment_method"
            )


            # =================================================
            # GỬI ĐƠN
            # =================================================

            if st.button(
                "🚀 GỬI ĐƠN HÀNG",

                type="primary",

                use_container_width=True
            ):

                c_name = customer_name.strip()
                t_num = table_num.strip()
                order_note = note.strip()


                if not c_name:

                    st.error(
                        "❌ Vui lòng nhập Họ và Tên!"
                    )


                elif not t_num:

                    st.error(
                        "❌ Vui lòng nhập Số Bàn / Số Phòng!"
                    )


                elif not st.session_state.cart:

                    st.error(
                        "❌ Giỏ hàng đang trống!"
                    )


                else:

                    conn = get_db_connection()


                    if conn:

                        try:

                            with conn.cursor() as cursor:

                                cursor.execute(
                                    "SET NAMES utf8mb4"
                                )


                                # ---------------------------------
                                # INSERT ORDERS
                                # ---------------------------------

                                sql_order = """
                                    INSERT INTO orders
                                    (
                                        customer_name,
                                        table_num,
                                        total_amount,
                                        payment_method,
                                        note
                                    )
                                    VALUES
                                    (
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s
                                    )
                                """


                                cursor.execute(
                                    sql_order,

                                    (
                                        c_name,
                                        t_num,
                                        int(total_bill),
                                        pay_method,
                                        order_note
                                    )
                                )


                                order_id = cursor.lastrowid


                                # ---------------------------------
                                # INSERT ORDER DETAILS
                                # ---------------------------------

                                sql_detail = """
                                    INSERT INTO order_details
                                    (
                                        order_id,
                                        item_name,
                                        size,
                                        sugar,
                                        ice,
                                        quantity,
                                        unit_price,
                                        total_price
                                    )
                                    VALUES
                                    (
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s,
                                        %s
                                    )
                                """


                                for cart_item in (
                                    st.session_state.cart
                                ):

                                    cursor.execute(
                                        sql_detail,

                                        (
                                            order_id,

                                            cart_item[
                                                "name"
                                            ],

                                            cart_item[
                                                "size"
                                            ],

                                            cart_item[
                                                "sugar"
                                            ],

                                            cart_item[
                                                "ice"
                                            ],

                                            int(
                                                cart_item[
                                                    "qty"
                                                ]
                                            ),

                                            int(
                                                cart_item[
                                                    "unit_price"
                                                ]
                                            ),

                                            int(
                                                cart_item[
                                                    "total_price"
                                                ]
                                            )
                                        )
                                    )


                            conn.commit()


                            # ---------------------------------
                            # LƯU ĐƠN VỪA TẠO
                            # ---------------------------------

                            st.session_state.last_order = {

                                "order_id":
                                    order_id,

                                "customer_name":
                                    c_name,

                                "table_num":
                                    t_num,

                                "pay_method":
                                    pay_method,

                                "note":
                                    order_note,

                                "items":
                                    list(
                                        st.session_state.cart
                                    ),

                                "total":
                                    int(total_bill)
                            }


                            # ---------------------------------
                            # XÓA GIỎ HÀNG
                            # ---------------------------------

                            st.session_state.cart = []


                            st.success(
                                f"🎉 Đặt hàng thành công! "
                                f"Mã đơn: #{order_id}"
                            )


                            st.rerun()


                        except Exception as e:

                            conn.rollback()

                            st.error(
                                "❌ Không thể lưu đơn hàng:\n\n"
                                f"{e}"
                            )

                        finally:

                            conn.close()


    # =====================================================
    # HÓA ĐƠN XÁC NHẬN
    # =====================================================

    if st.session_state.last_order:

        st.divider()

        st.balloons()

        order_info = (
            st.session_state.last_order
        )


        st.success(
            "🎉 ĐẶT HÀNG THÀNH CÔNG!"
        )


        st.markdown(
            """
            ## 🧾 HÓA ĐƠN XÁC NHẬN
            """
        )


        col_a, col_b = st.columns(2)


        with col_a:

            st.write(
                f"**Mã đơn:** "
                f"#{order_info['order_id']}"
            )

            st.write(
                f"**Khách hàng:** "
                f"{order_info['customer_name']}"
            )

            st.write(
                f"**Bàn / Phòng:** "
                f"{order_info['table_num']}"
            )


        with col_b:

            st.write(
                f"**Thanh toán:** "
                f"{order_info['pay_method']}"
            )

            if order_info["note"]:

                st.write(
                    f"**Ghi chú:** "
                    f"{order_info['note']}"
                )


        # -------------------------------------------------
        # BẢNG HÓA ĐƠN
        # -------------------------------------------------

        invoice_rows = []


        for item in order_info["items"]:

            invoice_rows.append(
                {
                    "Món":
                        item["name"],

                    "Size":
                        item["size"],

                    "Đường":
                        item["sugar"],

                    "Đá":
                        item["ice"],

                    "SL":
                        item["qty"],

                    "Đơn giá":
                        item["unit_price"],

                    "Thành tiền":
                        item["total_price"]
                }
            )


        df_invoice = pd.DataFrame(
            invoice_rows
        )


        st.dataframe(
            df_invoice,

            use_container_width=True,

            hide_index=True
        )


        st.markdown(
            f"""
            ## 💰 Tổng tiền:
            :red[{order_info['total']:,} VNĐ]
            """
        )


        if st.button(
            "➕ TẠO ĐƠN MỚI",

            use_container_width=True
        ):

            st.session_state.last_order = None

            st.rerun()


# =========================================================
# TAB 2 - QUẢN LÝ LỊCH SỬ
# =========================================================

with tab_admin:

    st.subheader(
        "📊 LỊCH SỬ ĐƠN HÀNG"
    )

    st.caption(
        "Dữ liệu được lấy trực tiếp từ Aiven MySQL."
    )


    if st.button(
        "🔄 CẬP NHẬT DỮ LIỆU"
    ):

        st.rerun()


    conn = get_db_connection()


    if conn:

        try:

            with conn.cursor() as cursor:

                cursor.execute(
                    "SET NAMES utf8mb4"
                )


            # =================================================
            # QUERY
            # =================================================

            query = """
                SELECT

                    o.id AS order_id,

                    o.customer_name
                        AS customer_name,

                    o.table_num
                        AS table_num,

                    o.total_amount
                        AS total_amount,

                    o.payment_method
                        AS payment_method,

                    o.note
                        AS note,

                    o.created_at
                        AS created_at

                FROM orders o

                ORDER BY
                    o.created_at DESC,
                    o.id DESC
            """


            df_orders = pd.read_sql(
                query,
                conn
            )


            # =================================================
            # KIỂM TRA DỮ LIỆU
            # =================================================

            if df_orders.empty:

                st.info(
                    "📭 Chưa có đơn hàng nào."
                )


            else:

                # -------------------------------------------------
                # ÉP KIỂU AN TOÀN
                # -------------------------------------------------

                df_orders["total_amount"] = pd.to_numeric(
                    df_orders["total_amount"],
                    errors="coerce"
                ).fillna(0)


                df_orders["order_id"] = pd.to_numeric(
                    df_orders["order_id"],
                    errors="coerce"
                ).fillna(0)


                # -------------------------------------------------
                # THỐNG KÊ
                # -------------------------------------------------

                total_orders = len(
                    df_orders
                )


                total_revenue = int(
                    df_orders[
                        "total_amount"
                    ].sum()
                )


                col1, col2 = st.columns(2)


                with col1:

                    st.metric(
                        "📦 Tổng số đơn",

                        f"{total_orders:,}"
                    )


                with col2:

                    st.metric(
                        "💰 Tổng doanh thu",

                        f"{total_revenue:,} VNĐ"
                    )


                st.divider()


                # =================================================
                # LẤY CHI TIẾT MÓN
                # =================================================

                detail_query = """
                    SELECT

                        order_id,

                        item_name,

                        size,

                        sugar,

                        ice,

                        quantity

                    FROM order_details

                    ORDER BY id ASC
                """


                df_details = pd.read_sql(
                    detail_query,
                    conn
                )


                # -------------------------------------------------
                # TẠO CHI TIẾT ĐƠN
                # -------------------------------------------------

                if not df_details.empty:

                    detail_groups = {}


                    for _, row in df_details.iterrows():

                        order_id = int(
                            row["order_id"]
                        )


                        text = (
                            f"{int(row['quantity'])}x "
                            f"{row['item_name']} "
                            f"(Size {row['size']}, "
                            f"Đường {row['sugar']}, "
                            f"Đá {row['ice']})"
                        )


                        if order_id not in detail_groups:

                            detail_groups[
                                order_id
                            ] = []


                        detail_groups[
                            order_id
                        ].append(text)


                    df_orders[
                        "order_details"
                    ] = df_orders[
                        "order_id"
                    ].apply(

                        lambda x:
                            " | ".join(
                                detail_groups.get(
                                    int(x),
                                    []
                                )
                            )
                    )


                else:

                    df_orders[
                        "order_details"
                    ] = ""


                # =================================================
                # TẠO DATAFRAME HIỂN THỊ
                # =================================================

                df_display = pd.DataFrame(
                    {
                        "Mã Đơn":
                            df_orders[
                                "order_id"
                            ].astype(int),

                        "Tên Khách Hàng":
                            df_orders[
                                "customer_name"
                            ].fillna(""),

                        "Số Bàn / Phòng":
                            df_orders[
                                "table_num"
                            ].fillna(""),

                        "Tên Món":
                            df_orders[
                                "order_details"
                            ],

                        "Tổng Tiền (VNĐ)":
                            df_orders[
                                "total_amount"
                            ].astype(int),

                        "Thanh Toán":
                            df_orders[
                                "payment_method"
                            ].fillna(""),

                        "Ghi Chú":
                            df_orders[
                                "note"
                            ].fillna(""),

                        "Thời Gian":
                            pd.to_datetime(
                                df_orders[
                                    "created_at"
                                ],
                                errors="coerce"
                            )
                    }
                )


                # =================================================
                # HIỂN THỊ
                # =================================================

                st.dataframe(

                    df_display,

                    use_container_width=True,

                    hide_index=True,

                    column_config={

                        "Mã Đơn":
                            st.column_config.NumberColumn(
                                "Mã Đơn",
                                format="%d"
                            ),

                        "Tên Khách Hàng":
                            st.column_config.TextColumn(
                                "Tên Khách Hàng"
                            ),

                        "Số Bàn / Phòng":
                            st.column_config.TextColumn(
                                "Số Bàn / Phòng"
                            ),

                        "Tên Món":
                            st.column_config.TextColumn(
                                "Tên Món",
                                width="large"
                            ),

                        "Tổng Tiền (VNĐ)":
                            st.column_config.NumberColumn(
                                "Tổng Tiền (VNĐ)",
                                format="%d VNĐ"
                            ),

                        "Thanh Toán":
                            st.column_config.TextColumn(
                                "Thanh Toán"
                            ),

                        "Ghi Chú":
                            st.column_config.TextColumn(
                                "Ghi Chú"
                            ),

                        "Thời Gian":
                            st.column_config.DatetimeColumn(
                                "Thời Gian",
                                format="DD/MM/YYYY HH:mm"
                            )
                    }
                )


                # =================================================
                # XUẤT EXCEL
                # =================================================

                st.divider()

                st.subheader(
                    "📥 Xuất dữ liệu"
                )


                csv_data = (
                    df_display.to_csv(
                        index=False
                    ).encode("utf-8-sig")
                )


                st.download_button(

                    label="📥 TẢI LỊCH SỬ ĐƠN HÀNG CSV",

                    data=csv_data,

                    file_name="lich_su_don_hang.csv",

                    mime="text/csv",

                    use_container_width=True
                )


        except Exception as e:

            st.error(
                "❌ LỖI TRUY VẤN DỮ LIỆU MYSQL:\n\n"
                f"{e}"
            )

        finally:

            conn.close()


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "☕ CFCU Coffee • Order System • "
    "Powered by Streamlit & Aiven MySQL"
)
```
