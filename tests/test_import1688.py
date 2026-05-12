"""Unit tests for 1688 HTML parsing (no network)."""
import sys
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

import import1688 as i1688


SAMPLE_HTML = """
<html><body>
<script>
var x = {"offerId":680789723446,"subject":"Test Metal Pen Product","consignPrice":"2.50","beginNum":200,
"offerDesc":"Material: Metal<br>Length: 14cm"};
</script>
<img src="https://img.alicdn.com/imgextra/i2/O1CN01Test_!!6000000001-0-tps-800-800.jpg" />
外箱尺寸 30*25*20cm 单箱毛重 8.5kg
</body></html>
"""


def test_parse_sample_html():
    r = i1688.parse_offer_html(SAMPLE_HTML, source_url="https://detail.1688.com/offer/680789723446.html", offer_id="680789723446")
    assert r.ok
    assert "Test Metal" in r.title
    assert r.moq == 200
    assert r.carton_l == 30.0 and r.carton_w == 25.0 and r.carton_h == 20.0
    assert abs(r.gw_per_ctn - 8.5) < 0.01
    assert r.unit_price_usd > 0


if __name__ == "__main__":
    test_parse_sample_html()
    print("OK import1688 parse")
