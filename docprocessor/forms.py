from django import forms
from .models import Document, YouTubeVideo

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'processing_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'processing_type': forms.Select(attrs={'class': 'form-select'}),
        }

class YouTubeURLForm(forms.ModelForm):
    class Meta:
        model = YouTubeVideo
        fields = ['url']
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter YouTube URL'}),
        }

class TranslationForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
    source_language = forms.ChoiceField(
        choices=[
            ('auto', 'Auto-detect'),
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German'),
            ('zh', 'Chinese'),
            ('ja', 'Japanese'),
            ('ko', 'Korean'),
            ('hi', 'Hindi'),
            ('ar', 'Arabic'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    target_language = forms.ChoiceField(
        choices=[
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German'),
            ('zh', 'Chinese'),
            ('ja', 'Japanese'),
            ('ko', 'Korean'),
            ('hi', 'Hindi'),
            ('ar', 'Arabic'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )