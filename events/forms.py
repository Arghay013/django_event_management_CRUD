from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Event, Category


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

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': BASE_INPUT_CLASS
            })


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
            # Check if this is an inactive user error
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
