from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import Event, Category, UserProfile


BASE_INPUT_CLASS = (
    "w-full px-4 py-2 border border-gray-300 rounded-lg "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 "
    "focus:border-blue-500"
)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"
        widgets = {
            'date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': BASE_INPUT_CLASS
                }
            ),
            'time': forms.TimeInput(
                format='%H:%M',
                attrs={
                    'type': 'time',
                    'class': BASE_INPUT_CLASS
                }
            ),
            'image': forms.FileInput(
                attrs={
                    'class': BASE_INPUT_CLASS,
                    'accept': 'image/*'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            widget = field.widget

            if isinstance(widget, (forms.DateInput, forms.TimeInput)):
                widget.attrs.setdefault("class", BASE_INPUT_CLASS)
                continue

            widget.attrs["class"] = BASE_INPUT_CLASS


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': BASE_INPUT_CLASS
            })


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        help_text='Optional. Enter phone number with country code (e.g., +1234567890)'
    )
    profile_picture = forms.ImageField(required=False, help_text='Optional. Upload a profile picture')

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "phone_number", "profile_picture", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': BASE_INPUT_CLASS
            })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            if self.cleaned_data.get('phone_number'):
                profile.phone_number = self.cleaned_data['phone_number']
            if self.cleaned_data.get('profile_picture'):
                profile.profile_picture = self.cleaned_data['profile_picture']
            profile.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': BASE_INPUT_CLASS
            })

    def clean(self):
        """Override clean to provide better error messages for inactive users"""
        try:
            cleaned_data = super().clean()
            return cleaned_data
        except forms.ValidationError as e:
            username = self.cleaned_data.get('username')
            if username:
                try:
                    user = User.objects.get(username=username)
                    if not user.is_active:
                        raise forms.ValidationError(
                            "This account is inactive. Please check your email for the activation link.",
                            code='inactive',
                        )
                except User.DoesNotExist:
                    pass
            raise e

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = UserProfile
        fields = ('profile_picture', 'phone_number', 'bio', 'date_of_birth')
        widgets = {
            'profile_picture': forms.FileInput(
                attrs={'class': BASE_INPUT_CLASS, 'accept': 'image/*'}
            ),
            'phone_number': forms.TextInput(
                attrs={
                    'class': BASE_INPUT_CLASS, 
                    'placeholder': '+1234567890',
                    'help_text': 'Enter phone number with country code (e.g., +1234567890)'
                }
            ),
            'bio': forms.Textarea(
                attrs={'class': BASE_INPUT_CLASS, 'rows': 4, 'placeholder': 'Tell us about yourself'}
            ),
            'date_of_birth': forms.DateInput(
                attrs={'class': BASE_INPUT_CLASS, 'type': 'date'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
        
        for field in self.fields.values():
            if field.widget.attrs.get('class') is None:
                field.widget.attrs.update({'class': BASE_INPUT_CLASS})
    
    def clean_phone_number(self):
        """Validate phone number format against UserProfile phone_regex validator"""
        phone = self.cleaned_data.get('phone_number', '')
        if phone: 
            from django.core.exceptions import ValidationError
            try:
                validator = UserProfile._meta.get_field('phone_number').validators[0]
                validator(phone)
            except ValidationError as e:
                raise forms.ValidationError(
                    f"Invalid phone number format. {e.message}",
                    code='invalid_phone'
                )
        return phone
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email')
        
        if commit:
            user.save()
            profile.save()
        return profile


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': BASE_INPUT_CLASS})


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': BASE_INPUT_CLASS})


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': BASE_INPUT_CLASS})