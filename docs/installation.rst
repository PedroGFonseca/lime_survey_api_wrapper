Installation
============

Requirements
------------

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)
- LimeSurvey instance with RemoteControl API enabled

From Source (Development Installation)
--------------------------------------

1. **Clone the Repository**

   .. code-block:: bash

      git clone <repository-url>
      cd lime-survey-analyzer

2. **Create Virtual Environment**

   .. code-block:: bash

      # Create virtual environment
      python -m venv venv

      # Activate virtual environment
      # On macOS/Linux:
      source venv/bin/activate

      # On Windows:
      venv\Scripts\activate

3. **Install Package**

   .. code-block:: bash

      # Basic installation
      pip install -e .

      # Install with development dependencies
      pip install -e ".[dev]"

      # Install with documentation dependencies
      pip install -e ".[docs]"

      # Install with all optional dependencies
      pip install -e ".[dev,docs]"

Verifying Installation
----------------------

To verify the installation worked correctly:

.. code-block:: python

   # Test import
   from lime_survey_analyzer import LimeSurveyDirectAPI
   
   # Check version
   import lime_survey_analyzer
   print(lime_survey_analyzer.__version__)

Setting Up Credentials
-----------------------

Environment Variables (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   export LIMESURVEY_URL="https://your-limesurvey.com/admin/remotecontrol"
   export LIMESURVEY_USERNAME="your_username"
   export LIMESURVEY_PASSWORD="your_password"

Configuration File
~~~~~~~~~~~~~~~~~~

Create a ``credentials.ini`` file:

.. code-block:: ini

   [limesurvey]
   url = https://your-limesurvey.com/admin/remotecontrol
   username = your_username
   password = your_password

.. warning::
   Never commit credential files to version control. Add them to your ``.gitignore``.

Testing the Connection
----------------------

.. code-block:: python

   from lime_survey_analyzer import LimeSurveyDirectAPI

   # Test connection
   try:
       api = LimeSurveyDirectAPI.from_env()
       with api:
           surveys = api.list_surveys()
           print(f"Successfully connected! Found {len(surveys)} surveys.")
   except Exception as e:
       print(f"Connection failed: {e}")

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**ImportError: No module named 'lime_survey_analyzer'**
   - Ensure you've activated your virtual environment
   - Reinstall with ``pip install -e .``

**Authentication Failed**
   - Check your credentials
   - Verify the LimeSurvey URL is correct and includes ``/admin/remotecontrol``
   - Ensure the RemoteControl API is enabled in LimeSurvey

**SSL Certificate Errors**
   - For development, you can use HTTP instead of HTTPS (not recommended for production)
   - For production, ensure your SSL certificates are properly configured

**Connection Timeout**
   - Check network connectivity
   - Verify firewall settings
   - Increase timeout in the client if needed

Dependencies
------------

Runtime Dependencies
~~~~~~~~~~~~~~~~~~~~

- ``requests >= 2.25.0`` - HTTP library for API requests

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

- ``pytest >= 6.0`` - Testing framework
- ``pytest-cov`` - Coverage reporting
- ``black`` - Code formatting
- ``isort`` - Import sorting
- ``flake8`` - Linting
- ``mypy`` - Type checking
- ``pre-commit`` - Git hooks

Documentation Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``sphinx >= 4.0`` - Documentation generator
- ``sphinx-rtd-theme`` - Read the Docs theme
- ``sphinx-autodoc-typehints`` - Type hints in documentation
- ``myst-parser`` - Markdown support in Sphinx 