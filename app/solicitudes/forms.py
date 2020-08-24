from django import forms
from .models import Solicitud


class SolicitudModelForm(forms.ModelForm):
    # item           = forms.ModelChoiceField(queryset=Item.objects.all())
    # solicitud_user = forms.ModelChoiceField(queryset=User.objects.all())
    # applicant      = forms.ModelChoiceField(queryset=Profile.objects.all())
    class Meta:
        model = Solicitud
        fields = ('message',)  # 'item', 'applicant',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message"].widget.attrs["class"] = "form-control"
        self.fields["message"].widget.attrs["rows"] = "6"
        self.fields["message"].widget.attrs["size"] = "6"
