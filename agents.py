import os
from groq import Groq
from tools import search_market_requirements
import json
import re
from rag_engine import RAGEngine
# --- 1. Groq Wrapper ---
def query_llm(system_instruction, user_prompt):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "[Error: GROQ API Key missing.]"

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=1,
            max_tokens=6000,
            top_p=1,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"[Error calling Groq: {str(e)}]"


# --- 2. Input Expander Agent ---
class InputExpanderAgent:
    def __init__(self):
        self.role = "Academic Advisor"

    def expand_topic(self, topic):
        sys_prompt = "You are a University Curriculum Planner."

        lang_instruction = "Output values in English."

        user_prompt = f"""
        User wants to learn: '{topic}'.
        {lang_instruction}

        Return JSON object:
        {{
            "duration": 12, "lec": 3, "tut": 1, "lab": 3,
            "obj": "Detailed learning goals",
            "topics": "List of core topics",
            "context": "Industry application",
            "know": "Prerequisites"
        }}
        """
        try:
            response = query_llm(sys_prompt, user_prompt)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except Exception as e:
            print(f"Expansion Error: {e}")
            return None


# --- 3. PDF Parser Agent ---
class PDFParserAgent:
    def __init__(self):
        self.role = "Document Analyzer"

    def extract_course_details(self, raw_text):
        sys_prompt = "You are a Data Extraction Specialist."
        user_prompt = f"""
        Analyze text: '''{raw_text[:8000]}'''
        Extract to JSON:
        {{
            "title": "Course Name", "duration": 12, 
            "lec": 2, "tut": 1, "lab": 2,
            "objectives": "Summary", "topics": "List", "context": "Industry"
        }}
        """
        try:
            response = query_llm(sys_prompt, user_prompt, json_mode=True)
            return json.loads(response)
        except:
            return None


# --- 4. The Slaves ---
class MarketSlave:
    def __init__(self):
        self.role = "Job Market Researcher"

    def research(self, course_title, topics):
        print(f"[{self.role}] Searching...")
        search_results = search_market_requirements(course_title)

        sys_prompt = "You are an expert Technical Recruiter."
        user_prompt = f"""
        Analyze search results for '{course_title}':
        {search_results}
        Proposed Topics: {topics}

        Output a detailed list:
        1. Top 7 Technical Skills.
        2. Top 3 Industry Tools.
        3. Top emerging trend.
        """
        return query_llm(sys_prompt, user_prompt)


class CurriculumSlave:
    def __init__(self):
        self.role = "Curriculum Designer"

    def draft_plan(self, course_info, market_data, rag_context=None, feedback="None"):
        print(f"[{self.role}] Drafting with RAG support...")

        # --- 1. Prepare RAG Context ---
        # If the Vector Store found relevant documents, we format them here.
        rag_section = "No specific reference documents provided. Use standard academic curriculum structures."
        if rag_context and len(rag_context) > 10:
            rag_section = f"""
            ### 📚 ACADEMIC REFERENCE MATERIAL (PRIMARY SOURCE):
            The user has provided the following text from textbooks or university guidelines.
            **You MUST align the weekly topics and theoretical flow with this content:**
            '''
            {rag_context}
            '''
            (End of Reference Material)
            """

        # --- 2. Enhanced Specificity Rules ---
        specific_instr = """
        **SPECIFICITY & RAG RULES:**
        1. **Source of Truth:** If 'ACADEMIC REFERENCE MATERIAL' is provided, the Lecture Plan (Weeks) must strictly follow its structure/chapters.
        2. **Market Alignment:** Use the 'JOB MARKET DATA' to determine which specific *tools, libraries, and frameworks* to teach in the Labs.
        3. **Content:** Each week MUST have detailed sub-points. Do NOT be vague.
        4. **Capstone:** Do NOT say "Build a model". You MUST specify the Dataset, the Problem Statement, and the Tech Stack.
        5. **Resources:** If the Reference Material mentions specific books, cite them. Otherwise, list real URLs/Books.
        6. **Format:** Use Markdown with clear headers.
        """

        lang_instruction = f"Output in detailed English. {specific_instr}"

        # --- 3. Determine Context (First Draft vs Revision) ---
        if feedback and feedback != "None" and feedback != "":
            task_context = f"""
            **TASK: REFINE EXISTING PLAN**
            The previous draft was evaluated.
            **CRITICAL FEEDBACK TO ADDRESS:** {feedback}

            Re-write the course plan. Keep the RAG-based structure but fix the issues identified above.
            """
        else:
            task_context = f"""
            **TASK: CREATE FIRST DRAFT**
            Create a comprehensive course plan blending the Academic References (Theory) with Market Data (Practice).
            """

        # --- 4. Construct Prompts ---
        sys_prompt = f"You are a Senior University Professor and Curriculum Architect. {lang_instruction}"

        user_prompt = f"""
        {task_context}

        ### COURSE METADATA:
        - **Title:** {course_info['title']}
        - **Duration:** {course_info['duration']} weeks
        - **Objectives:** {course_info.get('objectives', 'Standard proficiency')}

        ### 🏗️ INPUTS FOR GENERATION:

        {rag_section}

        ### 💼 JOB MARKET DATA (SKILLS & TOOLS):
        Use these requirements to design the **Labs** and **Capstone Project**:
        {market_data}

        ### REQUIRED OUTPUT STRUCTURE:
        # {course_info['title']}
        ## Course Overview
        ## 1. Lecture Plan (Week 1 to {course_info['duration']}) 
           *(Derive topics from Reference Material if available)*
        ## 2. Labs Content (Week by week)
           *(Derive tools/tasks from Market Data)*
        ## 3. Capstone Project (Specific & Industry-relevant)
        ## 4. Resources & References
        """

        return query_llm(sys_prompt, user_prompt)

class ArbitratorSlave:
    def __init__(self):
        self.role = "Quality Assurance"

    def evaluate(self, market_data, current_draft):
        system_instruction = "You are an expert Academic-Industry Arbitrator."
        system_instruction = (
            "You are an expert Academic-Industry Arbitrator. "
            "Evaluate the curriculum draft against the market requirements and technologies. "
            "Format response: SCORE: [0-100] | FEEDBACK: [Detailed critique]"
        )

        user_prompt = f"""
                ### JOB MARKET DATA:
                {market_data}

                ### PROPOSED DRAFT:
                {current_draft}

                Task:
                1. Compare the Draft against the Market Data.
                2. Are specific tools (from market data) missing in the Lecture topics or the Labs?
                3. Is the Capstone project mentioned relevant?
                4. Are the mentioned resources & references really helpful?
                4. Give a Score (0-100). If < 85, list specific missing topics to fix.
                """
        try:
            response = query_llm(system_instruction, user_prompt)
            match = re.search(r"SCORE:\s*(\d+)", response)
            score = int(match.group(1)) if match else 85

            if "FEEDBACK:" in response:
                feedback = response.split("FEEDBACK:")[-1].strip()
            elif "|" in response:
                feedback = response.split("|")[-1].strip()
            else:
                feedback = "Approved"

            return score, feedback
        except:
            return 100, "Approved"


# --- 5. Master Agent ---
class MasterAgent:
    def __init__(self):
        self.s1 = MarketSlave()
        self.s2 = CurriculumSlave()
        self.s3 = ArbitratorSlave()
        # Initialize RAG Engine (loads the persisted vector store)
        self.rag = RAGEngine()

    def run(self, course_data):
        status_log = []

        # --- Step 1: Market Research ---
        status_log.append("Slave 1: Scouting Job Market...")
        # We search specifically for the title and the topics provided
        market_data = self.s1.research(course_data['title'], course_data['topics'])
        status_log.append("Market Data Synthesized.")

        # --- Step 2: RAG Retrieval (The New Layer) ---
        status_log.append("Slave 4 (RAG): Querying Knowledge Base...")

        # Construct a retrieval query combining title and specific topics
        retrieval_query = f"{course_data['title']} {course_data['topics']} syllabus structure curriculum chapters"

        # Retrieve context (chunks of text) from the vector store
        rag_context = self.rag.retrieve_context(retrieval_query)

        if rag_context and len(rag_context) > 50:
            status_log.append("✅ Relevant Academic Context Retrieved.")
        else:
            status_log.append("⚠️ No specific Local Context found. Relying on General Knowledge.")

        # --- Step 3: Iterative Drafting ---
        score = 0
        feedback = None
        iteration = 0
        max_attempts = 2  # Keep low for demo speed
        draft = ""

        while score < 85 and iteration < max_attempts:
            iteration += 1
            status_log.append(f"--- Round {iteration} ---")

            if feedback:
                status_log.append("Slave 2: Refining based on Feedback...")
            else:
                status_log.append("Slave 2: Drafting Detailed Syllabus...")

            # PASS THE RAG CONTEXT HERE
            draft = self.s2.draft_plan(
                course_info=course_data,
                market_data=market_data,
                rag_context=rag_context,  # <--- INJECTED CONTEXT
                feedback=feedback
            )

            status_log.append("Slave 3: Quality Check...")
            score, feedback = self.s3.evaluate(market_data, draft)
            status_log.append(f"Score: {score}/100")

            if score < 85:
                status_log.append("Refining specificity...")

        status_log.append("Plan Finalized.")
        return draft, status_log

    def ingest_documents(self, file_path):
        """Helper to expose RAG ingestion to the UI"""
        return self.rag.ingest_file(file_path)