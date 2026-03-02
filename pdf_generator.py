"""
PDF Generator Module for U-Meking Sales Engine
Handles generation of Product Catalogs and Quotations using ReportLab.
"""

import os
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from PIL import Image as PILImage

try:
    from deep_translator import GoogleTranslator
    TRANSLATION_AVAILABLE = True
except:
    TRANSLATION_AVAILABLE = False

pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))

CJK_FONTS = {
    "Japanese": "HeiseiKakuGo-W5",
    "Korean": "HYSMyeongJo-Medium",
    "Arabic": "Helvetica",
    "Hebrew": "Helvetica",
    "Russian": "Helvetica",
}

LANG_CODES = {
    "English": "en",
    "Arabic": "ar",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Korean": "ko",
    "Japanese": "ja",
    "Russian": "ru",
    "Hebrew": "he",
}

_translation_cache = {}

def translate_text(text: str, target_lang: str) -> str:
    """Translate text to target language using Google Translate."""
    if not text or not text.strip() or target_lang == "English" or not TRANSLATION_AVAILABLE:
        return text
    
    cache_key = f"{text[:100]}_{target_lang}"
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]
    
    try:
        lang_code = LANG_CODES.get(target_lang, "en")
        translator = GoogleTranslator(source='en', target=lang_code)
        translated = translator.translate(text)
        if translated:
            _translation_cache[cache_key] = translated
            return translated
        return text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def get_font_for_language(lang: str, bold: bool = False) -> str:
    """Get appropriate font for language."""
    if lang in CJK_FONTS:
        return CJK_FONTS[lang]
    return "Helvetica-Bold" if bold else "Helvetica"


def wrap_text(text: str, max_width: float, font_name: str, font_size: float, canvas_obj) -> list:
    """Wrap text to fit within max_width, returning list of lines."""
    if not text:
        return []
    
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip() if current_line else word
        test_width = canvas_obj.stringWidth(test_line, font_name, font_size)
        
        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            if canvas_obj.stringWidth(word, font_name, font_size) > max_width:
                while word:
                    for i in range(len(word), 0, -1):
                        part = word[:i]
                        if canvas_obj.stringWidth(part, font_name, font_size) <= max_width:
                            lines.append(part)
                            word = word[i:]
                            break
                    else:
                        lines.append(word[0])
                        word = word[1:]
                current_line = ""
            else:
                current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

BRAND_COLOR = colors.HexColor("#003366")
LIGHT_BLUE = colors.HexColor("#E8F0F8")
WHITE = colors.white
BLACK = colors.black
GRAY = colors.HexColor("#666666")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TRANSLATIONS = {
    "English": {
        "product_catalog": "PRODUCT CATALOG",
        "catalog_number": "CATALOG NUMBER",
        "date": "DATE",
        "quote": "QUOTE",
        "quote_number": "QUOTE#",
        "customer_id": "CUSTOMER ID",
        "valid_until": "VALID UNTIL",
        "customer": "CUSTOMER",
        "item_no": "Item No.",
        "product_pic": "Product Pic.",
        "description": "Description",
        "qty": "QTY.",
        "unit": "Unit",
        "unit_price": "EXW Unit Price(USD)",
        "net_amount": "Net Amount (USD)",
        "ctn_qty": "CTN QTY.",
        "carton_size": "Carton Size",
        "gw_ctn": "G.W./CTN",
        "total_gw": "Total G.W.",
        "sub_total": "SUB TOTAL",
        "total_order_amount": "TOTAL ORDER AMOUNT",
        "shipping_cost": "SHIPPING COST",
        "terms_conditions": "TERMS & CONDITIONS",
        "pcs": "PCS",
        "inquiry": "INQUIRY",
    },
    "Arabic": {
        "product_catalog": "كتالوج المنتجات",
        "catalog_number": "رقم الكتالوج",
        "date": "التاريخ",
        "quote": "عرض سعر",
        "quote_number": "رقم العرض",
        "customer_id": "رقم العميل",
        "valid_until": "صالح حتى",
        "customer": "العميل",
        "item_no": "رقم الصنف",
        "product_pic": "صورة المنتج",
        "description": "الوصف",
        "qty": "الكمية",
        "unit": "الوحدة",
        "unit_price": "سعر الوحدة",
        "net_amount": "المبلغ الصافي",
        "ctn_qty": "عدد الكراتين",
        "carton_size": "حجم الكرتون",
        "gw_ctn": "الوزن/كرتون",
        "total_gw": "الوزن الإجمالي",
        "sub_total": "المجموع الفرعي",
        "total_order_amount": "إجمالي الطلب",
        "shipping_cost": "تكلفة الشحن",
        "terms_conditions": "الشروط والأحكام",
        "pcs": "قطعة",
        "inquiry": "استفسار",
    },
    "Spanish": {
        "product_catalog": "CATÁLOGO DE PRODUCTOS",
        "catalog_number": "NÚMERO DE CATÁLOGO",
        "date": "FECHA",
        "quote": "COTIZACIÓN",
        "quote_number": "N° COTIZACIÓN",
        "customer_id": "ID CLIENTE",
        "valid_until": "VÁLIDO HASTA",
        "customer": "CLIENTE",
        "item_no": "N° Artículo",
        "product_pic": "Imagen",
        "description": "Descripción",
        "qty": "CANT.",
        "unit": "Unidad",
        "unit_price": "Precio Unitario",
        "net_amount": "Importe Neto",
        "ctn_qty": "CTN QTY.",
        "carton_size": "Tamaño Caja",
        "gw_ctn": "Peso/Caja",
        "total_gw": "Peso Total",
        "sub_total": "SUBTOTAL",
        "total_order_amount": "TOTAL DEL PEDIDO",
        "shipping_cost": "COSTO DE ENVÍO",
        "terms_conditions": "TÉRMINOS Y CONDICIONES",
        "pcs": "PZA",
        "inquiry": "CONSULTA",
    },
    "French": {
        "product_catalog": "CATALOGUE DE PRODUITS",
        "catalog_number": "N° DE CATALOGUE",
        "date": "DATE",
        "quote": "DEVIS",
        "quote_number": "N° DEVIS",
        "customer_id": "ID CLIENT",
        "valid_until": "VALIDE JUSQU'AU",
        "customer": "CLIENT",
        "item_no": "N° Article",
        "product_pic": "Photo",
        "description": "Description",
        "qty": "QTÉ",
        "unit": "Unité",
        "unit_price": "Prix Unitaire",
        "net_amount": "Montant Net",
        "ctn_qty": "QTÉ CTN",
        "carton_size": "Taille Carton",
        "gw_ctn": "Poids/Ctn",
        "total_gw": "Poids Total",
        "sub_total": "SOUS-TOTAL",
        "total_order_amount": "MONTANT TOTAL",
        "shipping_cost": "FRAIS DE LIVRAISON",
        "terms_conditions": "CONDITIONS GÉNÉRALES",
        "pcs": "PCS",
        "inquiry": "DEMANDE",
    },
    "German": {
        "product_catalog": "PRODUKTKATALOG",
        "catalog_number": "KATALOGNUMMER",
        "date": "DATUM",
        "quote": "ANGEBOT",
        "quote_number": "ANGEBOTSNR.",
        "customer_id": "KUNDENNR.",
        "valid_until": "GÜLTIG BIS",
        "customer": "KUNDE",
        "item_no": "Artikel-Nr.",
        "product_pic": "Produktbild",
        "description": "Beschreibung",
        "qty": "MENGE",
        "unit": "Einheit",
        "unit_price": "Stückpreis",
        "net_amount": "Nettobetrag",
        "ctn_qty": "KTN MENGE",
        "carton_size": "Kartongröße",
        "gw_ctn": "Gewicht/Ktn",
        "total_gw": "Gesamtgewicht",
        "sub_total": "ZWISCHENSUMME",
        "total_order_amount": "GESAMTBETRAG",
        "shipping_cost": "VERSANDKOSTEN",
        "terms_conditions": "GESCHÄFTSBEDINGUNGEN",
        "pcs": "STK",
        "inquiry": "ANFRAGE",
    },
    "Korean": {
        "product_catalog": "제품 카탈로그",
        "catalog_number": "카탈로그 번호",
        "date": "날짜",
        "quote": "견적서",
        "quote_number": "견적 번호",
        "customer_id": "고객 ID",
        "valid_until": "유효 기간",
        "customer": "고객",
        "item_no": "품목 번호",
        "product_pic": "제품 사진",
        "description": "설명",
        "qty": "수량",
        "unit": "단위",
        "unit_price": "단가",
        "net_amount": "금액",
        "ctn_qty": "박스 수량",
        "carton_size": "박스 크기",
        "gw_ctn": "박스당 중량",
        "total_gw": "총 중량",
        "sub_total": "소계",
        "total_order_amount": "총 주문 금액",
        "shipping_cost": "배송비",
        "terms_conditions": "이용약관",
        "pcs": "개",
        "inquiry": "문의",
    },
    "Japanese": {
        "product_catalog": "製品カタログ",
        "catalog_number": "カタログ番号",
        "date": "日付",
        "quote": "見積書",
        "quote_number": "見積番号",
        "customer_id": "顧客ID",
        "valid_until": "有効期限",
        "customer": "お客様",
        "item_no": "品番",
        "product_pic": "製品写真",
        "description": "説明",
        "qty": "数量",
        "unit": "単位",
        "unit_price": "単価",
        "net_amount": "金額",
        "ctn_qty": "箱数",
        "carton_size": "箱サイズ",
        "gw_ctn": "箱重量",
        "total_gw": "総重量",
        "sub_total": "小計",
        "total_order_amount": "合計金額",
        "shipping_cost": "送料",
        "terms_conditions": "利用規約",
        "pcs": "個",
        "inquiry": "お問い合わせ",
    },
    "Russian": {
        "product_catalog": "КАТАЛОГ ПРОДУКЦИИ",
        "catalog_number": "НОМЕР КАТАЛОГА",
        "date": "ДАТА",
        "quote": "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ",
        "quote_number": "НОМЕР КП",
        "customer_id": "ID КЛИЕНТА",
        "valid_until": "ДЕЙСТВУЕТ ДО",
        "customer": "КЛИЕНТ",
        "item_no": "Артикул",
        "product_pic": "Фото",
        "description": "Описание",
        "qty": "КОЛ-ВО",
        "unit": "Ед.",
        "unit_price": "Цена за ед.",
        "net_amount": "Сумма",
        "ctn_qty": "Кол-во кор.",
        "carton_size": "Размер кор.",
        "gw_ctn": "Вес/кор.",
        "total_gw": "Общий вес",
        "sub_total": "ПОДЫТОГ",
        "total_order_amount": "ИТОГО",
        "shipping_cost": "СТОИМОСТЬ ДОСТАВКИ",
        "terms_conditions": "УСЛОВИЯ",
        "pcs": "ШТ",
        "inquiry": "ЗАПРОС",
    },
    "Hebrew": {
        "product_catalog": "קטלוג מוצרים",
        "catalog_number": "מספר קטלוג",
        "date": "תאריך",
        "quote": "הצעת מחיר",
        "quote_number": "מספר הצעה",
        "customer_id": "מספר לקוח",
        "valid_until": "בתוקף עד",
        "customer": "לקוח",
        "item_no": "מק״ט",
        "product_pic": "תמונה",
        "description": "תיאור",
        "qty": "כמות",
        "unit": "יחידה",
        "unit_price": "מחיר ליחידה",
        "net_amount": "סכום",
        "ctn_qty": "כמות קרטונים",
        "carton_size": "גודל קרטון",
        "gw_ctn": "משקל/קרטון",
        "total_gw": "משקל כולל",
        "sub_total": "סיכום ביניים",
        "total_order_amount": "סכום כולל",
        "shipping_cost": "עלות משלוח",
        "terms_conditions": "תנאים והגבלות",
        "pcs": "יח׳",
        "inquiry": "בירור",
    },
}

def get_translation(lang: str, key: str) -> str:
    """Get translated text for a given language and key."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"]).get(key, TRANSLATIONS["English"].get(key, key))


def get_absolute_path(relative_path):
    """Convert relative path to absolute path for file access."""
    if not relative_path or not isinstance(relative_path, str):
        return None
    if os.path.isabs(relative_path):
        if os.path.exists(relative_path):
            return relative_path
        return None
    abs_path = os.path.join(BASE_DIR, relative_path)
    if os.path.exists(abs_path):
        return abs_path
    return None


def hex_to_color(hex_string):
    """Convert hex color string to ReportLab color."""
    return colors.HexColor(hex_string)


class CatalogPDFGenerator:
    """Generate product catalog PDF with grid layout."""
    
    def __init__(self, settings: dict):
        self.settings = settings
        self.brand_color = hex_to_color(settings.get("brand_color", "#003366"))
        self.page_width, self.page_height = A4
        self.margin = 0.5 * inch
        self.content_width = self.page_width - 2 * self.margin
        
    def generate(self, products: list, catalog_number: str = None, catalog_date: str = None, language: str = "English") -> BytesIO:
        """Generate catalog PDF and return as BytesIO buffer."""
        buffer = BytesIO()
        self.language = language
        
        c = canvas.Canvas(buffer, pagesize=A4)
        
        if not catalog_number:
            catalog_number = f"CAT-{datetime.now().strftime('%Y-%m')}-001"
        if not catalog_date:
            catalog_date = datetime.now().strftime("%B %d, %Y")
        
        products_by_category = {}
        for product in products:
            cat = product.get("category", "Other")
            if cat not in products_by_category:
                products_by_category[cat] = []
            products_by_category[cat].append(product)
        
        page_num = 1
        header_height = 105
        footer_height = 40
        category_banner_height = 28
        row_height = 240
        category_spacing = 15
        
        content_top = self.page_height - self.margin - header_height
        content_bottom = self.margin + footer_height
        
        self._draw_header(c, catalog_number, catalog_date, True)
        current_y = content_top
        
        for cat_idx, (category, cat_products) in enumerate(products_by_category.items()):
            needed_height = category_banner_height + row_height
            
            if current_y - needed_height < content_bottom:
                self._draw_footer(c, page_num)
                c.showPage()
                page_num += 1
                self._draw_header(c, catalog_number, catalog_date, False)
                current_y = content_top
            
            self._draw_category_banner_at(c, category, current_y)
            current_y -= category_banner_height
            
            for row_start in range(0, len(cat_products), 3):
                row_products = cat_products[row_start:row_start + 3]
                
                if current_y - row_height < content_bottom:
                    self._draw_footer(c, page_num)
                    c.showPage()
                    page_num += 1
                    self._draw_header(c, catalog_number, catalog_date, False)
                    current_y = content_top
                
                self._draw_product_row(c, row_products, current_y)
                current_y -= row_height
            
            current_y -= category_spacing
        
        self._draw_footer(c, page_num)
        c.save()
        buffer.seek(0)
        return buffer
    
    def _draw_category_banner_at(self, c, category, y_top):
        """Draw category section banner at specified Y position."""
        banner_height = 22
        y = y_top - 5

        c.setFillColor(self.brand_color)
        c.rect(self.margin, y - banner_height, self.content_width, banner_height, fill=1, stroke=0)

        lang = getattr(self, 'language', 'English')
        font_name = get_font_for_language(lang, bold=True)
        translated_category = translate_text(category, lang)
        
        c.setFillColor(WHITE)
        c.setFont(font_name, 11)
        c.drawString(self.margin + 10, y - 15, translated_category.upper())
    
    def _draw_product_row(self, c, products, y_top):
        """Draw a row of products (up to 3)."""
        num_cols = 3
        col_width = self.content_width / num_cols
        card_height = 230
        card_padding = 6
        
        for i, product in enumerate(products):
            col = i % num_cols
            x = self.margin + col * col_width + card_padding
            y = y_top - card_height - 5
            
            self._draw_product_card(c, product, x, y, col_width - 2 * card_padding, card_height - card_padding)
    
    def _draw_header(self, c, catalog_number, catalog_date, is_first_page):
        """Draw page header with logo and title."""
        y_top = self.page_height - self.margin
        left_x = self.margin
        right_x = self.page_width - self.margin
        
        logo_path = get_absolute_path(self.settings.get("logo_path", ""))
        logo_height = 45
        if logo_path:
            try:
                c.drawImage(logo_path, left_x - 5, y_top - logo_height, 
                           width=120, height=logo_height, preserveAspectRatio=True)
            except:
                pass
        
        c.setFillColor(self.brand_color)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(left_x, y_top - 58, self.settings.get("company_name", ""))
        
        c.setFont("Helvetica", 7)
        c.setFillColor(GRAY)
        c.drawString(left_x, y_top - 70, self.settings.get("company_address", ""))
        web_info = f"Web: {self.settings.get('company_website', '')} | Phone: {self.settings.get('company_phone', '')} | Prepare By: {self.settings.get('prepared_by', '')}"
        c.drawString(left_x, y_top - 82, web_info)
        
        lang = getattr(self, 'language', 'English')
        font_name = get_font_for_language(lang, bold=True)
        
        c.setFont(font_name, 18)
        c.setFillColor(self.brand_color)
        title = get_translation(lang, "product_catalog")
        title_width = c.stringWidth(title, font_name, 18)
        c.drawString(right_x - title_width, y_top - 18, title)
        
        c.setFont(font_name, 8)
        c.setFillColor(BLACK)
        c.drawRightString(right_x, y_top - 52, f"{get_translation(lang, 'catalog_number')}: {catalog_number}")
        c.drawRightString(right_x, y_top - 64, f"{get_translation(lang, 'date')}: {catalog_date}")
        
        c.setStrokeColor(self.brand_color)
        c.setLineWidth(2)
        c.line(self.margin, y_top - 100, right_x, y_top - 100)
    
    def _draw_product_card(self, c, product, x, y, width, height):
        """Draw a single product card."""
        c.setStrokeColor(colors.HexColor("#CCCCCC"))
        c.setLineWidth(0.5)
        c.roundRect(x, y, width, height, 4, stroke=1, fill=0)
        
        img_height = 80
        img_y = y + height - img_height - 8
        image_path = get_absolute_path(product.get("image_path", ""))
        
        if image_path:
            try:
                img_width = width - 16
                c.drawImage(image_path, x + 8, img_y, 
                           width=img_width, height=img_height,
                           preserveAspectRatio=True)
            except Exception as e:
                c.setFillColor(LIGHT_BLUE)
                c.rect(x + 8, img_y, width - 16, img_height, fill=1, stroke=0)
                c.setFillColor(GRAY)
                c.setFont("Helvetica", 7)
                c.drawCentredString(x + width/2, img_y + img_height/2, "No Image")
        else:
            c.setFillColor(LIGHT_BLUE)
            c.rect(x + 8, img_y, width - 16, img_height, fill=1, stroke=0)
            c.setFillColor(GRAY)
            c.setFont("Helvetica", 7)
            c.drawCentredString(x + width/2, img_y + img_height/2, "No Image")
        
        text_y = img_y - 12
        lang = getattr(self, 'language', 'English')
        font_name = get_font_for_language(lang, bold=True)
        font_name_regular = get_font_for_language(lang, bold=False)
        
        c.setFillColor(self.brand_color)
        c.setFont(font_name, 7)
        
        name = product.get("name", "")
        name = translate_text(name, lang)
        if len(name) > 28:
            name = name[:25] + "..."
        c.drawString(x + 8, text_y, name)
        
        text_y -= 10
        c.setFillColor(GRAY)
        c.setFont(font_name_regular, 6)
        c.drawString(x + 8, text_y, f"({product.get('sku', '')})")
        
        text_y -= 12
        c.setFillColor(BLACK)
        c.setFont(font_name_regular, 5)
        
        description = product.get("description", "")
        description = translate_text(description, lang)
        specs = description.split("\n")[:5]
        for spec in specs:
            if spec.strip():
                spec_text = f"• {spec.strip()}"
                if len(spec_text) > 48:
                    spec_text = spec_text[:45] + "..."
                c.drawString(x + 8, text_y, spec_text)
                text_y -= 8
        
        price_y = y + 18
        c.setFillColor(self.brand_color)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 8, price_y, f"${product.get('unit_price', 0):.2f}/PCS")
        
        btn_width = 50
        btn_height = 13
        btn_x = x + width - btn_width - 8
        btn_y = price_y - 2
        
        c.setFillColor(WHITE)
        c.setStrokeColor(self.brand_color)
        c.setLineWidth(0.8)
        c.roundRect(btn_x, btn_y, btn_width, btn_height, 2, fill=1, stroke=1)
        
        c.setFillColor(self.brand_color)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(btn_x + btn_width/2, btn_y + 5, "Learn More")
    
    def _draw_footer(self, c, page_num):
        """Draw page footer."""
        y = self.margin - 10
        
        c.setStrokeColor(self.brand_color)
        c.setLineWidth(1)
        c.line(self.margin, y + 25, self.page_width - self.margin, y + 25)
        
        logo_path = get_absolute_path(self.settings.get("logo_path", ""))
        if logo_path:
            try:
                c.drawImage(logo_path, self.margin, y - 5, 
                           width=60, height=25, preserveAspectRatio=True)
            except:
                pass
        
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(self.margin + 70, y + 10, self.settings.get("company_name", ""))
        
        c.setFont("Helvetica", 7)
        c.setFillColor(GRAY)
        c.drawString(self.margin + 70, y, self.settings.get("company_address", ""))
        
        footer_right = f"Web: {self.settings.get('company_website', '')} | Phone: {self.settings.get('company_phone', '')} | Prepare By: {self.settings.get('prepared_by', '')}"
        c.drawString(self.margin + 70, y - 10, footer_right)
        
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 7)
        copyright_text = f"© {datetime.now().year} {self.settings.get('company_name', '')} All rights reserved."
        c.drawRightString(self.page_width - self.margin, y - 10, copyright_text)


class QuotationPDFGenerator:
    """Generate quotation PDF with table layout."""
    
    def __init__(self, settings: dict):
        self.settings = settings
        self.brand_color = hex_to_color(settings.get("brand_color", "#003366"))
        self.page_width, self.page_height = A4
        self.margin = 0.5 * inch
        self.content_width = self.page_width - 2 * self.margin
    
    def generate(
        self, 
        products: list,
        customer_info: dict,
        quote_number: str,
        quote_date: str,
        valid_until: str,
        shipping_cost: float = 0,
        shipping_terms: str = "",
        terms: str = "",
        language: str = "English"
    ) -> BytesIO:
        """Generate quotation PDF and return as BytesIO buffer."""
        buffer = BytesIO()
        self.language = language
        c = canvas.Canvas(buffer, pagesize=A4)
        
        current_page = 1
        y_position = self._draw_header(c, customer_info, quote_number, quote_date, valid_until)
        
        y_position = self._draw_products_table(c, products, y_position, shipping_cost, shipping_terms)
        
        if y_position < 200:
            self._draw_footer(c, current_page)
            c.showPage()
            current_page += 1
            y_position = self.page_height - self.margin - 50
        
        self._draw_footer(c, current_page)
        
        c.save()
        buffer.seek(0)
        return buffer
    
    def _draw_header(self, c, customer_info, quote_number, quote_date, valid_until):
        """Draw quotation header with company and customer info."""
        y_top = self.page_height - self.margin
        
        logo_path = get_absolute_path(self.settings.get("logo_path", ""))
        logo_height = 40
        if logo_path:
            try:
                c.drawImage(logo_path, self.margin, y_top - logo_height, 
                           width=80, height=logo_height, preserveAspectRatio=True)
            except:
                pass
        
        c.setFillColor(self.brand_color)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin + 90, y_top - 15, self.settings.get("company_name", ""))
        
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 8)
        y_info = y_top - 28
        c.drawString(self.margin + 90, y_info, self.settings.get("company_address", ""))
        y_info -= 10
        c.drawString(self.margin + 90, y_info, f"Web: {self.settings.get('company_website', '')} | Phone: {self.settings.get('company_phone', '')}")
        y_info -= 10
        c.drawString(self.margin + 90, y_info, f"Prepare By: {self.settings.get('prepared_by', '')}")
        
        lang = getattr(self, 'language', 'English')
        font_name = get_font_for_language(lang, bold=True)
        
        c.setFillColor(self.brand_color)
        c.setFont(font_name, 28)
        c.drawRightString(self.page_width - self.margin, y_top - 20, get_translation(lang, "quote"))
        
        right_x = self.page_width - self.margin
        info_x = right_x - 100
        
        c.setFont(font_name, 9)
        c.setFillColor(BLACK)
        y_quote_info = y_top - 45
        
        c.drawRightString(info_x, y_quote_info, f"{get_translation(lang, 'date')}:")
        c.drawRightString(right_x, y_quote_info, quote_date)
        
        y_quote_info -= 12
        c.drawRightString(info_x, y_quote_info, f"{get_translation(lang, 'quote_number')}:")
        c.drawRightString(right_x, y_quote_info, quote_number)
        
        y_quote_info -= 12
        c.drawRightString(info_x, y_quote_info, f"{get_translation(lang, 'customer_id')}:")
        c.drawRightString(right_x, y_quote_info, customer_info.get("customer_id", ""))
        
        y_quote_info -= 12
        c.drawRightString(info_x, y_quote_info, f"{get_translation(lang, 'valid_until')}:")
        c.drawRightString(right_x, y_quote_info, valid_until)
        
        customer_y = y_top - 100
        c.setFillColor(self.brand_color)
        c.rect(self.margin, customer_y - 20, self.content_width, 20, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(font_name, 10)
        c.drawString(self.margin + 10, customer_y - 14, get_translation(lang, "customer"))
        
        customer_y -= 35
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin + 10, customer_y, customer_info.get("name", ""))
        
        customer_y -= 12
        c.setFont("Helvetica", 9)
        c.drawString(self.margin + 10, customer_y, customer_info.get("address", ""))
        
        customer_y -= 12
        c.drawString(self.margin + 10, customer_y, customer_info.get("email", ""))
        
        customer_y -= 12
        c.drawString(self.margin + 10, customer_y, customer_info.get("phone", ""))
        
        return customer_y - 30
    
    def _draw_products_table(self, c, products, y_start, shipping_cost, shipping_terms):
        """Draw products table with detailed information."""
        col_widths = [48, 42, 130, 25, 20, 48, 45, 22]
        extra_col_widths = [50, 38, 38]
        col_labels = ["Item No.", "Product Pic.", "Description", "QTY.", "Unit", 
                      "EXW Unit Price(USD)", "Net Amount (USD)", "CTN QTY."]
        
        header_y = y_start
        header_height = 35
        
        c.setFillColor(self.brand_color)
        c.rect(self.margin, header_y - header_height, self.content_width, header_height, fill=1, stroke=0)
        
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 5)
        
        x_pos = self.margin
        for i, label in enumerate(col_labels):
            cell_x = x_pos + col_widths[i] / 2
            c.drawCentredString(cell_x, header_y - 20, label)
            x_pos += col_widths[i]
        
        extra_x = self.margin + sum(col_widths)
        c.drawCentredString(extra_x + extra_col_widths[0]/2, header_y - 12, "Carton Size")
        c.drawCentredString(extra_x + extra_col_widths[0]/2, header_y - 22, "L*W*D")
        extra_x += extra_col_widths[0]
        c.drawCentredString(extra_x + extra_col_widths[1]/2, header_y - 17, "G.W./CTN")
        extra_x += extra_col_widths[1]
        c.drawCentredString(extra_x + extra_col_widths[2]/2, header_y - 17, "Total G.W.")
        
        row_y = header_y - header_height
        subtotal = 0
        total_ctn = 0
        total_gw = 0
        
        for product in products:
            qty = product.get("quantity", 0)
            unit_price = product.get("unit_price", 0)
            net_amount = qty * unit_price
            subtotal += net_amount
            
            packaging_rate = product.get("packaging_rate", 1) or 1
            ctn_qty = qty / packaging_rate if packaging_rate > 0 else 0
            total_ctn += ctn_qty
            
            gw_per_ctn = product.get("gw_per_ctn", 0) or 0
            product_gw = ctn_qty * gw_per_ctn
            total_gw += product_gw
            
            row_height = 85
            
            if row_y - row_height < 100:
                c.showPage()
                row_y = self.page_height - self.margin - 50
                c.setFillColor(self.brand_color)
                c.rect(self.margin, row_y - header_height, self.content_width, header_height, fill=1, stroke=0)
                c.setFillColor(WHITE)
                c.setFont("Helvetica-Bold", 5)
                x_pos = self.margin
                for i, label in enumerate(col_labels):
                    cell_x = x_pos + col_widths[i] / 2
                    c.drawCentredString(cell_x, row_y - 20, label)
                    x_pos += col_widths[i]
                extra_x = self.margin + sum(col_widths)
                c.drawCentredString(extra_x + extra_col_widths[0]/2, row_y - 12, "Carton Size")
                c.drawCentredString(extra_x + extra_col_widths[0]/2, row_y - 22, "L*W*D")
                extra_x += extra_col_widths[0]
                c.drawCentredString(extra_x + extra_col_widths[1]/2, row_y - 17, "G.W./CTN")
                extra_x += extra_col_widths[1]
                c.drawCentredString(extra_x + extra_col_widths[2]/2, row_y - 17, "Total G.W.")
                row_y -= header_height
            
            c.setStrokeColor(colors.HexColor("#CCCCCC"))
            c.setLineWidth(0.5)
            c.rect(self.margin, row_y - row_height, self.content_width, row_height, stroke=1, fill=0)
            
            x_pos = self.margin
            all_widths = col_widths + extra_col_widths
            for i in range(len(all_widths) - 1):
                x_pos += all_widths[i]
                c.line(x_pos, row_y, x_pos, row_y - row_height)
            
            x_offset = self.margin
            
            c.setFillColor(BLACK)
            c.setFont("Helvetica", 5)
            sku = product.get("sku", "")
            sku_max_width = col_widths[0] - 4
            sku_width = c.stringWidth(sku, "Helvetica", 5)
            if sku_width > sku_max_width:
                ratio = sku_max_width / sku_width
                sku = sku[:int(len(sku) * ratio) - 1] + ".."
            c.drawCentredString(x_offset + col_widths[0]/2, row_y - 45, sku)
            x_offset += col_widths[0]
            
            image_path = get_absolute_path(product.get("image_path", ""))
            img_size = 38
            img_x = x_offset + (col_widths[1] - img_size) / 2
            img_y = row_y - row_height + (row_height - img_size) / 2
            
            if image_path:
                try:
                    c.drawImage(image_path, img_x, img_y, width=img_size, height=img_size, 
                               preserveAspectRatio=True)
                except:
                    pass
            x_offset += col_widths[1]
            
            desc_x = x_offset + 3
            desc_y = row_y - 10
            desc_max_width = col_widths[2] - 6
            
            lang = getattr(self, 'language', 'English')
            font_name = get_font_for_language(lang, bold=True)
            font_name_regular = get_font_for_language(lang, bold=False)
            
            c.setFont(font_name, 6)
            name = product.get("name", "")
            name = translate_text(name, lang)
            name_lines = wrap_text(name, desc_max_width, font_name, 6, c)
            for i, name_line in enumerate(name_lines[:2]):
                c.drawString(desc_x, desc_y, name_line)
                desc_y -= 8
            
            c.setFont(font_name_regular, 5)
            description = product.get("description", "")
            description = translate_text(description, lang)
            original_lines = description.split("\n")
            
            line_count = 0
            max_lines = 10
            for orig_line in original_lines:
                if orig_line.strip() and line_count < max_lines:
                    text = f"- {orig_line.strip()}"
                    wrapped = wrap_text(text, desc_max_width, font_name_regular, 5, c)
                    for wrap_line in wrapped:
                        if line_count < max_lines:
                            c.drawString(desc_x, desc_y, wrap_line)
                            desc_y -= 6
                            line_count += 1
            x_offset += col_widths[2]
            
            c.setFont("Helvetica", 8)
            c.drawCentredString(x_offset + col_widths[3]/2, row_y - 45, str(qty))
            x_offset += col_widths[3]
            
            c.drawCentredString(x_offset + col_widths[4]/2, row_y - 45, "PCS")
            x_offset += col_widths[4]
            
            c.drawCentredString(x_offset + col_widths[5]/2, row_y - 45, f"${unit_price:.2f}")
            x_offset += col_widths[5]
            
            c.drawCentredString(x_offset + col_widths[6]/2, row_y - 45, f"${net_amount:.2f}")
            x_offset += col_widths[6]
            
            c.drawCentredString(x_offset + col_widths[7]/2, row_y - 45, f"{int(ctn_qty)}")
            x_offset += col_widths[7]
            
            c.setFont("Helvetica", 6)
            carton_l = product.get("carton_l", 0) or 0
            carton_w = product.get("carton_w", 0) or 0
            carton_h = product.get("carton_h", 0) or 0
            
            carton_text = f"{int(carton_l)}*{int(carton_w)}*{int(carton_h)}"
            c.drawCentredString(x_offset + extra_col_widths[0]/2, row_y - 45, carton_text)
            x_offset += extra_col_widths[0]
            c.drawCentredString(x_offset + extra_col_widths[1]/2, row_y - 45, f"{gw_per_ctn:.2f}")
            x_offset += extra_col_widths[1]
            c.drawCentredString(x_offset + extra_col_widths[2]/2, row_y - 45, f"{product_gw:.2f}")
            
            row_y -= row_height
        
        summary_height = 25
        c.setStrokeColor(colors.HexColor("#CCCCCC"))
        c.setLineWidth(0.5)
        
        lang = getattr(self, 'language', 'English')
        font_name = get_font_for_language(lang, bold=True)
        
        label_x = self.margin + 10
        amount_x = self.margin + sum(col_widths[:5]) + col_widths[5]/2
        ctn_x = self.margin + sum(col_widths[:7]) + col_widths[7]/2
        gw_x = self.margin + sum(col_widths) + extra_col_widths[0] + extra_col_widths[1] + extra_col_widths[2]/2
        
        c.rect(self.margin, row_y - summary_height, self.content_width, summary_height, stroke=1, fill=0)
        c.setFillColor(BLACK)
        c.setFont(font_name, 9)
        c.drawString(label_x, row_y - 16, get_translation(lang, "sub_total"))
        c.drawRightString(amount_x + 40, row_y - 16, f"${subtotal:.2f}")
        c.drawCentredString(ctn_x, row_y - 16, f"{int(total_ctn)}")
        c.drawCentredString(gw_x, row_y - 16, f"{total_gw:.2f}")
        
        row_y -= summary_height
        
        if shipping_cost > 0:
            c.rect(self.margin, row_y - summary_height, self.content_width, summary_height, stroke=1, fill=0)
            c.setFont(font_name, 7)
            shipping_label = f"DDP SEA SHIPPING COST ({shipping_terms})" if shipping_terms else get_translation(lang, "shipping_cost")
            c.drawString(label_x, row_y - 16, shipping_label)
            c.drawRightString(amount_x + 40, row_y - 16, f"${shipping_cost:.2f}")
            row_y -= summary_height
        
        c.setFillColor(self.brand_color)
        c.rect(self.margin, row_y - summary_height, self.content_width, summary_height, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(font_name, 10)
        c.drawString(label_x, row_y - 17, get_translation(lang, "total_order_amount"))
        
        total_amount = subtotal + shipping_cost
        c.drawRightString(amount_x + 40, row_y - 17, f"${total_amount:.2f}")
        
        return row_y - summary_height - 20
    
    def _draw_footer(self, c, page_num):
        """Draw quotation footer."""
        y = self.margin - 10
        
        c.setStrokeColor(self.brand_color)
        c.setLineWidth(1)
        c.line(self.margin, y + 15, self.page_width - self.margin, y + 15)
        
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 7)
        c.drawCentredString(self.page_width / 2, y, 
                           f"Page {page_num} | {self.settings.get('company_name', '')} | {self.settings.get('company_website', '')}")


def generate_catalog_pdf(products: list, settings: dict, catalog_number: str = None, catalog_date: str = None, language: str = "English") -> BytesIO:
    """Convenience function to generate catalog PDF."""
    generator = CatalogPDFGenerator(settings)
    return generator.generate(products, catalog_number, catalog_date, language)


def generate_quotation_pdf(
    products: list,
    settings: dict,
    customer_info: dict,
    quote_number: str,
    quote_date: str,
    valid_until: str,
    shipping_cost: float = 0,
    shipping_terms: str = "",
    terms: str = "",
    language: str = "English"
) -> BytesIO:
    """Convenience function to generate quotation PDF."""
    generator = QuotationPDFGenerator(settings)
    return generator.generate(
        products, customer_info, quote_number, quote_date, 
        valid_until, shipping_cost, shipping_terms, terms, language
    )
