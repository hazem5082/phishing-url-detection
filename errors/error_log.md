# Error Log

This document tracks errors encountered during development and their fixes.

## Error Log Format

Each error entry should include:
- **Date**: When the error occurred
- **Error Type**: Category of error
- **Description**: What happened
- **Fix**: How it was resolved
- **Status**: Resolved/Pending

---

## Error Entries

### [Template for New Errors]

**Date**: YYYY-MM-DD  
**Error Type**: [ImportError/RuntimeError/ValueError/etc.]  
**Description**: [Describe the error]  
**Fix**: [Describe the fix]  
**Status**: [Resolved/Pending]

---

## Common Errors and Solutions

### Dataset Not Found
**Error Type**: FileNotFoundError  
**Description**: Dataset not found at expected path  
**Fix**: 
- Enable AUTO_DOWNLOAD_DATASET=true in .env
- Or manually download from Kaggle
- Run: python dataset_manager.py  
**Status**: Documented

### Kaggle API Credentials Missing
**Error Type**: OSError  
**Description**: Kaggle API credentials not found  
**Fix**:
1. Go to https://www.kaggle.com/account
2. Create API token
3. Save kaggle.json to ~/.kaggle/ (Linux/Mac) or %USERPROFILE%\.kaggle\ (Windows)  
**Status**: Documented

### Model Not Found
**Error Type**: FileNotFoundError  
**Description**: Trained model file not found  
**Fix**: Run python main.py to train models first  
**Status**: Documented

### Import Error for Config Module
**Error Type**: ModuleNotFoundError  
**Description**: Cannot import from config package  
**Fix**: Ensure config/__init__.py exists and all config files are present  
**Status**: Documented

### Feature Extraction Dimension Mismatch
**Error Type**: ValueError  
**Description**: Expected 48 features, got different number  
**Fix**: Ensure feature_extractor.py returns exactly 48 features  
**Status**: Documented

### Preprocessor Transform Error
**Error Type**: ValueError  
**Description**: Preprocessor transform failed due to dimension mismatch  
**Fix**: Ensure preprocessor was fit on training data with same feature count  
**Status**: Documented

### Port Already in Use
**Error Type**: OSError  
**Description**: API port already in use  
**Fix**:
- Change API_PORT in .env
- Or kill process using the port  
**Status**: Documented

---

## Notes

- This file should be updated whenever new errors are encountered
- Include stack traces for complex errors
- Document both temporary workarounds and permanent fixes
- Mark resolved errors with "Status: Resolved"
