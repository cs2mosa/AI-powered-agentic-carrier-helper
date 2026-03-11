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
            temperature=0.3,  # LOWERED TEMPERATURE: Makes the model less creative and more faithful to the RAG context
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

        # --- 1. Prepare STRICT RAG Context ---
        rag_section = "No specific reference documents provided. Rely on standard academic knowledge."
        if rag_context and len(rag_context) > 10:
            rag_section = f"""
            ### 🚨 STRICT REFERENCE MATERIAL (MANDATORY RAG CONTEXT) 🚨:
            '''
            {rag_context}
            '''
            CRITICAL SYSTEM DIRECTIVE: 
            You are operating in a strict Grounded-RAG environment. You MUST derive the theoretical topics, chapters, and flow EXCLUSIVELY from the Reference Material above. 
            DO NOT hallucinate chapters or concepts not present in the provided text.
            """

        # --- 2. Enhanced Specificity Rules ---
        specific_instr = """
        **SPECIFICITY & STRICT RAG RULES:**
        1. **Source of Truth:** If Reference Material is provided, the Lecture Plan MUST strictly mirror its content. Failure to do so is a catastrophic error.
        2. **Market Alignment:** Use the 'JOB MARKET DATA' ONLY to decide which practical tools/frameworks to use during the Hands-on Labs.
        3. **Content:** Each week MUST have detailed sub-points. Do NOT be vague.
        4. **Capstone:** You MUST specify a concrete Dataset, Problem Statement, and Tech Stack.
        5. **Resources:** If the Reference Material is provided, cite it heavily.
        6. **Format:** Use Markdown with clear headers (##).
        """

        lang_instruction = f"Output in detailed English. {specific_instr}"

        # --- 3. Determine Context (First Draft vs Revision) ---
        if feedback and feedback != "None" and feedback != "":
            task_context = f"""
            **TASK: REFINE EXISTING PLAN**
            The previous draft failed the quality check.
            **CRITICAL FEEDBACK TO FIX:** {feedback}

            Re-write the course plan. You MUST strictly obey the RAG context and address the feedback.
            """
        else:
            task_context = f"""
            **TASK: CREATE FIRST DRAFT**
            Create a comprehensive course plan tightly blending the Academic References (Theory) with Market Data (Practice).
            """

        # --- 4. Construct Prompts ---
        sys_prompt = f"You are a strict, detail-oriented University Curriculum Architect. {lang_instruction}"

        user_prompt = f"""
        {task_context}

        ### COURSE METADATA:
        - **Title:** {course_info['title']}
        - **Duration:** {course_info['duration']} weeks
        - **Objectives:** {course_info.get('objectives', 'Standard proficiency')}

        ### 🏗️ INPUTS FOR GENERATION:

        {rag_section}

        ### 💼 JOB MARKET DATA (For Labs Only):
        {market_data}

        ### REQUIRED OUTPUT STRUCTURE:
        # {course_info['title']}
        ## Course Overview
        ## 1. Lecture Plan (Week 1 to {course_info['duration']}) 
           *(MUST be derived from RAG Reference Material if provided)*
        ## 2. Labs Content (Week by week)
           *(Integrate tools from Market Data here)*
        ## 3. Capstone Project (Specific & Industry-relevant)
        ## 4. Resources & References
        """

        return query_llm(sys_prompt, user_prompt)


class ArbitratorSlave:
    def __init__(self):
        self.role = "Quality Assurance & Hallucination Checker"

    def evaluate(self, market_data, current_draft, rag_context=None):
        system_instruction = "You are a ruthless Academic QA Judge evaluating an AI-generated curriculum."

        # Introduce RAG-checking logic into the QA agent
        rag_qa_prompt = ""
        if rag_context and len(rag_context) > 10:
            rag_qa_prompt = f"""
            ### 🚨 MANDATORY SOURCE DOCUMENT (RAG CONTEXT):
            {rag_context}

            EVALUATION CRITERIA 1: FAITHFULNESS TO SOURCE.
            Did the draft hallucinate topics? Are the lectures clearly grounded in the Mandatory Source Document above? 
            If the draft includes major theoretical concepts NOT present in the source document, PENALIZE the score heavily (Score < 70).
            """
        else:
            rag_qa_prompt = "No specific source document was provided. Evaluate based on logical academic progression."

        user_prompt = f"""
                ### JOB MARKET DATA (Expected Practical Tools):
                {market_data}

                {rag_qa_prompt}

                ### PROPOSED DRAFT TO EVALUATE:
                {current_draft}

                Task:
                1. RAG Check: Did the draft strictly follow the Source Document?
                2. Market Check: Are specific tools from the Job Market Data present in the Labs?
                3. Capstone Check: Is the Capstone project highly specific?
                4. Give a Score (0-100). If < 85, output a bulleted list of specific gaps to fix.

                Format response exactly as: SCORE: [0-100] | FEEDBACK: [Detailed critique]
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
        self.rag = RAGEngine()

    def run(self, course_data):
        status_log = []

        # --- Step 1: Market Research ---
        status_log.append("Slave 1: Scouting Job Market...")
        market_data = self.s1.research(course_data['title'], course_data['topics'])
        status_log.append("Market Data Synthesized.")

        # --- Step 2: RAG Retrieval ---
        status_log.append("Slave 4 (RAG): Querying Knowledge Base...")
        retrieval_query = f"{course_data['title']} {course_data['topics']} syllabus structure chapters theory"
        rag_context = self.rag.retrieve_context(retrieval_query)

        if rag_context and len(rag_context) > 50:
            status_log.append("✅ Relevant Academic Context Retrieved.")
        else:
            status_log.append("⚠️ No specific Local Context found. Relying on General Knowledge.")

        # --- Step 3: Iterative Drafting ---
        score = 0
        feedback = None
        iteration = 0
        max_attempts = 3  # Increased slightly to give the QA agent room to enforce RAG corrections
        draft = ""

        while score < 85 and iteration < max_attempts:
            iteration += 1
            status_log.append(f"--- Round {iteration} ---")

            if feedback:
                status_log.append("Slave 2: Refining based on Feedback...")
            else:
                status_log.append("Slave 2: Drafting Detailed Syllabus...")

            # PASS RAG CONTEXT TO DRAFTER
            draft = self.s2.draft_plan(
                course_info=course_data,
                market_data=market_data,
                rag_context=rag_context,
                feedback=feedback
            )

            status_log.append("Slave 3: Quality & Groundedness Check...")

            # 🚨 PASS RAG CONTEXT TO ARBITRATOR FOR VERIFICATION 🚨
            score, feedback = self.s3.evaluate(
                market_data=market_data,
                current_draft=draft,
                rag_context=rag_context
            )

            status_log.append(f"Score: {score}/100")

            if score < 85:
                status_log.append("Refining specific RAG/Market alignment...")

        status_log.append("Plan Finalized.")
        return draft, status_log

    def ingest_documents(self, file_path):
        return self.rag.ingest_file(file_path)