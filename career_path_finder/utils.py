"""
Utility functions for the Career Path Finder application
"""

import os
import nltk
import threading
from rich.console import Console

# Initialize Rich console
console = Console()

def download_nltk_resources():
    """Download NLTK resources in a separate thread to avoid blocking"""
    try:
        # Create NLTK data directory if it doesn't exist
        nltk_data_dir = os.path.join(os.path.expanduser("~"), "nltk_data")
        if not os.path.exists(nltk_data_dir):
            os.makedirs(nltk_data_dir)
            
        # Download required resources
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not download NLTK resources: {str(e)}[/yellow]")

# Start download in background
def start_nltk_download():
    """Start NLTK resource download in background thread"""
    nltk_thread = threading.Thread(target=download_nltk_resources)
    nltk_thread.daemon = True
    nltk_thread.start()
    return nltk_thread
