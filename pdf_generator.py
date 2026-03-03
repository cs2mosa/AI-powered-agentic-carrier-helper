"""
PDF Generator for CMAS Course Plans
Supports both English and Arabic with proper text rendering
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import arabic_reshaper
from bidi.algorithm import get_display


class CMASPDFGenerator:
    """Generator for CMAS Course Plan PDFs with English and Arabic support"""

    def __init__(self):
        """Initialize the PDF generator with styles and fonts"""
        self.styles = getSampleStyleSheet()
        self._setup_arabic_fonts()
        self._create_custom_styles()

    def _setup_arabic_fonts(self):
        """Register Arabic fonts for proper text rendering"""
        try:
            # We attempt to download a known Arabic font if system fonts aren't found
            # (Added this fallback logic to ensure it works on cloud/streamlit share)
            font_path = "Amiri-Regular.ttf"
            if not os.path.exists(font_path):
                import urllib.request
                url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
                urllib.request.urlretrieve(url, font_path)

            pdfmetrics.registerFont(TTFont('Arabic', font_path))
            pdfmetrics.registerFont(TTFont('Arabic-Bold', font_path))
        except Exception as e:
            print(f"Warning: Could not register Arabic font: {e}")

    def _create_custom_styles(self):
        """Create custom paragraph styles for the document"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CMASTitle',
            parent=self.styles['Title'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CMASSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#4a4a4a'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='CMASHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#1a1a1a'),
            spaceBefore=12,
            spaceAfter=8,
            fontName='Helvetica-Bold',
            leftIndent=0
        ))

        # Subheader style
        self.styles.add(ParagraphStyle(
            name='CMASSubheader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2a2a2a'),
            spaceBefore=8,
            spaceAfter=6,
            fontName='Helvetica-Bold',
            leftIndent=0
        ))

        # Body text style
        self.styles.add(ParagraphStyle(
            name='CMASBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#3a3a3a'),
            spaceAfter=6,
            fontName='Helvetica',
            leftIndent=0,
            leading=14
        ))

        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='CMASBullet',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#3a3a3a'),
            spaceAfter=4,
            fontName='Helvetica',
            leftIndent=20,
            bulletIndent=10,
            leading=14
        ))

        # Arabic styles (right-to-left alignment)
        self.styles.add(ParagraphStyle(
            name='ArabicTitle',
            parent=self.styles['CMASTitle'],
            fontName='Arabic-Bold',
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='ArabicSubtitle',
            parent=self.styles['CMASSubtitle'],
            fontName='Arabic',
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='ArabicHeader',
            parent=self.styles['CMASHeader'],
            fontName='Arabic-Bold',
            alignment=TA_RIGHT
        ))

        self.styles.add(ParagraphStyle(
            name='ArabicSubheader',
            parent=self.styles['CMASSubheader'],
            fontName='Arabic-Bold',
            alignment=TA_RIGHT
        ))

        self.styles.add(ParagraphStyle(
            name='ArabicBody',
            parent=self.styles['CMASBody'],
            fontName='Arabic',
            alignment=TA_RIGHT
        ))

        self.styles.add(ParagraphStyle(
            name='ArabicBullet',
            parent=self.styles['CMASBullet'],
            fontName='Arabic',
            alignment=TA_RIGHT,
            rightIndent=20,
            bulletIndent=10
        ))

    def _process_arabic_text(self, text):
        """Process Arabic text for proper display (right-to-left)"""
        if not text:
            return text
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except:
            return text

    def _is_arabic(self, text):
        """Check if text contains Arabic characters"""
        if not text:
            return False
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        return arabic_chars > len(text) * 0.3

    def _create_header_footer(self, canvas, doc, page_num, is_arabic=False):
        """Add header and footer to each page"""
        canvas.saveState()
        width, height = letter

        # Footer
        footer_text = f"صفحة {page_num}" if is_arabic else f"Page {page_num}"

        # We need to register font for canvas usage as well if arabic
        if is_arabic:
            canvas.setFont('Arabic', 9)
            footer_text = self._process_arabic_text(footer_text)
        else:
            canvas.setFont('Helvetica', 9)

        canvas.drawCentredString(width / 2, 0.5 * inch, footer_text)

        # Header
        if page_num == 1:
            header_text = "خطة دورة متوافقة مع السوق" if is_arabic else "Market-Aligned Course Plan"
            if is_arabic:
                canvas.setFont('Arabic', 10)
                header_text = self._process_arabic_text(header_text)
            else:
                canvas.setFont('Helvetica', 10)

            canvas.drawCentredString(width / 2, height - 0.5 * inch, header_text)

        canvas.restoreState()

    def generate_pdf(self, output_path, content_data):
        """Generate a PDF file based on the content data"""
        # Detect if content is in Arabic
        is_arabic = self._is_arabic(content_data.get('title', ''))

        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        story = []

        # Title Data
        title = content_data.get('title', 'Course Plan')
        duration = content_data.get('duration', '15 Weeks')
        weekly_load = content_data.get('weekly_load', 'Lec: 2h | Lab: 3h')

        if is_arabic:
            title = self._process_arabic_text(title)
            style_title = self.styles['ArabicTitle']
            style_subtitle = self.styles['ArabicSubtitle']
        else:
            style_title = self.styles['CMASTitle']
            style_subtitle = self.styles['CMASSubtitle']

        # Add Title
        story.append(Paragraph(title, style_title))

        # Add Subtitle details
        details = f"<br/>{duration}<br/>{weekly_load}"
        if is_arabic:
            details = self._process_arabic_text(details)
        story.append(Paragraph(details, style_subtitle))

        # Add Spacer
        story.append(Spacer(1, 0.3 * inch))

        # Add Sections
        sections = content_data.get('sections', [])
        for section_idx, section in enumerate(sections):
            if section_idx > 0:
                story.append(PageBreak())

            section_title = section.get('title', '')

            # Determine Styles
            if is_arabic:
                section_title = self._process_arabic_text(section_title)
                header_style = self.styles['ArabicHeader']
                subheader_style = self.styles['ArabicSubheader']
                body_style = self.styles['ArabicBody']
                bullet_style = self.styles['ArabicBullet']
            else:
                header_style = self.styles['CMASHeader']
                subheader_style = self.styles['CMASSubheader']
                body_style = self.styles['CMASBody']
                bullet_style = self.styles['CMASBullet']

            # Section Header
            story.append(Paragraph(section_title, header_style))
            story.append(Spacer(1, 0.1 * inch))

            # Content items
            content_items = section.get('content', [])
            for item in content_items:
                item_type = item.get('type', 'text')
                item_text = item.get('text', '')

                if is_arabic:
                    item_text = self._process_arabic_text(item_text)

                if item_type == 'header':
                    story.append(Paragraph(item_text, subheader_style))
                elif item_type == 'text':
                    story.append(Paragraph(item_text, body_style))
                elif item_type == 'bullet':
                    story.append(Paragraph(item_text, bullet_style))

        # Build
        page_num = [1]

        def add_page_elements(canvas, doc):
            self._create_header_footer(canvas, doc, page_num[0], is_arabic)
            page_num[0] += 1

        doc.build(story, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
        return output_path


def generate_course_plan_pdf(output_path, content_data):
    """Entry point"""
    generator = CMASPDFGenerator()
    return generator.generate_pdf(output_path, content_data)