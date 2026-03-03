# 🎓 AlignEd: Career Market-Aligned Syllabus Generator

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**An AI-powered multi-agent system that generates market-aligned course plans tailored to current industry demands**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Bilingual Support](#-bilingual-support)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 🌟 Overview

**AlignEd (Career Market-Aligned Syllabus)** is an intelligent educational planning system that bridges the gap between academic curricula and real-world job market requirements. Using a sophisticated multi-agent AI architecture, AlignEd analyzes current industry trends, researches job market demands, and generates comprehensive course plans that prepare students for actual career opportunities.

### Why AlignEd?

- **Market-Driven**: Automatically researches current job requirements and industry trends
- **AI-Powered**: Multi-agent system with specialized roles (Market Research, Curriculum Design, Quality Assurance)
- **Bilingual**: Full support for English and Arabic (RTL layout included)
- **PDF Generation**: Professional course plans exported as formatted PDFs
- **Time-Saving**: Reduces curriculum planning from days to minutes
- **Student-Focused**: Designed for self-learners, educators, and institutions

---

## ✨ Features

### 🤖 Multi-Agent System
- **Market Researcher Agent**: Scrapes real-time job postings and analyzes skill demands
- **Curriculum Designer Agent**: Creates detailed week-by-week course plans
- **Quality Assurance Agent**: Validates alignment with market needs
- **Master Orchestrator**: Coordinates all agents for optimal results

### 📊 Intelligent Course Planning
- Week-by-week lecture breakdowns
- Hands-on lab exercises with specific tools/frameworks
- Industry-aligned capstone projects
- Curated learning resources
- Prerequisites and learning objectives

### 🌍 Bilingual Interface
- **English**: Professional academic tone
- **Arabic**: Modern Standard Arabic (فصحى معاصرة) with RTL support
- Auto-detection of language preferences
- Bilingual technical terms (e.g., "الشبكات العصبية (Neural Networks)")

### 📄 Advanced PDF Generation
- Professional formatting with custom styles
- Arabic text rendering with proper BiDi algorithm
- Multi-page layouts with headers/footers
- Downloadable course plans

### 🚀 Two Input Modes
1. **Manual Entry**: Step-by-step form with AI auto-complete
2. **Fast Mode**: Upload existing syllabus PDF for instant analysis

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                       │
│           (Bilingual Interface + Form Controls)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Master Agent                              │
│              (Orchestration & Control)                       │
└──────┬──────────────────┬──────────────────┬────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────────┐
│   Market    │  │  Curriculum  │  │   Arbitrator     │
│   Research  │  │   Designer   │  │  (QA & Review)   │
│   Agent     │  │    Agent     │  │     Agent        │
└──────┬──────┘  └──────┬───────┘  └──────┬───────────┘
       │                │                  │
       ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      Tool Layer                              │
│   • Web Search (DuckDuckGo)                                  │
│   • PDF Parser (PyPDF2)                                      │
│   • PDF Generator (ReportLab)                                │
│   • LLM Interface (Groq/Llama 3.3)                           │
└─────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

| Agent | Role | Key Functions |
|-------|------|---------------|
| **InputExpanderAgent** | Academic Advisor | Auto-completes course metadata from minimal input |
| **PDFParserAgent** | Document Analyzer | Extracts structured data from uploaded PDFs |
| **MarketSlave** | Market Researcher | Searches job boards for current skill demands |
| **CurriculumSlave** | Curriculum Designer | Generates detailed week-by-week syllabus |
| **ArbitratorSlave** | Quality Controller | Validates market alignment and completeness |
| **MasterAgent** | Orchestrator | Coordinates all agents and manages workflow |

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Groq API key ([Get one here](https://console.groq.com))

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/AlignEd-course-generator.git
cd GAPLER-course-generator
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

**⚠️ Security Note**: Never commit your `.env` file. Add it to `.gitignore`.

---

## ⚙️ Configuration

### API Key Setup

1. Visit [Groq Console](https://console.groq.com)
2. Create an account and generate an API key
3. Add the key to your `.env` file or directly in `app.py` (line 10) - **NOT recommended for production**

### Customizing the System

#### Modify LLM Model
In `agents.py`, change the model parameter:

```python
model="llama-3.3-70b-versatile"  # Current
# Options: llama-3.1-8b-instant, mixtral-8x7b-32768
```

#### Adjust Search Results
In `tools.py`, modify the search depth:

```python
results = DDGS().text(query, max_results=5)  # Increase for more data
```

#### Customize PDF Styles
In `pdf_generator.py`, modify the `_create_custom_styles()` method:

```python
fontSize=14,  # Adjust font sizes
textColor=colors.HexColor('#1a1a1a'),  # Change colors
```

---

## 💻 Usage

### Running the Application

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

### Manual Entry Mode

1. **Select Language**: Choose English or العربية in the sidebar
2. **Enter Core Subject**: e.g., "Machine Learning for Healthcare"
3. **Click Auto-Complete** (optional): AI fills in duration, topics, and objectives
4. **Customize Details**:
   - Course Code (e.g., CS401)
   - Duration (weeks)
   - Weekly hours (Lecture/Tutorial/Lab)
   - Career objectives
   - Prerequisites
   - Specific topics
   - Industry focus
5. **Generate Plan**: Click "Generate Personalized Study Plan"
6. **Review & Download**: View in browser or download PDF

### Fast Mode (PDF Upload)

1. **Toggle Input Method**: Select "Fast Mode" in sidebar
2. **Upload PDF**: Drag and drop an existing course specification
3. **Auto-Fill**: System extracts metadata automatically
4. **Generate**: Click to create enhanced version

### Example Use Cases

#### For Students
```
Subject: Full Stack Web Development
Objectives: Get hired as a Junior Developer at a startup
Duration: 16 weeks
Focus: React, Node.js, MongoDB, deployment
```

#### For Educators
```
Subject: Data Structures and Algorithms
Code: CS202
Duration: 15 weeks
Focus: Prepare students for technical interviews at FAANG
```

#### For Bootcamps
```
Subject: Cybersecurity Fundamentals
Duration: 12 weeks
Focus: Industry certifications (CEH, CompTIA Security+)
Industry: Banking and Financial Services
```

---

## 📁 Project Structure

```
GAPLER-course-generator/
│
├── app.py                    # Main Streamlit application
├── agents.py                 # Multi-agent system implementation
├── tools.py                  # Utility functions (search, PDF bridge)
├── pdf_generator.py          # PDF creation with ReportLab
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .env                      # Environment variables (not in repo)
├── .gitignore               # Git ignore rules
│
├── generated_pdfs/           # Output directory (auto-created)
│   └── GAPLER_*.pdf           # Generated course plans
│
└── assets/                   # UI assets (optional)
    └── logo.png
```

### File Descriptions

| File | Purpose | Key Components |
|------|---------|----------------|
| `app.py` | Main UI & routing | Streamlit interface, session management, bilingual UI |
| `agents.py` | AI logic | LLM wrapper, 6 agent classes, orchestration logic |
| `tools.py` | External integrations | Web search, PDF parsing, format conversion |
| `pdf_generator.py` | Document creation | ReportLab styling, Arabic rendering, BiDi support |
| `requirements.txt` | Dependencies | All required Python packages |

---

## 🔌 API Reference

### Core Functions

#### `query_llm(system_instruction, user_prompt)`
Sends prompts to Groq API and returns responses.

**Parameters:**
- `system_instruction` (str): Sets the AI's role and behavior
- `user_prompt` (str): The actual query

**Returns:** str - AI-generated response

**Example:**
```python
response = query_llm(
    "You are a curriculum expert",
    "Design a 10-week Python course"
)
```

---

#### `search_market_requirements(query)`
Performs web search for job market data.

**Parameters:**
- `query` (str): Search topic (e.g., "Data Scientist")

**Returns:** str - Formatted search results

**Example:**
```python
market_data = search_market_requirements("Machine Learning Engineer")
```

---

#### `generate_course_plan_pdf(output_path, content_data)`
Creates a professional PDF from structured data.

**Parameters:**
- `output_path` (str): File path for the PDF
- `content_data` (dict): Course data in the required format

**Content Data Structure:**
```python
{
    'title': 'Course Name',
    'course_code': 'CS101',
    'duration': '15 Weeks',
    'weekly_load': 'Lec: 3h | Lab: 2h',
    'sections': [
        {
            'title': 'Lecture Plan',
            'content': [
                {'type': 'header', 'text': 'Week 1'},
                {'type': 'text', 'text': 'Introduction to...'},
                {'type': 'bullet', 'text': 'Topic detail'}
            ]
        }
    ]
}
```

---

### Agent Methods

#### `InputExpanderAgent.expand_topic(topic, language)`
Auto-completes course details from minimal input.

**Parameters:**
- `topic` (str): Subject to expand
- `language` (str): "English" or "Arabic"

**Returns:** dict - Complete course metadata

---

#### `MasterAgent.run(course_data)`
Orchestrates all agents to generate the final plan.

**Parameters:**
- `course_data` (dict): Initial course information

**Returns:** tuple - (final_plan_text, status_logs)

---

## 🌍 Bilingual Support

### Arabic Features

- **Right-to-Left Layout**: Proper RTL text alignment
- **Arabic Reshaping**: Uses `arabic-reshaper` for correct character joining
- **BiDi Algorithm**: Implements Unicode bidirectional algorithm
- **Custom Fonts**: Amiri font for professional Arabic typography
- **Mixed Content**: Handles Arabic text with English technical terms

### Language Detection

The system automatically detects Arabic content using character analysis:

```python
def _is_arabic(self, text):
    arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
    return arabic_chars > len(text) * 0.3
```

### Adding New Languages

To add support for another language:

1. Add translations to `UI_TEXT` dictionary in `app.py`
2. Register appropriate fonts in `pdf_generator.py`
3. Add text direction CSS rules if needed
4. Update agent prompts in `agents.py`

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Reporting Issues

1. Check existing issues first
2. Provide detailed description
3. Include error messages and screenshots
4. Specify your environment (OS, Python version)

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Update README for new features
- Test with both English and Arabic
- Ensure PDF generation works on different platforms

---

## 🐛 Troubleshooting

### Common Issues

#### API Key Errors
```
Error: Groq API Key missing
```
**Solution**: Set `GROQ_API_KEY` in `.env` file or environment variables

---

#### Font Not Found (Arabic)
```
Warning: Could not register Arabic font
```
**Solution**: The system auto-downloads Amiri font. Check internet connection.

---

#### PDF Generation Fails
```
Error: Permission denied writing PDF
```
**Solution**: Ensure write permissions in the project directory

---

#### Search Tool Timeout
```
Search tool warning: Connection timeout
```
**Solution**: Check internet connection. System falls back to general knowledge.

---

#### Streamlit Port Already in Use
```
Error: Address already in use
```
**Solution**: 
```bash
streamlit run app.py --server.port 8502
```

---

### Debug Mode

Enable detailed logging:

```python
# In agents.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 Performance Tips

1. **Reduce API Calls**: Use cached results for similar queries
2. **Optimize Search**: Limit `max_results` in `search_market_requirements()`
3. **PDF Caching**: Store generated PDFs to avoid regeneration
4. **Session State**: Leverage Streamlit's session state for data persistence

---

## 🔐 Security Best Practices

- ✅ Never commit API keys to version control
- ✅ Use environment variables for sensitive data
- ✅ Implement rate limiting for API calls
- ✅ Validate user inputs before processing
- ✅ Sanitize file uploads (PDF mode)

---

## 📈 Future Roadmap

- [ ] Integration with more LLM providers (OpenAI, Anthropic)
- [ ] Real-time collaboration features
- [ ] Course analytics dashboard
- [ ] Integration with LMS platforms (Moodle, Canvas)
- [ ] Mobile app version
- [ ] More language support (French, Spanish, Chinese)
- [ ] AI-powered course recommendation engine
- [ ] Student progress tracking

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Groq** for providing fast LLM inference
- **Streamlit** for the amazing web framework
- **DuckDuckGo** for privacy-respecting search
- **ReportLab** for PDF generation capabilities
- **Anthropic** for Claude AI assistance in development

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/GAPLER-course-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/GAPLER-course-generator/discussions)
- **Email**: your.email@example.com

---

<div align="center">

**Made with ❤️ for educators and lifelong learners**

⭐ Star this repo if you find it helpful!

</div>
