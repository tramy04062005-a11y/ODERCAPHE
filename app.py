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
# THÔNG TIN KẾT NỐI MYSQL AIVEN
# =========================================================

DB_HOST = "mysql-24eda0f5-tramy04062005-899b.k.aivencloud.com"
DB_PORT = 13321
DB_USER = "avnadmin"
DB_PASSWORD = "AVNS_eyALQ_tYt5oQ7pItFnm"
DB_NAME = "defaultdb"


# =========================================================
# HÀM KẾT NỐI MYSQL AIVEN
# =========================================================

def get_db_connection():

    try:

        connection = pymysql.connect(
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

            # Aiven yêu cầu SSL
            ssl={
                "check_hostname": False
            }
        )

        return connection

    except Exception as e:

        st.error(
            f"❌ LỖI KẾT NỐI MYSQL AIVEN:\n\n{e}"
        )

        return None


# =========================================================
# KHỞI TẠO BẢNG MYSQL
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

            # =================================================
            # BẢNG ORDERS
            # =================================================

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


            # =================================================
            # BẢNG ORDER_DETAILS
            # =================================================

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
            f"❌ LỖI KHỞI TẠO BẢNG MYSQL:\n\n{e}"
        )

        return False

    finally:

        conn.close()


# =========================================================
# KHỞI TẠO DATABASE
# =========================================================

database_ready = init_db()


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.main-title {
    color: #3E2723;
    font-family: 'Helvetica Neue', sans-serif;
    font-weight: 700;
    text-align: center;
    margin-bottom: 10px;
}

.stButton > button {
    background-color: #6D4C41;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #3E2723;
    color: white;
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


# =========================================================
# MENU
# =========================================================

MENU = {

    "Cà Phê Truyền Thống": [

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
            "desc": "Nhiều sữa ít cà phê, dễ uống"
        },

        {
            "id": "c4",
            "name": "Cà Phê Muối",
            "price": 35000,
            "desc": "Vị mặn nhẹ tôn lên nét béo ngậy"
        }

    ],

    "Trà & Trà Sữa": [

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
            "desc": "Ngọt dịu hương hoa lài và vải tươi"
        },

        {
            "id": "t3",
            "name": "Trà Sữa Oolong",
            "price": 42000,
            "desc": "Đậm vị trà Oolong kết hợp kem béo"
        }

    ],

    "Bánh & Đi Kèm": [

        {
            "id": "b1",
            "name": "Bánh Croissant",
            "price": 30000,
            "desc": "Bánh sừng bò nướng giòn rụm"
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
# SIDEBAR - KIỂM TRA DATABASE
# =========================================================

with st.sidebar:

    st.markdown("## 🗄️ MYSQL AIVEN")

    if database_ready:

        st.success("🟢 Database đã sẵn sàng")

    else:

        st.error("🔴 Database chưa kết nối")


    if st.button(
        "🔌 KIỂM TRA KẾT NỐI",
        use_container_width=True
    ):

        test_conn = get_db_connection()

        if test_conn:

            try:

                with test_conn.cursor() as cursor:

                    cursor.execute("""
                        SELECT
                            VERSION() AS version,
                            DATABASE() AS database_name
                    """)

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
                    f"❌ Lỗi kiểm tra: {e}"
                )

            finally:

                test_conn.close()


# =========================================================
# HEADER
# =========================================================

col_banner, col_title = st.columns([1, 2])


with col_banner:

    if os.path.exists("CFCU.jpg"):

        st.image(
            Image.open("CFCU.jpg"),
            use_container_width=True
        )

    else:

        st.info(
            "📌 Thêm file CFCU.jpg "
            "vào thư mục cùng với app.py"
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

    st.caption(
        "Thưởng thức hương vị cà phê đậm đà mỗi ngày. "
        "Đặt món nhanh chóng & tiện lợi!"
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

    col_menu, col_cart = st.columns([2, 1])


    # =====================================================
    # MENU
    # =====================================================

    with col_menu:

        st.subheader("📋 Menu Quán")

        category = st.radio(
            "Chọn danh mục:",
            list(MENU.keys()),
            horizontal=True
        )


        for item in MENU[category]:

            with st.container():

                st.markdown(
                    f"""
                    <div class="card">

                        <h4>{item['name']}</h4>

                        <p style="color:#666;
                                  margin-bottom:5px;">
                            {item['desc']}
                        </p>

                        <p class="price-tag">
                            {item['price']:,} VNĐ
                        </p>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


                col_opt1, col_opt2, col_opt3 = st.columns(3)


                with col_opt1:

                    size = st.selectbox(
                        f"Size ({item['name']})",

                        [
                            "Nhỏ (S)",
                            "Vừa (M) (+5k)",
                            "Lớn (L) (+10k)"
                        ],

                        key=f"size_{item['id']}"
                    )


                with col_opt2:

                    sugar = st.select_slider(
                        f"Đường ({item['name']})",

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
                        f"Đá ({item['name']})",

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


                col_qty, col_btn = st.columns([1, 2])


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
                    st.write("")

                    if st.button(
                        f"🛒 Thêm {item['name']}",
                        key=f"add_{item['id']}"
                    ):

                        extra = 0

                        if "M" in size:

                            extra = 5000

                        elif "L" in size:

                            extra = 10000


                        unit_price = (
                            item["price"] + extra
                        )


                        cart_item = {

                            "id":
                                item["id"],

                            "name":
                                item["name"],

                            "size":
                                size.split()[0],

                            "sugar":
                                sugar,

                            "ice":
                                ice,

                            "qty":
                                qty,

                            "unit_price":
                                unit_price,

                            "total_price":
                                unit_price * qty
                        }


                        st.session_state.cart.append(
                            cart_item
                        )


                        st.toast(
                            f"Đã thêm {qty}x "
                            f"{item['name']} vào giỏ hàng!",
                            icon="✅"
                        )


                st.divider()


    # =====================================================
    # GIỎ HÀNG
    # =====================================================

    with col_cart:

        st.subheader("🛍️ Giỏ Hàng Của Bạn")


        if not st.session_state.cart:

            st.info(
                "Giỏ hàng đang trống. "
                "Vui lòng chọn món!"
            )


        else:

            total_bill = 0

            to_delete = None


            for idx, item in enumerate(
                st.session_state.cart
            ):

                with st.expander(
                    f"{item['qty']}x "
                    f"{item['name']} "
                    f"({item['size']})",

                    expanded=True
                ):

                    st.write(
                        f"**Đường:** "
                        f"{item['sugar']} "
                        f"| **Đá:** "
                        f"{item['ice']}"
                    )

                    st.write(
                        f"**Đơn giá:** "
                        f"{item['unit_price']:,} VNĐ"
                    )

                    st.write(
                        f"**Thành tiền:** "
                        f"{item['total_price']:,} VNĐ"
                    )


                    if st.button(
                        "🗑️ Xóa",
                        key=f"del_{idx}"
                    ):

                        to_delete = idx


                total_bill += item[
                    "total_price"
                ]


            if to_delete is not None:

                st.session_state.cart.pop(
                    to_delete
                )

                st.rerun()


            st.markdown(
                f"""
                ### **Tổng cộng:
                :red[{total_bill:,} VNĐ]**
                """
            )


            if st.button(
                "🗑️ Xóa tất cả món",
                use_container_width=True
            ):

                st.session_state.cart = []

                st.rerun()


            st.divider()


            # =================================================
            # THÔNG TIN ĐẶT HÀNG
            # =================================================

            st.subheader(
                "📝 Thông Tin Đặt Hàng"
            )


            customer_name = st.text_input(
                "Họ và Tên*",
                key="cust_name_input"
            )


            table_num = st.text_input(
                "Số Bàn / Số Phòng*",
                key="table_num_input"
            )


            note = st.text_area(
                "Ghi chú thêm "
                "(vd: Ít ngọt, không đá...)",
                key="note_input"
            )


            pay_method = st.radio(
                "Hình thức thanh toán",

                [
                    "Tiền mặt",
                    "Chuyển khoản QR",
                    "Ví MoMo"
                ]
            )


            # =================================================
            # GỬI ĐƠN HÀNG
            # =================================================

            if st.button(
                "🚀 GỬI ĐƠN HÀNG",
                type="primary",
                use_container_width=True
            ):

                c_name = customer_name.strip()

                t_num = table_num.strip()


                if not c_name or not t_num:

                    st.error(
                        "❌ Vui lòng điền đầy đủ "
                        "Họ tên và Số bàn!"
                    )


                else:

                    conn = get_db_connection()


                    if conn:

                        try:

                            with conn.cursor() as cursor:

                                cursor.execute(
                                    "SET NAMES utf8mb4"
                                )


                                # =================================
                                # LƯU ĐƠN HÀNG
                                # =================================

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
                                    (%s, %s, %s, %s, %s)
                                """


                                cursor.execute(
                                    sql_order,

                                    (
                                        c_name,
                                        t_num,
                                        total_bill,
                                        pay_method,
                                        note.strip()
                                    )
                                )


                                order_id = (
                                    cursor.lastrowid
                                )


                                # =================================
                                # LƯU CHI TIẾT ĐƠN
                                # =================================

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

                                            cart_item[
                                                "qty"
                                            ],

                                            cart_item[
                                                "unit_price"
                                            ],

                                            cart_item[
                                                "total_price"
                                            ]
                                        )
                                    )


                            conn.commit()


                            # =================================
                            # LƯU ĐƠN VỪA TẠO
                            # =================================

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
                                    note.strip(),

                                "items":
                                    list(
                                        st.session_state.cart
                                    ),

                                "total":
                                    total_bill
                            }


                            st.session_state.cart = []


                            st.success(
                                f"🎉 Đặt hàng thành công! "
                                f"Mã đơn: #{order_id}"
                            )


                            st.rerun()


                        except Exception as e:

                            conn.rollback()

                            st.error(
                                "❌ Lỗi khi lưu đơn hàng:\n\n"
                                f"{e}"
                            )

                        finally:

                            conn.close()


    # =====================================================
    # HÓA ĐƠN XÁC NHẬN
    # =====================================================

    if st.session_state.last_order:

        st.balloons()


        order_info = (
            st.session_state.last_order
        )


        st.success(
            "🎉 Đặt hàng thành công! "
            "Đơn hàng đã được lưu vào "
            "Aiven MySQL."
        )


        st.markdown("---")


        st.markdown(
            "### 📜 HÓA ĐƠN XÁC NHẬN"
        )


        st.write(
            f"**Mã đơn:** "
            f"#{order_info['order_id']}"
        )


        st.write(
            f"**Khách hàng:** "
            f"{order_info['customer_name']}"
        )


        st.write(
            f"**Vị trí:** "
            f"Bàn / Phòng "
            f"{order_info['table_num']}"
        )


        st.write(
            f"**Thanh toán:** "
            f"{order_info['pay_method']}"
        )


        if order_info["note"]:

            st.write(
                f"**Ghi chú:** "
                f"{order_info['note']}"
            )


        df_cart = pd.DataFrame(
            order_info["items"]
        )[
            [
                "name",
                "size",
                "qty",
                "total_price"
            ]
        ]


        df_cart.columns = [
            "Món",
            "Size",
            "SL",
            "Tổng (VNĐ)"
        ]


        st.table(df_cart)


        st.markdown(
            f"""
            ### 💰 Tổng tiền:
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
# TAB 2 - QUẢN LÝ LỊCH SỬ ĐƠN HÀNG
# =========================================================

with tab_admin:

    st.subheader(
        "📊 Danh Sách Chi Tiết Đơn Hàng "
        "(Aiven MySQL)"
    )


    if st.button(
        "🔄 Cập nhật dữ liệu",
        use_container_width=False
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
            # TRUY VẤN ĐƠN HÀNG
            # =================================================

            query = """

                SELECT

                    o.id AS `Mã Đơn`,

                    o.customer_name
                        AS `Tên Khách Hàng`,

                    o.table_num
                        AS `Số Bàn`,

                    GROUP_CONCAT(

                        CONCAT(

                            d.quantity,
                            'x ',
                            d.item_name,
                            ' (',
                            d.size,
                            ', Đường: ',
                            d.sugar,
                            ', Đá: ',
                            d.ice,
                            ')'

                        )

                        SEPARATOR ' | '

                    ) AS `Chi Tiết Món Đặt`,

                    o.total_amount
                        AS `Tổng Tiền (VNĐ)`,

                    o.payment_method
                        AS `Hình Thức Thanh Toán`,

                    o.note
                        AS `Ghi Chú`,

                    o.created_at
                        AS `Thời Gian Tạo`

                FROM orders o

                LEFT JOIN order_details d
                    ON o.id = d.order_id

                GROUP BY
                    o.id,
                    o.customer_name,
                    o.table_num,
                    o.total_amount,
                    o.payment_method,
                    o.note,
                    o.created_at

                ORDER BY
                    o.created_at DESC

            """


            df_orders = pd.read_sql(
                query,
                conn
            )


            # =================================================
            # HIỂN THỊ
            # =================================================

            if df_orders.empty:

                st.info(
                    "📭 Chưa có đơn hàng nào "
                    "trong CSDL Aiven."
                )


            else:

                # =============================================
                # THỐNG KÊ
                # =============================================

                total_orders = len(
                    df_orders
                )


                total_revenue = int(
                    df_orders[
                        "Tổng Tiền (VNĐ)"
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


                # =============================================
                # BẢNG LỊCH SỬ
                # =============================================

                st.dataframe(

                    df_orders,

                    use_container_width=True,

                    hide_index=True,

                    column_config={

                        "Mã Đơn":
                            st.column_config.NumberColumn(
                                width="small"
                            ),

                        "Tên Khách Hàng":
                            st.column_config.TextColumn(
                                width="medium"
                            ),

                        "Số Bàn":
                            st.column_config.TextColumn(
                                width="small"
                            ),

                        "Chi Tiết Món Đặt":
                            st.column_config.TextColumn(
                                width="large"
                            ),

                        "Tổng Tiền (VNĐ)":
                            st.column_config.NumberColumn(
                                format="%d VNĐ"
                            ),

                        "Hình Thức Thanh Toán":
                            st.column_config.TextColumn(
                                width="medium"
                            ),

                        "Thời Gian Tạo":
                            st.column_config.DatetimeColumn(
                                format="DD/MM/YYYY HH:mm"
                            )
                    }
                )


        except Exception as e:

            st.error(
                "❌ LỖI TRUY VẤN DỮ LIỆU MYSQL:\n\n"
                f"{e}"
            )

        finally:

            conn.close()
