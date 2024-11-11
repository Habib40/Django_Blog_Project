from django import forms
from .models import Comment,NewsletterSubscription

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment  # Use 'model' instead of 'Model'
        fields = ['message','parent']  # Specify the fields to include in the form

    message = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 30, 'rows': 5, 'class': 'form-control'}),
        label='Message *',
        required=True
    )
    
    
class SubscriptionForm(forms.ModelForm):
    email = forms.EmailField(
        error_messages={
            'required': 'Please enter an email address.',
            'invalid': 'Please enter a valid email address.'
        }
    )

    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Your Email'})
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check for the presence of '@'
        if '@' not in email:
            raise forms.ValidationError('Please enter a valid email address, including "@" symbol.')

        # Split the email into local and domain parts
        try:
            local_part, domain_part = email.split('@')
            if not local_part:
                raise forms.ValidationError('The email must have a local part before the "@" symbol.')
            if '.' not in domain_part:
                raise forms.ValidationError('The domain part must contain a "." character.')
            if domain_part.startswith('.') or domain_part.endswith('.'):
                raise forms.ValidationError('The domain part cannot start or end with a "." character.')

            # Check if 'm' and 'o' are present in the email
            if 'm' not in email:
                raise forms.ValidationError('The email address must contain "m".')
            if 'o' not in email:
                raise forms.ValidationError('The email address must contain "o".')

        except ValueError:
            raise forms.ValidationError('Please enter a valid email address format.')

        return email