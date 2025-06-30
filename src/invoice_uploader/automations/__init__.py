"""
Automation modules for SnelStart application interaction.
"""

# Import classes
from .launch_snelstart import LaunchAutomation
from .login import LoginAutomation
from .administration import AdministrationAutomation
from .read_invoices import InvoiceReaderAutomation

# Import backwards compatibility functions
from .launch_snelstart import get_snelstart_path, start_snelstart_application, get_main_window
from .login import get_login_dialog, perform_login, login_to_snelstart
from .administration import get_administratie_window
from .read_invoices import click_afschriften_inlezen

__all__ = [
    # Classes
    'LaunchAutomation',
    'LoginAutomation',
    'AdministrationAutomation', 
    'InvoiceReaderAutomation',
    # Backwards compatibility functions
    'get_snelstart_path',
    'start_snelstart_application', 
    'get_main_window',
    'get_login_dialog',
    'perform_login',
    'login_to_snelstart',
    'get_administratie_window',
    'click_afschriften_inlezen'
]