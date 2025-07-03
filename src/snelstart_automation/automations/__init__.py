"""
Automation modules for SnelStart application interaction.
"""

# Import classes
from .launch_snelstart import LaunchAutomation
from .login import LoginAutomation
from .navigate_to_bookkeeping import NavigateToBookkeepingAutomation
from .do_bookkeeping import DoBookkeepingAutomation

# Import backwards compatibility functions
from .launch_snelstart import get_snelstart_path, start_snelstart_application, get_main_window
from .login import get_login_dialog, perform_login, login_to_snelstart
from .navigate_to_bookkeeping import navigate_to_administration, navigate_to_bookkeeping_tab

__all__ = [
    # Classes
    'LaunchAutomation',
    'LoginAutomation',
    'NavigateToBookkeepingAutomation', 
    'DoBookkeepingAutomation',
    # Backwards compatibility functions
    'get_snelstart_path',
    'start_snelstart_application', 
    'get_main_window',
    'get_login_dialog',
    'perform_login',
    'login_to_snelstart',
    'navigate_to_administration',
    'navigate_to_bookkeeping_tab'
]