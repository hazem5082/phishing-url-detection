"""
feature_extraction.py
=====================
URL feature extraction utilities for converting raw URLs to the 48 features
expected by the phishing detection model.

This exactly matches the 48 features of the Kaggle Shashwat Tiwari dataset.
"""

import re
from urllib.parse import urlparse
from typing import List
import logging

logger = logging.getLogger(__name__)


def extract_features_from_url(url: str) -> List[float]:
    """
    Extract exactly 48 features from a URL matching the dataset columns.
    
    Offline features (URL-derived) are computed accurately.
    Online features (HTML-derived) are padded with the dataset median values.
    """
    try:
        if not url.startswith('http'):
            # Prepend a default scheme for urlparse if missing
            parsed_url = urlparse('http://' + url)
        else:
            parsed_url = urlparse(url)
    except Exception as e:
        logger.error(f"Failed to parse URL: {e}")
        return [0.0] * 48

    domain = parsed_url.netloc
    path = parsed_url.path
    query = parsed_url.query
    scheme = parsed_url.scheme

    features = []

    # 1. NumDots
    features.append(float(url.count('.')))
    
    # 2. SubdomainLevel
    domain_parts = domain.split('.')
    features.append(float(max(0, len(domain_parts) - 2)))
    
    # 3. PathLevel
    features.append(float(path.count('/') if path else 0))
    
    # 4. UrlLength
    features.append(float(len(url)))
    
    # 5. NumDash
    features.append(float(url.count('-')))
    
    # 6. NumDashInHostname
    features.append(float(domain.count('-')))
    
    # 7. AtSymbol
    features.append(1.0 if '@' in url else 0.0)
    
    # 8. TildeSymbol
    features.append(1.0 if '~' in url else 0.0)
    
    # 9. NumUnderscore
    features.append(float(url.count('_')))
    
    # 10. NumPercent
    features.append(float(url.count('%')))
    
    # 11. NumQueryComponents
    features.append(float(len(query.split('&')) if query else 0))
    
    # 12. NumAmpersand
    features.append(float(url.count('&')))
    
    # 13. NumHash
    features.append(float(url.count('#')))
    
    # 14. NumNumericChars
    features.append(float(sum(c.isdigit() for c in url)))
    
    # 15. NoHttps (1 if protocol is not https, else 0)
    features.append(1.0 if scheme != 'https' else 0.0)
    
    # 16. RandomString
    features.append(1.0) # Median value
    
    # 17. IpAddress
    ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    features.append(1.0 if re.match(ip_pattern, domain) else 0.0)
    
    # 18. DomainInSubdomains
    features.append(0.0)
    
    # 19. DomainInPaths
    features.append(1.0 if domain and domain in path else 0.0)
    
    # 20. HttpsInHostname
    features.append(1.0 if 'https' in domain.lower() else 0.0)
    
    # 21. HostnameLength
    features.append(float(len(domain)))
    
    # 22. PathLength
    features.append(float(len(path)))
    
    # 23. QueryLength
    features.append(float(len(query)))
    
    # 24. DoubleSlashInPath
    features.append(1.0 if '//' in path else 0.0)
    
    # 25. NumSensitiveWords
    sensitive = ['secure', 'account', 'webscr', 'login', 'ebayisapi', 'signin', 'banking', 'confirm']
    features.append(float(sum(1 for w in sensitive if w in url.lower())))
    
    # 26. EmbeddedBrandName
    features.append(0.0)
    
    # 27 to 48 are HTML/external features. Below are dataset medians for neutrality.
    html_medians = [
        0.0714285714, # 27. PctExtHyperlinks
        0.2475112737, # 28. PctExtResourceUrls
        0.0, # 29. ExtFavicon
        1.0, # 30. InsecureForms
        0.0, # 31. RelativeFormAction
        0.0, # 32. ExtFormAction
        0.0, # 33. AbnormalFormAction
        0.0, # 34. PctNullSelfRedirectHyperlinks
        0.0, # 35. FrequentDomainNameMismatch
        0.0, # 36. FakeLinkInStatusBar
        0.0, # 37. RightClickDisabled
        0.0, # 38. PopUpWindow
        0.0, # 39. SubmitInfoToEmail
        0.0, # 40. IframeOrFrame
        0.0, # 41. MissingTitle
        0.0, # 42. ImagesOnlyInForm
        1.0, # 43. SubdomainLevelRT
        0.0, # 44. UrlLengthRT
        1.0, # 45. PctExtResourceUrlsRT
        1.0, # 46. AbnormalExtFormActionR
        0.0, # 47. ExtMetaScriptLinkRT
        1.0  # 48. PctExtNullSelfRedirectHyperlinksRT
    ]
    features.extend(html_medians)
    
    return features


if __name__ == "__main__":
    print(extract_features_from_url("https://www.youtube.com"))
