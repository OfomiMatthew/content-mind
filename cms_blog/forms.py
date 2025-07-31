from django import forms 
from .models import Comment

class EmailPostForm(forms.Form):
  name = forms.CharField(max_length=50)
  email = forms.EmailField()
  to = forms.EmailField()
  comments = forms.CharField(required=False,widget=forms.Textarea)
  
class CommentForm(forms.ModelForm):
  class Meta:
    model = Comment
    fields = ['name','email','body']
    
    
class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100, required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'Search posts...'}))