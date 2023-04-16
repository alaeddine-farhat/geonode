#########################################################################
#
# Copyright (C) 2016 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import taggit

from django import forms
from allauth.account.forms import SignupForm, setup_user_email
from django.contrib.auth import get_user_model
from allauth.account.adapter import get_adapter
from allauth.utils import set_form_field_order
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext as _
from geonode.base.enumerations import COUNTRIES
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from captcha.fields import ReCaptchaField

# Ported in from django-registration
attrs_dict = {'class': 'required'}

class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields["organization"] = forms.CharField(
            label=_("Organization"),
            widget=forms.TextInput(
                attrs={"placeholder": _("Organization"),
                    "autocomplete": "organization"}
            ),
        )
        self.fields["voice"] = forms.CharField(
            label=_("Voice"),
            widget=forms.TextInput(
                attrs={"placeholder": _("Voice"), "autocomplete": "voice"}
                ),
            )
        self.fields["position"] = forms.CharField(
            label=_("Position"),
            widget=forms.TextInput(
                attrs={"placeholder": _("Position"),
                                        "autocomplete": "position"}
            ),
        )
        self.fields["country"] = forms.CharField(
            label=_("Country"),
            widget=forms.Select(
                choices=COUNTRIES
            ),
        )
        
        self.field_order = [
            "email",
            "email2",  # ignored when not present
            "username",
            "voice",
            "organization",
            "position",
            "country",
            "password1",
            "password2",  # ignored when not present
        ]

        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)

    def save(self, request):
        adapter = get_adapter(request)
        user = adapter.new_user(request)
        user.organization = self.cleaned_data['organization']
        user.voice = self.cleaned_data['voice']
        user.position = self.cleaned_data['position']
        user.country = self.cleaned_data['country']
        user.expiration_date = timezone.now() + relativedelta(months=1)
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        # TODO: Move into adapter `save_user` ?
        setup_user_email(request, user, [])
        return user

class AllauthReCaptchaSignupForm(forms.Form):

    captcha = ReCaptchaField()

    def signup(self, request, user):
        """ Required, or else it thorws deprecation warnings """
        pass


class ProfileCreationForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ("username",)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )


class ProfileChangeForm(UserChangeForm):

    class Meta:
        model = get_user_model()
        fields = '__all__'


class ForgotUsernameForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_('Email Address'))


class ProfileForm(forms.ModelForm):
    keywords = taggit.forms.TagField(
        label=_("Keywords"),
        required=False,
        help_text=_("A space or comma-separated list of keywords"))

    class Meta:
        model = get_user_model()
        exclude = (
            'user',
            'password',
            'last_login',
            'groups',
            'user_permissions',
            'username',
            'is_staff',
            'is_superuser',
            'is_active',
            'date_joined',
            'expiration_date',
            'is_expirable'
        )
