import os
import PyPDF2
import docx
import pytesseract
from PIL import Image
import openai
from django.conf import settings
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Configure OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)

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
    """Extract text from image using OCR"""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

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

def summarize_text(text, target_words=None, max_tokens=500):
    """Summarize text using OpenAI API, allowing target word count in prompt"""
    try:
        word_instruction = "" if not target_words else f" in approximately {int(target_words)} words"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text clearly and faithfully."},
                {"role": "user", "content": f"Summarize the following text{word_instruction}. Avoid omitting key points.\n\n{text}"}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

def generate_answers(text, target_words=None, max_tokens=500):
    """Generate answers using OpenAI API, allowing target word count in prompt"""
    try:
        word_instruction = "" if not target_words else f" in approximately {int(target_words)} words"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates accurate, well-structured answers."},
                {"role": "user", "content": f"Generate clear, step-by-step answers{word_instruction} to the following questions or content:\n\n{text}"}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating answers: {str(e)}"

def analyze_text(text, target_words=None, max_tokens=500):
    """Analyze text using OpenAI API, allowing target word count in prompt"""
    try:
        word_instruction = "" if not target_words else f" in approximately {int(target_words)} words"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes text and ranks topics by importance."},
                {"role": "user", "content": f"Analyze the following text, identify key insights, and rank topics by importance{word_instruction}.\n\n{text}"}
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