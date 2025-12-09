"""
Configuration for analysis_reporting module.
Contains AI integration settings for report generation.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Groq AI Integration Settings
GROQ_API_KEY = os.getenv('GROQ_API_KEY', None)
GROQ_MODEL = 'llama-3.3-70b-versatile'
