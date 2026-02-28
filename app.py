"""
U-Meking Sales Engine
A local web application for generating product catalogs and quotations.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

import data_manager as dm
import pdf_generator as pdfgen

st.set_page_config(
    page_title="U-Meking Sales Engine",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        color: #003366;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666666;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background-color: #003366;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .stButton > button:hover {
        background-color: #004488;
        color: white;
    }
    .product-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #fafafa;
    }
    .category-header {
        background-color: #003366;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "selected_products" not in st.session_state:
        st.session_state.selected_products = []
    if "quote_items" not in st.session_state:
        st.session_state.quote_items = []
    if "editing_product" not in st.session_state:
        st.session_state.editing_product = None


def main():
    init_session_state()
    dm.init_directories()
    
    st.sidebar.markdown('<p class="main-header">U-Meking</p>', unsafe_allow_html=True)
    st.sidebar.markdown('<p class="sub-header">Sales Engine</p>', unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Dashboard", "📦 Product Inventory", "📚 Catalog Creator", "💰 Quotation Builder", "⚙️ Settings"],
        index=0
    )
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📦 Product Inventory":
        show_product_inventory()
    elif page == "📚 Catalog Creator":
        show_catalog_creator()
    elif page == "💰 Quotation Builder":
        show_quotation_builder()
    elif page == "⚙️ Settings":
        show_settings()


def show_dashboard():
    """Display dashboard with overview statistics."""
    st.markdown('<p class="main-header">Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Welcome to U-Meking Sales Engine</p>', unsafe_allow_html=True)
    
    df = dm.get_products_df()
    settings = dm.get_settings()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(df))
    
    with col2:
        categories = df["category"].nunique() if len(df) > 0 else 0
        st.metric("Categories", categories)
    
    with col3:
        avg_price = df["unit_price"].mean() if len(df) > 0 else 0
        st.metric("Avg. Price", f"${avg_price:.2f}")
    
    with col4:
        total_value = df["unit_price"].sum() if len(df) > 0 else 0
        st.metric("Catalog Value", f"${total_value:.2f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Quick Actions")
        st.info("Use the sidebar navigation to access features:")
        st.markdown("""
        - **📦 Product Inventory** - Add/Edit products
        - **📚 Catalog Creator** - Generate PDF catalogs
        - **💰 Quotation Builder** - Create price quotes
        - **⚙️ Settings** - Configure company info
        """)
    
    with col2:
        st.subheader("Company Info")
        st.write(f"**Company:** {settings.get('company_name', 'N/A')}")
        st.write(f"**Website:** {settings.get('company_website', 'N/A')}")
        st.write(f"**Phone:** {settings.get('company_phone', 'N/A')}")
        st.write(f"**Prepared By:** {settings.get('prepared_by', 'N/A')}")
    
    if len(df) > 0:
        st.markdown("---")
        st.subheader("Recent Products")
        
        recent_df = df.tail(5)[["sku", "name", "category", "unit_price"]]
        st.dataframe(recent_df, use_container_width=True, hide_index=True)


def show_product_inventory():
    """Display product inventory management page."""
    st.markdown('<p class="main-header">Product Inventory</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Manage your product database</p>', unsafe_allow_html=True)
    
    editing_sku = st.session_state.get("editing_product")
    
    if editing_sku:
        show_product_form()
    else:
        tab1, tab2 = st.tabs(["📋 Product List", "➕ Add New Product"])
        
        with tab1:
            show_product_list()
        
        with tab2:
            show_product_form()


def show_product_list():
    """Display list of all products."""
    df = dm.get_products_df()
    
    if len(df) == 0:
        st.info("No products in inventory. Add your first product using the 'Add/Edit Product' tab.")
        return
    
    col1, col2 = st.columns([1, 3])
    with col1:
        categories = ["All"] + dm.get_categories()
        selected_category = st.selectbox("Filter by Category", categories)
    
    with col2:
        search = st.text_input("Search products", placeholder="Enter SKU or product name...")
    
    filtered_df = df.copy()
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]
    
    if search:
        mask = (
            filtered_df["sku"].str.contains(search, case=False, na=False) |
            filtered_df["name"].str.contains(search, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} products**")
    
    for _, product in filtered_df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
            
            with col1:
                if product["image_path"] and os.path.exists(str(product["image_path"])):
                    st.image(product["image_path"], width=80)
                else:
                    st.markdown("🖼️ No Image")
            
            with col2:
                st.markdown(f"**{product['name']}**")
                st.caption(f"SKU: {product['sku']} | Category: {product['category']}")
                st.caption(f"Price: ${product['unit_price']:.2f} | MOQ: {product.get('moq', 'N/A')}")
            
            with col3:
                if st.button("✏️ Edit", key=f"edit_{product['sku']}"):
                    st.session_state.editing_product = product["sku"]
                    st.rerun()
            
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{product['sku']}"):
                    if dm.delete_product(product["sku"]):
                        st.success(f"Deleted {product['name']}")
                        st.rerun()
            
            st.markdown("---")


def show_product_form():
    """Display form for adding/editing products."""
    editing_sku = st.session_state.get("editing_product")
    existing_product = None
    
    if editing_sku:
        existing_product = dm.get_product_by_sku(editing_sku)
        st.subheader(f"Editing: {existing_product['name']}")
        if st.button("Cancel Edit"):
            st.session_state.editing_product = None
            st.rerun()
    else:
        st.subheader("Add New Product")
    
    with st.form("product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            sku = st.text_input(
                "SKU *",
                value=existing_product["sku"] if existing_product else "",
                placeholder="e.g., MPS-090226-01",
                disabled=bool(existing_product)
            )
            
            name = st.text_input(
                "Product Name *",
                value=existing_product["name"] if existing_product else "",
                placeholder="e.g., Signature Metal Ballpoint Pen"
            )
            
            categories = dm.get_categories()
            category_options = categories + ["+ New Category"]
            
            if existing_product and existing_product["category"] in categories:
                default_idx = categories.index(existing_product["category"])
            else:
                default_idx = 0 if categories else 0
            
            category_select = st.selectbox(
                "Category",
                category_options if category_options else ["+ New Category"],
                index=default_idx if category_options and default_idx < len(category_options) else 0
            )
            
            if category_select == "+ New Category":
                category = st.text_input("New Category Name", placeholder="e.g., WRITING INSTRUMENTS")
            else:
                category = category_select
            
            unit_price = st.number_input(
                "Unit Price (USD) *",
                min_value=0.0,
                value=float(existing_product["unit_price"]) if existing_product else 0.0,
                step=0.01,
                format="%.2f"
            )
            
            moq = st.number_input(
                "MOQ (Minimum Order Quantity)",
                min_value=1,
                value=int(existing_product.get("moq", 100)) if existing_product else 100,
                step=1
            )
        
        with col2:
            st.markdown("**Product Images**")
            image_file = st.file_uploader(
                "Main Image (Used in PDF)",
                type=["jpg", "jpeg", "png"],
                help="This is the primary image shown in catalogs and quotations"
            )
            
            if existing_product and existing_product.get("image_path") and os.path.exists(str(existing_product["image_path"])):
                st.image(existing_product["image_path"], width=100, caption="Current Main Image")
            
            img_col1, img_col2 = st.columns(2)
            with img_col1:
                image_file_2 = st.file_uploader(
                    "Backup Image 2",
                    type=["jpg", "jpeg", "png"],
                    help="Internal backup only"
                )
                if existing_product and existing_product.get("image_path_2") and os.path.exists(str(existing_product.get("image_path_2", ""))):
                    st.image(existing_product["image_path_2"], width=60, caption="Image 2")
            
            with img_col2:
                image_file_3 = st.file_uploader(
                    "Backup Image 3",
                    type=["jpg", "jpeg", "png"],
                    help="Internal backup only"
                )
                if existing_product and existing_product.get("image_path_3") and os.path.exists(str(existing_product.get("image_path_3", ""))):
                    st.image(existing_product["image_path_3"], width=60, caption="Image 3")
            
            packaging_rate = st.number_input(
                "Packaging Rate (pcs/carton)",
                min_value=1,
                value=int(existing_product.get("packaging_rate", 200)) if existing_product else 200,
                step=1
            )
            
            st.markdown("**Carton Dimensions (cm)**")
            col_l, col_w, col_h = st.columns(3)
            with col_l:
                carton_l = st.number_input("L", min_value=0.0, 
                    value=float(existing_product.get("carton_l", 0)) if existing_product else 0.0, step=1.0)
            with col_w:
                carton_w = st.number_input("W", min_value=0.0, 
                    value=float(existing_product.get("carton_w", 0)) if existing_product else 0.0, step=1.0)
            with col_h:
                carton_h = st.number_input("H", min_value=0.0, 
                    value=float(existing_product.get("carton_h", 0)) if existing_product else 0.0, step=1.0)
            
            gw_per_ctn = st.number_input(
                "G.W. per Carton (kg)",
                min_value=0.0,
                value=float(existing_product.get("gw_per_ctn", 0)) if existing_product else 0.0,
                step=0.1,
                format="%.2f"
            )
        
        description = st.text_area(
            "Description / Specifications *",
            value=existing_product["description"] if existing_product else "",
            height=150,
            placeholder="Enter specifications, one per line:\nMaterial: Solid ABS\nInk: 1.0mm Black\nBranding: Silk Screen",
            help="Enter product specifications, one per line. Each line will appear as a bullet point."
        )
        
        st.markdown("**Supplier Links (Internal Use Only)**")
        st.caption("These fields are for internal reference only and will NOT appear in catalogs or quotations.")
        
        sup_col1, sup_col2, sup_col3 = st.columns(3)
        with sup_col1:
            supplier_link = st.text_input(
                "Supplier Link 1",
                value=existing_product.get("supplier_link", "") if existing_product else "",
                placeholder="https://1688.com/..."
            )
        with sup_col2:
            supplier_link_2 = st.text_input(
                "Supplier Link 2",
                value=existing_product.get("supplier_link_2", "") if existing_product else "",
                placeholder="https://1688.com/..."
            )
        with sup_col3:
            supplier_link_3 = st.text_input(
                "Supplier Link 3",
                value=existing_product.get("supplier_link_3", "") if existing_product else "",
                placeholder="https://1688.com/..."
            )
        
        submit_btn = st.form_submit_button(
            "Update Product" if existing_product else "Add Product",
            use_container_width=True
        )
        
        if submit_btn:
            if not sku or not name or not description:
                st.error("Please fill in all required fields (SKU, Name, Description)")
            else:
                if existing_product:
                    success = dm.update_product(
                        sku=sku,
                        name=name,
                        category=category,
                        description=description,
                        unit_price=unit_price,
                        moq=moq,
                        image_file=image_file,
                        image_file_2=image_file_2,
                        image_file_3=image_file_3,
                        packaging_rate=packaging_rate,
                        carton_l=carton_l,
                        carton_w=carton_w,
                        carton_h=carton_h,
                        gw_per_ctn=gw_per_ctn,
                        supplier_link=supplier_link,
                        supplier_link_2=supplier_link_2,
                        supplier_link_3=supplier_link_3
                    )
                    if success:
                        st.success(f"Product '{name}' updated successfully!")
                        st.session_state.editing_product = None
                        st.rerun()
                    else:
                        st.error("Failed to update product")
                else:
                    success = dm.add_product(
                        sku=sku,
                        name=name,
                        category=category,
                        description=description,
                        unit_price=unit_price,
                        moq=moq,
                        image_file=image_file,
                        image_file_2=image_file_2,
                        image_file_3=image_file_3,
                        packaging_rate=packaging_rate,
                        carton_l=carton_l,
                        carton_w=carton_w,
                        carton_h=carton_h,
                        gw_per_ctn=gw_per_ctn,
                        supplier_link=supplier_link,
                        supplier_link_2=supplier_link_2,
                        supplier_link_3=supplier_link_3
                    )
                    if success:
                        st.success(f"Product '{name}' added successfully!")
                        st.rerun()
                    else:
                        st.error(f"SKU '{sku}' already exists. Please use a different SKU.")


def show_catalog_creator():
    """Display catalog creation page."""
    st.markdown('<p class="main-header">Catalog Creator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Generate professional product catalogs</p>', unsafe_allow_html=True)
    
    df = dm.get_products_df()
    settings = dm.get_settings()
    
    if len(df) == 0:
        st.warning("No products available. Please add products first.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Select Products")
        
        categories = ["All"] + dm.get_categories()
        selected_category = st.selectbox("Filter by Category", categories, key="catalog_category")
        
        if selected_category != "All":
            filtered_df = df[df["category"] == selected_category]
        else:
            filtered_df = df
        
        if st.button("Select All"):
            st.session_state.selected_products = filtered_df["sku"].tolist()
            st.rerun()
        
        if st.button("Clear Selection"):
            st.session_state.selected_products = []
            st.rerun()
        
        for _, product in filtered_df.iterrows():
            col_a, col_b, col_c = st.columns([0.5, 1, 3])
            
            with col_a:
                is_selected = product["sku"] in st.session_state.selected_products
                if st.checkbox("", value=is_selected, key=f"cat_sel_{product['sku']}"):
                    if product["sku"] not in st.session_state.selected_products:
                        st.session_state.selected_products.append(product["sku"])
                else:
                    if product["sku"] in st.session_state.selected_products:
                        st.session_state.selected_products.remove(product["sku"])
            
            with col_b:
                if product["image_path"] and os.path.exists(str(product["image_path"])):
                    st.image(product["image_path"], width=60)
                else:
                    st.write("🖼️")
            
            with col_c:
                st.markdown(f"**{product['name']}**")
                st.caption(f"{product['sku']} | ${product['unit_price']:.2f}")
    
    with col2:
        st.subheader("Catalog Settings")
        
        catalog_number = st.text_input(
            "Catalog Number",
            value=f"CAT-{datetime.now().strftime('%Y')}-001",
            placeholder="e.g., CAT-2026-001"
        )
        
        catalog_date = st.date_input("Catalog Date", value=datetime.now())
        
        st.markdown("---")
        st.markdown(f"**Selected Products:** {len(st.session_state.selected_products)}")
        
        if st.session_state.selected_products:
            st.markdown("**Products in catalog:**")
            for sku in st.session_state.selected_products[:10]:
                product = dm.get_product_by_sku(sku)
                if product:
                    st.caption(f"• {product['name']}")
            if len(st.session_state.selected_products) > 10:
                st.caption(f"... and {len(st.session_state.selected_products) - 10} more")
        
        st.markdown("---")
        
        if st.button("📄 Generate Catalog PDF", use_container_width=True, type="primary"):
            if not st.session_state.selected_products:
                st.error("Please select at least one product")
            else:
                products = []
                for sku in st.session_state.selected_products:
                    product = dm.get_product_by_sku(sku)
                    if product:
                        products.append(product)
                
                with st.spinner("Generating PDF..."):
                    pdf_buffer = pdfgen.generate_catalog_pdf(
                        products=products,
                        settings=settings,
                        catalog_number=catalog_number,
                        catalog_date=catalog_date.strftime("%B %d, %Y")
                    )
                
                st.download_button(
                    label="⬇️ Download Catalog PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"catalog_{catalog_number}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("Catalog generated successfully!")


def show_quotation_builder():
    """Display quotation builder page."""
    st.markdown('<p class="main-header">Quotation Builder</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Create professional price quotations</p>', unsafe_allow_html=True)
    
    df = dm.get_products_df()
    settings = dm.get_settings()
    
    if len(df) == 0:
        st.warning("No products available. Please add products first.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Customer Information")
        
        cust_col1, cust_col2 = st.columns(2)
        with cust_col1:
            customer_name = st.text_input("Customer Name *", placeholder="e.g., Christian Wielaender")
            customer_address = st.text_input("Address", placeholder="e.g., Süßgraben 11, 3392 Dunkelsteinerwald, Austria")
        with cust_col2:
            customer_email = st.text_input("Email", placeholder="e.g., christian@wielaender.co.at")
            customer_phone = st.text_input("Phone", placeholder="e.g., 43-677-61530828")
        
        customer_id = st.text_input("Customer ID", value=f"{datetime.now().strftime('%d%m%Y')}01", placeholder="e.g., 2102202601")
        
        st.markdown("---")
        st.subheader("Add Products to Quote")
        
        add_col1, add_col2, add_col3 = st.columns([3, 1, 1])
        
        with add_col1:
            product_options = {f"{p['sku']} - {p['name']}": p['sku'] for _, p in df.iterrows()}
            selected_product_label = st.selectbox("Select Product", list(product_options.keys()))
        
        with add_col2:
            quantity = st.number_input("Quantity", min_value=1, value=200, step=100)
        
        with add_col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add", use_container_width=True):
                selected_sku = product_options[selected_product_label]
                
                existing_idx = None
                for i, item in enumerate(st.session_state.quote_items):
                    if item["sku"] == selected_sku:
                        existing_idx = i
                        break
                
                product = dm.get_product_by_sku(selected_sku)
                quote_item = {
                    "sku": product["sku"],
                    "name": product["name"],
                    "description": product["description"],
                    "unit_price": product["unit_price"],
                    "quantity": quantity,
                    "image_path": product.get("image_path", ""),
                    "packaging_rate": product.get("packaging_rate", 1),
                    "carton_l": product.get("carton_l", 0),
                    "carton_w": product.get("carton_w", 0),
                    "carton_h": product.get("carton_h", 0),
                    "gw_per_ctn": product.get("gw_per_ctn", 0)
                }
                
                if existing_idx is not None:
                    st.session_state.quote_items[existing_idx] = quote_item
                else:
                    st.session_state.quote_items.append(quote_item)
                st.rerun()
        
        st.markdown("---")
        st.subheader("Quote Items")
        
        if not st.session_state.quote_items:
            st.info("No products added to quote yet. Use the selector above to add products.")
        else:
            for i, item in enumerate(st.session_state.quote_items):
                item_col1, item_col2, item_col3, item_col4, item_col5 = st.columns([1, 3, 1, 1, 0.5])
                
                with item_col1:
                    if item.get("image_path") and os.path.exists(str(item["image_path"])):
                        st.image(item["image_path"], width=50)
                    else:
                        st.write("🖼️")
                
                with item_col2:
                    st.markdown(f"**{item['name']}**")
                    st.caption(f"SKU: {item['sku']}")
                
                with item_col3:
                    new_qty = st.number_input(
                        "Qty",
                        min_value=1,
                        value=item["quantity"],
                        step=100,
                        key=f"qty_{i}"
                    )
                    if new_qty != item["quantity"]:
                        st.session_state.quote_items[i]["quantity"] = new_qty
                        st.rerun()
                
                with item_col4:
                    subtotal = item["unit_price"] * item["quantity"]
                    st.markdown(f"**${subtotal:.2f}**")
                    st.caption(f"@ ${item['unit_price']:.2f}")
                
                with item_col5:
                    if st.button("🗑️", key=f"del_item_{i}"):
                        st.session_state.quote_items.pop(i)
                        st.rerun()
                
                st.markdown("---")
    
    with col2:
        st.subheader("Quote Settings")
        
        quote_number = st.text_input(
            "Quote Number",
            value=f"QS-{datetime.now().strftime('%d%m%y')}-001",
            placeholder="e.g., QS-210226-001"
        )
        
        quote_date = st.date_input("Quote Date", value=datetime.now())
        
        validity_days = settings.get("quote_validity_days", 7)
        valid_until = st.date_input(
            "Valid Until",
            value=datetime.now() + timedelta(days=validity_days)
        )
        
        st.markdown("---")
        st.subheader("Shipping")
        
        shipping_cost = st.number_input(
            "Shipping Cost (USD)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            format="%.2f"
        )
        
        shipping_terms = st.text_input(
            "Shipping Terms",
            value="45-60 WORKING DAYS AFTER VESSEL DISPATCHED",
            placeholder="e.g., DDP Sea Shipping"
        )
        
        st.markdown("---")
        st.subheader("Summary")
        
        subtotal = sum(item["unit_price"] * item["quantity"] for item in st.session_state.quote_items)
        total = subtotal + shipping_cost
        
        st.markdown(f"**Items:** {len(st.session_state.quote_items)}")
        st.markdown(f"**Subtotal:** ${subtotal:.2f}")
        st.markdown(f"**Shipping:** ${shipping_cost:.2f}")
        st.markdown(f"### Total: ${total:.2f}")
        
        st.markdown("---")
        
        if st.button("Clear Quote", use_container_width=True):
            st.session_state.quote_items = []
            st.rerun()
        
        if st.button("📄 Generate Quote PDF", use_container_width=True, type="primary"):
            if not customer_name:
                st.error("Please enter customer name")
            elif not st.session_state.quote_items:
                st.error("Please add at least one product")
            else:
                customer_info = {
                    "name": customer_name,
                    "address": customer_address,
                    "email": customer_email,
                    "phone": customer_phone,
                    "customer_id": customer_id
                }
                
                with st.spinner("Generating PDF..."):
                    pdf_buffer = pdfgen.generate_quotation_pdf(
                        products=st.session_state.quote_items,
                        settings=settings,
                        customer_info=customer_info,
                        quote_number=quote_number,
                        quote_date=quote_date.strftime("%d/%m/%Y"),
                        valid_until=valid_until.strftime("%d/%m/%Y"),
                        shipping_cost=shipping_cost,
                        shipping_terms=shipping_terms,
                        terms=settings.get("default_terms", "")
                    )
                
                st.download_button(
                    label="⬇️ Download Quote PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"quote_{quote_number}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("Quotation generated successfully!")


def show_settings():
    """Display settings page."""
    st.markdown('<p class="main-header">Settings</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Configure your company information and preferences</p>', unsafe_allow_html=True)
    
    settings = dm.get_settings()
    
    tab1, tab2, tab3 = st.tabs(["🏢 Company Info", "📄 Document Settings", "🎨 Branding"])
    
    with tab1:
        st.subheader("Company Information")
        
        with st.form("company_form"):
            company_name = st.text_input(
                "Company Name",
                value=settings.get("company_name", ""),
                placeholder="e.g., Guangzhou U-meking Co., Ltd."
            )
            
            company_address = st.text_input(
                "Address",
                value=settings.get("company_address", ""),
                placeholder="e.g., Block 5, Phase 6, Chancheng District, Foshan, China, 528041"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                company_phone = st.text_input(
                    "Phone",
                    value=settings.get("company_phone", ""),
                    placeholder="e.g., +86-135-3300-0344"
                )
            with col2:
                company_email = st.text_input(
                    "Email",
                    value=settings.get("company_email", ""),
                    placeholder="e.g., sales@umeking.com"
                )
            
            company_website = st.text_input(
                "Website",
                value=settings.get("company_website", ""),
                placeholder="e.g., https://umeking.com/"
            )
            
            prepared_by = st.text_input(
                "Prepared By (Default)",
                value=settings.get("prepared_by", ""),
                placeholder="e.g., Evelyn Luk"
            )
            
            if st.form_submit_button("Save Company Info", use_container_width=True):
                settings["company_name"] = company_name
                settings["company_address"] = company_address
                settings["company_phone"] = company_phone
                settings["company_email"] = company_email
                settings["company_website"] = company_website
                settings["prepared_by"] = prepared_by
                dm.save_settings(settings)
                st.success("Company information saved!")
    
    with tab2:
        st.subheader("Document Settings")
        
        with st.form("doc_settings_form"):
            catalog_title = st.text_input(
                "Catalog Title",
                value=settings.get("catalog_title", "PRODUCT CATALOG"),
                placeholder="e.g., PRODUCT CATALOG"
            )
            
            quote_validity_days = st.number_input(
                "Quote Validity (Days)",
                min_value=1,
                value=settings.get("quote_validity_days", 7),
                step=1
            )
            
            default_terms = st.text_area(
                "Default Terms & Conditions",
                value=settings.get("default_terms", ""),
                height=200,
                placeholder="Enter your standard terms and conditions..."
            )
            
            if st.form_submit_button("Save Document Settings", use_container_width=True):
                settings["catalog_title"] = catalog_title
                settings["quote_validity_days"] = quote_validity_days
                settings["default_terms"] = default_terms
                dm.save_settings(settings)
                st.success("Document settings saved!")
    
    with tab3:
        st.subheader("Branding")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Company Logo**")
            logo_file = st.file_uploader(
                "Upload Logo",
                type=["jpg", "jpeg", "png"],
                help="Upload your company logo (recommended size: 200x80 pixels)"
            )
            
            if logo_file:
                if st.button("Save Logo"):
                    logo_path = dm.save_logo(logo_file)
                    st.success("Logo uploaded successfully!")
                    st.rerun()
            
            if settings.get("logo_path") and os.path.exists(settings["logo_path"]):
                st.markdown("**Current Logo:**")
                st.image(settings["logo_path"], width=200)
        
        with col2:
            st.markdown("**Brand Color**")
            
            brand_color = st.color_picker(
                "Select Brand Color",
                value=settings.get("brand_color", "#003366")
            )
            
            st.markdown(f"""
            <div style="background-color: {brand_color}; color: white; padding: 1rem; border-radius: 5px; text-align: center;">
                Preview: Header Color
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Save Brand Color"):
                settings["brand_color"] = brand_color
                dm.save_settings(settings)
                st.success("Brand color saved!")


if __name__ == "__main__":
    main()
