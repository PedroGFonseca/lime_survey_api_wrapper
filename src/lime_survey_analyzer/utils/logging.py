"""
Centralized logging configuration for LimeSurvey Analyzer.

This module provides consistent logging setup across the entire package,
replacing print statements with proper logging calls.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "lime_survey_analyzer", level: str = "INFO", debug: bool = False) -> logging.Logger:
    """
    Setup a logger for LimeSurvey Analyzer components.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        debug: If True, sets level to DEBUG and enables verbose formatting
        
    Returns:
        Configured logger instance
        
    Example:
        logger = setup_logger(__name__, debug=True)
        logger.info("API call successful")
        logger.debug("Detailed debugging information")
        logger.warning("Non-critical issue occurred")
        logger.error("Error occurred but can continue")
    """
    logger = logging.getLogger(name)
    
    # Set level based on debug flag or explicit level
    if debug:
        log_level = logging.DEBUG
    else:
        log_level = getattr(logging, level.upper(), logging.INFO)
    
    logger.setLevel(log_level)
    
    # Only add handler if logger doesn't already have one
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        
        # Create formatter
        if debug:
            # Verbose format for debugging
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
        else:
            # Clean format for production
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for the given name.
    
    This is a convenience function that ensures consistent logger configuration
    across the package. If the logger hasn't been setup yet, it will use
    default configuration.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        
    Returns:
        Logger instance
        
    Example:
        # In any module:
        from ..utils.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Operation completed")
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, it hasn't been setup yet
    if not logger.handlers and not logger.parent.handlers:
        # Setup with default configuration
        setup_logger(name)
    
    return logger


def configure_package_logging(debug: bool = False, level: str = "INFO") -> None:
    """
    Configure logging for the entire lime_survey_analyzer package.
    
    This sets up the root logger for the package and should be called
    once during package initialization or at the start of applications.
    
    Args:
        debug: Enable debug mode with verbose logging
        level: Default logging level for the package
        
    Example:
        # At start of application:
        from lime_survey_analyzer.utils.logging import configure_package_logging
        configure_package_logging(debug=True)
        
        # Or in client initialization:
        api = LimeSurveyClient(url, username, password, debug=True)
        # This would automatically configure logging
    """
    setup_logger("lime_survey_analyzer", level=level, debug=debug)


# Performance monitoring decorator
def log_performance(threshold: float = 1.0):
    """
    Decorator to log performance of slow operations.
    
    Args:
        threshold: Time threshold in seconds to trigger warning
        
    Example:
        @log_performance(threshold=0.5)
        def slow_api_call(self):
            # This will log a warning if it takes >0.5 seconds
            return self._make_request("slow_operation", [])
    """
    import time
    from functools import wraps
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Get logger for the function's module
            logger = get_logger(func.__module__)
            
            if duration > threshold:
                logger.warning(f"{func.__name__} took {duration:.2f}s (>{threshold}s threshold)")
            else:
                logger.debug(f"{func.__name__} completed in {duration:.2f}s")
                
            return result
        return wrapper
    return decorator 