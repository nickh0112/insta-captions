#!/usr/bin/env python3
"""
Content Analysis Tool for Instagram Reels Transcripts
Extracts insights and content ideas from transcribed text files
"""

import re
from pathlib import Path
from collections import Counter
import json

def analyze_transcripts():
    """Analyze all transcript files and extract insights"""
    sub_dir = Path("subs")
    txt_files = list(sub_dir.glob("*.txt"))
    
    if not txt_files:
        print("❌ No transcript files found in subs/ directory")
        return
    
    print(f"📊 Analyzing {len(txt_files)} transcript files...")
    
    all_text = ""
    topics = []
    questions = []
    keywords = []
    
    for txt_file in txt_files:
        print(f"\n📄 Analyzing: {txt_file.name}")
        
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract the main transcript (after "Transcribed:")
        transcript_match = re.search(r'Transcribed: (.+?)(?=\n\n===)', content, re.DOTALL)
        if transcript_match:
            transcript = transcript_match.group(1).strip()
            all_text += transcript + " "
            
            # Extract topics (common content themes)
            topics.extend(extract_topics(transcript))
            
            # Extract questions
            questions.extend(extract_questions(transcript))
            
            # Extract keywords
            keywords.extend(extract_keywords(transcript))
    
    # Generate insights
    print("\n" + "="*50)
    print("🎯 CONTENT INSIGHTS & IDEAS")
    print("="*50)
    
    # Most common topics
    topic_counter = Counter(topics)
    print(f"\n📈 TOP TOPICS DISCUSSED:")
    for topic, count in topic_counter.most_common(10):
        print(f"   • {topic}: {count} mentions")
    
    # Questions asked
    question_counter = Counter(questions)
    print(f"\n❓ QUESTIONS ASKED:")
    for question, count in question_counter.most_common(5):
        print(f"   • {question}")
    
    # Keywords
    keyword_counter = Counter(keywords)
    print(f"\n🔑 KEYWORDS:")
    for keyword, count in keyword_counter.most_common(15):
        print(f"   • {keyword}: {count} mentions")
    
    # Content ideas
    print(f"\n💡 CONTENT IDEA SUGGESTIONS:")
    generate_content_ideas(topic_counter, question_counter, keyword_counter)
    
    # Save analysis to file
    analysis_data = {
        "total_transcripts": len(txt_files),
        "top_topics": dict(topic_counter.most_common(10)),
        "questions": dict(question_counter.most_common(10)),
        "keywords": dict(keyword_counter.most_common(20)),
        "full_text": all_text
    }
    
    with open("content_analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Analysis saved to: content_analysis.json")

def extract_topics(text):
    """Extract common content topics"""
    topics = []
    
    # Common content themes
    theme_patterns = {
        "product reviews": r"\b(review|test|try|buy|purchase|recommend)\b",
        "tutorials": r"\b(how to|tutorial|guide|step|learn|teach)\b",
        "lifestyle": r"\b(life|daily|routine|morning|night|day)\b",
        "fitness": r"\b(workout|exercise|fitness|gym|train|health)\b",
        "cooking": r"\b(cook|recipe|food|kitchen|ingredient|meal)\b",
        "travel": r"\b(travel|trip|visit|go|place|location)\b",
        "fashion": r"\b(fashion|style|outfit|wear|clothes|dress)\b",
        "beauty": r"\b(beauty|makeup|skincare|hair|product)\b",
        "tech": r"\b(tech|technology|app|software|device|phone)\b",
        "business": r"\b(business|work|job|career|money|income)\b"
    }
    
    text_lower = text.lower()
    for topic, pattern in theme_patterns.items():
        if re.search(pattern, text_lower):
            topics.append(topic)
    
    return topics

def extract_questions(text):
    """Extract questions from text"""
    questions = []
    
    # Find sentences ending with question marks
    question_pattern = r'[^.!?]*\?'
    matches = re.findall(question_pattern, text)
    
    for match in matches:
        question = match.strip()
        if len(question) > 10:  # Filter out very short questions
            questions.append(question)
    
    return questions

def extract_keywords(text):
    """Extract important keywords"""
    # Remove common words and punctuation
    text_lower = text.lower()
    words = re.findall(r'\b[a-z]{3,}\b', text_lower)
    
    # Filter out common stop words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
        'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her',
        'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs'
    }
    
    keywords = [word for word in words if word not in stop_words]
    return keywords

def generate_content_ideas(topic_counter, question_counter, keyword_counter):
    """Generate content ideas based on analysis"""
    ideas = []
    
    # Ideas based on popular topics
    top_topics = [topic for topic, count in topic_counter.most_common(3)]
    for topic in top_topics:
        ideas.append(f"Create a comprehensive {topic} guide")
        ideas.append(f"Share your {topic} journey/story")
        ideas.append(f"Review different {topic} options")
    
    # Ideas based on questions
    if question_counter:
        ideas.append("Answer common questions in a Q&A format")
        ideas.append("Create a FAQ video based on viewer questions")
    
    # Ideas based on keywords
    top_keywords = [kw for kw, count in keyword_counter.most_common(5)]
    if top_keywords:
        ideas.append(f"Create content around: {', '.join(top_keywords[:3])}")
    
    # General content ideas
    ideas.extend([
        "Share behind-the-scenes content",
        "Create a 'day in the life' video",
        "Make a tutorial based on your expertise",
        "Share tips and tricks you've learned",
        "Create a 'before and after' comparison",
        "Make a reaction video to related content",
        "Share your personal story/experience",
        "Create a listicle (top 5, 10, etc.)",
        "Make a challenge or trend video",
        "Share your goals and progress updates"
    ])
    
    # Print ideas
    for i, idea in enumerate(ideas[:10], 1):
        print(f"   {i}. {idea}")

if __name__ == "__main__":
    analyze_transcripts() 