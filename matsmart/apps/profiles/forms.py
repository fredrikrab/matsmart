from django.forms import CharField, ImageField
from django.contrib.auth.forms import User, UserCreationForm
from django.forms import ModelForm, Textarea
from .models import UserProfile

class UserProfileCreationForm(UserCreationForm):
    description = CharField(max_length=100)
    profile_picture = ImageField(required=False, initial='profiles/placeholder.png')

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
    
    def save(self, commit=True):
        user = super(UserProfileCreationForm, self).save()

        description_submission = self.cleaned_data['description']
        profile_picture_submission = self.cleaned_data['profile_picture']
        user_profile = UserProfile(user=user,
            description=description_submission,
            profile_picture = profile_picture_submission
            )
        user_profile.save()
        return user_profile

    def __init__(self, *args, **kwargs):
        super(UserProfileCreationForm, self).__init__(*args, **kwargs)
        
        self.fields['username'].label = "Brukernavn"
        self.fields['password1'].label = "Passord"
        self.fields['password2'].label = "Passord (igjen)"
        self.fields['description'].label = "Beskrivelse"
        self.fields['profile_picture'].label = "Profilbilde"

        self.fields['username'].help_text = None
        self.fields['password1'].help_text = "Minst 8 tegn"
        self.fields['password2'].help_text = "Må være likt"

class EditProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ["username"]

class ProfileForm(ModelForm):
    class Meta:
         model = UserProfile
         fields = ('description', 'profile_picture')
         labels = {
             'description': 'Beskrivelse',
             'profile_picture': 'Profilbilde'
         }
         widgets = {
            'description': Textarea(attrs={'cols':50, 'rows':4}),
        }