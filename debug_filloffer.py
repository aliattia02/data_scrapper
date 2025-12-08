"""
Debug script to inspect Filloffer page structure
Usage: python debug_filloffer.py
"""
import requests
from bs4 import BeautifulSoup
import re

# Test URL
TEST_URL = "https://www.filloffer.com/markets/Kazyon-Market/new-offers-from-Kazyon-market-Weekend-starting-from-2-december-to-8-december/pdf"

print(f"🔍 Inspecting: {TEST_URL}\n")

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

response = session.get(TEST_URL, timeout=30)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.text, 'lxml')

print("=" * 60)
print("METHOD 1: Looking for <img> tags")
print("=" * 60)
images = soup.find_all('img')
print(f"Found {len(images)} img tags\n")

for i, img in enumerate(images[:5], 1):
    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
    alt = img.get('alt', '')
    print(f"{i}. SRC: {src}")
    print(f"   ALT: {alt}")
    print(f"   CLASS: {img.get('class')}")
    print()

print("=" * 60)
print("METHOD 2: Searching for image URLs in HTML")
print("=" * 60)

# Look for .jpg, .png patterns
img_pattern = r'(https?://[^\s"\'<>]+\.(?:jpg|jpeg|png))'
img_urls = re.findall(img_pattern, response.text, re.IGNORECASE)
print(f"Found {len(img_urls)} image URLs\n")

for i, url in enumerate(img_urls[:10], 1):
    print(f"{i}. {url}")

print("\n" + "=" * 60)
print("METHOD 3: Looking for PDF patterns")
print("=" * 60)

pdf_pattern = r'(https?://[^\s"\'<>]+\.pdf)'
pdf_urls = re.findall(pdf_pattern, response.text, re.IGNORECASE)
print(f"Found {len(pdf_urls)} PDF URLs\n")

for i, url in enumerate(pdf_urls[:5], 1):
    print(f"{i}. {url}")

print("\n" + "=" * 60)
print("METHOD 4: Looking in <script> tags")
print("=" * 60)

scripts = soup.find_all('script')
print(f"Found {len(scripts)} script tags\n")

for i, script in enumerate(scripts[:3], 1):
    if script.string and len(script.string) > 100:
        print(f"Script {i} (first 500 chars):")
        print(script.string[:500])
        print("...\n")

print("=" * 60)
print("METHOD 5: Looking for specific Filloffer patterns")
print("=" * 60)

# Filloffer specific patterns
patterns = [
    r'uploads/catalogues/[^"\']+',
    r'catalogue.*?\.jpg',
    r'page.*?\.(?:jpg|png)',
    r'viewer.*?src.*?["\']([^"\']+)',
]

for pattern in patterns:
    matches = re.findall(pattern, response.text, re.IGNORECASE)
    if matches:
        print(f"\nPattern '{pattern}':")
        for match in matches[:3]:
            print(f"  - {match}")

print("\n" + "=" * 60)
print("METHOD 6: Looking for canvas/embed elements")
print("=" * 60)

embeds = soup.find_all(['embed', 'object', 'iframe', 'canvas'])
print(f"Found {len(embeds)} embed-like elements\n")

for elem in embeds:
    print(f"<{elem.name}>")
    for attr in ['src', 'data', 'data-src']:
        if elem.get(attr):
            print(f"  {attr}: {elem.get(attr)}")
    print()

print("=" * 60)
print("SAVING HTML for manual inspection")
print("=" * 60)

with open('debug_filloffer_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print("✓ Saved to: debug_filloffer_page.html")
print("\nOpen this file in a text editor and search for:")
print("  - 'uploads/'")
print("  - '.jpg'")
print("  - 'catalogue'")
print("  - 'page'")
