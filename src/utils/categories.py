"""
src/utils/categories.py - Egyptian Product Categories
"""

CATEGORIES = [
    {'id': 'dairy', 'name_ar': 'ألبان', 'name_en': 'Dairy', 'icon': 'milk', 'keywords_ar': ['حليب', 'لبن', 'جبن', 'زبادي', 'قشطة'], 'keywords_en': ['milk', 'cheese', 'yogurt', 'cream']},
    {'id': 'meat', 'name_ar': 'لحوم', 'name_en': 'Meat', 'icon': 'meat', 'keywords_ar': ['لحم', 'دجاج', 'فراخ', 'سمك'], 'keywords_en': ['meat', 'chicken', 'fish', 'beef']},
    {'id': 'oils', 'name_ar': 'زيوت', 'name_en': 'Oils', 'icon': 'oil', 'keywords_ar': ['زيت', 'سمن'], 'keywords_en': ['oil', 'ghee', 'butter']},
    {'id': 'grains', 'name_ar': 'حبوب', 'name_en': 'Grains', 'icon': 'grain', 'keywords_ar': ['أرز', 'مكرونة', 'دقيق', 'عيش'], 'keywords_en': ['rice', 'pasta', 'flour', 'bread']},
    {'id': 'beverages', 'name_ar': 'مشروبات', 'name_en': 'Beverages', 'icon': 'drink', 'keywords_ar': ['عصير', 'مياه', 'شاي', 'قهوة', 'نسكافيه'], 'keywords_en': ['juice', 'water', 'tea', 'coffee']},
    {'id': 'snacks', 'name_ar': 'سناكس', 'name_en': 'Snacks', 'icon': 'snack', 'keywords_ar': ['شيبسي', 'بسكويت', 'شوكولاتة'], 'keywords_en': ['chips', 'biscuits', 'chocolate', 'cookies']},
    {'id': 'household', 'name_ar': 'منظفات', 'name_en': 'Household', 'icon': 'clean', 'keywords_ar': ['منظف', 'صابون', 'فيري', 'أومو'], 'keywords_en': ['detergent', 'soap', 'cleaner']},
    {'id': 'personal_care', 'name_ar': 'عناية شخصية', 'name_en': 'Personal Care', 'icon': 'person', 'keywords_ar': ['شامبو', 'معجون', 'صابون'], 'keywords_en': ['shampoo', 'toothpaste', 'soap']},
    {'id': 'baby', 'name_ar': 'أطفال', 'name_en': 'Baby', 'icon': 'baby', 'keywords_ar': ['حفاضات', 'بامبرز', 'لبن أطفال'], 'keywords_en': ['diapers', 'pampers', 'baby milk']},
    {'id': 'frozen', 'name_ar': 'مجمدات', 'name_en': 'Frozen', 'icon': 'frozen', 'keywords_ar': ['مجمد', 'ايس كريم'], 'keywords_en': ['frozen', 'ice cream']},
    {'id': 'bakery', 'name_ar': 'مخبوزات', 'name_en': 'Bakery', 'icon': 'bread', 'keywords_ar': ['خبز', 'توست', 'كعك'], 'keywords_en': ['bread', 'toast', 'cake']},
    {'id': 'vegetables', 'name_ar': 'خضروات', 'name_en': 'Vegetables', 'icon': 'vegetable', 'keywords_ar': ['خضار', 'طماطم', 'بطاطس', 'فاكهة'], 'keywords_en': ['vegetable', 'tomato', 'potato', 'fruit']},
]

def get_all_categories():
    """Get all categories"""
    return CATEGORIES

def match_category(product_name: str):
    """Match product name to category based on keywords"""
    product_lower = product_name.lower()
    
    for cat in CATEGORIES:
        # Check Arabic keywords
        for keyword in cat['keywords_ar']:
            if keyword in product_lower:
                return cat['name_ar'], cat['name_en']
        # Check English keywords
        for keyword in cat['keywords_en']:
            if keyword in product_lower:
                return cat['name_ar'], cat['name_en']
    
    return 'أخرى', 'Other'

def get_category_by_id(category_id: str):
    """Get category by ID"""
    for cat in CATEGORIES:
        if cat['id'] == category_id:
            return cat
    return None
