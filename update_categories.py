import pandas as pd

# New bilingual categories in order
NEW_CATEGORIES = [
    "1. New Employee Onboarding Pack (新员工入职礼包)",
    "2. Employee Wellness Gift Set (员工健康关怀)",
    "3. Spring Corporate Gift Set (春季企业答谢)",
    "4. Corporate Promotional Package (企业通用促销包)",
    "5. On-site Branding for Large Events (大型活动现场周边)",
    "6. ABA Therapy Toolkit Gift (ABA 特教感官工具)",
    "7. NGO or Healthcare Charity (NGO/医疗慈善机构)",
    "8. Gym Membership Package (健身会员礼包)",
    "9. Sports Brand Collection Swag (运动品牌联名周边)",
    "10. University Campus Spirit & Alumni Kit (大学校园/校友纪念)",
    "11. Eco-friendly Activity Pack (环保主题活动礼包)",
    "12. Summer Beach Vacation Kit (夏日沙滩度假)",
    "13. Outdoor Hiking Gear Set (户外徒步装备)",
    "14. Fishing Lure Equipment Set (路亚钓鱼装备)",
    "15. Travel Agency VIP Kit (旅行社 VIP 礼包)",
    "16. Globally Theme Park Water World Resort (主题乐园/水上世界)",
    "17. Music Festival / Rave Survival Kit (音乐节/狂欢生存包)",
    "18. Esports Gaming Exhibition Swag (电竞游戏展览周边)",
    "19. Coffee / Baking Shop Merch Kit (精品咖啡/烘焙店周边)",
    "20. Bar Craft Brewery Swag (精酿酒吧联名周边)",
    "21. Cosmetics Membership Package (美妆品牌会员礼盒)",
    "22. Jewelry Packaging Set (首饰/高定包装套装)",
    "23. Pet Love Package (宠物关怀/品牌主题礼包)",
    "24. Souvenir Gift Items (高端旅游纪念品)",
]

# Mapping from old category name to new bilingual
OLD_TO_NEW = {
    "New Employee Onboarding Pack": "1. New Employee Onboarding Pack (新员工入职礼包)",
    "Corporate Promotional Package": "4. Corporate Promotional Package (企业通用促销包)",
    "Cosmetics Membership Package": "21. Cosmetics Membership Package (美妆品牌会员礼盒)",
    "Esports Gaming Exhibition Swag": "18. Esports Gaming Exhibition Swag (电竞游戏展览周边)",
    "Eco-friendly Activity Pack": "11. Eco-friendly Activity Pack (环保主题活动礼包)",
    "Fishing Lure Equipment Set": "14. Fishing Lure Equipment Set (路亚钓鱼装备)",
    "Globally Theme Park Water World Resort": "16. Globally Theme Park Water World Resort (主题乐园/水上世界)",
    "Gym Membership Package": "8. Gym Membership Package (健身会员礼包)",
    "NGO or Healthcare Charity": "7. NGO or Healthcare Charity (NGO/医疗慈善机构)",
    "On-site Branding for Large Events": "5. On-site Branding for Large Events (大型活动现场周边)",
    "Outdoor Hiking Gear Set": "13. Outdoor Hiking Gear Set (户外徒步装备)",
    "Pet Love Package": "23. Pet Love Package (宠物关怀/品牌主题礼包)",
    "Sports Brand Collection Swag": "9. Sports Brand Collection Swag (运动品牌联名周边)",
    "Souvenir Gift Items": "24. Souvenir Gift Items (高端旅游纪念品)",
    "The Sand-Free Beach Vacation Kit": "12. Summer Beach Vacation Kit (夏日沙滩度假)",
    "Travel Agency VIP Kit": "15. Travel Agency VIP Kit (旅行社 VIP 礼包)",
    "University Campus Spirit & Alumni Kit": "10. University Campus Spirit & Alumni Kit (大学校园/校友纪念)",
    "Summer Beach Vacation Kit": "12. Summer Beach Vacation Kit (夏日沙滩度假)",
    # Add more if needed, some products may have "Coffee / Baking Shop Merch Kit" etc.
    "Coffee / Baking Shop Merch Kit": "19. Coffee / Baking Shop Merch Kit (精品咖啡/烘焙店周边)",
    "Bar Craft Brewery Swag": "20. Bar Craft Brewery Swag (精酿酒吧联名周边)",
    "Jewelry Packaging Set": "22. Jewelry Packaging Set (首饰/高定包装套装)",
    "Employee Wellness Gift Set": "2. Employee Wellness Gift Set (员工健康关怀)",
    "Spring Corporate Gift Set": "3. Spring Corporate Gift Set (春季企业答谢)",
    "ABA Therapy Toolkit Gift": "6. ABA Therapy Toolkit Gift (ABA 特教感官工具)",
    "Music Festival / Rave Survival Kit": "17. Music Festival / Rave Survival Kit (音乐节/狂欢生存包)",
}

def update_products_categories():
    df = pd.read_csv("data/products.csv")
    print("Before update, unique categories:")
    print(df["category"].unique().tolist())
    
    df["category"] = df["category"].map(lambda x: OLD_TO_NEW.get(x, x))
    
    df.to_csv("data/products.csv", index=False)
    print("\nAfter update, unique categories:")
    print(df["category"].unique().tolist())
    print("\nCSV updated successfully!")

if __name__ == "__main__":
    update_products_categories()