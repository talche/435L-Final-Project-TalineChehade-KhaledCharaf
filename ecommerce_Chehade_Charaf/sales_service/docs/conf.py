# conf.py

import os
import sys

# -- Path setup --------------------------------------------------------------

# Add the project's root directory to sys.path
# Assuming the project root is three levels up from conf.py
sys.path.insert(0, os.path.abspath('../'))
print( os.path.abspath('../../'))

# -- Project information -----------------------------------------------------
project = 'sales_service'
author = 'Your Name'
release = '1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',             # Core Sphinx extension for auto documentation
    'sphinx.ext.napoleon',            # Support for Google and NumPy docstring styles
    'sphinx_autodoc_typehints',       # Integrate type hints into documentation
    'sphinx.ext.viewcode',            # Add links to highlighted source code
    'sphinx.ext.todo',                # Support for TODOs
    'sphinx.ext.coverage',            # Check documentation coverage
    'sphinx.ext.mathjax',             # Render math via JavaScript
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and directories to ignore.
exclude_patterns = []

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'  # Read the Docs theme

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the built-in static files.
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------

# Autodoc settings
autodoc_member_order = 'bysource'  # Order members as they appear in the source code
autodoc_typehints = 'description'  # Show type hints in descriptions

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False

# Todo extension settings
todo_include_todos = True
