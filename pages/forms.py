from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"placeholder": "Name"}))
    email = forms.CharField(max_length=256, widget=forms.TextInput(attrs={"type": "email", "placeholder": "Email"}))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Message'}))