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
from PIL import Image as PILImage

BRAND_COLOR = colors.HexColor("#003366")
LIGHT_BLUE = colors.HexColor("#E8F0F8")
WHITE = colors.white
BLACK = colors.black
GRAY = colors.HexColor("#666666")


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
        
    def generate(self, products: list, catalog_number: str = None, catalog_date: str = None) -> BytesIO:
        """Generate catalog PDF and return as BytesIO buffer."""
        buffer = BytesIO()
        
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
        is_first_page = True
        
        for category, cat_products in products_by_category.items():
            products_on_page = []
            
            for i, product in enumerate(cat_products):
                products_on_page.append(product)
                
                if len(products_on_page) == 3 or i == len(cat_products) - 1:
                    self._draw_page(
                        c, products_on_page, category,
                        catalog_number, catalog_date,
                        is_first_page, page_num,
                        is_first_of_category=(i < 3)
                    )
                    c.showPage()
                    page_num += 1
                    is_first_page = False
                    products_on_page = []
        
        c.save()
        buffer.seek(0)
        return buffer
    
    def _draw_page(self, c, products, category, catalog_number, catalog_date, 
                   is_first_page, page_num, is_first_of_category):
        """Draw a single page of the catalog."""
        self._draw_header(c, catalog_number, catalog_date, is_first_page)
        
        if is_first_of_category:
            self._draw_category_banner(c, category)
        
        y_start = self.page_height - 165 if is_first_of_category else self.page_height - 130
        self._draw_product_grid(c, products, y_start)
        
        self._draw_footer(c, page_num)
    
    def _draw_header(self, c, catalog_number, catalog_date, is_first_page):
        """Draw page header with logo and title."""
        y_top = self.page_height - self.margin
        left_x = self.margin
        right_x = self.page_width - self.margin
        
        logo_path = self.settings.get("logo_path", "")
        logo_height = 45
        if logo_path and isinstance(logo_path, str) and os.path.exists(logo_path):
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
        
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(self.brand_color)
        title = self.settings.get("catalog_title", "PRODUCT CATALOG")
        title_width = c.stringWidth(title, "Helvetica-Bold", 20)
        c.drawString(right_x - title_width, y_top - 18, title)
        
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(BLACK)
        c.drawRightString(right_x, y_top - 52, f"CATALOG NUMBER: {catalog_number}")
        c.drawRightString(right_x, y_top - 64, f"DATE: {catalog_date}")
        
        c.setStrokeColor(self.brand_color)
        c.setLineWidth(2)
        c.line(self.margin, y_top - 100, right_x, y_top - 100)
    
    def _draw_category_banner(self, c, category):
        """Draw category section banner."""
        y = self.page_height - 125
        banner_height = 22
        
        c.setFillColor(self.brand_color)
        c.rect(self.margin, y - banner_height, self.content_width, banner_height, fill=1, stroke=0)
        
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(self.margin + 10, y - 15, category.upper())
    
    def _draw_product_grid(self, c, products, y_start):
        """Draw products in a 3-column grid layout."""
        num_cols = 3
        col_width = self.content_width / num_cols
        card_height = 320
        card_padding = 8
        
        for i, product in enumerate(products):
            col = i % num_cols
            x = self.margin + col * col_width + card_padding
            y = y_start - card_height
            
            self._draw_product_card(c, product, x, y, col_width - 2 * card_padding, card_height - card_padding)
    
    def _draw_product_card(self, c, product, x, y, width, height):
        """Draw a single product card."""
        c.setStrokeColor(colors.HexColor("#CCCCCC"))
        c.setLineWidth(0.5)
        c.roundRect(x, y, width, height, 5, stroke=1, fill=0)
        
        img_height = 100
        img_y = y + height - img_height - 10
        image_path = product.get("image_path", "")
        
        if image_path and isinstance(image_path, str) and os.path.exists(image_path):
            try:
                img_width = width - 20
                c.drawImage(image_path, x + 10, img_y, 
                           width=img_width, height=img_height,
                           preserveAspectRatio=True)
            except Exception as e:
                c.setFillColor(LIGHT_BLUE)
                c.rect(x + 10, img_y, width - 20, img_height, fill=1, stroke=0)
                c.setFillColor(GRAY)
                c.setFont("Helvetica", 8)
                c.drawCentredString(x + width/2, img_y + img_height/2, "No Image")
        else:
            c.setFillColor(LIGHT_BLUE)
            c.rect(x + 10, img_y, width - 20, img_height, fill=1, stroke=0)
            c.setFillColor(GRAY)
            c.setFont("Helvetica", 8)
            c.drawCentredString(x + width/2, img_y + img_height/2, "No Image")
        
        text_y = img_y - 15
        c.setFillColor(self.brand_color)
        c.setFont("Helvetica-Bold", 9)
        
        name = product.get("name", "")
        if len(name) > 25:
            name = name[:22] + "..."
        c.drawString(x + 10, text_y, name)
        
        text_y -= 12
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 7)
        c.drawString(x + 10, text_y, f"({product.get('sku', '')})")
        
        text_y -= 15
        c.setFillColor(BLACK)
        c.setFont("Helvetica", 7)
        
        description = product.get("description", "")
        specs = description.split("\n")[:6]
        for spec in specs:
            if spec.strip():
                spec_text = f"• {spec.strip()}"
                if len(spec_text) > 45:
                    spec_text = spec_text[:42] + "..."
                c.drawString(x + 10, text_y, spec_text)
                text_y -= 10
        
        price_y = y + 35
        c.setFillColor(self.brand_color)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 10, price_y, f"${product.get('unit_price', 0):.2f}/PCS")
        
        btn_width = 60
        btn_height = 16
        btn_x = x + width - btn_width - 10
        btn_y = price_y - 3
        
        c.setFillColor(WHITE)
        c.setStrokeColor(self.brand_color)
        c.setLineWidth(1)
        c.roundRect(btn_x, btn_y, btn_width, btn_height, 3, fill=1, stroke=1)
        
        c.setFillColor(self.brand_color)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(btn_x + btn_width/2, btn_y + 5, "Learn More")
    
    def _draw_footer(self, c, page_num):
        """Draw page footer."""
        y = self.margin - 10
        
        c.setStrokeColor(self.brand_color)
        c.setLineWidth(1)
        c.line(self.margin, y + 25, self.page_width - self.margin, y + 25)
        
        logo_path = self.settings.get("logo_path", "")
        if logo_path and os.path.exists(logo_path):
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
        terms: str = ""
    ) -> BytesIO:
        """Generate quotation PDF and return as BytesIO buffer."""
        buffer = BytesIO()
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
        
        logo_path = self.settings.get("logo_path", "")
        logo_height = 40
        if logo_path and os.path.exists(logo_path):
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
        
        c.setFillColor(self.brand_color)
        c.setFont("Helvetica-Bold", 32)
        c.drawRightString(self.page_width - self.margin, y_top - 20, "QUOTE")
        
        right_x = self.page_width - self.margin
        info_x = right_x - 100
        
        c.setFont("Helvetica", 9)
        c.setFillColor(BLACK)
        y_quote_info = y_top - 45
        
        c.drawRightString(info_x, y_quote_info, "DATE:")
        c.drawRightString(right_x, y_quote_info, quote_date)
        
        y_quote_info -= 12
        c.drawRightString(info_x, y_quote_info, "QUOTE#:")
        c.drawRightString(right_x, y_quote_info, quote_number)
        
        y_quote_info -= 12
        c.drawRightString(info_x, y_quote_info, "CUSTOMER ID:")
        c.drawRightString(right_x, y_quote_info, customer_info.get("customer_id", ""))
        
        y_quote_info -= 12
        c.drawRightString(info_x, y_quote_info, "VALID UNTIL:")
        c.drawRightString(right_x, y_quote_info, valid_until)
        
        customer_y = y_top - 100
        c.setFillColor(self.brand_color)
        c.rect(self.margin, customer_y - 20, self.content_width, 20, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin + 10, customer_y - 14, "CUSTOMER")
        
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
        col_widths = [65, 55, 180, 30, 22, 55, 55, 25, 55]
        col_labels = ["Item No.", "Product Pic.", "Description", "QTY.", "Unit", 
                      "EXW Unit Price(USD)", "Net Amount (USD)", "CTN QTY.", "Packaging Rate"]
        
        header_y = y_start
        header_height = 35
        
        c.setFillColor(self.brand_color)
        c.rect(self.margin, header_y - header_height, self.content_width, header_height, fill=1, stroke=0)
        
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 6)
        
        x_pos = self.margin
        for i, label in enumerate(col_labels):
            if i < 8:
                cell_x = x_pos + col_widths[i] / 2
                c.drawCentredString(cell_x, header_y - 20, label)
                x_pos += col_widths[i]
        
        extra_x = self.margin + sum(col_widths[:8])
        c.drawCentredString(extra_x + 25, header_y - 12, "Carton Size/cm")
        c.drawCentredString(extra_x + 25, header_y - 22, "L    W    D")
        c.drawCentredString(extra_x + 60, header_y - 17, "G.W./CTN")
        c.drawCentredString(extra_x + 95, header_y - 17, "Total G.W.")
        
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
                c.setFont("Helvetica-Bold", 6)
                x_pos = self.margin
                for i, label in enumerate(col_labels):
                    if i < 8:
                        cell_x = x_pos + col_widths[i] / 2
                        c.drawCentredString(cell_x, row_y - 20, label)
                        x_pos += col_widths[i]
                row_y -= header_height
            
            c.setStrokeColor(colors.HexColor("#CCCCCC"))
            c.setLineWidth(0.5)
            c.rect(self.margin, row_y - row_height, self.content_width, row_height, stroke=1, fill=0)
            
            x_pos = self.margin
            for i in range(len(col_widths) - 1):
                x_pos += col_widths[i]
                c.line(x_pos, row_y, x_pos, row_y - row_height)
            
            x_offset = self.margin
            
            c.setFillColor(BLACK)
            c.setFont("Helvetica", 7)
            c.drawCentredString(x_offset + col_widths[0]/2, row_y - 45, product.get("sku", ""))
            x_offset += col_widths[0]
            
            image_path = product.get("image_path", "")
            img_size = 45
            img_x = x_offset + (col_widths[1] - img_size) / 2
            img_y = row_y - row_height + (row_height - img_size) / 2
            
            if image_path and isinstance(image_path, str) and os.path.exists(image_path):
                try:
                    c.drawImage(image_path, img_x, img_y, width=img_size, height=img_size, 
                               preserveAspectRatio=True)
                except:
                    pass
            x_offset += col_widths[1]
            
            desc_x = x_offset + 5
            desc_y = row_y - 12
            c.setFont("Helvetica-Bold", 7)
            c.drawString(desc_x, desc_y, product.get("name", ""))
            
            c.setFont("Helvetica", 6)
            desc_lines = product.get("description", "").split("\n")
            desc_y -= 10
            for line in desc_lines[:7]:
                if line.strip():
                    c.drawString(desc_x, desc_y, f"- {line.strip()}")
                    desc_y -= 8
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
            
            remaining_width = self.content_width - sum(col_widths[:8])
            carton_text = f"{int(carton_l)}  {int(carton_w)}  {int(carton_h)}"
            c.drawCentredString(x_offset + 25, row_y - 45, carton_text)
            c.drawCentredString(x_offset + 60, row_y - 45, f"{gw_per_ctn:.2f}")
            c.drawCentredString(x_offset + 95, row_y - 45, f"{product_gw:.2f}")
            
            row_y -= row_height
        
        summary_height = 25
        c.setStrokeColor(colors.HexColor("#CCCCCC"))
        c.setLineWidth(0.5)
        
        c.rect(self.margin, row_y - summary_height, self.content_width, summary_height, stroke=1, fill=0)
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(self.margin + 200, row_y - 16, "SUB TOTAL")
        
        x_net = self.margin + sum(col_widths[:6]) + col_widths[6]/2
        c.drawCentredString(x_net, row_y - 16, f"${subtotal:.2f}")
        
        x_ctn = self.margin + sum(col_widths[:7]) + col_widths[7]/2
        c.drawCentredString(x_ctn, row_y - 16, f"{int(total_ctn)}")
        
        x_gw = self.margin + sum(col_widths[:8]) + 95
        c.drawCentredString(x_gw, row_y - 16, f"{total_gw:.2f}")
        
        row_y -= summary_height
        
        if shipping_cost > 0:
            c.rect(self.margin, row_y - summary_height, self.content_width, summary_height, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 8)
            shipping_label = f"DDP SEA SHIPPING COST ({shipping_terms})" if shipping_terms else "SHIPPING COST"
            c.drawCentredString(self.margin + 200, row_y - 16, shipping_label)
            c.drawCentredString(x_net, row_y - 16, f"${shipping_cost:.2f}")
            row_y -= summary_height
        
        c.setFillColor(self.brand_color)
        c.rect(self.margin, row_y - summary_height, self.content_width, summary_height, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.margin + 200, row_y - 17, "TOTAL ORDER AMOUNT")
        
        total_amount = subtotal + shipping_cost
        c.drawCentredString(x_net, row_y - 17, f"${total_amount:.2f}")
        
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


def generate_catalog_pdf(products: list, settings: dict, catalog_number: str = None, catalog_date: str = None) -> BytesIO:
    """Convenience function to generate catalog PDF."""
    generator = CatalogPDFGenerator(settings)
    return generator.generate(products, catalog_number, catalog_date)


def generate_quotation_pdf(
    products: list,
    settings: dict,
    customer_info: dict,
    quote_number: str,
    quote_date: str,
    valid_until: str,
    shipping_cost: float = 0,
    shipping_terms: str = "",
    terms: str = ""
) -> BytesIO:
    """Convenience function to generate quotation PDF."""
    generator = QuotationPDFGenerator(settings)
    return generator.generate(
        products, customer_info, quote_number, quote_date, 
        valid_until, shipping_cost, shipping_terms, terms
    )
