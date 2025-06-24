#!/usr/bin/env python3
"""
Career Path Finder - Find your true calling based on your passions and skills
"""

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
import time
import json
import os
import random
from pathlib import Path
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import spacy
import threading

# Initialize Rich console
console = Console()

# Download NLTK resources in a separate thread to avoid blocking
def download_nltk_resources():
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
nltk_thread = threading.Thread(target=download_nltk_resources)
nltk_thread.daemon = True
nltk_thread.start()

# Try to load spaCy model, fall back to simpler analysis if not available
try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except:
    SPACY_AVAILABLE = False
    
# Define dharma data path
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DHARMA_DATA_PATH = DATA_DIR / "dharma_data.json"

class CareerFinder:
    def __init__(self):
        self.user_data = {
            "name": "",
            "passions": [],
            "childhood_memories": [],
            "skills": [],
            "qualifications": [],
            "dream_impact": "",
            "responses_raw": []  # Store all raw responses for NLP analysis
        }
        
        # Load dharma descriptions and career paths
        self.dharma_paths = self.load_dharma_data()
        
        # Personalized messages for different dharma types
        self.personalized_messages = {
            "helping_others_grow": [
                "You have a natural gift for bringing out the best in others.",
                "Your ability to see potential in people is remarkable.",
                "You find joy in witnessing others' growth and development.",
                "Teaching and mentoring seem to come naturally to you."
            ],
            "creating_and_innovating": [
                "You have a natural drive to bring new ideas into reality.",
                "Your creative energy is a powerful force that seeks expression.",
                "You see possibilities where others see limitations.",
                "Building and creating seems to be in your DNA."
            ],
            "solving_problems": [
                "You have a natural talent for finding solutions to complex challenges.",
                "Your analytical mind thrives when tackling difficult problems.",
                "You see obstacles as puzzles waiting to be solved.",
                "Finding better ways to do things energizes you."
            ],
            "caring_for_others": [
                "Your compassionate nature is a gift to those around you.",
                "You have a natural ability to sense others' needs and respond with care.",
                "Supporting others through difficult times gives you a sense of purpose.",
                "Your empathy allows you to connect deeply with others."
            ],
            "organizing_and_planning": [
                "Your ability to create order from chaos is remarkable.",
                "Your talent for seeing the big picture while managing details is a rare gift.",
                "You find satisfaction in systems that run smoothly and efficiently.",
                "Planning and coordinating seem to come naturally to you."
            ],
            "expressing_creativity": [
                "Your creative spirit seeks outlets for expression.",
                "You see the world through a unique lens that others benefit from.",
                "Bringing beauty and meaning into the world drives you.",
                "Your imagination is a powerful tool for innovation."
            ],
            "discovering_knowledge": [
                "Your curious mind constantly seeks deeper understanding.",
                "You find joy in the pursuit of knowledge and insight.",
                "Learning and sharing wisdom seems central to who you are.",
                "Your analytical nature helps you uncover hidden truths."
            ],
            "leading_and_inspiring": [
                "You have a natural ability to inspire others toward a shared vision.",
                "Your leadership qualities draw people to follow your guidance.",
                "You see potential in groups that others might miss.",
                "Bringing people together for a common purpose energizes you."
            ]
        }
        
        # Career alignment explanations (more varied and specific)
        self.alignment_explanations = {
            "Teacher/Professor": [
                "This role lets you directly shape minds and witness the 'aha' moments when students grasp new concepts.",
                "As an educator, you'll guide others through their learning journey, helping them discover their own potential.",
                "Teaching allows you to create transformative learning experiences that change how people see themselves and the world."
            ],
            "Corporate Trainer": [
                "As a trainer in industry, you'll help professionals develop skills that transform their careers and confidence.",
                "This role lets you combine technical expertise with your passion for developing others' potential.",
                "You'll design learning experiences that help professionals overcome challenges and reach new heights."
            ],
            "Coach": [
                "Coaching allows you to walk alongside others as they navigate their personal and professional growth.",
                "This role lets you ask powerful questions that help others discover their own answers and potential.",
                "As a coach, you'll create a safe space for transformation and breakthrough moments."
            ],
            "Software Developer": [
                "This role allows you to create solutions that solve real problems and improve people's lives.",
                "As a developer, you'll build digital experiences that transform how people work and connect.",
                "This path lets you express your creativity through code, bringing new possibilities into existence."
            ],
            "Product Designer": [
                "Design work allows you to shape how people experience and interact with the world around them.",
                "This role lets you solve human problems through thoughtful, creative design solutions.",
                "As a designer, you'll create products that seamlessly blend form and function to enhance lives."
            ],
            "Consultant": [
                "Consulting lets you tackle a variety of complex problems across different organizations and industries.",
                "This role allows you to analyze situations from multiple angles and develop innovative solutions.",
                "As a consultant, you'll help organizations overcome their biggest challenges and reach their potential."
            ],
            "Engineer": [
                "Engineering allows you to apply scientific principles to create solutions to real-world problems.",
                "This role lets you design and build systems that improve efficiency, safety, or quality of life.",
                "As an engineer, you'll solve complex technical challenges that others might find overwhelming."
            ],
            "Healthcare Professional": [
                "This path allows you to provide care and comfort to people during their most vulnerable moments.",
                "As a healthcare provider, you'll make a direct impact on people's wellbeing and quality of life.",
                "This role lets you combine technical expertise with deep compassion to heal and support others."
            ],
            "Project Manager": [
                "This role lets you orchestrate complex initiatives, bringing order to multifaceted challenges.",
                "As a project manager, you'll guide teams through uncertainty toward successful outcomes.",
                "This path allows you to create systems and processes that make ambitious goals achievable."
            ],
            "Graphic Designer": [
                "This role allows you to communicate powerful messages through visual storytelling.",
                "As a designer, you'll create work that evokes emotion and inspires action.",
                "This path lets you transform abstract concepts into tangible visual experiences."
            ],
            "Researcher": [
                "Research allows you to push the boundaries of what's known and discover new insights.",
                "This role lets you dive deep into questions that fascinate you and share your findings with the world.",
                "As a researcher, you'll contribute to humanity's collective knowledge and understanding."
            ],
            "Team Leader/Manager": [
                "This role lets you build and nurture teams that accomplish more together than individuals could alone.",
                "As a leader, you'll help team members develop their strengths and navigate challenges.",
                "This path allows you to create environments where people feel empowered to do their best work."
            ]
        }
        
        # For other careers not specifically listed
        self.generic_alignments = [
            "This role allows you to express your dharma by creating value through your natural gifts and inclinations.",
            "This path provides a platform where your unique strengths can make a meaningful difference.",
            "In this role, you can align your work with your deeper purpose, bringing fulfillment beyond just earning a living."
        ]
    
    def welcome(self):
        """Display welcome message and introduction"""
        console.clear()
        console.print(Panel.fit(
            "[bold cyan]Welcome to Career Path Finder[/bold cyan]\n\n"
            "This application will help you discover your true calling (dharma) and career paths\n"
            "where you can express it. We'll guide you through introspective questions to understand\n"
            "what truly motivates you and where you can best serve with your unique gifts.",
            title="🌟 Find Your True Calling 🌟",
            border_style="cyan"
        ))
        time.sleep(1)
        
        self.user_data["name"] = questionary.text("What's your name?").ask()
        console.print(f"\n[green]Great to meet you, {self.user_data['name']}! Let's begin your journey of self-discovery.[/green]")
        time.sleep(1)

    def explore_passions(self):
        """Guide user through questions about their passions and interests"""
        console.clear()
        console.print(Panel.fit(
            "[bold yellow]Exploring Your True Calling[/bold yellow]\n\n"
            "Let's discover what activities and experiences truly light you up inside.\n"
            "Take a moment to reflect deeply on these questions about your dharma (true calling).",
            title="✨ Soul Searching ✨",
            border_style="yellow"
        ))
        time.sleep(1)
        
        # Childhood memories
        console.print("\n[bold]Think back to your childhood...[/bold]")
        childhood_q = [
            "What activities made you lose track of time as a child?",
            "What did you love doing that felt effortless and joyful?",
            "What were you naturally drawn to before others' expectations came into play?"
        ]
        
        for question in childhood_q:
            answer = questionary.text(question).ask()
            if answer and answer.strip():
                self.user_data["childhood_memories"].append(answer)
                self.user_data["responses_raw"].append(answer)  # Store for NLP analysis
        
        # Current passions
        console.print("\n[bold]Now think about your current life...[/bold]")
        passion_q = [
            "What activities make you lose track of time now?",
            "If money were no object, what would you spend your days doing?",
            "What topics do you find yourself constantly reading about or discussing?"
        ]
        
        for question in passion_q:
            answer = questionary.text(question).ask()
            if answer and answer.strip():
                self.user_data["passions"].append(answer)
                self.user_data["responses_raw"].append(answer)  # Store for NLP analysis
        
        # Impact question
        impact_answer = questionary.text(
            "If you could make any positive impact on the world, what would it be?"
        ).ask()
        self.user_data["dream_impact"] = impact_answer
        self.user_data["responses_raw"].append(impact_answer)  # Store for NLP analysis
        
    def load_dharma_data(self):
        """Load dharma paths data or create default if not exists"""
        if not DHARMA_DATA_PATH.exists():
            # Create default dharma data
            default_data = {
                "helping_others_grow": {
                    "keywords": ["teach", "help others", "mentor", "guide", "develop people", "inspire", "educate", "growth", "potential"],
                    "description": "Your true calling is to help others develop and reach their potential. You find fulfillment in guiding, teaching, and witnessing the growth of others.",
                    "careers": [
                        {"title": "Teacher/Professor", "description": "Educate and inspire students in formal educational settings"},
                        {"title": "Corporate Trainer", "description": "Help professionals develop new skills and knowledge in business settings"},
                        {"title": "Coach", "description": "Guide individuals to achieve their personal or professional goals"},
                        {"title": "Mentor", "description": "Provide guidance and wisdom to help others navigate their path"},
                        {"title": "Instructional Designer", "description": "Create educational content and learning experiences"},
                        {"title": "Educational Content Creator", "description": "Develop videos, articles, or courses that teach others"}
                    ]
                },
                "creating_and_innovating": {
                    "keywords": ["build", "create", "make", "design", "craft", "construct", "develop", "invent", "innovate"],
                    "description": "Your true calling is to bring new things into existence. You thrive when you're creating, designing, or building something meaningful.",
                    "careers": [
                        {"title": "Software Developer", "description": "Create applications and systems that solve problems"},
                        {"title": "Product Designer", "description": "Design products that meet user needs and provide value"},
                        {"title": "Artist", "description": "Express ideas and emotions through various artistic mediums"},
                        {"title": "Writer", "description": "Craft stories, articles, or content that informs or entertains"},
                        {"title": "Architect", "description": "Design spaces and structures that serve human needs"},
                        {"title": "Entrepreneur", "description": "Create and build businesses that provide value"}
                    ]
                },
                "solving_problems": {
                    "keywords": ["solve", "fix", "figure out", "analyze", "troubleshoot", "improve", "optimize", "solution"],
                    "description": "Your true calling is to solve complex problems. You find satisfaction in analyzing situations, identifying issues, and developing effective solutions.",
                    "careers": [
                        {"title": "Consultant", "description": "Help organizations solve business problems and improve performance"},
                        {"title": "Engineer", "description": "Apply scientific principles to design solutions to technical problems"},
                        {"title": "Research Scientist", "description": "Investigate questions and develop new knowledge through research"},
                        {"title": "Data Analyst/Scientist", "description": "Extract insights from data to solve business problems"},
                        {"title": "Technical Support Specialist", "description": "Help users solve technical issues with products or services"},
                        {"title": "Quality Assurance Specialist", "description": "Identify and solve quality issues in products or processes"}
                    ]
                },
                "caring_for_others": {
                    "keywords": ["care", "nurture", "support", "heal", "comfort", "protect", "help", "serve", "empathy"],
                    "description": "Your true calling is to care for and support others. You find meaning in helping people through difficult times and improving their wellbeing.",
                    "careers": [
                        {"title": "Healthcare Professional", "description": "Provide medical care and support to patients"},
                        {"title": "Counselor/Therapist", "description": "Help people navigate emotional challenges and improve mental health"},
                        {"title": "Social Worker", "description": "Support individuals and families facing difficult circumstances"},
                        {"title": "Customer Support Specialist", "description": "Help customers solve problems and have positive experiences"},
                        {"title": "Community Outreach Coordinator", "description": "Connect people with resources and support in their community"},
                        {"title": "Caregiver", "description": "Provide direct care and support to those who need assistance"}
                    ]
                },
                "organizing_and_planning": {
                    "keywords": ["organize", "plan", "arrange", "coordinate", "structure", "manage", "order", "systematize"],
                    "description": "Your true calling is to create order from chaos. You thrive when organizing, planning, and ensuring things run smoothly and efficiently.",
                    "careers": [
                        {"title": "Project Manager", "description": "Plan and execute projects to achieve specific goals"},
                        {"title": "Operations Manager", "description": "Ensure efficient and effective daily operations"},
                        {"title": "Event Planner", "description": "Coordinate and organize events from concept to execution"},
                        {"title": "Logistics Coordinator", "description": "Manage the flow of goods, information, or people"},
                        {"title": "Administrative Professional", "description": "Support organizations by maintaining order and efficiency"},
                        {"title": "Process Improvement Specialist", "description": "Analyze and optimize organizational processes"}
                    ]
                },
                "expressing_creativity": {
                    "keywords": ["express", "create art", "perform", "write", "play music", "design", "imagine", "creative"],
                    "description": "Your true calling is to express yourself creatively. You find fulfillment in artistic expression and bringing beauty or meaning into the world.",
                    "careers": [
                        {"title": "Graphic Designer", "description": "Create visual content to communicate messages"},
                        {"title": "Content Creator", "description": "Develop engaging content across various platforms"},
                        {"title": "UX/UI Designer", "description": "Design user experiences for digital products"},
                        {"title": "Marketing Creative", "description": "Develop creative campaigns and materials"},
                        {"title": "Performer", "description": "Express yourself through acting, music, or other performance arts"},
                        {"title": "Creative Director", "description": "Guide the creative vision for projects or organizations"}
                    ]
                },
                "discovering_knowledge": {
                    "keywords": ["learn", "discover", "research", "investigate", "study", "examine", "understand", "knowledge"],
                    "description": "Your true calling is to discover and share knowledge. You thrive when learning, researching, and understanding complex topics.",
                    "careers": [
                        {"title": "Researcher", "description": "Investigate questions and contribute to knowledge in your field"},
                        {"title": "Journalist", "description": "Investigate and report on events and issues"},
                        {"title": "Market Research Analyst", "description": "Gather and analyze data about markets and consumers"},
                        {"title": "Business Intelligence Analyst", "description": "Transform data into actionable business insights"},
                        {"title": "Librarian/Information Specialist", "description": "Help others access and navigate information"},
                        {"title": "Curriculum Developer", "description": "Research and develop educational content and programs"}
                    ]
                },
                "leading_and_inspiring": {
                    "keywords": ["lead", "direct", "guide team", "manage people", "influence", "motivate", "inspire", "vision"],
                    "description": "Your true calling is to lead and inspire others. You find fulfillment in guiding groups toward a shared vision and bringing out the best in people.",
                    "careers": [
                        {"title": "Team Leader/Manager", "description": "Guide teams to achieve goals while developing team members"},
                        {"title": "Executive", "description": "Set organizational direction and make high-level decisions"},
                        {"title": "Community Leader", "description": "Bring people together around shared interests or causes"},
                        {"title": "Motivational Speaker", "description": "Inspire and motivate others through public speaking"},
                        {"title": "Leadership Coach", "description": "Help others develop their leadership abilities"},
                        {"title": "Entrepreneur", "description": "Lead organizations that bring your vision to life"}
                    ]
                }
            }
            
            # Save default data
            with open(DHARMA_DATA_PATH, 'w') as f:
                json.dump(default_data, f, indent=4)
            
            return default_data
        else:
            # Load existing data
            try:
                with open(DHARMA_DATA_PATH, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                console.print("[bold red]Error loading dharma data. Using default data.[/bold red]")
                return {}
    def assess_skills(self):
        """Gather information about user's skills and qualifications"""
        console.clear()
        console.print(Panel.fit(
            "[bold green]Your Skills & Qualifications[/bold green]\n\n"
            "Now let's take stock of your current skills and qualifications.\n"
            "This will help us understand how you might express your dharma in practical ways.",
            title="🛠️ Your Toolkit 🛠️",
            border_style="green"
        ))
        time.sleep(1)
        
        # Skills assessment
        console.print("\n[bold]What are your key skills?[/bold] (Enter one at a time, type 'done' when finished)")
        while True:
            skill = questionary.text("Skill:").ask()
            if skill.lower() == 'done' or not skill:
                break
            self.user_data["skills"].append(skill)
        
        # Qualifications
        console.print("\n[bold]What formal qualifications do you have?[/bold] (Degrees, certifications, etc. Type 'done' when finished)")
        while True:
            qual = questionary.text("Qualification:").ask()
            if qual.lower() == 'done' or not qual:
                break
            self.user_data["qualifications"].append(qual)
            
    def analyze_text_with_nlp(self):
        """Use NLP to analyze user responses and identify themes"""
        # Combine all responses
        all_text = " ".join(self.user_data["responses_raw"]).lower()
        
        # Use spaCy if available for more sophisticated analysis
        if SPACY_AVAILABLE:
            try:
                # Process text with spaCy
                doc = nlp(all_text)
                
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
                console.print(f"[yellow]NLP analysis encountered an issue: {str(e)}. Using simpler analysis.[/yellow]")
                return self.analyze_text_simple()
        else:
            return self.analyze_text_simple()
    
    def analyze_text_simple(self):
        """Simpler text analysis as fallback"""
        all_text = " ".join(self.user_data["responses_raw"]).lower()
        
        try:
            # Try to tokenize with NLTK
            try:
                # Tokenize and remove stopwords
                tokens = word_tokenize(all_text)
                try:
                    stop_words = set(stopwords.words('english'))
                    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
                except:
                    # If stopwords fail, just filter out non-alphanumeric
                    filtered_tokens = [word for word in tokens if word.isalnum()]
            except:
                # If NLTK tokenization fails, use simple split
                console.print("[yellow]NLTK tokenization failed. Using simple word splitting.[/yellow]")
                tokens = all_text.split()
                filtered_tokens = [word for word in tokens if len(word) > 2]
            
            # Count word frequencies
            word_freq = Counter(filtered_tokens)
            most_common = word_freq.most_common(10)
            
            # Extract simple phrases (consecutive words)
            words = all_text.split()
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
    
    def analyze_results(self):
        """Identify true calling and suggest career paths that align with it using NLP"""
        console.clear()
        console.print(Panel.fit(
            "[bold magenta]Discovering Your True Calling[/bold magenta]\n\n"
            "Based on your passions, memories, and aspirations,\n"
            "we're identifying your dharma (true calling) and career paths where you can express it.",
            title="🔍 Finding Your Dharma 🔍",
            border_style="magenta"
        ))
        
        # Simple animation to show "thinking"
        for _ in range(3):
            console.print("[bold]Analyzing[/bold]", end="")
            for _ in range(3):
                time.sleep(0.3)
                console.print(".", end="")
            console.print()
        
        # Combine all user inputs to identify themes
        all_inputs = " ".join(self.user_data["passions"] + 
                             self.user_data["childhood_memories"] + 
                             [self.user_data["dream_impact"]]).lower()
        
        # Use NLP to extract key themes from user responses
        nlp_results = self.analyze_text_with_nlp()
        
        # Calculate dharma scores using both keyword matching and NLP results
        dharma_scores = {}
        for dharma_type, data in self.dharma_paths.items():
            score = 0
            
            # Score based on direct keyword matches
            for keyword in data["keywords"]:
                if keyword in all_inputs:
                    score += 2  # Direct matches get higher weight
            
            # Score based on NLP-extracted keywords and phrases
            for word in nlp_results["key_words"]:
                if any(keyword in word or word in keyword for keyword in data["keywords"]):
                    score += 1
                    
            for phrase in nlp_results["key_phrases"]:
                if any(keyword in phrase for keyword in data["keywords"]):
                    score += 1.5  # Phrases get higher weight than single words
            
            dharma_scores[dharma_type] = score
        
        # Get top 2 dharma types
        top_dharmas = sorted(dharma_scores.items(), key=lambda x: x[1], reverse=True)[:2]
        
        # If no clear matches, use some defaults
        if top_dharmas[0][1] == 0:
            # Default to helping others and creating things if no keywords matched
            top_dharmas = [("helping_others_grow", 1), ("creating_and_innovating", 1)]
        
        # Prepare career suggestions based on true callings
        career_suggestions = []
        
        for dharma_type, _ in top_dharmas:
            dharma_data = self.dharma_paths[dharma_type]
            
            # Add careers from this dharma type
            for career in dharma_data["careers"]:
                # Check if user already has relevant skills
                has_relevant_skills = False
                skill_relevance = []
                
                for skill in self.user_data["skills"]:
                    # Check if skill is relevant to this career
                    skill_lower = skill.lower()
                    if career["title"].lower() in skill_lower or any(keyword in skill_lower for keyword in dharma_data["keywords"]):
                        has_relevant_skills = True
                        skill_relevance.append(skill)
                
                # Generate personalized alignment explanation
                if career["title"] in self.alignment_explanations:
                    alignment = random.choice(self.alignment_explanations[career["title"]])
                else:
                    alignment = random.choice(self.generic_alignments)
                
                # Generate personalized skill development suggestions
                if not has_relevant_skills:
                    # Suggest skills based on dharma type and career
                    suggested_skills = []
                    if "Teacher" in career["title"] or "Trainer" in career["title"]:
                        suggested_skills = ["communication", "curriculum development", "presentation skills"]
                    elif "Developer" in career["title"]:
                        suggested_skills = ["programming", "problem-solving", "technical design"]
                    elif "Designer" in career["title"]:
                        suggested_skills = ["visual design", "user research", "creative thinking"]
                    elif "Manager" in career["title"] or "Leader" in career["title"]:
                        suggested_skills = ["leadership", "team management", "strategic planning"]
                    else:
                        # Use some keywords from the dharma type as skill suggestions
                        suggested_skills = [k.capitalize() for k in dharma_data["keywords"][:3]]
                else:
                    suggested_skills = []
                
                career_suggestions.append({
                    "title": career["title"],
                    "description": career["description"],
                    "true_calling": dharma_type,
                    "calling_description": dharma_data["description"],
                    "has_relevant_skills": has_relevant_skills,
                    "relevant_skills": skill_relevance,
                    "suggested_skills": suggested_skills,
                    "alignment_explanation": alignment
                })
        
        # Get personalized messages for the top dharma types
        personalized_insights = []
        for dharma_type, _ in top_dharmas:
            if dharma_type in self.personalized_messages:
                personalized_insights.append(random.choice(self.personalized_messages[dharma_type]))
        
        return {
            "true_callings": [self.dharma_paths[dharma_type]["description"] for dharma_type, _ in top_dharmas],
            "career_suggestions": career_suggestions,
            "personalized_insights": personalized_insights,
            "nlp_keywords": nlp_results["key_words"][:5]  # Top 5 keywords for display
        }
    def display_results(self, results):
        """Display true calling and career suggestions to the user"""
        console.clear()
        console.print(Panel.fit(
            f"[bold blue]Your True Calling - {self.user_data['name']}[/bold blue]\n\n"
            f"Based on your reflections, we've identified your dharma (true calling).",
            title="🌟 Your Dharma 🌟",
            border_style="blue"
        ))
        
        # Display identified true callings
        console.print("\n[bold yellow]Your True Calling Appears To Be:[/bold yellow]")
        for i, calling in enumerate(results["true_callings"], 1):
            console.print(f"\n[bold]{i}.[/bold] {calling}")
        
        # Display personalized insights
        if results["personalized_insights"]:
            console.print("\n[bold cyan]Personal Insights:[/bold cyan]")
            for insight in results["personalized_insights"]:
                console.print(f"• {insight}")
        
        # Display key themes from NLP analysis
        if results["nlp_keywords"]:
            console.print("\n[bold]Key Themes In Your Responses:[/bold]")
            console.print(", ".join(results["nlp_keywords"]).capitalize())
        
        # Display career suggestions
        console.print("\n\n[bold green]Career Paths Where You Can Express Your True Calling:[/bold green]")
        console.print("[italic]These are roles where you can serve your dharma with your unique gifts[/italic]\n")
        
        # Group careers by true calling
        careers_by_calling = {}
        for career in results["career_suggestions"]:
            if career["true_calling"] not in careers_by_calling:
                careers_by_calling[career["true_calling"]] = []
            careers_by_calling[career["true_calling"]].append(career)
        
        # Display careers grouped by calling
        for calling, careers in careers_by_calling.items():
            console.print(f"\n[bold cyan]For your calling to {calling.replace('_', ' ')}:[/bold cyan]")
            
            for i, career in enumerate(careers, 1):
                console.print(f"\n[bold]{i}. {career['title']}[/bold]")
                console.print(f"[italic]{career['description']}[/italic]")
                
                # Show if they have relevant skills
                if career["has_relevant_skills"]:
                    console.print("[green]✓ You already have relevant skills for this path:[/green]")
                    for skill in career["relevant_skills"]:
                        console.print(f"  • {skill}")
                else:
                    console.print("[yellow]To pursue this path, consider developing these skills:[/yellow]")
                    for skill in career["suggested_skills"]:
                        console.print(f"  • {skill}")
                
                # Show personalized alignment explanation
                console.print("\n[bold]How This Aligns With Your Dharma:[/bold]")
                console.print(career["alignment_explanation"])
            
        # Final encouragement
        console.print(Panel.fit(
            "[bold]Remember:[/bold] Your true calling isn't just about what you do, but how you do it and why.\n"
            "Any role can become a vehicle for your dharma when approached with the right intention.\n"
            "The perfect career is where your true calling meets your skills and the world's needs.",
            title="🌱 Living Your Dharma 🌱",
            border_style="green"
        ))
        
        # Practical next steps
        console.print("\n[bold]Practical Next Steps:[/bold]")
        console.print("1. Reflect on which of these paths resonates most deeply with you")
        console.print("2. Research the specific roles that interest you")
        console.print("3. Connect with people already in these fields")
        console.print("4. Identify one small step you can take this week toward your dharma")
        console.print("5. Remember that living your dharma is a journey, not a destination")

    def run(self):
        """Run the full application flow"""
        try:
            self.welcome()
            self.explore_passions()
            self.assess_skills()
            results = self.analyze_results()
            self.display_results(results)
            
            # Ask if user wants to save results
            if questionary.confirm("Would you like to save your results to a file?").ask():
                filename = f"{self.user_data['name'].lower().replace(' ', '_')}_dharma_path.json"
                with open(filename, 'w') as f:
                    json.dump({
                        "user_data": self.user_data,
                        "true_callings": results["true_callings"],
                        "career_suggestions": results["career_suggestions"],
                        "personalized_insights": results["personalized_insights"],
                        "nlp_keywords": results["nlp_keywords"]
                    }, f, indent=4)
                console.print(f"[green]Results saved to {filename}[/green]")
            
            console.print("\n[bold cyan]Thank you for using Career Path Finder![/bold cyan]")
            console.print("[italic]Remember, finding your dharma is a journey of self-discovery and service.[/italic]")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Program interrupted. Exiting...[/yellow]")
        except Exception as e:
            console.print(f"[bold red]An error occurred: {str(e)}[/bold red]")


if __name__ == "__main__":
    app = CareerFinder()
    app.run()
