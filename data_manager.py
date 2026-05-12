"""
Data Manager Module for U-Meking Sales Engine
Handles CSV data persistence and image file management.
"""

import os
import re
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


# Four major parts (大类) — bilingual labels for UI & PDF
PRESET_PARTS = [
    "Part 1: Corporate & Employee Experience (企业职场与员工体验)",
    "Part 2: Institutional, Health & Education (机构、健康与教育)",
    "Part 3: Outdoor, Travel & Entertainment (户外、旅游与娱乐)",
    "Part 4: Retail, Lifestyle & Hospitality (零售、生活方式与招待)",
]

# 24 kit categories (套装) — aligned with latest bilingual list
PRESET_CATEGORIES = [
    "1. New Employee Onboarding Pack (新员工入职礼包)",
    "2. Employee Wellness Gift Set (员工健康关怀)",
    "3. Spring Corporate Gift Set (春季企业答谢)",
    "4. Corporate Promotional Package (企业通用促销包)",
    "5. On-site Branding for Large Events (大型活动现场周边)",
    "6. ABA Therapy Toolkit Gift (ABA 特教感官工具)",
    "7. NGO or Healthcare Charity (NGO/医疗慈善机构)",
    "8. Gym Membership Package (健身房会员入会包)",
    "9. Sports Brand Collection Swag (运动品牌联名周边)",
    "10. University Campus Spirit & Alumni Kit (大学校园/校友纪念)",
    "11. Eco-friendly Activity Pack (环保主题活动套装)",
    "12. Summer Beach Vacation Kit (夏日沙滩度假)",
    "13. Outdoor Hiking Gear Set (户外徒步装备)",
    "14. Fishing Lure Equipment Set (路亚钓鱼装备)",
    "15. Travel Agency VIP Kit (旅行社 VIP 礼遇)",
    "16. Globally Theme Park Water World Resort (主题乐园/水上世界)",
    "17. Music Festival / Rave Survival Kit (音乐节/狂欢生存包)",
    "18. Esports Gaming Exhibition Swag (电竞游戏展会周边)",
    "19. Coffee / Baking Shop Merch Kit (精品咖啡/烘焙店周边)",
    "20. Bar Craft Brewery Swag (精酿酒吧联名周边)",
    "21. Cosmetics Membership Package (美妆品牌会员礼盒)",
    "22. Jewelry Packaging Set (首饰高定包装套装)",
    "23. Pet Love Package (宠物关怀/品牌主题礼盒)",
    "24. Souvenir Gift Items (高端旅游纪念品)",
]

# Map each preset kit to its major part (for PDF grouping & filters)
CATEGORY_TO_PART = {}
for _i, _cat in enumerate(PRESET_CATEGORIES):
    if _i < 5:
        CATEGORY_TO_PART[_cat] = PRESET_PARTS[0]
    elif _i < 11:
        CATEGORY_TO_PART[_cat] = PRESET_PARTS[1]
    elif _i < 18:
        CATEGORY_TO_PART[_cat] = PRESET_PARTS[2]
    else:
        CATEGORY_TO_PART[_cat] = PRESET_PARTS[3]


def get_part_for_category(category: str) -> str:
    """Return major part label for a preset category, or empty string if unknown/custom."""
    if not category or not isinstance(category, str):
        return ""
    return CATEGORY_TO_PART.get(category.strip(), "")


def get_preset_categories_for_part(part: str) -> list:
    """List preset kit categories that belong to a given major part."""
    if not part:
        return []
    return [c for c in PRESET_CATEGORIES if CATEGORY_TO_PART.get(c) == part]


def normalize_category_value(category: str) -> str:
    """Map legacy / mangled category strings to current PRESET_CATEGORIES by leading number."""
    if not category or not isinstance(category, str):
        return ""
    cat = category.strip()
    if cat in CATEGORY_TO_PART:
        return cat
    m = re.match(r"^\s*(\d+)\.", cat)
    if m:
        idx = int(m.group(1))
        if 1 <= idx <= len(PRESET_CATEGORIES):
            return PRESET_CATEGORIES[idx - 1]
    return cat


def normalize_products_df(df: pd.DataFrame) -> tuple:
    """Ensure part column exists and sync part/category for preset kits. Returns (df, changed)."""
    changed = False
    if "part" not in df.columns:
        df["part"] = ""
        changed = True
    for idx in df.index:
        old_cat = df.at[idx, "category"]
        old_cat_s = str(old_cat).strip() if pd.notna(old_cat) else ""
        new_cat = normalize_category_value(old_cat_s)
        if new_cat != old_cat_s:
            df.at[idx, "category"] = new_cat
            changed = True
        p = get_part_for_category(new_cat)
        old_p = str(df.at[idx, "part"]).strip() if pd.notna(df.at[idx, "part"]) else ""
        if p:
            if old_p != p:
                df.at[idx, "part"] = p
                changed = True
        # custom category: keep existing part if any
    return df, changed


def get_products_df() -> pd.DataFrame:
    """Load products from CSV file."""
    init_directories()
    if os.path.exists(PRODUCTS_CSV):
        df = pd.read_csv(PRODUCTS_CSV, encoding="utf-8")
        df, changed = normalize_products_df(df)
        if changed:
            save_products_df(df)
        return df
    else:
        columns = [
            "sku", "name", "category", "description",
            "unit_price", "moq", "image_path", "image_path_2", "image_path_3",
            "packaging_rate", "carton_l", "carton_w", "carton_h",
            "gw_per_ctn", "supplier_link", "supplier_link_2", "supplier_link_3",
            "created_at", "updated_at", "part",
        ]
        return pd.DataFrame(columns=columns)


def save_products_df(df: pd.DataFrame):
    """Save products DataFrame to CSV file."""
    init_directories()
    df.to_csv(PRODUCTS_CSV, index=False, encoding="utf-8")


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
    supplier_link_3: str = "",
    part: str = None,
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
    cat_norm = normalize_category_value(category.strip()) if category else ""
    row_category = cat_norm if cat_norm else (category or "")
    row_part = (part or "").strip() if part else ""
    if not row_part:
        row_part = get_part_for_category(row_category) or ""
    new_row = {
        "sku": sku,
        "name": name,
        "category": row_category,
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
        "updated_at": now,
        "part": row_part,
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
    supplier_link_3: str = None,
    part: str = None,
) -> bool:
    """Update an existing product."""
    df = get_products_df()
    
    if sku not in df["sku"].values:
        return False
    
    idx = df[df["sku"] == sku].index[0]
    
    if name is not None:
        df.at[idx, "name"] = name
    if category is not None:
        cat_stripped = category.strip()
        cat_norm = normalize_category_value(cat_stripped) or cat_stripped
        df.at[idx, "category"] = cat_norm
    if part is not None:
        df.at[idx, "part"] = (part.strip() if isinstance(part, str) else part) or ""
    elif category is not None:
        p = get_part_for_category(str(df.at[idx, "category"]))
        if p:
            df.at[idx, "part"] = p
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
    """Get unique categories from products (bilingual names)."""
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


def get_hidden_categories() -> list:
    """Get list of hidden/deleted categories."""
    settings = get_settings()
    return settings.get("hidden_categories", [])


def hide_category(category: str):
    """Hide a category from the preset list."""
    settings = get_settings()
    hidden = settings.get("hidden_categories", [])
    if category not in hidden:
        hidden.append(category)
        settings["hidden_categories"] = hidden
        save_settings(settings)


def unhide_category(category: str):
    """Restore a hidden category."""
    settings = get_settings()
    hidden = settings.get("hidden_categories", [])
    if category in hidden:
        hidden.remove(category)
        settings["hidden_categories"] = hidden
        save_settings(settings)
