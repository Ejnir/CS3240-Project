from django import forms
from .models import CommonUser, Project, ProjectFile, ProjectMessage
from taggit.forms import TagField, TagWidget
import json
import re

class ProjectForm(forms.ModelForm):
    event_date = forms.DateTimeField(
        required=False, 
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    sport_type = forms.ChoiceField(
        choices=Project.SPORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    skill_level = forms.ChoiceField(
        choices=Project.SKILL_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Optional: Select the required skill level for the event."
    )
    zip_code = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 22903'}),
        help_text="Optional: Enter a broad zip code for the event location."
    )
    venue = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Main Stadium'}),
        help_text="Optional: Specify the venue for the event."
    )

    class Meta:
        model = Project
        fields = ['title', 'description', 'event_date', 'sport_type', 'skill_level', 'zip_code', 'venue']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

class ProjectFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFile
        fields = ['file', 'title', 'description', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Add tags separated by commas',
                'data-role': 'tagsinput'
            }),
        }

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')

        if not tags:
            return ""

        try:
            # Very ugly fix for taggit doing some very strange stuff
            if isinstance(tags, list):
                meaningful_tags = [tag for tag in tags if tag and tag not in [':', '[{', 'value', '{', '}', '}]']]
                return ','.join(meaningful_tags)
            
            if isinstance(tags, str):
                tags = tags.strip('[]{}()')
                tag_list = [tag.strip('"{} ') for tag in re.split('[,\s]+', tags) if tag.strip('"{} ')]
                
                return ','.join(tag_list)
            
            return str(tags)
        
        except Exception as e:
            print("Error processing tags:", e)
            raise forms.ValidationError(f"Invalid tag format: {e}")

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            allowed_types = ['.txt', '.pdf', '.jpg', '.jpeg']
            if not any(file.name.lower().endswith(ext) for ext in allowed_types):
                raise forms.ValidationError('Invalid file type. Allowed types are .txt, .pdf, .jpg, .jpeg')
        return file

class ProjectMessageForm(forms.ModelForm):
    class Meta:
        model = ProjectMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }