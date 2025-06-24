"""
Main CareerFinder class for the Career Path Finder application
"""

import os
import time
import random
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .utils import start_nltk_download
from .data_manager import DataManager
from .nlp_analyzer import NLPAnalyzer

# Try to load spaCy model, fall back to simpler analysis if not available
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except:
    nlp = None
    SPACY_AVAILABLE = False

# Initialize Rich console
console = Console()

# Start NLTK download in background
nltk_thread = start_nltk_download()

class CareerFinder:
    """Main class for the Career Path Finder application"""
    
    def __init__(self):
        """Initialize the Career Finder application"""
        self.user_data = {
            "name": "",
            "passions": [],
            "childhood_memories": [],
            "skills": [],
            "qualifications": [],
            "dream_impact": "",
            "responses_raw": []  # Store all raw responses for NLP analysis
        }
        
        # Initialize components
        self.data_manager = DataManager()
        self.nlp_analyzer = NLPAnalyzer(nlp if SPACY_AVAILABLE else None)
        
        # Load dharma descriptions and career paths
        self.dharma_paths = self.data_manager.load_dharma_data()
        
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
        nlp_results = self.nlp_analyzer.analyze_text(all_inputs)
        
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
                saved = self.data_manager.save_results(filename, {
                    "user_data": self.user_data,
                    "true_callings": results["true_callings"],
                    "career_suggestions": results["career_suggestions"],
                    "personalized_insights": results["personalized_insights"],
                    "nlp_keywords": results["nlp_keywords"]
                })
                if saved:
                    console.print(f"[green]Results saved to {filename}[/green]")
            
            console.print("\n[bold cyan]Thank you for using Career Path Finder![/bold cyan]")
            console.print("[italic]Remember, finding your dharma is a journey of self-discovery and service.[/italic]")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Program interrupted. Exiting...[/yellow]")
        except Exception as e:
            console.print(f"[bold red]An error occurred: {str(e)}[/bold red]")
