from django import forms
from .models import AdoptionApplication


class AdoptionApplicationForm(forms.ModelForm):
    class Meta:
        model = AdoptionApplication
        # Expose only the fields we want adopters to fill directly
        fields = [
            'phone_number',
            'address',
            'city',
            'province',
            'reason_for_adoption',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'reason_for_adoption': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if not phone:
            raise forms.ValidationError('Please provide a phone number.')
        return phone
