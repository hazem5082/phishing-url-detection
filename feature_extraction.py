"""
feature_extraction.py
=====================
URL feature extraction utilities for converting raw URLs to the 48 features
expected by the phishing detection model.

The Kaggle dataset uses Selenium-based feature extraction to generate 48 features
from URLs. This module provides similar feature extraction for testing.

Features extracted (48 total):
1. URL Length features (5-7)
2. Domain features (8-15)
3. Protocol features (16-18)
4. Special character counts (19-25)
5. Path/Query features (26-35)
6. TLD features (36-40)
7. Domain validity (41-48)
"""

import re
from urllib.parse import urlparse
from typing import List
import logging

logger = logging.getLogger(__name__)


class URLFeatureExtractor:
    """Extract 48 features from a URL for phishing detection."""
    
    def __init__(self):
        """Initialize the extractor."""
        self.features = []
    
    def extract(self, url: str) -> List[float]:
        """
        Extract 48 features from a URL.
        
        Parameters
        ----------
        url : str
            The URL to analyze
            
        Returns
        -------
        List[float]
            Array of 48 features
        """
        self.features = []
        self.url = url
        
        try:
            self.parsed_url = urlparse(url)
        except Exception as e:
            logger.error(f"Failed to parse URL: {e}")
            return [0.0] * 48
        
        # Extract all 48 features
        self._extract_url_length_features()      # 1-5
        self._extract_domain_features()          # 6-13
        self._extract_protocol_features()        # 14-16
        self._extract_special_char_features()    # 17-23
        self._extract_path_query_features()      # 24-33
        self._extract_tld_features()             # 34-38
        self._extract_domain_validity_features() # 39-48
        
        # Pad to 48 if needed
        while len(self.features) < 48:
            self.features.append(0.0)
        
        return self.features[:48]
    
    def _extract_url_length_features(self):
        """Extract URL length-based features."""
        url_len = len(self.url)
        self.features.extend([
            1 if url_len < 54 else -1,           # Short URL
            1 if 54 <= url_len < 75 else -1,     # Medium URL
            1 if url_len >= 75 else -1,          # Long URL
            len(self.parsed_url.path) / max(len(self.url), 1),  # Path ratio
            len(self.parsed_url.query) / max(len(self.url), 1), # Query ratio
        ])
    
    def _extract_domain_features(self):
        """Extract domain-based features."""
        domain = self.parsed_url.netloc
        
        # Subdomain count
        subdomain_count = domain.count('.')
        self.features.append(1 if subdomain_count < 2 else -1)
        
        # IP-based domain
        ip_pattern = r'^\d+\.\d+\.\d+\.\d+$'
        self.features.append(-1 if re.match(ip_pattern, domain) else 1)
        
        # Domain length
        self.features.append(1 if len(domain) < 40 else -1)
        
        # Domain starts with dash
        self.features.append(-1 if domain.startswith('-') else 1)
        
        # Domain ends with dash
        self.features.append(-1 if domain.endswith('-') else 1)
        
        # Hyphen count
        hyphen_count = domain.count('-')
        self.features.append(1 if hyphen_count < 2 else -1)
        
        # Multiple dots
        dot_count = domain.count('.')
        self.features.append(1 if dot_count < 3 else -1)
        
        # Numbers in domain
        has_numbers = any(c.isdigit() for c in domain)
        self.features.append(-1 if has_numbers else 1)
    
    def _extract_protocol_features(self):
        """Extract protocol-related features."""
        scheme = self.parsed_url.scheme
        
        # HTTPS scheme
        self.features.append(1 if scheme == 'https' else -1)
        
        # HTTP scheme
        self.features.append(1 if scheme == 'http' else -1)
        
        # Other scheme
        self.features.append(-1 if scheme not in ['http', 'https'] else 1)
    
    def _extract_special_char_features(self):
        """Extract special character count features."""
        path = self.parsed_url.path + (self.parsed_url.query or '')
        
        # At symbol (@)
        at_count = self.url.count('@')
        self.features.append(-1 if at_count > 0 else 1)
        
        # Question mark (?)
        question_count = self.url.count('?')
        self.features.append(1 if question_count < 2 else -1)
        
        # Ampersand (&)
        amp_count = self.url.count('&')
        self.features.append(1 if amp_count < 3 else -1)
        
        # Percent (%)
        percent_count = self.url.count('%')
        self.features.append(-1 if percent_count > 0 else 1)
        
        # Slash count in path
        slash_count = path.count('/')
        self.features.append(1 if slash_count < 5 else -1)
        
        # Dot count in path
        dot_count = path.count('.')
        self.features.append(1 if dot_count < 2 else -1)
        
        # Total special characters
        special_chars = len(re.findall(r'[^a-zA-Z0-9]', self.url))
        self.features.append(1 if special_chars < 15 else -1)
    
    def _extract_path_query_features(self):
        """Extract path and query features."""
        path = self.parsed_url.path
        query = self.parsed_url.query or ''
        
        # Path length
        self.features.append(1 if len(path) < 50 else -1)
        
        # Query length
        self.features.append(1 if len(query) < 80 else -1)
        
        # Query parameters count
        param_count = query.count('=')
        self.features.append(1 if param_count < 3 else -1)
        
        # Repeated parameters
        params = query.split('&')
        param_names = [p.split('=')[0] for p in params if '=' in p]
        unique_ratio = len(set(param_names)) / max(len(param_names), 1)
        self.features.append(unique_ratio)
        
        # Fragment (anchor) presence
        has_fragment = '#' in self.url
        self.features.append(1 if not has_fragment else -1)
        
        # File extension in path
        has_extension = bool(re.search(r'\.\w{2,4}$', path))
        self.features.append(-1 if has_extension else 1)
        
        # Directory levels
        dir_levels = len([x for x in path.split('/') if x])
        self.features.append(1 if dir_levels < 4 else -1)
        
        # Encoded characters in path
        encoded_count = len(re.findall(r'%[0-9A-F]{2}', self.url.upper()))
        self.features.append(-1 if encoded_count > 0 else 1)
        
        # Repeated slashes
        double_slash = '//' in path or '///' in self.url
        self.features.append(-1 if double_slash else 1)
    
    def _extract_tld_features(self):
        """Extract TLD (Top-Level Domain) features."""
        domain = self.parsed_url.netloc
        parts = domain.split('.')
        
        if len(parts) > 1:
            tld = parts[-1]
            
            # Common TLDs
            common_tlds = ['com', 'org', 'net', 'edu', 'gov', 'co', 'uk']
            self.features.append(1 if tld in common_tlds else -1)
            
            # TLD length
            self.features.append(1 if 2 <= len(tld) <= 6 else -1)
            
            # Numeric TLD
            is_numeric = tld.isdigit()
            self.features.append(-1 if is_numeric else 1)
            
            # Country TLD
            country_tlds = ['uk', 'us', 'ca', 'de', 'fr', 'au', 'jp', 'cn']
            is_country = tld in country_tlds
            self.features.append(1 if is_country else -1)
            
            # Suspicious TLD
            suspicious_tlds = ['tk', 'ml', 'ga', 'cf']
            is_suspicious = tld in suspicious_tlds
            self.features.append(-1 if is_suspicious else 1)
        else:
            self.features.extend([-1, -1, -1, -1, -1])
    
    def _extract_domain_validity_features(self):
        """Extract domain validity and trust features."""
        domain = self.parsed_url.netloc
        
        # Valid domain format
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        is_valid = bool(re.match(domain_pattern, domain))
        self.features.append(1 if is_valid else -1)
        
        # Consecutive dots
        has_consecutive_dots = '..' in domain
        self.features.append(-1 if has_consecutive_dots else 1)
        
        # Starts with www
        has_www = domain.startswith('www')
        self.features.append(1 if has_www else -1)
        
        # Registered domain length
        registered_domain = '.'.join(domain.split('.')[-2:])
        self.features.append(1 if 4 <= len(registered_domain) <= 20 else -1)
        
        # Subdomain level
        subdomain_levels = len(domain.split('.'))
        self.features.append(1 if subdomain_levels <= 3 else -1)
        
        # Domain age (we can't determine this, so estimate)
        self.features.append(0.5)
        
        # Google index (we can't check, so neutral)
        self.features.append(0.5)
        
        # PageRank (we can't check, so neutral)
        self.features.append(0.5)
        
        # Known phishing site (simplified check)
        known_phishing = ['paypal-verify', 'amazon-confirm', 'apple-signin']
        is_known_phishing = any(p in self.url.lower() for p in known_phishing)
        self.features.append(-1 if is_known_phishing else 1)


def extract_features_from_url(url: str) -> List[float]:
    """
    Convenience function to extract features from a URL.
    
    Parameters
    ----------
    url : str
        The URL to analyze
        
    Returns
    -------
    List[float]
        Array of 48 features
    """
    extractor = URLFeatureExtractor()
    return extractor.extract(url)


# ============================================================================
# Example URLs for Testing
# ============================================================================

EXAMPLE_PHISHING_URLS = [
    "http://paypal-verify.com/login.html",
    "https://www.amaz0n.com/account",
    "http://apple-signin.co.uk/verify",
    "https://199.192.168.1/bank/login",
    "http://secure-paypal.tk/verify",
]

EXAMPLE_LEGITIMATE_URLS = [
    "https://www.google.com",
    "https://www.github.com",
    "https://www.wikipedia.org",
    "https://www.amazon.com",
    "https://www.facebook.com",
]


if __name__ == "__main__":
    print("\n" + "="*80)
    print("URL FEATURE EXTRACTION EXAMPLES")
    print("="*80 + "\n")
    
    print("PHISHING URLS:")
    print("-" * 80)
    for url in EXAMPLE_PHISHING_URLS:
        features = extract_features_from_url(url)
        print(f"\nURL: {url}")
        print(f"Features (first 10): {features[:10]}")
        print(f"Feature array length: {len(features)}")
    
    print("\n\nLEGITIMATE URLS:")
    print("-" * 80)
    for url in EXAMPLE_LEGITIMATE_URLS:
        features = extract_features_from_url(url)
        print(f"\nURL: {url}")
        print(f"Features (first 10): {features[:10]}")
        print(f"Feature array length: {len(features)}")
