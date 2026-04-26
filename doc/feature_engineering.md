# Feature Engineering Documentation

## Overview

The feature engineering module converts raw URLs into the 48-dimensional feature vectors required by the phishing detection models. These features are based on the Kaggle Phishing Dataset for Machine Learning by Shashwat Tiwari.

## Feature Categories

### 1. Lexical Features (URL-based)
These features are extracted directly from the URL string without making any network requests.

#### 1.1 NumDots
- **Description**: Count of dot (.) characters in the URL
- **Rationale**: Phishing URLs often have excessive subdomains
- **Example**: `https://www.example.com` → 2 dots

#### 1.2 SubdomainLevel
- **Description**: Number of subdomain levels
- **Calculation**: max(0, domain_parts.length - 2)
- **Example**: `a.b.c.example.com` → 3 subdomain levels

#### 1.3 PathLevel
- **Description**: Number of path segments (count of /)
- **Rationale**: Deep paths may indicate obfuscation
- **Example**: `/path/to/page` → 3 path levels

#### 1.4 UrlLength
- **Description**: Total length of the URL string
- **Rationale**: Phishing URLs are often unusually long
- **Example**: `https://example.com` → 18 characters

#### 1.5 NumDash
- **Description**: Count of dash (-) characters
- **Rationale**: Dashes used to mimic legitimate domains
- **Example**: `https://my-example.com` → 1 dash

#### 1.6 NumDashInHostname
- **Description**: Count of dashes in the hostname only
- **Rationale**: Dash-heavy hostnames are suspicious
- **Example**: `my-example-site.com` → 2 dashes

#### 1.7 AtSymbol
- **Description**: Binary indicator (1 if @ present, else 0)
- **Rationale**: @ symbol used for credential theft
- **Example**: `https://user@example.com` → 1

#### 1.8 TildeSymbol
- **Description**: Binary indicator (1 if ~ present, else 0)
- **Rationale**: Tilde often indicates personal/home directories
- **Example**: `https://example.com/~user` → 1

#### 1.9 NumUnderscore
- **Description**: Count of underscore (_) characters
- **Rationale**: Uncommon in legitimate URLs
- **Example**: `https://example.com/page_1` → 1

#### 1.10 NumPercent
- **Description**: Count of percent (%) characters
- **Rationale**: URL encoding often used in phishing
- **Example**: `https://example.com/%20` → 1

#### 1.11 NumQueryComponents
- **Description**: Number of query parameters
- **Calculation**: Count of & in query string
- **Example**: `?a=1&b=2&c=3` → 3 components

#### 1.12 NumAmpersand
- **Description**: Count of ampersand (&) characters
- **Rationale**: Multiple parameters may indicate tracking
- **Example**: `?a=1&b=2` → 1 ampersand

#### 1.13 NumHash
- **Description**: Count of hash (#) characters
- **Rationale**: Fragment identifiers used for obfuscation
- **Example**: `https://example.com#section` → 1

#### 1.14 NumNumericChars
- **Description**: Count of numeric characters (0-9)
- **Rationale**: Phishing URLs often contain random numbers
- **Example**: `https://example123.com` → 3

#### 1.15 NoHttps
- **Description**: Binary indicator (1 if not https, else 0)
- **Rationale**: Phishing sites often use http
- **Example**: `http://example.com` → 1

#### 1.16 RandomString
- **Description**: Indicator of random character sequences
- **Note**: Padded with dataset median (1.0) for offline prediction

### 2. Host-Based Features
These features analyze the domain and host structure.

#### 2.1 IpAddress
- **Description**: Binary indicator (1 if IP address used, else 0)
- **Pattern**: `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`
- **Rationale**: Direct IP addresses are suspicious
- **Example**: `https://192.168.1.1` → 1

#### 2.2 DomainInSubdomains
- **Description**: Binary indicator if domain appears in subdomains
- **Note**: Currently set to 0.0 (simplified)

#### 2.3 DomainInPaths
- **Description**: Binary indicator if domain appears in path
- **Rationale**: May indicate URL manipulation
- **Example**: `https://example.com/example.com/page` → 1

#### 2.4 HttpsInHostname
- **Description**: Binary indicator if 'https' in hostname
- **Rationale**: Attempt to appear secure
- **Example**: `https-secure.example.com` → 1

#### 2.5 HostnameLength
- **Description**: Length of the hostname
- **Rationale**: Unusually long hostnames are suspicious
- **Example**: `www.example.com` → 15

#### 2.6 PathLength
- **Description**: Length of the path component
- **Rationale**: Long paths may indicate obfuscation
- **Example**: `/path/to/page` → 13

#### 2.7 QueryLength
- **Description**: Length of the query string
- **Rationale**: Long queries may contain malicious payloads
- **Example**: `?a=1&b=2` → 6

#### 2.8 DoubleSlashInPath
- **Description**: Binary indicator if // in path
- **Rationale**: May indicate protocol confusion
- **Example**: `/path//to/page` → 1

#### 2.9 NumSensitiveWords
- **Description**: Count of sensitive keywords
- **Keywords**: secure, account, webscr, login, ebayisapi, signin, banking, confirm
- **Rationale**: Phishing often mimics login pages
- **Example**: `https://example.com/login` → 1

#### 2.10 EmbeddedBrandName
- **Description**: Binary indicator if brand name embedded
- **Note**: Currently set to 0.0 (simplified)

### 3. HTML-Derived Features (Features 27-48)
These features require analyzing the HTML content of the page. For offline prediction, these are padded with dataset median values to maintain the 48-feature dimensionality.

#### 3.1 PctExtHyperlinks (Feature 27)
- **Description**: Percentage of external hyperlinks
- **Median**: 0.0714285714

#### 3.2 PctExtResourceUrls (Feature 28)
- **Description**: Percentage of external resource URLs
- **Median**: 0.2475112737

#### 3.3 ExtFavicon (Feature 29)
- **Description**: Binary indicator for external favicon
- **Median**: 0.0

#### 3.4 InsecureForms (Feature 30)
- **Description**: Binary indicator for insecure forms
- **Median**: 1.0

#### 3.5 RelativeFormAction (Feature 31)
- **Description**: Binary indicator for relative form action
- **Median**: 0.0

#### 3.6 ExtFormAction (Feature 32)
- **Description**: Binary indicator for external form action
- **Median**: 0.0

#### 3.7 AbnormalFormAction (Feature 33)
- **Description**: Binary indicator for abnormal form action
- **Median**: 0.0

#### 3.8 PctNullSelfRedirectHyperlinks (Feature 34)
- **Description**: Percentage of null self-redirect hyperlinks
- **Median**: 0.0

#### 3.9 FrequentDomainNameMismatch (Feature 35)
- **Description**: Binary indicator for domain name mismatch
- **Median**: 0.0

#### 3.10 FakeLinkInStatusBar (Feature 36)
- **Description**: Binary indicator for fake status bar links
- **Median**: 0.0

#### 3.11 RightClickDisabled (Feature 37)
- **Description**: Binary indicator if right-click disabled
- **Median**: 0.0

#### 3.12 PopUpWindow (Feature 38)
- **Description**: Binary indicator for popup windows
- **Median**: 0.0

#### 3.13 SubmitInfoToEmail (Feature 39)
- **Description**: Binary indicator if form submits to email
- **Median**: 0.0

#### 3.14 IframeOrFrame (Feature 40)
- **Description**: Binary indicator for iframe/frame usage
- **Median**: 0.0

#### 3.15 MissingTitle (Feature 41)
- **Description**: Binary indicator if page title missing
- **Median**: 0.0

#### 3.16 ImagesOnlyInForm (Feature 42)
- **Description**: Binary indicator if form contains only images
- **Median**: 0.0

#### 3.17 SubdomainLevelRT (Feature 43)
- **Description**: Subdomain level (right-click test)
- **Median**: 1.0

#### 3.18 UrlLengthRT (Feature 44)
- **Description**: URL length (right-click test)
- **Median**: 0.0

#### 3.19 PctExtResourceUrlsRT (Feature 45)
- **Description**: External resource percentage (right-click test)
- **Median**: 1.0

#### 3.20 AbnormalExtFormActionR (Feature 46)
- **Description**: Abnormal external form action (right-click test)
- **Median**: 1.0

#### 3.21 ExtMetaScriptLinkRT (Feature 47)
- **Description**: External meta/script/link (right-click test)
- **Median**: 0.0

#### 3.22 PctExtNullSelfRedirectHyperlinksRT (Feature 48)
- **Description**: Null self-redirect percentage (right-click test)
- **Median**: 1.0

## Feature Extraction Process

### Input
```python
url = "https://www.example.com/login?user=test"
```

### Processing Steps
1. **Parse URL**: Use urllib.parse to extract components
2. **Extract Lexical Features**: Count characters, analyze structure
3. **Extract Host Features**: Analyze domain, path, query
4. **Pad HTML Features**: Use dataset medians for offline prediction
5. **Return**: List of 48 float values

### Output
```python
features = [
    2.0,    # NumDots
    1.0,    # SubdomainLevel
    1.0,    # PathLevel
    42.0,   # UrlLength
    0.0,    # NumDash
    0.0,    # NumDashInHostname
    0.0,    # AtSymbol
    0.0,    # TildeSymbol
    0.0,    # NumUnderscore
    0.0,    # NumPercent
    1.0,    # NumQueryComponents
    0.0,    # NumAmpersand
    0.0,    # NumHash
    0.0,    # NumNumericChars
    0.0,    # NoHttps
    1.0,    # RandomString (median)
    0.0,    # IpAddress
    0.0,    # DomainInSubdomains
    0.0,    # DomainInPaths
    0.0,    # HttpsInHostname
    15.0,   # HostnameLength
    6.0,    # PathLength
    10.0,   # QueryLength
    0.0,    # DoubleSlashInPath
    1.0,    # NumSensitiveWords
    0.0,    # EmbeddedBrandName
    # ... HTML features (median values)
]
```

## Usage Example

```python
from src.feature_engineering.feature_extractor import extract_features_from_url

url = "https://www.example.com/login"
features = extract_features_from_url(url)
print(f"Extracted {len(features)} features")
```

## Limitations

1. **HTML Features**: Offline prediction cannot extract HTML-derived features
2. **Brand Detection**: Simplified brand name detection
3. **Domain Analysis**: Basic domain analysis without external lookups
4. **Context**: No historical or reputation-based features

## Future Enhancements

1. **Real HTML Analysis**: Fetch and analyze actual page content
2. **Domain Reputation**: Integrate with domain reputation APIs
3. **Brand Database**: Comprehensive brand name detection
4. **Behavioral Features**: Mouse movement, typing patterns
5. **Time-Based Features**: Registration age, SSL certificate age
