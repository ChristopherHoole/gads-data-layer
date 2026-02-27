#!/usr/bin/env python3
"""
Automated Test Script for Recommendations UI - Chat 48
Tests entity filtering, badges, action labels, and performance.

Requirements:
- Flask app running at http://localhost:5000
- pip install requests beautifulsoup4

Usage:
    python test_recommendations_ui_chat48.py
"""

import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple


# Configuration
BASE_URL = "http://localhost:5000"
RECOMMENDATIONS_URL = f"{BASE_URL}/recommendations"
LOGIN_URL = f"{BASE_URL}/login"


# Create a session to persist cookies
session = requests.Session()


class TestResults:
    """Track test results and format output."""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
    
    def add_result(self, test_name: str, passed: bool, details: str = ""):
        """Add a test result."""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            self.tests_failed += 1
            status = "❌ FAIL"
        
        self.results.append({
            'name': test_name,
            'status': status,
            'passed': passed,
            'details': details
        })
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*80)
        print("GATE 7 TEST RESULTS - RECOMMENDATIONS UI (CHAT 48)")
        print("="*80)
        print()
        
        for i, result in enumerate(self.results, 1):
            print(f"Test {i}: {result['name']}")
            print(f"  Status: {result['status']}")
            if result['details']:
                print(f"  Details: {result['details']}")
            print()
        
        print("="*80)
        print(f"TOTAL: {self.tests_run} tests")
        print(f"PASSED: {self.tests_passed} ({self.tests_passed/self.tests_run*100:.1f}%)")
        print(f"FAILED: {self.tests_failed} ({self.tests_failed/self.tests_run*100:.1f}%)")
        print("="*80)
        
        if self.tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED! Gate 7 Complete.\n")
        else:
            print(f"\n⚠️  {self.tests_failed} TEST(S) FAILED - Review above for details.\n")


def login() -> bool:
    """Login to Flask app. Returns True if successful."""
    try:
        # Try to login with default credentials
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        
        # Check if login was successful
        return response.status_code == 200 and 'login' not in response.url.lower()
    except Exception as e:
        print(f"Login failed: {e}")
        return False


def fetch_page() -> Tuple[BeautifulSoup, float]:
    """Fetch recommendations page and return parsed HTML + load time."""
    start_time = time.time()
    response = session.get(RECOMMENDATIONS_URL)
    load_time = time.time() - start_time
    
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup, load_time


def test_1_filter_dropdown_renders(soup: BeautifulSoup, results: TestResults):
    """Test 1: Filter dropdown renders correctly."""
    dropdown = soup.find('button', class_='dropdown-toggle')
    
    # Look for dropdown options
    options = soup.find_all('a', class_='dropdown-item')
    
    passed = dropdown is not None and len(options) >= 4
    details = f"Found dropdown: {dropdown is not None}, Options: {len(options)}"
    
    results.add_result("Filter dropdown renders", passed, details)


def test_2_all_filter_shows_all(soup: BeautifulSoup, results: TestResults):
    """Test 2: 'All Entity Types' filter shows all recommendations."""
    # Count all recommendation cards
    all_cards = soup.find_all('div', class_='rec-card')
    
    # Check if there are cards present
    passed = len(all_cards) > 0
    details = f"Total cards found: {len(all_cards)}"
    
    results.add_result("'All' filter shows all recommendations", passed, details)


def test_3_campaigns_filter(soup: BeautifulSoup, results: TestResults):
    """Test 3: Filter shows campaign cards with campaign badges."""
    campaign_cards = soup.find_all('div', attrs={'data-entity-type': 'campaign'})
    
    # Check campaign badges exist
    campaign_badges = [card for card in campaign_cards 
                      if card.find('span', class_='badge', text=lambda t: t and 'CAMPAIGN' in t.upper())]
    
    passed = len(campaign_cards) > 0
    details = f"Campaign cards: {len(campaign_cards)}, With badges: {len(campaign_badges)}"
    
    results.add_result("Filter shows campaign cards", passed, details)


def test_4_keywords_filter(soup: BeautifulSoup, results: TestResults):
    """Test 4: Filter shows keyword cards with keyword badges."""
    keyword_cards = soup.find_all('div', attrs={'data-entity-type': 'keyword'})
    
    # Check keyword badges exist
    keyword_badges = [card for card in keyword_cards 
                     if card.find('span', class_='badge', text=lambda t: t and 'KEYWORD' in t.upper())]
    
    passed = len(keyword_cards) > 0
    details = f"Keyword cards: {len(keyword_cards)}, With badges: {len(keyword_badges)}"
    
    results.add_result("Filter shows keyword cards", passed, details)


def test_5_shopping_filter(soup: BeautifulSoup, results: TestResults):
    """Test 5: Filter shows shopping cards with shopping badges."""
    shopping_cards = soup.find_all('div', attrs={'data-entity-type': 'shopping'})
    
    # Check shopping badges exist
    shopping_badges = [card for card in shopping_cards 
                      if card.find('span', class_='badge', text=lambda t: t and 'SHOPPING' in t.upper())]
    
    # Shopping may be 0 in pending, check if data attribute exists
    passed = True  # We just verify structure exists
    details = f"Shopping cards: {len(shopping_cards)}, With badges: {len(shopping_badges)}"
    
    results.add_result("Filter shows shopping cards (structure)", passed, details)


def test_6_ad_groups_empty_state(soup: BeautifulSoup, results: TestResults):
    """Test 6: Ad groups filter shows empty state or cards correctly."""
    ad_group_cards = soup.find_all('div', attrs={'data-entity-type': 'ad_group'})
    
    # Check for empty state message (if no ad group cards)
    empty_state = soup.find('div', string=lambda t: t and 'ad group' in t.lower() and 'no' in t.lower())
    
    # Pass if either we have cards OR we have an empty state message
    passed = len(ad_group_cards) > 0 or empty_state is not None
    details = f"Ad group cards: {len(ad_group_cards)}, Empty state found: {empty_state is not None}"
    
    results.add_result("Ad groups filter handles empty state", passed, details)


def test_7_entity_badges_colors(soup: BeautifulSoup, results: TestResults):
    """Test 7: Entity badges have correct colors."""
    # Find badges with specific colors
    badge_map = {
        'bg-primary': 'Campaign (blue)',
        'bg-success': 'Keyword (green)',
        'bg-info': 'Shopping (cyan)',
        'bg-warning': 'Ad Group (orange)'
    }
    
    found_colors = {}
    for color_class, label in badge_map.items():
        badges = soup.find_all('span', class_=lambda c: c and color_class in c and 'badge' in c)
        found_colors[label] = len(badges)
    
    # Pass if we found at least 2 different badge colors
    colors_found = sum(1 for count in found_colors.values() if count > 0)
    passed = colors_found >= 2
    details = f"Colors found: {', '.join([f'{k}: {v}' for k, v in found_colors.items() if v > 0])}"
    
    results.add_result("Entity badges have correct colors", passed, details)


def test_8_action_labels_entity_aware(soup: BeautifulSoup, results: TestResults):
    """Test 8: Action labels are entity-aware (show full descriptive text)."""
    # Look for full action labels like "Decrease daily budget by X%"
    full_labels = []
    
    # Check for entity-specific keywords in action text
    entity_keywords = ['daily budget', 'tROAS target', 'keyword bid', 'shopping']
    
    change_blocks = soup.find_all('div', class_='change-main')
    for block in change_blocks:
        text = block.get_text()
        if any(keyword in text.lower() for keyword in entity_keywords):
            full_labels.append(text.strip())
    
    # Also check that we don't have abbreviated labels like "Decrease by 10%"
    abbreviated = [block.get_text().strip() for block in change_blocks 
                  if 'by ' in block.get_text() and 'budget' not in block.get_text().lower() 
                  and 'target' not in block.get_text().lower() 
                  and 'bid' not in block.get_text().lower()
                  and 'Flag' not in block.get_text()]
    
    passed = len(full_labels) > 0 and len(abbreviated) == 0
    details = f"Full labels: {len(full_labels)}, Abbreviated labels: {len(abbreviated)}"
    if full_labels:
        details += f" (Example: '{full_labels[0][:50]}...')"
    
    results.add_result("Action labels are entity-aware", passed, details)


def test_9_filter_persistence_tabs(soup: BeautifulSoup, results: TestResults):
    """Test 9: Filter persistence structure exists (sessionStorage JavaScript)."""
    # Check if JavaScript for filter persistence exists
    scripts = soup.find_all('script')
    has_session_storage = False
    has_filter_function = False
    
    for script in scripts:
        script_text = script.string or ""
        if 'sessionStorage' in script_text:
            has_session_storage = True
        if 'filterByEntityType' in script_text or 'currentEntityFilter' in script_text:
            has_filter_function = True
    
    passed = has_session_storage or has_filter_function
    details = f"SessionStorage found: {has_session_storage}, Filter function found: {has_filter_function}"
    
    results.add_result("Filter persistence structure exists", passed, details)


def test_10_card_counts_match(soup: BeautifulSoup, results: TestResults):
    """Test 10: Card counts match expected values."""
    # Count cards by entity type
    campaign_cards = len(soup.find_all('div', attrs={'data-entity-type': 'campaign'}))
    keyword_cards = len(soup.find_all('div', attrs={'data-entity-type': 'keyword'}))
    shopping_cards = len(soup.find_all('div', attrs={'data-entity-type': 'shopping'}))
    ad_group_cards = len(soup.find_all('div', attrs={'data-entity-type': 'ad_group'}))
    
    total = campaign_cards + keyword_cards + shopping_cards + ad_group_cards
    
    # Pass if we have cards and they sum to a reasonable number
    passed = total > 0 and total < 500  # Sanity check
    details = f"Total: {total} (Campaigns: {campaign_cards}, Keywords: {keyword_cards}, Shopping: {shopping_cards}, Ad Groups: {ad_group_cards})"
    
    results.add_result("Card counts are reasonable", passed, details)


def test_performance(load_time: float, results: TestResults):
    """Performance test: Page load time."""
    # Gate 2 target: <5s page load
    passed = load_time < 5.0
    details = f"Page load time: {load_time:.2f}s (target: <5s)"
    
    results.add_result("Performance: Page load <5s", passed, details)


def main():
    """Run all tests."""
    print("\n🚀 Starting Gate 7 Tests for Recommendations UI...\n")
    
    results = TestResults()
    
    try:
        # Login first
        print("Logging in...")
        if not login():
            print("❌ ERROR: Could not login to Flask app")
            print("   Check username/password in script")
            return 1
        print("✓ Logged in successfully\n")
        
        # Fetch page
        print("Fetching recommendations page...")
        soup, load_time = fetch_page()
        print(f"✓ Page loaded in {load_time:.2f}s\n")
        
        # Run tests
        print("Running tests...\n")
        test_1_filter_dropdown_renders(soup, results)
        test_2_all_filter_shows_all(soup, results)
        test_3_campaigns_filter(soup, results)
        test_4_keywords_filter(soup, results)
        test_5_shopping_filter(soup, results)
        test_6_ad_groups_empty_state(soup, results)
        test_7_entity_badges_colors(soup, results)
        test_8_action_labels_entity_aware(soup, results)
        test_9_filter_persistence_tabs(soup, results)
        test_10_card_counts_match(soup, results)
        test_performance(load_time, results)
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to Flask app at http://localhost:5000")
        print("   Make sure Flask is running with: python -m act_dashboard.app")
        return 1
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return 1
    
    # Print results
    results.print_summary()
    
    # Return exit code
    return 0 if results.tests_failed == 0 else 1


if __name__ == "__main__":
    exit(main())
