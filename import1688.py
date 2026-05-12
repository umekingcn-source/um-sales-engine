"""
Best-effort fetch & parse 1688 offer pages for Streamlit import.

Notes:
- 1688 often returns a short anti-bot / captcha HTML from cloud IPs; mobile m.1688.com
  usually returns richer HTML when accessed from a normal browser / home network.
- Optional: install Playwright locally for higher success rate:
    pip install playwright && playwright install chromium
"""

from __future__ import annotations

import re
import ssl
import urllib.request
from dataclasses import dataclass, field
from typing import List, Optional

MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)
DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def extract_offer_id(url: str) -> Optional[str]:
    if not url or not isinstance(url, str):
        return None
    m = re.search(r"offer/(\d+)", url, re.I)
    if m:
        return m.group(1)
    m = re.search(r"offerId[=](\d+)", url, re.I)
    if m:
        return m.group(1)
    return None


def mobile_offer_url(offer_id: str) -> str:
    return f"https://m.1688.com/offer/{offer_id}.html"


def _http_get(url: str, referer: str = "") -> str:
    ctx = ssl.create_default_context()
    headers = {
        "User-Agent": MOBILE_UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        return resp.read().decode("utf-8", "replace")


def _json_unescape(s: str) -> str:
    try:
        return bytes(s, "utf-8").decode("unicode_escape")
    except Exception:
        return s.replace("\\n", "\n").replace("\\/", "/")


def _strip_html(html: str) -> str:
    t = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    t = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:8000]


def _extract_subject(html: str) -> str:
    m = re.search(r'"subject"\s*:\s*"((?:[^"\\]|\\.)*)"', html)
    if m:
        return _json_unescape(m.group(1))
    m = re.search(r'"title"\s*:\s*"((?:[^"\\]|\\.)*)"', html)
    if m:
        return _json_unescape(m.group(1))
    return ""


def _extract_offer_images(html: str, limit: int = 12) -> List[str]:
    urls = set()
    for m in re.finditer(
        r"(https://img\.alicdn\.com/imgextra/[^\"'\\s<>]+?\.(?:jpg|jpeg|png|webp))",
        html,
        re.I,
    ):
        u = m.group(1)
        if "avatar" in u.lower() or "30x30" in u or "40x40" in u:
            continue
        urls.add(u.split("?")[0])
    out = list(urls)[:limit]
    return out


def _extract_prices(html: str) -> List[float]:
    nums: List[float] = []
    for pat in [
        r'"consignPrice"\s*:\s*"([0-9.]+)"',
        r'"price"\s*:\s*"([0-9.]+)"',
        r'"referencePrice"\s*:\s*"([0-9.]+)"',
        r'"promotionPrice"\s*:\s*"([0-9.]+)"',
    ]:
        for m in re.finditer(pat, html):
            try:
                nums.append(float(m.group(1)))
            except ValueError:
                continue
    return sorted(set([n for n in nums if 0 < n < 1_000_000]))


def _extract_moq(html: str) -> Optional[int]:
    for pat in [
        r'"beginNum"\s*:\s*(\d+)',
        r'"minOrderQuantity"\s*:\s*(\d+)',
        r'"minOrderCount"\s*:\s*(\d+)',
        r'"saleNum"\s*:\s*(\d+)',
    ]:
        m = re.search(pat, html)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                continue
    return None


def _extract_carton_cm(html: str) -> tuple[float, float, float]:
    """Try common 1688 / logistics text patterns for L*W*H cm."""
    text = _strip_html(html)
    for pat in [
        r"外箱[^\d]{0,12}(\d+(?:\.\d+)?)\s*[×xX\*]\s*(\d+(?:\.\d+)?)\s*[×xX\*]\s*(\d+(?:\.\d+)?)\s*(?:cm|CM)?",
        r"纸箱[^\d]{0,12}(\d+(?:\.\d+)?)\s*[×xX\*]\s*(\d+(?:\.\d+)?)\s*[×xX\*]\s*(\d+(?:\.\d+)?)",
        r"包装[^\d]{0,12}(\d+(?:\.\d+)?)\s*[×xX\*]\s*(\d+(?:\.\d+)?)\s*[×xX\*]\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*[×xX\*]\s*(\d+(?:\.\d+)?)\s*[×xX\*]\s*(\d+(?:\.\d+)?)\s*(?:cm|厘米)",
    ]:
        m = re.search(pat, text)
        if m:
            try:
                return float(m.group(1)), float(m.group(2)), float(m.group(3))
            except ValueError:
                continue
    return 0.0, 0.0, 0.0


def _extract_gw_kg(html: str) -> float:
    text = _strip_html(html)
    for pat in [
        r"单箱毛重[^\d]{0,12}(\d+(?:\.\d+)?)\s*(?:kg|KG|千克)",
        r"毛重[^\d]{0,12}(\d+(?:\.\d+)?)\s*(?:kg|KG)",
        r"G\.?W\.?\s*[：:]\s*(\d+(?:\.\d+)?)\s*(?:kg|KG)?",
        r"箱重[^\d]{0,12}(\d+(?:\.\d+)?)\s*(?:kg|KG)",
    ]:
        m = re.search(pat, text, re.I)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                continue
    return 0.0


def _extract_description_text(html: str) -> str:
    """Pull plain-ish text from common detail JSON blobs."""
    chunks: List[str] = []
    for key in ("offerDesc", "detailUrl", "content", "attributes"):
        for m in re.finditer(
            rf'"{key}"\s*:\s*"((?:[^"\\]|\\.){{20,8000}})"',
            html,
        ):
            chunks.append(_strip_html(_json_unescape(m.group(1))))
    if not chunks:
        # table rows in page
        for m in re.finditer(r"<td[^>]*>([^<]{5,200})</td>", html, re.I):
            t = m.group(1).strip()
            if re.search(r"[规格尺寸重量材质]", t):
                chunks.append(t)
    body = "\n".join(dict.fromkeys([c for c in chunks if c]))
    return body[:4000] if body else ""


def _download_bytes(img_url: str, referer: str) -> Optional[bytes]:
    try:
        headers = {"User-Agent": MOBILE_UA, "Referer": referer or "https://m.1688.com/"}
        req = urllib.request.Request(img_url, headers=headers)
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            return r.read()
    except Exception:
        return None


def _try_playwright(url: str) -> Optional[str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=MOBILE_UA)
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            html = page.content()
            browser.close()
        return html
    except Exception:
        return None


@dataclass
class OfferImportResult:
    ok: bool = False
    error: str = ""
    offer_id: str = ""
    source_url: str = ""
    title: str = ""
    description: str = ""
    unit_price_usd: float = 0.0
    price_note: str = ""
    moq: int = 100
    carton_l: float = 0.0
    carton_w: float = 0.0
    carton_h: float = 0.0
    gw_per_ctn: float = 0.0
    packaging_rate: int = 1
    image_urls: List[str] = field(default_factory=list)
    main_image_bytes: Optional[bytes] = None
    main_image_filename: str = "1688_main.jpg"


def parse_offer_html(html: str, source_url: str, offer_id: str) -> OfferImportResult:
    res = OfferImportResult(ok=False, source_url=source_url, offer_id=offer_id or "")
    if not html or len(html) < 80:
        res.error = "页面内容过短，可能未加载成功。"
        return res
    if len(html) < 15000 and ("_____tmd_____" in html or "punish" in html or "captcha" in html.lower()):
        res.error = (
            "1688 返回了风控/验证页（非商品详情）。"
            "请在本地网络重试，或安装 Playwright：pip install playwright && playwright install chromium"
        )
        return res

    res.title = _extract_subject(html)
    res.image_urls = _extract_offer_images(html)
    prices = _extract_prices(html)
    if prices:
        # 1688 国内批发价多为人民币；粗略换算为美元展示（可在表单中再改）
        res.unit_price_usd = round(min(prices) * 0.14, 2)
        res.price_note = f"抓取到人民币参考价约 {min(prices):.2f} 元起（已按 0.14 估算美元，仅供参考）"
    res.moq = _extract_moq(html) or 100
    res.carton_l, res.carton_w, res.carton_h = _extract_carton_cm(html)
    res.gw_per_ctn = _extract_gw_kg(html)
    desc = _extract_description_text(html)
    if desc:
        res.description = desc
    elif res.title:
        res.description = res.title

    if res.image_urls:
        ref = mobile_offer_url(offer_id) if offer_id else source_url
        data = _download_bytes(res.image_urls[0], referer=ref)
        if data and len(data) > 500:
            res.main_image_bytes = data
            ext = ".jpg"
            low = res.image_urls[0].lower()
            if ".png" in low:
                ext, res.main_image_filename = ".png", "1688_main.png"
            elif ".webp" in low:
                ext, res.main_image_filename = ".webp", "1688_main.webp"
            res.main_image_filename = f"1688_main{ext}"

    res.ok = bool(res.title or res.image_urls or prices)
    if not res.ok:
        res.error = "未能从页面解析到标题/价格/图片。页面结构可能已变更或仍需验证。"
    return res


def fetch_1688_offer(url: str) -> OfferImportResult:
    url = (url or "").strip().splitlines()[0].strip()
    oid = extract_offer_id(url)
    if not oid:
        return OfferImportResult(ok=False, error="无法从链接中识别 offer id（需包含 offer/数字）。")
    mob = mobile_offer_url(oid)
    html = ""
    err_net = ""
    try:
        html = _http_get(mob, referer=mob)
    except Exception as e:
        err_net = str(e)

    result = parse_offer_html(html, source_url=url, offer_id=oid)
    if result.ok:
        return result

    if ("风控" in (result.error or "")) or len(html) < 15000:
        pw_html = _try_playwright(mob)
        if pw_html:
            result2 = parse_offer_html(pw_html, source_url=url, offer_id=oid)
            if result2.ok:
                return result2
            if len(pw_html) > len(html):
                return result2

    if err_net and not result.error:
        result.error = f"网络请求失败: {err_net}"
    return result
