"""
Data Manager Module for U-Meking Sales Engine
Handles CSV data persistence and image file management.
"""

import os
import pandas as pd
from PIL import Image
import shutil
from datetime import datetime
import json

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
PRODUCTS_CSV = os.path.join(DATA_DIR, "products.csv")
SETTINGS_JSON = os.path.join(DATA_DIR, "settings.json")


def init_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)


def get_products_df() -> pd.DataFrame:
    """Load products from CSV file."""
    init_directories()
    if os.path.exists(PRODUCTS_CSV):
        df = pd.read_csv(PRODUCTS_CSV)
        return df
    else:
        columns = [
            "sku", "name", "category", "description", 
            "unit_price", "moq", "image_path", "image_path_2", "image_path_3",
            "packaging_rate", "carton_l", "carton_w", "carton_h",
            "gw_per_ctn", "supplier_link", "supplier_link_2", "supplier_link_3",
            "created_at", "updated_at"
        ]
        return pd.DataFrame(columns=columns)


def save_products_df(df: pd.DataFrame):
    """Save products DataFrame to CSV file."""
    init_directories()
    df.to_csv(PRODUCTS_CSV, index=False)


def add_product(
    sku: str,
    name: str,
    category: str,
    description: str,
    unit_price: float,
    moq: int,
    image_file=None,
    image_file_2=None,
    image_file_3=None,
    packaging_rate: int = 1,
    carton_l: float = 0,
    carton_w: float = 0,
    carton_h: float = 0,
    gw_per_ctn: float = 0,
    supplier_link: str = "",
    supplier_link_2: str = "",
    supplier_link_3: str = ""
) -> bool:
    """Add a new product to the inventory."""
    df = get_products_df()
    
    if sku in df["sku"].values:
        return False
    
    image_path = ""
    if image_file is not None:
        image_path = save_product_image(sku, image_file)
    
    image_path_2 = ""
    if image_file_2 is not None:
        image_path_2 = save_product_image(f"{sku}_2", image_file_2)
    
    image_path_3 = ""
    if image_file_3 is not None:
        image_path_3 = save_product_image(f"{sku}_3", image_file_3)
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = {
        "sku": sku,
        "name": name,
        "category": category,
        "description": description,
        "unit_price": unit_price,
        "moq": moq,
        "image_path": image_path,
        "image_path_2": image_path_2,
        "image_path_3": image_path_3,
        "packaging_rate": packaging_rate,
        "carton_l": carton_l,
        "carton_w": carton_w,
        "carton_h": carton_h,
        "gw_per_ctn": gw_per_ctn,
        "supplier_link": supplier_link,
        "supplier_link_2": supplier_link_2,
        "supplier_link_3": supplier_link_3,
        "created_at": now,
        "updated_at": now
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_products_df(df)
    return True


def update_product(
    sku: str,
    name: str = None,
    category: str = None,
    description: str = None,
    unit_price: float = None,
    moq: int = None,
    image_file=None,
    image_file_2=None,
    image_file_3=None,
    packaging_rate: int = None,
    carton_l: float = None,
    carton_w: float = None,
    carton_h: float = None,
    gw_per_ctn: float = None,
    supplier_link: str = None,
    supplier_link_2: str = None,
    supplier_link_3: str = None
) -> bool:
    """Update an existing product."""
    df = get_products_df()
    
    if sku not in df["sku"].values:
        return False
    
    idx = df[df["sku"] == sku].index[0]
    
    if name is not None:
        df.at[idx, "name"] = name
    if category is not None:
        df.at[idx, "category"] = category
    if description is not None:
        df.at[idx, "description"] = description
    if unit_price is not None:
        df.at[idx, "unit_price"] = unit_price
    if moq is not None:
        df.at[idx, "moq"] = moq
    if packaging_rate is not None:
        df.at[idx, "packaging_rate"] = packaging_rate
    if carton_l is not None:
        df.at[idx, "carton_l"] = carton_l
    if carton_w is not None:
        df.at[idx, "carton_w"] = carton_w
    if carton_h is not None:
        df.at[idx, "carton_h"] = carton_h
    if gw_per_ctn is not None:
        df.at[idx, "gw_per_ctn"] = gw_per_ctn
    if supplier_link is not None:
        df.at[idx, "supplier_link"] = supplier_link
    if supplier_link_2 is not None:
        df.at[idx, "supplier_link_2"] = supplier_link_2
    if supplier_link_3 is not None:
        df.at[idx, "supplier_link_3"] = supplier_link_3
    
    if image_file is not None:
        image_path = save_product_image(sku, image_file)
        df.at[idx, "image_path"] = image_path
    if image_file_2 is not None:
        image_path_2 = save_product_image(f"{sku}_2", image_file_2)
        df.at[idx, "image_path_2"] = image_path_2
    if image_file_3 is not None:
        image_path_3 = save_product_image(f"{sku}_3", image_file_3)
        df.at[idx, "image_path_3"] = image_path_3
    
    df.at[idx, "updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_products_df(df)
    return True


def delete_product(sku: str) -> bool:
    """Delete a product from the inventory."""
    df = get_products_df()
    
    if sku not in df["sku"].values:
        return False
    
    product = df[df["sku"] == sku].iloc[0]
    if product["image_path"] and os.path.exists(product["image_path"]):
        try:
            os.remove(product["image_path"])
        except:
            pass
    
    df = df[df["sku"] != sku]
    save_products_df(df)
    return True


def get_product_by_sku(sku: str) -> dict:
    """Get a single product by SKU."""
    df = get_products_df()
    if sku in df["sku"].values:
        return df[df["sku"] == sku].iloc[0].to_dict()
    return None


def get_absolute_path(relative_path: str) -> str:
    """Convert relative path to absolute path based on BASE_DIR."""
    if not relative_path or not isinstance(relative_path, str):
        return ""
    if os.path.isabs(relative_path):
        return relative_path
    return os.path.join(BASE_DIR, relative_path)


def save_product_image(sku: str, uploaded_file) -> str:
    """Save uploaded image file and return the relative path."""
    init_directories()
    
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif"]:
        ext = ".png"
    
    safe_sku = "".join(c if c.isalnum() or c in "-_" else "_" for c in sku)
    filename = f"{safe_sku}{ext}"
    filepath = os.path.join(IMAGES_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        img = Image.open(filepath)
        max_size = (800, 800)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        img.save(filepath, quality=90, optimize=True)
    except Exception as e:
        print(f"Image optimization failed: {e}")
    
    return f"assets/images/{filename}"


def get_settings() -> dict:
    """Load application settings from JSON file."""
    init_directories()
    default_settings = {
        "company_name": "Guangzhou U-meking Co., Ltd.",
        "company_address": "Block 5, Phase 6, Chancheng District, Foshan, China, 528041",
        "company_phone": "+86-135-3300-0344",
        "company_website": "https://umeking.com/",
        "company_email": "",
        "prepared_by": "Evelyn Luk",
        "logo_path": "",
        "default_terms": """1. Prices are quoted in USD, EXW Foshan, China.
2. Payment Terms: 30% deposit, 70% before shipment.
3. Lead Time: 25-30 working days after order confirmation.
4. Quotation valid for 7 days from date of issue.
5. All products are subject to final confirmation.""",
        "quote_validity_days": 7,
        "catalog_title": "PRODUCT CATALOG",
        "brand_color": "#003366"
    }
    
    if os.path.exists(SETTINGS_JSON):
        try:
            with open(SETTINGS_JSON, "r", encoding="utf-8") as f:
                saved_settings = json.load(f)
                default_settings.update(saved_settings)
        except:
            pass
    
    return default_settings


def save_settings(settings: dict):
    """Save application settings to JSON file."""
    init_directories()
    with open(SETTINGS_JSON, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def save_logo(uploaded_file) -> str:
    """Save company logo and return the relative path."""
    init_directories()
    
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif"]:
        ext = ".png"
    
    filename = f"company_logo{ext}"
    filepath = os.path.join(ASSETS_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    relative_path = f"assets/{filename}"
    settings = get_settings()
    settings["logo_path"] = relative_path
    save_settings(settings)
    
    return relative_path


def get_categories() -> list:
    """Get unique categories from products."""
    df = get_products_df()
    if "category" in df.columns and len(df) > 0:
        return sorted(df["category"].dropna().unique().tolist())
    return []


def get_products_by_category(category: str) -> pd.DataFrame:
    """Get products filtered by category."""
    df = get_products_df()
    if category and category != "All":
        return df[df["category"] == category]
    return df
