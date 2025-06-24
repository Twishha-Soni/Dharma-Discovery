#!/usr/bin/env python3
"""
Download NLTK resources needed for Career Path Finder
"""

import nltk
import os
import sys
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    console.print(Panel.fit(
        "[bold cyan]Career Path Finder - NLTK Resource Downloader[/bold cyan]\n\n"
        "This script will download the required NLTK resources for the Career Path Finder application.",
        title="📚 NLTK Resources 📚",
        border_style="cyan"
    ))
    
    # Create NLTK data directory if it doesn't exist
    nltk_data_dir = os.path.join(os.path.expanduser("~"), "nltk_data")
    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir)
        console.print(f"[green]Created NLTK data directory: {nltk_data_dir}[/green]")
    
    # Download required resources
    resources = ['punkt', 'stopwords', 'wordnet']
    for resource in resources:
        console.print(f"Downloading [bold]{resource}[/bold]...")
        try:
            nltk.download(resource)
            console.print(f"[green]✓ Successfully downloaded {resource}[/green]")
        except Exception as e:
            console.print(f"[bold red]Error downloading {resource}: {str(e)}[/bold red]")
            console.print("[yellow]You may need to run this script with administrator privileges.[/yellow]")
            sys.exit(1)
    
    console.print(Panel.fit(
        "[bold green]All resources downloaded successfully![/bold green]\n\n"
        f"NLTK data directory: {nltk_data_dir}\n\n"
        "You can now run the Career Path Finder application.",
        title="✅ Download Complete ✅",
        border_style="green"
    ))

if __name__ == "__main__":
    main()
