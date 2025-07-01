# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python automation tool for SnelStart (Dutch accounting software) that automates the process of logging in, opening the administration module, and uploading bank statements ("afschriften"). The application uses Windows UI automation via pywinauto to interact with the SnelStart desktop application.

## Architecture

The codebase follows a modular architecture with clear separation of concerns:

- **main.py**: Entry point that orchestrates the complete workflow (initialize → login → open admin → upload statements)
- **SnelstartAutomation**: Main automation class that coordinates all operations and manages application lifecycle
- **Automation modules**: Organized in `src/invoice_uploader/automations/` folder with distinct responsibilities:
  - `launch_snelstart.py`: Application startup and window detection logic
  - `login.py`: Handles authentication flow with credential management
  - `administration.py`: Opens the administration window by double-clicking "Row 1"
  - `read_invoices.py`: Clicks the "Afschriften Inlezen" button for bank statement import
- **Utility modules**: Organized in `src/utils/` with comprehensive functionality:
  - `ui_utils.py`: UI debugging, element location, and window report generation
  - `wait_utils.py`: Advanced wait operations, retry logic, and UI element interactions
  - `config.py`: Centralized configuration management with environment variable support
  - `logging_setup.py`: Configurable logging system with per-class log levels
- **Configuration**: `configs/settings.py` contains all application settings, timing configurations, and UI element identifiers
- **Testing**: `src/invoice_uploader/tests/` folder contains connection testing and debugging scripts

## Key Dependencies and Environment

- **pywinauto**: Windows UI automation library for desktop application control
- **python-dotenv**: Environment variable management for credentials
- **uv**: Package manager (based on uv.lock presence and pyproject.toml configuration)

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
├── main.py                             # Entry point - orchestrates complete workflow
├── pyproject.toml                      # Project configuration with dependencies (name: invoice-agent2)
├── uv.lock                             # Dependency lock file
├── CLAUDE.md                           # This documentation file
├── README.md                           # (empty - project documentation)
├── configs/                            # Configuration directory
│   ├── __init__.py                     # Config package initialization
│   └── settings.py                     # All application settings and constants
├── reports/                            # Auto-generated UI window reports (JSON + TXT)
├── screenshots/                        # Auto-generated debug screenshots
└── src/
    ├── invoice_uploader/               # Main automation package
    │   ├── snelstart_automation.py     # Core automation orchestrator class
    │   ├── automations/                # Automation modules with class-based design
    │   │   ├── __init__.py             # Module exports (classes + backwards compatibility)
    │   │   ├── launch_snelstart.py     # LaunchAutomation - application startup
    │   │   ├── login.py                # LoginAutomation - authentication workflow
    │   │   ├── administration.py       # AdministrationAutomation - admin window opening
    │   │   └── read_invoices.py        # InvoiceReaderAutomation - bank statement processing
    │   └── tests/                      # Testing modules
    │       ├── __init__.py             # Test package initialization
    │       └── test_connection.py      # Connection testing and debugging
    └── utils/                          # Utility modules
        ├── __init__.py                 # Package initialization
        ├── ui_utils.py                 # UI debugging, element search, and report generation
        ├── wait_utils.py               # Advanced wait operations and retry logic
        ├── config.py                   # Centralized configuration management
        └── logging_setup.py            # Configurable logging system
```

## Implementation Status

### ✅ Completed Steps

- **Application Lifecycle Management**: SnelStart application startup, window detection, and graceful shutdown
- **Authentication Flow**: Complete login automation with environment variable credential management and auto-login detection
- **Administration Access**: Successfully opens admin window by locating and double-clicking "Row 1" 
- **UI Debugging Infrastructure**: Advanced control tree printing, element search utilities, and automated window report generation
- **Error Handling**: Comprehensive logging and exception handling throughout all modules with configurable log levels
- **Connection Testing**: Standalone test script for debugging UI automation issues
- **Code Organization**: Fully restructured codebase with proper separation of concerns into modular class-based architecture
- **Configuration Management**: Centralized configuration system with environment variable overrides and timing configurations
- **Advanced Wait Operations**: Sophisticated retry logic, timeout handling, and UI element interaction safety

### ⚠️ Partially Implemented

- **Bank Statement Upload Initiation**: Button click for "Afschriften Inlezen" is implemented, but file upload workflow is incomplete

### ❌ Next Steps Needed

1. **File Upload Dialog Handling**: Implement file selection dialog automation for choosing bank statement files
2. **File Format Validation**: Add validation for supported bank statement formats before upload
3. **Upload Progress Monitoring**: Track upload status and handle success/failure states  
4. **Batch File Processing**: Support uploading multiple bank statement files in sequence
5. **Integration Testing**: Test with actual bank statement files to ensure end-to-end functionality

### Suggested Next Implementation Priority

1. ✅ **FIXED**: The workflow bug in main.py has been corrected (line 84: correctly calls `load_in_afschriften()`)
2. Implement file dialog handling in `automations/read_invoices.py`
3. Add file path configuration to environment variables
4. Test complete workflow with sample bank statement files

## Recent Changes (Code Restructuring)

**✅ Completed Restructuring (Latest Update):**
- **Modular Class-Based Architecture**: Converted all automation modules to class-based design with proper inheritance and separation of concerns
- **Advanced Configuration System**: Implemented centralized configuration management in `configs/settings.py` with environment variable overrides
- **Sophisticated Utility Framework**: Created comprehensive utility modules for UI interactions, wait operations, and logging
- **Enhanced Error Handling**: Added advanced retry logic, timeout management, and detailed logging throughout the system
- **Automated Debugging**: Implemented automatic window report generation (JSON + TXT) and enhanced UI debugging capabilities
- **Backwards Compatibility**: Maintained function-based API compatibility while upgrading to class-based internals
- **Proper Package Structure**: Organized code into logical packages with proper `__init__.py` exports

**Key Architectural Improvements:**
- **Class-Based Automation**: `LaunchAutomation`, `LoginAutomation`, `AdministrationAutomation`, `InvoiceReaderAutomation`
- **Centralized Configuration**: All settings, timing, and UI elements managed in `configs/settings.py`
- **Advanced Wait Operations**: `WaitUtils` class with sophisticated retry patterns and timeout handling
- **Configurable Logging**: Per-class log levels with environment variable overrides
- **Automated Reporting**: Window structure analysis and debug report generation