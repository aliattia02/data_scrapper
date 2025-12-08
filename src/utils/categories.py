"""
src/utils/categories.py - Category matching and management
"""
from typing import Tuple, List, Dict


CATEGORIES = [
    {
        'id': 'dairy',
        'name_ar': 'منتجات الألبان',
        'name_en': 'Dairy Products',
        'icon': '🥛',
        'keywords_ar': ['حليب', 'لبن', 'جبن', 'زبادي', 'روب', 'قشطة', 'زبدة', 'جبنة'],
        'keywords_en': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'dairy']
    },
    {
        'id': 'meat',
        'name_ar': 'اللحوم والدواجن',
        'name_en': 'Meat & Poultry',
        'icon': '🍖',
        'keywords_ar': ['لحم', 'دجاج', 'فراخ', 'بيف', 'كفتة', 'سجق', 'همبرجر'],
        'keywords_en': ['meat', 'chicken', 'beef', 'poultry', 'burger', 'sausage']
    },
    {
        'id': 'fish',
        'name_ar': 'الأسماك والمأكولات البحرية',
        'name_en': 'Fish & Seafood',
        'icon': '🐟',
        'keywords_ar': ['سمك', 'جمبري', 'كابوريا', 'تونة'],
        'keywords_en': ['fish', 'shrimp', 'tuna', 'seafood', 'salmon']
    },
    {
        'id': 'fruits',
        'name_ar': 'الفواكه',
        'name_en': 'Fruits',
        'icon': '🍎',
        'keywords_ar': ['تفاح', 'موز', 'برتقال', 'عنب', 'فراولة', 'مانجو', 'بطيخ', 'فاكهة'],
        'keywords_en': ['apple', 'banana', 'orange', 'grape', 'strawberry', 'mango', 'fruit']
    },
    {
        'id': 'vegetables',
        'name_ar': 'الخضروات',
        'name_en': 'Vegetables',
        'icon': '🥕',
        'keywords_ar': ['طماطم', 'بطاطس', 'خيار', 'جزر', 'بصل', 'خضار', 'فلفل', 'كوسة'],
        'keywords_en': ['tomato', 'potato', 'cucumber', 'carrot', 'onion', 'vegetable', 'pepper']
    },
    {
        'id': 'bakery',
        'name_ar': 'المخبوزات',
        'name_en': 'Bakery',
        'icon': '🍞',
        'keywords_ar': ['خبز', 'عيش', 'كيك', 'بسكويت', 'كرواسون'],
        'keywords_en': ['bread', 'cake', 'cookie', 'biscuit', 'croissant', 'bakery']
    },
    {
        'id': 'rice',
        'name_ar': 'الأرز والمكرونة',
        'name_en': 'Rice & Pasta',
        'icon': '🍚',
        'keywords_ar': ['أرز', 'رز', 'مكرونة', 'معكرونة', 'باستا', 'شعرية'],
        'keywords_en': ['rice', 'pasta', 'noodles', 'spaghetti', 'macaroni']
    },
    {
        'id': 'oils',
        'name_ar': 'الزيوت والسمن',
        'name_en': 'Oils & Ghee',
        'icon': '🛢️',
        'keywords_ar': ['زيت', 'سمن', 'زبدة'],
        'keywords_en': ['oil', 'ghee', 'butter', 'margarine']
    },
    {
        'id': 'beverages',
        'name_ar': 'المشروبات',
        'name_en': 'Beverages',
        'icon': '🥤',
        'keywords_ar': ['عصير', 'مياه', 'ماء', 'شاي', 'قهوة', 'نسكافيه', 'كولا', 'بيبسي'],
        'keywords_en': ['juice', 'water', 'tea', 'coffee', 'cola', 'pepsi', 'beverage', 'drink']
    },
    {
        'id': 'snacks',
        'name_ar': 'الوجبات الخفيفة',
        'name_en': 'Snacks',
        'icon': '🍿',
        'keywords_ar': ['شيبسي', 'بسكويت', 'شوكولاتة', 'حلويات', 'سناك'],
        'keywords_en': ['chips', 'snack', 'chocolate', 'candy', 'sweets', 'popcorn']
    },
    {
        'id': 'frozen',
        'name_ar': 'المجمدات',
        'name_en': 'Frozen Foods',
        'icon': '❄️',
        'keywords_ar': ['مجمد', 'آيس كريم', 'بوظة'],
        'keywords_en': ['frozen', 'ice cream', 'popsicle']
    },
    {
        'id': 'cleaning',
        'name_ar': 'منتجات التنظيف',
        'name_en': 'Cleaning Products',
        'icon': '🧹',
        'keywords_ar': ['منظف', 'صابون', 'مسحوق', 'تايد', 'أومو', 'فيري', 'ديتول'],
        'keywords_en': ['detergent', 'soap', 'cleaner', 'tide', 'omo', 'fairy', 'dettol']
    },
    {
        'id': 'personal_care',
        'name_ar': 'العناية الشخصية',
        'name_en': 'Personal Care',
        'icon': '🧴',
        'keywords_ar': ['شامبو', 'صابون', 'معجون', 'فرشاة', 'كريم', 'مزيل'],
        'keywords_en': ['shampoo', 'soap', 'toothpaste', 'cream', 'deodorant', 'lotion']
    },
    {
        'id': 'baby',
        'name_ar': 'منتجات الأطفال',
        'name_en': 'Baby Products',
        'icon': '👶',
        'keywords_ar': ['حفاضات', 'بامبرز', 'لبن أطفال', 'سيريلاك'],
        'keywords_en': ['diaper', 'pampers', 'baby', 'infant', 'cerelac']
    },
    {
        'id': 'other',
        'name_ar': 'منتجات أخرى',
        'name_en': 'Other Products',
        'icon': '📦',
        'keywords_ar': [],
        'keywords_en': []
    }
]


def match_category(product_name: str) -> Tuple[str, str]:
    """
    Match product name to category
    Returns: (category_ar, category_en)
    """
    if not product_name:
        return "منتجات أخرى", "Other Products"

    product_name_lower = product_name.lower()

    # Check each category
    for category in CATEGORIES:
        # Check Arabic keywords
        for keyword in category['keywords_ar']:
            if keyword in product_name_lower:
                return category['name_ar'], category['name_en']

        # Check English keywords
        for keyword in category['keywords_en']:
            if keyword in product_name_lower:
                return category['name_ar'], category['name_en']

    # Default to "Other"
    return "منتجات أخرى", "Other Products"


def get_all_categories() -> List[Dict]:
    """Get all categories for database seeding"""
    return CATEGORIES


def get_category_by_id(category_id: str) -> Dict:
    """Get category by ID"""
    for category in CATEGORIES:
        if category['id'] == category_id:
            return category
    return CATEGORIES[-1]  # Return 'other' as default