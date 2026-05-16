from django import forms
from django.utils.translation import gettext_lazy as _
from .models import OrganizerReview, Service, ProjectRequest, ProjectBid

class OrganizerReviewForm(forms.ModelForm):
    class Meta:
        model = OrganizerReview
        fields = ['name', 'rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
        }





from django.contrib.auth import get_user_model
from .models import OrganizerReview, Service

User = get_user_model()

class ProjectRequestForm(forms.ModelForm):
    class Meta:
        model = ProjectRequest
        fields = ['title', 'category', 'description', 'budget', 'delivery_days']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('What do you need?')}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'delivery_days': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ProjectBidForm(forms.ModelForm):
    class Meta:
        model = ProjectBid
        fields = ['price', 'delivery_days', 'message']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'delivery_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'title', 'description', 'category', 'subcategory', 'image',
            'price', 'delivery_days',
            'has_tier_2', 'tier_2_name', 'tier_2_price', 'tier_2_delivery_days', 'tier_2_description',
            'has_tier_3', 'tier_3_name', 'tier_3_price', 'tier_3_delivery_days', 'tier_3_description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g. Professional Logo Design')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _('Describe your service in detail...')}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Basic Price in EGP')}),
            'delivery_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Basic delivery days')}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            
            'has_tier_2': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tier_2_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g. Premium/Gold')}),
            'tier_2_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Price in EGP')}),
            'tier_2_delivery_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Days to deliver')}),
            'tier_2_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),

            'has_tier_3': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tier_3_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g. Imperial/Diamond')}),
            'tier_3_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Price in EGP')}),
            'tier_3_delivery_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Days to deliver')}),
            'tier_3_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


from .models import PayoutRequest, PortfolioItem

class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['title', 'description', 'image', 'link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Project Title')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('What did you do? Achievements?')}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }

class PayoutRequestForm(forms.ModelForm):
    class Meta:
        model = PayoutRequest
        fields = ['amount', 'payout_method_details']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Amount to withdraw...')}),
            'payout_method_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': _('Vodafone Cash number, Bank details, etc.')}),
        }





