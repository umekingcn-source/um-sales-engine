import json
import urllib.request

OFFER = "680789723446"
endpoints = [
    f"https://detail.1688.com/offer/ajax/OfferDesc.json?offerId={OFFER}",
    f"https://detail.1688.com/offer/ajax/JsonpDetailData.do?offerId={OFFER}",
    f"https://m.1688.com/offer/ajax/OfferDetail.json?offerId={OFFER}",
]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
for ep in endpoints:
    try:
        req = urllib.request.Request(ep, headers={"User-Agent": UA, "Referer": f"https://detail.1688.com/offer/{OFFER}.html"})
        raw = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "replace")
        print("---", ep[:70])
        print("len", len(raw), "head", raw[:200].replace("\n", " "))
    except Exception as e:
        print("--- ERR", ep, e)
