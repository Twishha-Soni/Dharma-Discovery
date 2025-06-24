"""
NLP analysis functionality for Career Path Finder
"""

from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from rich.console import Console

# Initialize Rich console
console = Console()

class NLPAnalyzer:
    """Class for analyzing text using NLP techniques"""
    
    def __init__(self, spacy_nlp=None):
        """Initialize the analyzer with optional spaCy model"""
        self.nlp = spacy_nlp
        self.spacy_available = spacy_nlp is not None
    
    def analyze_text(self, text):
        """Analyze text using NLP techniques"""
        if self.spacy_available:
            return self._analyze_with_spacy(text)
        else:
            return self._analyze_simple(text)
    
    def _analyze_with_spacy(self, text):
        """Use spaCy for more sophisticated analysis"""
        try:
            # Process text with spaCy
            doc = self.nlp(text.lower())
            
            # Extract key nouns and verbs that might indicate interests
            key_words = []
            for token in doc:
                # Get verbs and nouns that aren't stopwords
                if (token.pos_ in ["VERB", "NOUN"]) and not token.is_stop:
                    key_words.append(token.lemma_)
            
            # Count frequencies
            word_freq = Counter(key_words)
            most_common = word_freq.most_common(10)
            
            # Extract key phrases using noun chunks
            key_phrases = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text) > 3]
            
            return {
                "key_words": [word for word, _ in most_common],
                "key_phrases": key_phrases
            }
        except Exception as e:
            console.print(f"[yellow]spaCy analysis encountered an issue: {str(e)}. Using simpler analysis.[/yellow]")
            return self._analyze_simple(text)
    
    def _analyze_simple(self, text):
        """Simpler text analysis as fallback"""
        try:
            # Try to tokenize with NLTK
            try:
                # Tokenize and remove stopwords
                tokens = word_tokenize(text.lower())
                try:
                    stop_words = set(stopwords.words('english'))
                    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
                except:
                    # If stopwords fail, just filter out non-alphanumeric
                    filtered_tokens = [word for word in tokens if word.isalnum()]
            except:
                # If NLTK tokenization fails, use simple split
                console.print("[yellow]NLTK tokenization failed. Using simple word splitting.[/yellow]")
                tokens = text.lower().split()
                filtered_tokens = [word for word in tokens if len(word) > 2]
            
            # Count word frequencies
            word_freq = Counter(filtered_tokens)
            most_common = word_freq.most_common(10)
            
            # Extract simple phrases (consecutive words)
            words = text.lower().split()
            phrases = []
            for i in range(len(words)-1):
                if len(words[i]) > 3 and len(words[i+1]) > 3:
                    phrases.append(words[i] + " " + words[i+1])
            
            phrase_freq = Counter(phrases)
            common_phrases = phrase_freq.most_common(5) if phrases else []
            
            return {
                "key_words": [word for word, _ in most_common] if most_common else [],
                "key_phrases": [phrase for phrase, _ in common_phrases] if common_phrases else []
            }
        except Exception as e:
            console.print(f"[yellow]Simple text analysis failed: {str(e)}. Using keyword matching only.[/yellow]")
            return {
                "key_words": [],
                "key_phrases": []
            }
