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
- **invoice_matching/core/transaction_filter.py**: Transaction filtering system for Royal Canin-specific transactions
- **demo_matcher.py**: Standalone demo script for testing invoice matching functionality

### Shared Utility Modules
- **src/utils/**: Common utilities shared across both automation and matching components:
  - `ui_utils.py`: UI debugging, element location, and window report generation
  - `wait_utils.py`: Advanced wait operations, retry logic, and UI element interactions
  - `config.py`: Centralized configuration management with environment variable support
  - `logging_setup.py`: Configurable logging system with per-class log levels

### Configuration
- **configs/settings.py**: All application settings, timing configurations, UI element identifiers, invoice matching parameters, and transaction filtering settings (including Royal Canin keyword filtering)

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

# Run standalone invoice matching demo (command line)
python demo_matcher.py

# Run invoice matching with graphical user interface
python demo_app.py

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

### Professional UI System
- **Theme Management**: Centralized styling system in `ui/styles/theme.py` with professional color palette
- **Component Styling**: Consistent TTK styling across all components with light blue buttons and proper contrast
- **Grid Layout System**: Sophisticated layout management with internal container frames and responsive design
- **Interactive Tables**: Professional data tables with row selection, hover states, and deletion controls
- **Visual Feedback**: Real-time updates, progress indicators, and confirmation dialogs for user actions
- **Data Integrity**: Automatic recalculation of statistics and UI refresh after user modifications

## Testing Approach

#### SnelStart Automation Testing
- **Production Testing**: Use `python main.py` to test the complete SnelStart automation workflow
- **UI Debugging**: Use the built-in `print_control_tree()` function in `ui_utils.py` for debugging UI structure
- **Manual Testing**: The automation includes comprehensive logging for troubleshooting issues

#### Invoice Matching Testing
- **Command Line**: Use `python demo_matcher.py` to test invoice matching functionality
- **Graphical Interface**: Use `python demo_app.py` for interactive testing with UI feedback
- **Test Data**: Place MT940 files (*.STA, *.MT940) in `data/transactions/` and PDF invoices in `data/invoices/`

#### Interactive Data Management Testing
- **Row Selection**: Test multi-row selection in matches table using Ctrl+Click and Shift+Click
- **Deletion Workflow**: Verify deletion confirmation dialog and automatic data updates
- **Data Integrity**: Confirm that deleted matches return to unmatched lists and statistics recalculate
- **UI Responsiveness**: Check that all tables, cards, and progress logs update in real-time

## Folder Structure

```
invoice-uploader-new/
├── main.py                             # Entry point - orchestrates SnelStart automation workflow
├── demo_matcher.py                     # Standalone invoice matching demo script
├── demo_app.py                         # Graphical UI launcher for invoice matching
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
    │   └── core/                       # Core matching functionality
    │       ├── __init__.py             # Core module initialization
    │       ├── matcher.py              # InvoiceMatcher - core matching logic
    │       ├── models.py               # Data models (Transaction, Invoice, MatchResult)
    │       ├── mt940_parser.py         # MT940 bank statement parser
    │       ├── pdf_scanner.py          # PDF invoice scanner and metadata extractor
    │       └── transaction_filter.py   # Transaction filtering for Royal Canin transactions
    ├── snelstart_automation/           # SnelStart UI automation package
    │   ├── snelstart_auto.py           # Core automation orchestrator class
    │   └── automations/                # Automation modules with class-based design
    │       ├── __init__.py             # Module exports (classes + backwards compatibility)
    │       ├── launch_snelstart.py     # LaunchAutomation - application startup
    │       ├── login.py                # LoginAutomation - authentication workflow
    │       ├── navigate_to_bookkeeping.py # NavigateToBookkeepingAutomation - workspace navigation
    │       └── do_bookkeeping.py       # DoBookkeepingAutomation - bookkeeping initiation
    └── utils/                          # Shared utility modules
        ├── __init__.py                 # Package initialization
        ├── ui_utils.py                 # UI debugging, element search, and report generation
        ├── wait_utils.py               # Advanced wait operations and retry logic
        ├── config.py                   # Centralized configuration management
        └── logging_setup.py            # Configurable logging system
└── ui/                                 # Graphical user interface package
    ├── __init__.py                     # UI package initialization  
    ├── main_app.py                     # Main application window (modular architecture)
    ├── components/                     # Reusable UI components
    │   ├── __init__.py                 # Components package initialization
    │   ├── file_selector.py            # File selection UI component with professional styling
    │   ├── results_display.py          # Results display and progress UI component with data management
    │   ├── data_tables.py              # Professional data tables with row selection and deletion
    │   └── summary_cards.py            # Metric display cards for statistics visualization
    ├── controllers/                    # Business logic controllers
    │   ├── __init__.py                 # Controllers package initialization
    │   └── matching_controller.py      # Invoice matching business logic controller
    └── styles/                         # Professional UI styling system
        ├── __init__.py                 # Styles package initialization
        └── theme.py                    # Centralized theme management and TTK styling
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
- **Code Organization**: Fully restructured codebase with proper separation of concerns into modular class-based architecture
- **Configuration Management**: Centralized configuration system with environment variable overrides and timing configurations
- **Advanced Wait Operations**: Sophisticated retry logic, timeout handling, and UI element interaction safety

#### Invoice Matching Engine
- **MT940 Parser**: Complete parsing of MT940 bank statement files with transaction extraction
- **PDF Scanner**: Invoice metadata extraction from PDF filenames with flexible number detection (duplicate detection fixed)
- **Transaction Filter**: Royal Canin-specific transaction filtering system with configurable keywords
- **Core Matching Logic**: Intelligent matching of transactions to invoices based on invoice numbers in descriptions
- **Data Models**: Comprehensive data structures for transactions, invoices, and matching results
- **Reporting System**: Detailed matching statistics, confidence scoring, and summary reporting
- **Demo Applications**: Both command-line (`demo_matcher.py`) and graphical (`demo_app.py`) interfaces for testing functionality

#### Graphical User Interface
- **Modular Architecture**: Clean separation of UI components, business logic, and data handling with MVC pattern
- **Professional UI Styling**: Comprehensive theme system with consistent colors, typography, and component styling
- **File Selection Component**: Professional TTK-styled file selection with validation and visual feedback
- **Interactive Data Tables**: Multi-row selection, deletion controls, and real-time data management
- **Results Display Component**: Tabbed interface with progress tracking and comprehensive results presentation
- **Data Management System**: Persistent summary storage with automatic recalculation and UI refresh
- **Matching Controller**: Business logic orchestration with progress callbacks and error handling
- **Professional Desktop Interface**: Native Tkinter application with consistent styling and user feedback
- **Row Selection and Deletion**: Multi-select capability with confirmation dialogs and data integrity
- **Import Path Management**: Clean package structure with proper relative imports from project root

### ⚠️ Areas for Enhancement

#### SnelStart Integration
- **File Upload Dialog Handling**: The automation clicks "Afschriften Inlezen" but doesn't handle the subsequent file selection dialog
- **End-to-End Integration**: Connection between invoice matching results and SnelStart file upload

#### Invoice Matching Refinements
- **PDF Content Parsing**: Currently extracts invoice numbers from filenames only, not from PDF content
- **Advanced Matching Algorithms**: Could implement fuzzy matching, amount-based matching, or date-based matching
- **Configuration Flexibility**: More configurable matching parameters and thresholds

### 🚀 Suggested Next Steps

#### Phase 1: Complete SnelStart Integration
1. **UI Integration with SnelStart**: Add SnelStart automation controls to the graphical interface
2. **File Dialog Automation**: Implement file selection dialog handling in `do_bookkeeping.py`
3. **End-to-End Workflow**: Connect invoice matching results directly to SnelStart file upload

#### Phase 2: Enhanced Features
1. **Configuration UI**: Add settings panel for SnelStart credentials and matching parameters
2. **Export Functionality**: Add ability to export matching results to CSV/Excel
3. **Enhanced PDF Processing**: Add PDF content parsing for more robust invoice number extraction
4. **Batch Processing**: Support for processing multiple MT940/PDF file sets

#### Phase 3: Advanced Capabilities
1. **Workflow Automation**: One-click processing from file selection to SnelStart upload
2. **Historical Tracking**: Keep track of processed files and matching history
3. **Advanced Matching Algorithms**: Fuzzy matching, amount-based matching, date-based matching
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
- **TransactionFilter**: Royal Canin-specific filtering with configurable keywords and case sensitivity options
- **PDFScanner**: Invoice metadata extraction from PDF files with flexible number detection and duplicate prevention
- **Data Models**: Complete type-safe data structures for all entities

#### Graphical User Interface (Latest Addition)
- **Modular UI Architecture**: Complete refactoring from monolithic 275-line file to clean modular components
- **FileSelector Component**: Dedicated file selection UI with validation, progress callbacks, and professional TTK styling
- **ResultsDisplay Component**: Professional results presentation with real-time progress updates and data management
- **MatchingController**: Business logic separation with comprehensive error handling and progress notifications
- **Clean Import Structure**: Proper package organization allowing execution from project root
- **MVC Pattern Implementation**: Clear separation of Model (data), View (UI), and Controller (business logic)

#### Enhanced User Interface and Data Management (Latest Enhancement)
- **Professional Styling System**: Comprehensive theme management with consistent color palette, typography, and component styling
- **Interactive Data Tables**: Multi-row selection capability with Ctrl+Click, Shift+Click, and keyboard shortcuts (Delete key)
- **Row Deletion Functionality**: Confirmation dialogs, real-time data updates, and automatic statistics recalculation
- **Grid Layout Optimization**: Resolved critical layout conflicts with internal container frames and proper column management
- **Data Integrity Management**: Persistent summary storage with automatic refresh of all UI components after modifications
- **Visual Feedback System**: Professional button styling, selection indicators, progress logging, and status updates
- **Component Architecture Enhancement**: Clean separation between base DataTable and specialized MatchesTable with deletion controls

#### Technical Infrastructure
- **Centralized Configuration**: All settings, timing, and UI elements managed in `configs/settings.py`
- **Advanced Wait Operations**: Sophisticated retry patterns and timeout handling with user feedback
- **Configurable Logging**: Per-class log levels with environment variable overrides
- **Automated Debugging**: Window structure analysis and debug report generation (JSON + TXT formats)
- **Backwards Compatibility**: Maintained function-based API compatibility while upgrading to class-based internals