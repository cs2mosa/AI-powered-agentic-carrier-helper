from duckduckgo_search import DDGS
from pdf_generator import generate_course_plan_pdf
import re


# --- Tool 1: Internet Search ---
def search_market_requirements(query):
    """
    Searches for job requirements relevant to the course.
    """
    try:
        results = DDGS().text(f"{query} job requirements skills 2024 2025", max_results=5)
        summary = ""
        for r in results:
            summary += f"- {r['title']}: {r['body']}\n"
        return summary
    except Exception as e:
        return f"Search tool warning: {str(e)}. Using general knowledge."


# --- Tool 2: PDF Parsing & Bridge ---
def create_course_pdf(course_data, plan_text):
    """
    Converts the raw text from AI into the structured dict required by CMASPDFGenerator.
    Robustly handles different Markdown styles.
    """

    # 1. Prepare Base Metadata
    content_data = {
        'title': course_data['title'],
        'duration': f"{course_data['duration']} Weeks",
        'weekly_load': f"Lec: {course_data['lec']}h | Lab: {course_data['lab']}h",
        'sections': []
    }

    # 2. Parse the Markdown Text
    lines = plan_text.split('\n')

    # Initialize a default section in case the AI forgets the first header
    current_section = {
        'title': 'Course Overview',
        'content': []
    }

    # Flags to help parsing
    has_started_parsing = False

    for line in lines:
        raw_line = line
        line = line.strip()
        if not line: continue

        # --- CASE A: Main Sections (Starts with #) ---
        # Matches # Title, ## Title, or ### Title (if it looks like a main section)
        if line.startswith('# ') or (line.startswith('## ') and not has_started_parsing):
            clean_title = line.replace('#', '').strip()

            # Save the previous section if it has content
            if current_section and current_section['content']:
                content_data['sections'].append(current_section)

            # Start new section
            current_section = {
                'title': clean_title,
                'content': []
            }
            has_started_parsing = True
            continue

        # --- CASE B: Sub-Headers (Starts with ## or ### or bold **Text**) ---
        # We treat ##, ###, and **** as bold sub-headers in the PDF
        is_header = False
        clean_sub = ""

        if line.startswith('##') or line.startswith('###'):
            clean_sub = line.replace('#', '').strip()
            is_header = True
        elif line.startswith('**') and line.endswith('**') and len(line) < 60:
            # Detect bold lines acting as headers (e.g. **Week 1**)
            clean_sub = line.replace('*', '').strip()
            is_header = True

        if is_header:
            if current_section:
                current_section['content'].append({
                    'type': 'header',
                    'text': clean_sub
                })
            continue

        # --- CASE C: Bullet Points ---
        if line.startswith('- ') or line.startswith('* ') or line.startswith('• '):
            clean_item = re.sub(r'^[-*•]\s+', '', line).strip()
            # Remove bolding inside bullets for cleaner PDF
            clean_item = clean_item.replace('**', '')

            if current_section:
                current_section['content'].append({
                    'type': 'bullet',
                    'text': clean_item
                })
            continue

        # --- CASE D: Normal Text ---
        # If it's not a header or bullet, it's body text
        clean_text = line.replace('**', '')
        if current_section:
            current_section['content'].append({
                'type': 'text',
                'text': clean_text
            })

    # Append the last section
    if current_section and current_section['content']:
        content_data['sections'].append(current_section)

    # 3. Generate PDF
    # Sanitize filename
    safe_title = "".join([c for c in course_data['title'] if c.isalnum() or c in (' ', '-', '_')]).strip()
    filename = f"{safe_title}_Plan.pdf"

    generate_course_plan_pdf(filename, content_data)

    return filename