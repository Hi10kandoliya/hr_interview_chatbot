"""
HR Interview Chatbot - Streamlit Version
A simple bot that conducts HR interview rounds
"""

import streamlit as st
import datetime
import time
import random
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="HR Interview Chatbot",
    page_icon="💼",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Interview header */
    .interview-header {
        background: linear-gradient(135deg, #2E86C1, #1B4F72);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Chat message styling */
    .bot-message {
        background-color: #2E86C1;
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .user-message {
        background-color: #28B463;
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .system-message {
        background-color: #F39C12;
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
        clear: both;
    }
    
    .message-time {
        font-size: 0.7rem;
        opacity: 0.7;
        margin-top: 5px;
        text-align: right;
    }
    
    /* Feedback card */
    .feedback-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 20px 0;
        border-left: 5px solid #2E86C1;
    }
    
    /* Progress indicator */
    .progress-container {
        background-color: #e0e0e0;
        border-radius: 10px;
        margin: 20px 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #2E86C1, #28B463);
        color: white;
        padding: 5px;
        border-radius: 10px;
        text-align: center;
        font-size: 0.9rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #2E86C1;
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #1B4F72;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(46,134,193,0.3);
    }
    
    /* Score display */
    .score-circle {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2E86C1, #28B463);
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 20px auto;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    
    .score-number {
        font-size: 3rem;
        font-weight: bold;
        line-height: 1;
    }
    
    .score-label {
        font-size: 1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.messages = []
    st.session_state.current_question = 0
    st.session_state.answers = {}
    st.session_state.interview_started = False
    st.session_state.interview_completed = False
    st.session_state.candidate_name = ""
    st.session_state.candidate_email = ""
    st.session_state.candidate_phone = ""
    st.session_state.start_time = None
    st.session_state.feedback = {}
    st.session_state.evaluations = []

# HR Interview Questions Database
class HRInterviewBot:
    def __init__(self):
        self.questions = [
            {
                "id": 1,
                "category": "Introduction",
                "question": "Tell me about yourself and your background.",
                "keywords": ["experience", "background", "education", "skills", "years"],
                "ideal_points": ["Clear structure", "Relevant experience", "Career progression"],
                "weight": 1.0
            },
            {
                "id": 2,
                "category": "Motivation",
                "question": "Why are you interested in this position and our company?",
                "keywords": ["company", "position", "growth", "learn", "opportunity", "values"],
                "ideal_points": ["Company research shown", "Role alignment", "Enthusiasm"],
                "weight": 1.2
            },
            {
                "id": 3,
                "category": "Strengths",
                "question": "What are your top 3 professional strengths?",
                "keywords": ["strength", "skill", "expert", "good at", "excel", "proficient"],
                "ideal_points": ["Relevant to job", "Specific examples", "Balanced"],
                "weight": 1.0
            },
            {
                "id": 4,
                "category": "Weaknesses",
                "question": "What would you consider your biggest weakness, and how do you work on it?",
                "keywords": ["weakness", "improve", "learning", "develop", "working on", "growth"],
                "ideal_points": ["Honest", "Self-aware", "Improvement plan"],
                "weight": 1.1
            },
            {
                "id": 5,
                "category": "Achievement",
                "question": "Tell me about your proudest professional achievement.",
                "keywords": ["achievement", "accomplished", "success", "completed", "project", "award"],
                "ideal_points": ["Quantifiable results", "Challenges overcome", "Impact"],
                "weight": 1.2
            },
            {
                "id": 6,
                "category": "Teamwork",
                "question": "Describe a time you had to work in a team to achieve a goal.",
                "keywords": ["team", "collaboration", "together", "group", "helped", "supported"],
                "ideal_points": ["Team player", "Conflict resolution", "Contribution clarity"],
                "weight": 1.0
            },
            {
                "id": 7,
                "category": "Conflict",
                "question": "How do you handle conflict or difficult situations at work?",
                "keywords": ["conflict", "difficult", "challenge", "problem", "resolve", "handle"],
                "ideal_points": ["Professional approach", "Solution-oriented", "Emotional intelligence"],
                "weight": 1.1
            },
            {
                "id": 8,
                "category": "Goals",
                "question": "Where do you see yourself in 5 years?",
                "keywords": ["future", "years", "plan", "goal", "aspire", "growth", "career path"],
                "ideal_points": ["Ambition", "Realistic", "Company alignment"],
                "weight": 1.0
            },
            {
                "id": 9,
                "category": "Salary",
                "question": "What are your salary expectations for this role?",
                "keywords": ["salary", "compensation", "expectations", "package", "range", "negotiable"],
                "ideal_points": ["Market awareness", "Flexibility", "Justified"],
                "weight": 0.8
            },
            {
                "id": 10,
                "category": "Questions",
                "question": "Do you have any questions for me about the role or company?",
                "keywords": ["question", "ask", "curious", "wonder", "clarify", "know more"],
                "ideal_points": ["Engagement", "Thoughtful questions", "Interest shown"],
                "weight": 1.0
            }
        ]
        
        self.tips = {
            "Introduction": "Keep it concise (2-3 minutes). Focus on professional journey, not personal details.",
            "Motivation": "Research the company beforehand. Mention specific projects or values that attract you.",
            "Strengths": "Use STAR method (Situation, Task, Action, Result) for examples.",
            "Weaknesses": "Be honest but show improvement. Never say 'I work too hard'.",
            "Achievement": "Quantify results whenever possible (%, $, numbers).",
            "Teamwork": "Highlight your specific role in team success.",
            "Conflict": "Stay professional. Focus on resolution, not blame.",
            "Goals": "Show ambition but keep it realistic and aligned with the role.",
            "Salary": "Research market rates. Provide a range, not a fixed number.",
            "Questions": "Always have 2-3 thoughtful questions prepared."
        }
    
    def get_current_question(self, index):
        """Get question by index"""
        if 0 <= index < len(self.questions):
            return self.questions[index]
        return None
    
    def evaluate_response(self, question_id, response):
        """Simple evaluation of response based on keywords"""
        question = next((q for q in self.questions if q["id"] == question_id), None)
        if not question:
            return 0, []
        
        response_lower = response.lower()
        
        # Count keyword matches
        keywords_found = []
        for keyword in question["keywords"]:
            if keyword in response_lower:
                keywords_found.append(keyword)
        
        # Calculate score (0-10)
        keyword_score = min(len(keywords_found) * 2, 8)  # Max 8 from keywords
        
        # Length bonus (very short answers get penalized)
        words = response.split()
        if len(words) < 5:
            length_score = 0
        elif len(words) < 10:
            length_score = 1
        else:
            length_score = 2
        
        total_score = keyword_score + length_score
        
        return total_score, keywords_found
    
    def get_question_progress(self, current_index):
        """Get progress percentage"""
        return (current_index / len(self.questions)) * 100

# Initialize bot
bot = HRInterviewBot()

# Header
st.markdown("""
<div class="interview-header">
    <h1>💼 HR Interview Chatbot</h1>
    <p>Practice your HR interview skills with AI • Answer questions • Get instant feedback</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for candidate info
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/business-conference.png", width=80)
    st.title("Interview Details")
    
    if not st.session_state.interview_started and not st.session_state.interview_completed:
        with st.form("candidate_form"):
            name = st.text_input("Full Name *")
            email = st.text_input("Email *")
            phone = st.text_input("Phone Number")
            position = st.selectbox(
                "Position Applying For",
                ["Software Engineer", "Data Scientist", "Product Manager", "Marketing Specialist", "Sales Representative", "Other"]
            )
            experience = st.slider("Years of Experience", 0, 20, 2)
            
            submitted = st.form_submit_button("Start Interview 🚀")
            
            if submitted and name and email:
                st.session_state.candidate_name = name
                st.session_state.candidate_email = email
                st.session_state.candidate_phone = phone
                st.session_state.candidate_position = position
                st.session_state.candidate_experience = experience
                st.session_state.interview_started = True
                st.session_state.start_time = datetime.datetime.now()
                
                # Add welcome message
                st.session_state.messages.append({
                    "role": "bot",
                    "content": f"Hello {name}! Welcome to your HR interview for the {position} position. I'll ask you 10 questions. Take your time with each response. Let's begin with the first question."
                })
                
                # Add first question
                first_q = bot.get_current_question(0)
                st.session_state.messages.append({
                    "role": "bot",
                    "content": f"**Question 1 ({first_q['category']}):** {first_q['question']}"
                })
                
                st.rerun()
    
    elif st.session_state.interview_started:
        st.info(f"**Candidate:** {st.session_state.candidate_name}")
        st.info(f"**Position:** {st.session_state.candidate_position}")
        
        # Progress bar
        progress = bot.get_question_progress(st.session_state.current_question)
        st.markdown(f"**Progress:** Question {st.session_state.current_question + 1}/10")
        st.progress(progress / 100)
        
        # Timer
        if st.session_state.start_time:
            elapsed = datetime.datetime.now() - st.session_state.start_time
            mins, secs = divmod(elapsed.seconds, 60)
            st.info(f"⏱️ Time: {mins:02d}:{secs:02d}")
        
        # Tips for current question
        current_q = bot.get_current_question(st.session_state.current_question)
        if current_q:
            with st.expander("💡 Interview Tip"):
                st.write(bot.tips.get(current_q['category'], "Take your time and be honest."))
        
        if st.button("End Interview Early"):
            st.session_state.interview_started = False
            st.session_state.interview_completed = True
            st.rerun()
    
    else:
        st.success("Complete the form to start your interview!")

# Main chat area
chat_container = st.container()

with chat_container:
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "bot":
            st.markdown(f'<div class="bot-message">{message["content"]}<div class="message-time">Bot</div></div>', unsafe_allow_html=True)
        elif message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}<div class="message-time">You</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="system-message">{message["content"]}</div>', unsafe_allow_html=True)

# Input area (only if interview is in progress)
if st.session_state.interview_started and not st.session_state.interview_completed:
    st.markdown("---")
    
    with st.form("response_form", clear_on_submit=True):
        user_response = st.text_area("Your Answer:", height=100, placeholder="Type your response here...")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            submitted = st.form_submit_button("Submit Answer 📤", use_container_width=True)
        
        with col2:
            skip = st.form_submit_button("Skip Question ⏭️", use_container_width=True)
        
        with col3:
            if st.form_submit_button("Clear ✖️", use_container_width=True):
                st.rerun()
    
    if submitted and user_response:
        # Store answer
        current_q = bot.get_current_question(st.session_state.current_question)
        
        # Evaluate response
        score, keywords = bot.evaluate_response(current_q["id"], user_response)
        
        # Store in session
        st.session_state.answers[current_q["id"]] = {
            "question": current_q["question"],
            "category": current_q["category"],
            "response": user_response,
            "score": score,
            "keywords_found": keywords,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        }
        
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_response})
        
        # Move to next question
        st.session_state.current_question += 1
        
        # Check if interview completed
        if st.session_state.current_question >= len(bot.questions):
            st.session_state.interview_started = False
            st.session_state.interview_completed = True
            
            # Add completion message
            st.session_state.messages.append({
                "role": "bot",
                "content": "Thank you for completing the interview! I'll now generate your feedback report."
            })
        else:
            # Add next question
            next_q = bot.get_current_question(st.session_state.current_question)
            st.session_state.messages.append({
                "role": "bot",
                "content": f"**Question {next_q['id']} ({next_q['category']}):** {next_q['question']}"
            })
        
        st.rerun()
    
    elif skip:
        # Skip current question
        current_q = bot.get_current_question(st.session_state.current_question)
        
        st.session_state.answers[current_q["id"]] = {
            "question": current_q["question"],
            "category": current_q["category"],
            "response": "[SKIPPED]",
            "score": 0,
            "keywords_found": [],
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        }
        
        st.session_state.messages.append({
            "role": "system",
            "content": f"⏭️ You skipped Question {current_q['id']}"
        })
        
        st.session_state.current_question += 1
        
        if st.session_state.current_question >= len(bot.questions):
            st.session_state.interview_started = False
            st.session_state.interview_completed = True
            st.session_state.messages.append({
                "role": "bot",
                "content": "Interview completed! Generating feedback..."
            })
        else:
            next_q = bot.get_current_question(st.session_state.current_question)
            st.session_state.messages.append({
                "role": "bot",
                "content": f"**Question {next_q['id']} ({next_q['category']}):** {next_q['question']}"
            })
        
        st.rerun()

# Interview completed - Show feedback
if st.session_state.interview_completed:
    st.markdown("---")
    st.markdown("## 📊 Interview Feedback Report")
    
    # Calculate total score
    total_possible = sum([q["weight"] * 10 for q in bot.questions])
    total_earned = 0
    category_scores = {}
    
    for q_id, answer in st.session_state.answers.items():
        question = next((q for q in bot.questions if q["id"] == q_id), None)
        if question:
            weighted_score = answer["score"] * question["weight"]
            total_earned += weighted_score
            category_scores[question["category"]] = answer["score"]
    
    overall_percentage = (total_earned / total_possible) * 100 if total_possible > 0 else 0
    
    # Score display
    col1, col2, col3 = st.columns(3)
    
    with col2:
        st.markdown(f"""
        <div class="score-circle">
            <div class="score-number">{overall_percentage:.0f}%</div>
            <div class="score-label">Overall Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Candidate info
    st.markdown(f"""
    <div class="feedback-card">
        <h4>👤 Candidate: {st.session_state.candidate_name}</h4>
        <p>📧 {st.session_state.candidate_email} | 📞 {st.session_state.candidate_phone}</p>
        <p>💼 Position: {st.session_state.candidate_position} | Experience: {st.session_state.candidate_experience} years</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed answers table
    st.markdown("### 📝 Response Analysis")
    
    feedback_data = []
    for q_id, answer in st.session_state.answers.items():
        question = next((q for q in bot.questions if q["id"] == q_id), None)
        if question:
            # Determine rating
            if answer["score"] >= 8:
                rating = "🌟 Excellent"
                rating_color = "#28B463"
            elif answer["score"] >= 6:
                rating = "✅ Good"
                rating_color = "#2E86C1"
            elif answer["score"] >= 4:
                rating = "⚠️ Average"
                rating_color = "#F39C12"
            else:
                rating = "❌ Needs Improvement"
                rating_color = "#E74C3C"
            
            feedback_data.append({
                "Question": f"{question['category']} (Q{question['id']})",
                "Response Preview": answer["response"][:100] + "..." if len(answer["response"]) > 100 else answer["response"],
                "Score": f"{answer['score']}/10",
                "Keywords Found": ", ".join(answer["keywords_found"]) if answer["keywords_found"] else "None",
                "Rating": rating
            })
    
    if feedback_data:
        df = pd.DataFrame(feedback_data)
        st.dataframe(df, use_container_width=True)
    
    # Category-wise performance
    st.markdown("### 📊 Category Performance")
    
    # Create columns for each category
    cols = st.columns(5)
    categories = list(category_scores.keys())
    
    for i, category in enumerate(categories[:5]):  # First 5
        with cols[i % 5]:
            score = category_scores.get(category, 0)
            st.metric(category, f"{score}/10")
    
    if len(categories) > 5:
        cols2 = st.columns(5)
        for i, category in enumerate(categories[5:]):  # Next 5
            with cols2[i % 5]:
                score = category_scores.get(category, 0)
                st.metric(category, f"{score}/10")
    
    # Strengths and weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💪 Strengths")
        strengths = []
        for q_id, answer in st.session_state.answers.items():
            if answer["score"] >= 7:
                question = next((q for q in bot.questions if q["id"] == q_id), None)
                if question:
                    strengths.append(f"• **{question['category']}**: Good keyword usage and detailed response")
        
        if strengths:
            for s in strengths:
                st.success(s)
        else:
            st.info("No strong areas identified yet. Focus on providing more detailed responses.")
    
    with col2:
        st.markdown("### 🎯 Areas to Improve")
        improvements = []
        for q_id, answer in st.session_state.answers.items():
            if answer["score"] < 5:
                question = next((q for q in bot.questions if q["id"] == q_id), None)
                if question:
                    tip = bot.tips.get(question['category'], "Provide more specific examples.")
                    improvements.append(f"• **{question['category']}**: {tip}")
        
        if improvements:
            for i in improvements:
                st.warning(i)
        else:
            st.info("Great job! You performed well across all categories.")
    
    # General tips
    st.markdown("### 🎓 Interview Tips for Next Time")
    st.info("""
    1. **Use the STAR method** (Situation, Task, Action, Result) for behavioral questions
    2. **Quantify achievements** with numbers, percentages, or time saved
    3. **Research the company** before the interview
    4. **Prepare 3-5 questions** to ask the interviewer
    5. **Practice aloud** to improve delivery and confidence
    """)
    
    # Download report
    st.markdown("### 📥 Download Report")
    
    # Create detailed report
    report = f"""
    HR INTERVIEW FEEDBACK REPORT
    ============================
    
    Candidate: {st.session_state.candidate_name}
    Email: {st.session_state.candidate_email}
    Position: {st.session_state.candidate_position}
    Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
    Overall Score: {overall_percentage:.1f}%
    
    DETAILED RESPONSES:
    ==================
    """
    
    for q_id, answer in st.session_state.answers.items():
        question = next((q for q in bot.questions if q["id"] == q_id), None)
        if question:
            report += f"""
    
    Q{question['id']} ({question['category']}): {question['question']}
    Response: {answer['response']}
    Score: {answer['score']}/10
    Keywords Found: {', '.join(answer['keywords_found']) if answer['keywords_found'] else 'None'}
    --------------------------------------------------
    """
    
    col1, col2, col3 = st.columns(3)
    with col2:
        st.download_button(
            label="📄 Download Full Report",
            data=report,
            file_name=f"HR_Interview_{st.session_state.candidate_name}_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # New interview button
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("🔄 Start New Interview", use_container_width=True):
            # Clear session state
            for key in ['messages', 'current_question', 'answers', 'interview_started', 
                       'interview_completed', 'candidate_name', 'candidate_email', 
                       'candidate_phone', 'start_time']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 10px;">
    <p>💼 HR Interview Practice Bot • Practice makes perfect • All responses are simulated feedback</p>
    <p style="font-size: 0.8rem;">© 2024 • For practice purposes only. Real interviews may vary.</p>
</div>
""", unsafe_allow_html=True)