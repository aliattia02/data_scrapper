"""
tests/test_models.py - Tests for database models
"""
import pytest
from datetime import datetime
from src.database.models import Store, Branch, Category, Product


def test_store_model():
    """Test Store model creation"""
    store = Store(
        store_id="kazyon",
        name_ar="كازيون",
        name_en="Kazyon",
        active=True
    )
    
    assert store.store_id == "kazyon"
    assert store.name_ar == "كازيون"
    assert store.name_en == "Kazyon"
    assert store.active is True


def test_category_model():
    """Test Category model creation"""
    category = Category(
        category_id="dairy",
        name_ar="ألبان",
        name_en="Dairy",
        icon="milk",
        active=True
    )
    
    assert category.category_id == "dairy"
    assert category.name_ar == "ألبان"
    assert category.name_en == "Dairy"
    assert category.icon == "milk"


def test_product_model():
    """Test Product model creation"""
    product = Product(
        store_product_id="kazyon_123",
        store="kazyon",
        name_ar="حليب المراعي",
        name_en="Almarai Milk",
        category_ar="ألبان",
        category_en="Dairy",
        price=25.99,
        currency="EGP",
        in_stock=True
    )
    
    assert product.store == "kazyon"
    assert product.price == 25.99
    assert product.currency == "EGP"


def test_product_to_dict():
    """Test Product model to_dict method"""
    product = Product(
        store_product_id="test_123",
        store="carrefour",
        name_ar="منتج تجريبي",
        name_en="Test Product",
        price=10.0,
        currency="EGP"
    )
    
    product_dict = product.to_dict()
    
    assert "id" in product_dict
    assert product_dict["store"] == "carrefour"
    assert product_dict["price"] == 10.0
