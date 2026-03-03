import streamlit as st
import time
import os
import shutil
import PyPDF2
from agents import MasterAgent, PDFParserAgent, InputExpanderAgent
from tools import create_course_pdf
from dotenv import load_dotenv

load_dotenv()

if "GROQ_API_KEY" not in os.environ:
    try:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    except FileNotFoundError:
        pass
    except KeyError:
        pass

if "GROQ_API_KEY" not in os.environ:
    st.error("🚨 GROQ_API_KEY is missing! Please set it in .env or .streamlit/secrets.toml")
    st.stop()

st.set_page_config(page_title="GAPLER - RAG Course Generator", layout="wide", page_icon="🎓")

UI = {
    "sb_guide_title": "📖 Quick Guide",
    "sb_steps": "**Steps:**\n1. (Optional) Upload Knowledge Base\n2. Enter course details\n3. Click Generate\n4. Download PDF",
    "sb_kb_title": "📚 Knowledge Base (RAG)",
    "sb_kb_info": "Upload textbooks, university guidelines, or accreditation standards here. The AI will use these as the 'Source of Truth'.",
    "sb_kb_btn": "📥 Ingest Documents",
    "sb_kb_success": "Knowledge Base Updated!",

    # Input Methods
    "method_manual": "Manual Entry",
    "method_pdf": "Fast Mode (Target Spec PDF)",

    # Headers
    "header_title": "🚀 GAPLER: AI-Powered Curriculum",
    "header_caption": "Generate market-aligned syllabi grounded in YOUR reference materials.",

    # Form Labels (Standard)
    "lbl_subject": "Core Subject",
    "ph_subject": "e.g. Advanced Computer Vision",
    "lbl_duration": "Duration (Weeks)",
    "lbl_hours": "Study Hours / Week",
    "lbl_lec": "Reading", "lbl_tut": "Tutorials", "lbl_lab": "Coding/Lab",
    "lbl_obj": "Career Objectives",
    "ph_obj": "e.g. Prepare for Senior AI Engineer role...",
    "lbl_topics": "Specific Topics",
    "ph_topics": "- Transformers\n- Diffusion Models...",
    "lbl_context": "Industry Focus",

    # Actions
    "btn_gen": "✨ Generate RAG-Enhanced Plan",
    "btn_auto": "✨ Auto-Complete",
    "err_fill": "⚠️ Please fill in Subject and Objectives.",
    "status_init": "🤖 AI Agents are working...",
    "status_rag": "🔍 Retrieving context from Knowledge Base...",
    "success_ready": "Roadmap Ready!",
    "tab_plan": "📄 Study Plan",
    "tab_pdf": "📥 Download PDF"
}

# --- SESSION STATE ---
if 'form_data' not in st.session_state:
    st.session_state['form_data'] = {
        "title": "", "duration": 12,
        "lec": 2, "tut": 1, "lab": 3,
        "obj": "", "know": "", "topics": "", "context": ""
    }

# --- CSS STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #262730; color: white; border: 1px solid #4f4f4f;
    }
    h1, h2, h3 { text-align: center !important; }
    .stButton>button { width: 100%; border-radius: 5px; }
    /* Success message style */
    .element-container:has(.stAlert) { margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)


# --- HELPER: RAG INGESTION ---
def process_knowledge_base(uploaded_files):
    """Handles file saving and ingestion into Vector Store"""
    if not uploaded_files:
        return

    # Create temp directory
    temp_dir = "temp_rag_docs"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    master_agent = MasterAgent()
    total_chunks = 0

    progress_bar = st.sidebar.progress(0)

    try:
        for i, file in enumerate(uploaded_files):
            # Save file to disk
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            # Ingest
            chunks = master_agent.ingest_documents(file_path)
            total_chunks += chunks

            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))

        st.sidebar.success(f"✅ Ingested {len(uploaded_files)} files ({total_chunks} chunks)")
    except Exception as e:
        st.sidebar.error(f"Ingestion Error: {e}")
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        time.sleep(2)
        progress_bar.empty()


# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### {UI['sb_guide_title']}")
    st.markdown(UI['sb_steps'])
    st.markdown("---")

    # --- KNOWLEDGE BASE SECTION (RAG) ---
    st.markdown(f"### {UI['sb_kb_title']}")
    st.info(UI['sb_kb_info'])

    kb_files = st.file_uploader(
        "Upload Reference PDFs",
        type="pdf",
        accept_multiple_files=True,
        key="rag_uploader"
    )

    if kb_files and st.button(UI['sb_kb_btn']):
        with st.spinner("Processing Knowledge Base..."):
            process_knowledge_base(kb_files)

    st.markdown("---")

    # Input Type Toggle
    st.markdown("### Input Method")
    input_method = st.radio("input_method_hidden", [UI["method_manual"], UI["method_pdf"]],
                            label_visibility="collapsed")
    is_pdf_mode = (input_method == UI["method_pdf"])

# --- MAIN CONTENT ---
st.title(UI["header_title"])
st.markdown(f"<div style='text-align: center; color: #a3a8b8; margin-bottom: 30px;'>{UI['header_caption']}</div>",
            unsafe_allow_html=True)

# --- MODE: PDF PARSING (TARGET SPEC) ---
if is_pdf_mode:
    st.info(f"💡 {UI['method_pdf']}: Upload the course specification you want to build/improve.")
    uploaded_file = st.file_uploader("Upload Target Spec (PDF)", type="pdf")

    if uploaded_file and st.button("⚡ Analyze & Auto-Fill"):
        with st.spinner("Reading PDF..."):
            try:
                reader = PyPDF2.PdfReader(uploaded_file)
                text = "".join([p.extract_text() for p in reader.pages])
                parser = PDFParserAgent()
                data = parser.extract_course_details(text)
                if data:
                    st.session_state['form_data'].update(data)
                    # Ensure numeric types
                    st.session_state['form_data']['duration'] = int(data.get('duration', 12))
                    st.success("Form auto-filled from PDF.")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading PDF: {e}")

# --- MODE: MANUAL ENTRY ---
else:
    st.subheader("🎯 Define Learning Goal")

    # Subject & Auto-Complete
    col_title, col_btn = st.columns([4, 1], vertical_alignment="bottom")
    with col_title:
        course_title = st.text_input(UI["lbl_subject"],
                                     value=st.session_state['form_data']['title'],
                                     placeholder=UI["ph_subject"])
    with col_btn:
        if st.button(UI["btn_auto"]):
            if not course_title:
                st.warning("Enter a subject first.")
            else:
                with st.spinner("✨ Expanding..."):
                    expander = InputExpanderAgent()
                    data = expander.expand_topic(course_title)
                    if data:
                        st.session_state['form_data'].update(data)
                        st.session_state['form_data']['title'] = course_title
                        st.rerun()

    # Detailed Inputs
    c1, c2 = st.columns(2)
    with c1:
        duration = st.number_input(UI["lbl_duration"], min_value=1, value=st.session_state['form_data']['duration'])
        st.markdown(f"**{UI['lbl_hours']}**")
        h1, h2, h3 = st.columns(3)
        lec = h1.number_input(UI["lbl_lec"], min_value=1, value=st.session_state['form_data']['lec'])
        tut = h2.number_input(UI["lbl_tut"], min_value=0, value=st.session_state['form_data']['tut'])
        lab = h3.number_input(UI["lbl_lab"], min_value=0, value=st.session_state['form_data']['lab'])

    with c2:
        objectives = st.text_area(UI["lbl_obj"], value=st.session_state['form_data']['obj'], height=140)

    topics = st.text_area(UI["lbl_topics"], value=st.session_state['form_data']['topics'], height=100)
    context = st.text_input(UI["lbl_context"], value=st.session_state['form_data']['context'])

# --- GENERATION LOGIC ---
st.markdown("---")
if st.button(UI["btn_gen"], type="primary"):
    # Validation
    title_to_use = course_title if not is_pdf_mode else st.session_state['form_data']['title']
    obj_to_use = objectives if not is_pdf_mode else st.session_state['form_data']['obj']

    if not title_to_use or not obj_to_use:
        st.warning(UI["err_fill"])
    elif "PASTE_YOUR" in os.environ.get("GROQ_API_KEY", ""):
        st.error("🚨 Please set the GROQ_API_KEY environment variable.")
    else:
        # Prepare Data
        course_data = {
            "title": title_to_use,
            "duration": duration if not is_pdf_mode else st.session_state['form_data']['duration'],
            "lec": lec if not is_pdf_mode else st.session_state['form_data']['lec'],
            "tut": tut if not is_pdf_mode else st.session_state['form_data']['tut'],
            "lab": lab if not is_pdf_mode else st.session_state['form_data']['lab'],
            "topics": topics if not is_pdf_mode else st.session_state['form_data']['topics'],
            "objectives": obj_to_use + f" ({context})",
            "language": "English"
        }

        # UI Progress Setup
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text(UI["status_init"])

        # Instantiate Master Agent (This loads RAG engine)
        master = MasterAgent()

        try:
            # Run Agent Workflow
            final_plan, logs = master.run(course_data)

            # Animate Logs
            for i, log in enumerate(logs):
                time.sleep(0.3)
                prog = min(95, 10 + (i * 15))
                progress_bar.progress(prog)
                status_text.text(f"🤖 {log}")

            progress_bar.progress(100)
            status_text.success(UI["success_ready"])

            # Display Results
            st.success(f"Plan generated for: {course_data['title']}")

            tab1, tab2 = st.tabs([UI["tab_plan"], UI["tab_pdf"]])

            with tab1:
                st.markdown(final_plan)

            with tab2:
                # Generate PDF using the existing tool
                pdf_file = create_course_pdf(course_data, final_plan)
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="Download PDF Plan",
                        data=f,
                        file_name=pdf_file,
                        mime="application/pdf"
                    )

        except Exception as e:
            st.error(f"Generation Error: {str(e)}")
            st.warning("Check if Groq API Key is valid and RAG dependencies are installed.")