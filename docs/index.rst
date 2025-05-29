LimeSurvey Analyzer Documentation
==================================

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.8+

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

A secure, read-only Python client for LimeSurvey's RemoteControl 2 API that provides
direct access to survey data, metadata, and structure without external dependencies.

Features
--------

- 🔒 **Security First**: Secure credential handling with environment variables, config files, and interactive prompts
- 📖 **Read-Only Operations**: Safe, non-destructive API operations only
- 🐍 **Pythonic Interface**: Clean, intuitive API with comprehensive type hints
- 📚 **Comprehensive Documentation**: Detailed docstrings and examples for every method
- 🛡️ **Built-in Protections**: HTTPS validation, credential sanitization, and error handling
- 🔄 **Automatic Session Management**: Context managers for reliable resource cleanup
- 🐛 **Debug Support**: Optional debug logging with sensitive data redaction

Quick Start
-----------

Installation
~~~~~~~~~~~~

Install the package in development mode:

.. code-block:: bash

   git clone <repository-url>
   cd lime-survey-analyzer
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from lime_survey_analyzer import LimeSurveyDirectAPI
   
   # Set environment variables:
   # export LIMESURVEY_URL="https://your-limesurvey.com/admin/remotecontrol"
   # export LIMESURVEY_USERNAME="your_username"
   # export LIMESURVEY_PASSWORD="your_password"
   
   # Create client from environment variables
   api = LimeSurveyDirectAPI.from_env()
   
   # Use context manager for automatic session management
   with api:
       # List all surveys
       surveys = api.list_surveys()
       for survey in surveys:
           print(f"Survey {survey['sid']}: {survey['surveyls_title']}")
       
       # Get survey details
       survey_props = api.get_survey_properties("123456")
       print(f"Survey status: {survey_props['active']}")
       
       # Export responses
       responses = api.export_responses("123456", "json")

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   security
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/client
   api/modules

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 