# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Python automation and invoice matching tool for SnelStart (Dutch accounting software). The project combines two main functionalities:

1. **SnelStart UI Automation**: Automates the process of logging in, navigating to bookkeeping, and interacting with SnelStart desktop application via Windows UI automation (pywinauto)
2. **Invoice Matching Engine**: Matches bank transactions (from MT940 files) with PDF invoices based on invoice numbers found in transaction descriptions

The application provides both automated SnelStart integration and standalone invoice matching capabilities through a demo script.

## Architecture

The codebase follows a modular architecture with clear separation of concerns:

### SnelStart Automation Components
- **main.py**: Entry point that orchestrates the complete workflow (initialize → login → navigate to bookkeeping → do bookkeeping)
- **SnelstartAutomation**: Main automation class that coordinates all operations and manages application lifecycle
- **Automation modules**: Organized in `src/snelstart_automation/automations/` folder with distinct responsibilities:
  - `launch_snelstart.py`: Application startup and window detection logic with class `LaunchAutomation`
  - `login.py`: Handles authentication flow with credential management via `LoginAutomation`
  - `navigate_to_bookkeeping.py`: Opens administration workspace and navigates to bookkeeping tab via `NavigateToBookkeepingAutomation`
  - `do_bookkeeping.py`: Initiates bookkeeping processes by clicking "Afschriften Inlezen" button via `DoBookkeepingAutomation`

### Invoice Matching Components
- **invoice_matching/core/matcher.py**: Core invoice matching logic with `InvoiceMatcher` class
- **invoice_matching/core/models.py**: Data models for transactions, invoices, and matching results
- **invoice_matching/core/mt940_parser.py**: MT940 bank statement file parser
- **invoice_matching/core/pdf_scanner.py**: PDF invoice file scanner and metadata extractor
- **demo.py**: Standalone demo script for testing invoice matching functionality

### Shared Utility Modules
- **src/utils/**: Common utilities shared across both automation and matching components:
  - `ui_utils.py`: UI debugging, element location, and window report generation
  - `wait_utils.py`: Advanced wait operations, retry logic, and UI element interactions
  - `config.py`: Centralized configuration management with environment variable support
  - `logging_setup.py`: Configurable logging system with per-class log levels

### Configuration
- **configs/settings.py**: All application settings, timing configurations, UI element identifiers, and invoice matching parameters

## Key Dependencies and Environment

- **pywinauto**: Windows UI automation library for desktop application control
- **python-dotenv**: Environment variable management for credentials
- **pandas**: Data manipulation for transaction and invoice handling
- **mt-940**: MT940 bank statement parsing library
- **uv**: Package manager (based on uv.lock presence and pyproject.toml configuration)
- **Windows Environment**: Required for UI automation functionality

## Required Environment Variables

The application requires these environment variables (typically in .env file):
- `SNELSTART_PATH`: Path to SnelStart executable (defaults to `C:\Program Files\Snelstart\Snelstart.exe`)
- `SNELSTART_EMAIL`: Login email/username
- `SNELSTART_PASSWORD`: Login password

## Common Development Commands

```bash
# Install dependencies
uv sync

# Run the main SnelStart automation workflow
python main.py

# Run standalone invoice matching demo
python demo.py

# Test SnelStart connection and debug UI elements
python src/snelstart_automation/tests/test_connection.py

# Run with debug logging (modify logging level in respective files)
# Default logging is INFO level with timestamped output
```

## Development Notes

### SnelStart Automation
- The application uses Windows-specific UI automation and requires Windows environment
- All UI interactions include strategic sleep/wait periods for stability
- The automation includes fallback logic for already-authenticated sessions
- Error handling is implemented at each major workflow step with detailed logging
- UI element discovery uses text matching and class name identification
- The `print_control_tree()` function in ui_utils.py is essential for debugging UI structure when elements can't be found

### Invoice Matching
- The matching engine processes MT940 bank statement files and PDF invoices
- Invoice numbers are extracted from PDF filenames (not content parsing)
- Matching is based on finding invoice numbers within transaction descriptions
- The system supports confidence scoring and detailed match reporting
- Demo script works with `data/transactions/` and `data/invoices/` directories

## Testing Approach

### SnelStart Automation Testing
Use `src/snelstart_automation/tests/test_connection.py` to verify:
- SnelStart application startup
- Window detection and connection
- Login process functionality
- UI element tree structure for debugging

The test script includes interactive debugging features and comprehensive logging to troubleshoot automation issues.

### Invoice Matching Testing
Use `demo.py` to test invoice matching functionality:
- Place MT940 files (*.STA, *.MT940) in `data/transactions/`
- Place PDF invoices in `data/invoices/`
- Run the demo to see matching results and statistics

## Folder Structure

```
invoice-uploader-new/
├── main.py                             # Entry point - orchestrates SnelStart automation workflow
├── demo.py                             # Standalone invoice matching demo script
├── pyproject.toml                      # Project configuration with dependencies (name: invoice-agent2)
├── uv.lock                             # Dependency lock file
├── CLAUDE.md                           # This documentation file
├── README.md                           # (empty - project documentation)
├── configs/                            # Configuration directory
│   ├── __init__.py                     # Config package initialization
│   └── settings.py                     # All application settings and constants
├── data/                               # Data directories for invoice matching
│   ├── invoices/                       # PDF invoice files for demo
│   └── transactions/                   # MT940 transaction files for demo
├── reports/                            # Auto-generated UI window reports (JSON + TXT)
├── screenshots/                        # Auto-generated debug screenshots
└── src/
    ├── invoice_matching/               # Invoice matching engine package
    │   ├── __init__.py                 # Package initialization and exports
    │   ├── core/                       # Core matching functionality
    │   │   ├── __init__.py             # Core module initialization
    │   │   ├── matcher.py              # InvoiceMatcher - core matching logic
    │   │   ├── models.py               # Data models (Transaction, Invoice, MatchResult)
    │   │   ├── mt940_parser.py         # MT940 bank statement parser
    │   │   └── pdf_scanner.py          # PDF invoice scanner and metadata extractor
    │   ├── tests/                      # Invoice matching tests and sample data
    │   │   ├── __init__.py             # Test package initialization
    │   │   ├── test_matcher.py         # Unit tests for matching functionality
    │   │   └── sample_data/            # Sample files for testing
    │   ├── ui/                         # Future UI components (currently unused)
    │   │   └── __init__.py
    │   └── utils/                      # Invoice matching utilities (currently unused)
    │       └── __init__.py
    ├── snelstart_automation/           # SnelStart UI automation package
    │   ├── snelstart_auto.py           # Core automation orchestrator class
    │   ├── automations/                # Automation modules with class-based design
    │   │   ├── __init__.py             # Module exports (classes + backwards compatibility)
    │   │   ├── launch_snelstart.py     # LaunchAutomation - application startup
    │   │   ├── login.py                # LoginAutomation - authentication workflow
    │   │   ├── navigate_to_bookkeeping.py # NavigateToBookkeepingAutomation - workspace navigation
    │   │   └── do_bookkeeping.py       # DoBookkeepingAutomation - bookkeeping initiation
    │   └── tests/                      # Testing modules
    │       ├── __init__.py             # Test package initialization
    │       └── test_connection.py      # Connection testing and debugging
    └── utils/                          # Shared utility modules
        ├── __init__.py                 # Package initialization
        ├── ui_utils.py                 # UI debugging, element search, and report generation
        ├── wait_utils.py               # Advanced wait operations and retry logic
        ├── config.py                   # Centralized configuration management
        └── logging_setup.py            # Configurable logging system
```

## Implementation Status

### ✅ Fully Completed Components

#### SnelStart UI Automation
- **Application Lifecycle Management**: SnelStart application startup, window detection, and graceful shutdown
- **Authentication Flow**: Complete login automation with environment variable credential management and auto-login detection
- **Navigation Workflow**: Successfully opens administration workspace and navigates to bookkeeping tab
- **Bookkeeping Process Initiation**: Clicks "Afschriften Inlezen" button to start bank statement import process
- **UI Debugging Infrastructure**: Advanced control tree printing, element search utilities, and automated window report generation
- **Error Handling**: Comprehensive logging and exception handling throughout all modules with configurable log levels
- **Connection Testing**: Standalone test script for debugging UI automation issues
- **Code Organization**: Fully restructured codebase with proper separation of concerns into modular class-based architecture
- **Configuration Management**: Centralized configuration system with environment variable overrides and timing configurations
- **Advanced Wait Operations**: Sophisticated retry logic, timeout handling, and UI element interaction safety

#### Invoice Matching Engine
- **MT940 Parser**: Complete parsing of MT940 bank statement files with transaction extraction
- **PDF Scanner**: Invoice metadata extraction from PDF filenames with flexible number detection
- **Core Matching Logic**: Intelligent matching of transactions to invoices based on invoice numbers in descriptions
- **Data Models**: Comprehensive data structures for transactions, invoices, and matching results
- **Reporting System**: Detailed matching statistics, confidence scoring, and summary reporting
- **Demo Application**: Standalone script for testing invoice matching with sample data
- **Test Infrastructure**: Unit tests and sample data for validation

### ⚠️ Areas for Enhancement

#### SnelStart Integration
- **File Upload Dialog Handling**: The automation clicks "Afschriften Inlezen" but doesn't handle the subsequent file selection dialog
- **End-to-End Integration**: Connection between invoice matching results and SnelStart file upload

#### Invoice Matching Refinements
- **PDF Content Parsing**: Currently extracts invoice numbers from filenames only, not from PDF content
- **Advanced Matching Algorithms**: Could implement fuzzy matching, amount-based matching, or date-based matching
- **Configuration Flexibility**: More configurable matching parameters and thresholds

### 🚀 Suggested Enhancement Priority

1. **File Dialog Automation**: Implement file selection dialog handling in `do_bookkeeping.py`
2. **Integration Bridge**: Connect invoice matching results to SnelStart file upload workflow
3. **Enhanced PDF Processing**: Add PDF content parsing for more robust invoice number extraction
4. **Comprehensive Testing**: Integration tests with real-world data files

## Recent Changes and Architecture Evolution

### ✅ Major Architectural Improvements

#### Complete Code Restructuring
- **Modular Class-Based Architecture**: Converted all automation modules to class-based design with proper inheritance and separation of concerns
- **Dual-Purpose System**: Integrated both SnelStart UI automation and standalone invoice matching capabilities
- **Advanced Configuration System**: Implemented centralized configuration management in `configs/settings.py` with environment variable overrides
- **Sophisticated Utility Framework**: Created comprehensive utility modules for UI interactions, wait operations, and logging
- **Enhanced Error Handling**: Added advanced retry logic, timeout management, and detailed logging throughout the system

#### SnelStart Automation Classes
- **LaunchAutomation**: Application startup and window detection with robust error handling
- **LoginAutomation**: Authentication workflow with auto-login detection and manual fallback
- **NavigateToBookkeepingAutomation**: Administration workspace navigation and bookkeeping tab access
- **DoBookkeepingAutomation**: Bookkeeping process initiation and UI interaction

#### Invoice Matching System
- **InvoiceMatcher**: Core matching algorithm with confidence scoring and detailed reporting
- **MT940Parser**: Bank statement parsing with comprehensive transaction extraction
- **PDFScanner**: Invoice metadata extraction from PDF files with flexible number detection
- **Data Models**: Complete type-safe data structures for all entities

#### Technical Infrastructure
- **Centralized Configuration**: All settings, timing, and UI elements managed in `configs/settings.py`
- **Advanced Wait Operations**: Sophisticated retry patterns and timeout handling with user feedback
- **Configurable Logging**: Per-class log levels with environment variable overrides
- **Automated Debugging**: Window structure analysis and debug report generation (JSON + TXT formats)
- **Backwards Compatibility**: Maintained function-based API compatibility while upgrading to class-based internals