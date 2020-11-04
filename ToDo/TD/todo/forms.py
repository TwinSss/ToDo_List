from django import forms

class TodoForm(forms.Form):
    text = forms.CharField(max_length=40, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your tasks e.g. "Go to the gym at 5 PM"', 'aria-label': 'Todo', 'aria-describedby': 'add-btn'}
    ))