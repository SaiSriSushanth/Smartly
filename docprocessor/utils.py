import os
import PyPDF2
import docx
import pytesseract
from PIL import Image, ImageOps, ImageFilter
import openai
from django.conf import settings
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Configure OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)

# Configure Tesseract OCR binary path if provided via env or settings
_tesseract_cmd = os.getenv('TESSERACT_CMD') or getattr(settings, 'TESSERACT_CMD', None)
if _tesseract_cmd:
    try:
        pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd
    except Exception:
        # Silently ignore misconfig; we'll surface a clearer error during use
        pass

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_image(file_path):
    """Extract text from image using OCR with light preprocessing.
    - Supports JPG/PNG and similar raster formats.
    - Applies grayscale + contrast + slight sharpening to improve OCR.
    - Uses page segmentation mode suitable for blocks of text.
    """
    try:
        image = Image.open(file_path)
        # Convert to grayscale and lightly enhance contrast
        img = ImageOps.grayscale(image)
        img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=150, threshold=3))
        # Optional light normalization for very dark or bright scans
        img = ImageOps.autocontrast(img, cutoff=2)

        # Use an OCR configuration tuned for uniform text blocks
        ocr_config = "--psm 6"
        text = pytesseract.image_to_string(img, config=ocr_config)
        return text.strip()
    except pytesseract.TesseractNotFoundError:
        return (
            "OCR not available: Tesseract binary not found. "
            "Install Tesseract OCR and set TESSERACT_CMD to its path (e.g., "
            "C:\\Program Files\\Tesseract-OCR\\tesseract.exe on Windows)."
        )
    except Exception as e:
        return f"Error extracting text from image: {str(e)}"

def extract_text_from_file(file_path, file_type):
    """Extract text from file based on file type"""
    if file_type == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_type == 'docx':
        return extract_text_from_docx(file_path)
    elif file_type == 'image':
        return extract_text_from_image(file_path)
    elif file_type == 'txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        return "Unsupported file type"

def get_youtube_video_id(url):
    """Extract YouTube video ID from URL"""
    youtube_regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(youtube_regex, url)
    return match.group(1) if match else None

def get_youtube_transcript(video_id):
    """Get transcript from YouTube video"""
    try:
        # Create an instance of the API and use the fetch method
        transcript_api = YouTubeTranscriptApi()
        fetched_transcript = transcript_api.fetch(video_id)
        # Convert to raw data and extract text
        transcript = ' '.join([item['text'] for item in fetched_transcript.to_raw_data()])
        return transcript
    except Exception as e:
        return f"Error getting transcript: {str(e)}"

def summarize_text(text, target_words=None, max_tokens=500, preset=None):
    """Summarize text using OpenAI API with optional preset formatting."""
    try:
        word_instruction = "" if not target_words else f" in approximately {int(target_words)} words"
        preset_instruction = ""
        if preset == 'bullet_points':
            preset_instruction = "Format strictly as a markdown bullet list. Use '-' at the start of each line. No introduction or conclusion. Keep bullets concise and study-friendly."
        elif preset == 'detailed_summary':
            preset_instruction = " Provide a comprehensive paragraph-style summary."
        elif preset == 'study_notes':
            preset_instruction = " Produce study notes: headings for topics, sub-bullets for key concepts and definitions."
        elif preset == 'brief_summary':
            preset_instruction = " Keep it brief for quick revision."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text clearly and faithfully."},
                {"role": "user", "content": f"Summarize the following text{word_instruction} and {preset_instruction} Avoid omitting key points.\n\n{text}"}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

def generate_answers(text, target_words=None, max_tokens=500, preset=None):
    """Generate answers using OpenAI API with optional preset type."""
    try:
        word_instruction = "" if not target_words else f" in approximately {int(target_words)} words"
        preset_instruction = ""
        if preset == 'exam_answers':
            preset_instruction = " Generate comprehensive, step-by-step exam answers. Use numbered steps and short headings for clarity."
        elif preset == 'practice_questions':
            preset_instruction = " Create 6-10 practice questions with detailed answers. Format as a numbered list where each item contains 'Q:' followed by the question and 'A:' followed by the answer."
        elif preset == 'study_plan':
            preset_instruction = " Draft a personalized study schedule. Use a bullet list grouped by days/weeks with time blocks and goals."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates accurate, well-structured answers."},
                {"role": "user", "content": f"Generate clear, step-by-step answers{word_instruction} to the following questions or content.{preset_instruction}\n\n{text}"}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating answers: {str(e)}"

def analyze_text(text, target_words=None, max_tokens=500, preset=None):
    """Analyze text using OpenAI API with optional preset for analysis type."""
    try:
        word_instruction = "" if not target_words else f" in approximately {int(target_words)} words"
        preset_instruction = ""
        if preset == 'question_patterns':
            preset_instruction = " Identify recurring question patterns and topics. Output a bullet list. For each pattern, include a short label and 1-2 example phrasings."
        elif preset == 'predict_questions':
            preset_instruction = " Predict likely exam questions based on the content. Output as a numbered list of questions only, optionally include one-sentence rationale per item."
        elif preset == 'topic_importance':
            preset_instruction = " Rank topics by exam importance as a numbered list from most to least important, with a brief justification for each."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes text and ranks topics by importance."},
                {"role": "user", "content": f"Analyze the following text, identify key insights, and rank topics by importance{word_instruction}.{preset_instruction}\n\n{text}"}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing text: {str(e)}"

def translate_text(text, target_language, source_language='auto', max_tokens=500):
    """Translate text using OpenAI API"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates text."},
                {"role": "user", "content": f"Please translate the following text from {source_language} to {target_language}:\n\n{text}"}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error translating text: {str(e)}"

def chat_with_openai(messages, system_prompt=None, model="gpt-3.5-turbo", max_tokens=800):
    """Generic chat helper using OpenAI ChatCompletion.
    - messages: list of dicts with roles and content
    - system_prompt: optional system message to guide behavior
    """
    try:
        final_messages = []
        if system_prompt:
            final_messages.append({"role": "system", "content": system_prompt})
        final_messages.extend(messages)
        response = openai.ChatCompletion.create(
            model=model,
            messages=final_messages,
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error chatting with OpenAI: {str(e)}"