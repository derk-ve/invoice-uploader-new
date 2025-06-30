# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python automation tool for SnelStart (Dutch accounting software) that automates the process of logging in, opening the administration module, and uploading bank statements ("afschriften"). The application uses Windows UI automation via pywinauto to interact with the SnelStart desktop application.

## Architecture

The codebase follows a modular architecture with clear separation of concerns:

- **main.py**: Entry point that orchestrates the complete workflow (initialize → login → open admin → upload statements)
- **SnelstartAutomation**: Main automation class that coordinates all operations and manages application lifecycle
- **Automation modules**: Organized in `automations/` folder with distinct responsibilities:
  - `launch_snelstart.py`: Application startup and window detection logic
  - `login.py`: Handles authentication flow with credential management
  - `administration.py`: Opens the administration window by double-clicking "Row 1"
  - `read_invoices.py`: Clicks the "Afschriften Inlezen" button for bank statement import
- **UI utilities**: `utils/ui_utils.py` provides debugging and element location helpers
- **Testing**: `tests/` folder contains connection testing and debugging scripts

## Key Dependencies and Environment

- **pywinauto**: Windows UI automation library for desktop application control
- **python-dotenv**: Environment variable management for credentials
- **uv**: Package manager (based on uv.lock presence)

## Required Environment Variables

The application requires these environment variables (typically in .env file):
- `SNELSTART_PATH`: Path to SnelStart executable (defaults to `C:\Program Files\Snelstart\Snelstart.exe`)
- `SNELSTART_EMAIL`: Login email/username
- `SNELSTART_PASSWORD`: Login password

## Common Development Commands

```bash
# Install dependencies
uv sync

# Run the main automation workflow
python main.py

# Test connection and debug UI elements
python src/invoice_uploader/tests/test_connection.py

# Run with debug logging (modify logging level in respective files)
# Default logging is INFO level with timestamped output
```

## Development Notes

- The application uses Windows-specific UI automation and requires Windows environment
- All UI interactions include strategic sleep/wait periods for stability
- The automation includes fallback logic for already-authenticated sessions
- Error handling is implemented at each major workflow step with detailed logging
- UI element discovery uses text matching and class name identification
- The `print_control_tree()` function in ui_utils.py is essential for debugging UI structure when elements can't be found

## Testing Approach

Use `tests/test_connection.py` to verify:
- SnelStart application startup
- Window detection and connection
- Login process functionality
- UI element tree structure for debugging

The test script includes interactive debugging features and comprehensive logging to troubleshoot automation issues.

## Folder Structure

```
invoice-uploader-new/
├── main.py                    # Entry point - orchestrates complete workflow
├── pyproject.toml            # Project configuration with dependencies
├── uv.lock                   # Dependency lock file
├── CLAUDE.md                 # This documentation file
├── README.md                 # (empty - project documentation)
└── src/
    ├── invoice_uploader/     # Main automation package
    │   ├── snelstart_automation.py      # Core automation orchestrator class
    │   ├── automations/      # Automation modules (English naming)
    │   │   ├── __init__.py   # Module exports
    │   │   ├── launch_snelstart.py      # Application startup and window detection
    │   │   ├── login.py                 # Authentication workflow
    │   │   ├── administration.py        # Admin window opening
    │   │   └── read_invoices.py         # Bank statement processing
    │   └── tests/            # Testing modules
    │       ├── __init__.py   # Test package initialization
    │       └── test_connection.py       # Connection testing and debugging
    └── utils/
        ├── __init__.py       # Package initialization
        └── ui_utils.py       # UI debugging and element search utilities
```

## Implementation Status

### ✅ Completed Steps

- **Application Lifecycle Management**: SnelStart application startup, window detection, and graceful shutdown
- **Authentication Flow**: Complete login automation with environment variable credential management and auto-login detection
- **Administration Access**: Successfully opens admin window by locating and double-clicking "Row 1" 
- **UI Debugging Infrastructure**: Control tree printing and element search utilities for development
- **Error Handling**: Comprehensive logging and exception handling throughout all modules
- **Connection Testing**: Standalone test script for debugging UI automation issues
- **Code Organization**: Restructured codebase with proper separation of concerns into `automations/` and `tests/` folders

### ⚠️ Partially Implemented

- **Bank Statement Upload Initiation**: Button click for "Afschriften Inlezen" is implemented, but file upload workflow is incomplete

### ❌ Next Steps Needed

1. **File Upload Dialog Handling**: Implement file selection dialog automation for choosing bank statement files
2. **File Format Validation**: Add validation for supported bank statement formats before upload
3. **Upload Progress Monitoring**: Track upload status and handle success/failure states  
4. **Batch File Processing**: Support uploading multiple bank statement files in sequence
5. **Integration Testing**: Test with actual bank statement files to ensure end-to-end functionality
6. **Fix Main Workflow Bug**: The `upload_afschriften()` function in main.py incorrectly calls `open_administratie()` instead of `load_in_afschriften()`

### Suggested Next Implementation Priority

1. Fix the workflow bug in main.py (line 70: should call `load_in_afschriften()`)
2. Implement file dialog handling in `automations/read_invoices.py`
3. Add file path configuration to environment variables
4. Test complete workflow with sample bank statement files

## Recent Changes (Code Restructuring)

**✅ Completed Restructuring (Latest Update):**
- Moved all automation modules to `src/invoice_uploader/automations/` with English naming
- Moved test files to `src/invoice_uploader/tests/`
- Extracted application launch logic into separate `launch_snelstart.py` module
- Updated all import statements to reflect new structure
- Added proper `__init__.py` files with module exports
- Removed old Dutch-named files after successful migration

**File Mapping:**
- `snelstart_login.py` → `automations/login.py`
- `snelstart_administratie.py` → `automations/administration.py`  
- `snelstart_afschriften_inlezen.py` → `automations/read_invoices.py`
- `test_connection.py` → `tests/test_connection.py`
- New: `automations/launch_snelstart.py` (extracted from main automation class)