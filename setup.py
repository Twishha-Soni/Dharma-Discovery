from setuptools import setup, find_packages

setup(
    name="career_path_finder",
    version="1.0.0",
    description="Discover your true calling (dharma) and find career paths where you can express it",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "questionary>=1.10.0",
        "rich>=10.0.0",
        "nltk>=3.8.1",
        "scikit-learn>=1.3.0",
        "python-Levenshtein>=0.12.2",
        "spacy>=3.6.0"
    ],
    entry_points={
        'console_scripts': [
            'career-path-finder=career_path_finder.main:main',
        ],
    },
    python_requires=">=3.6",
)
