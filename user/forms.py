from django import forms

from user.models import User, Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'sex', 'birthday', 'location']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'

    def clean_max_dating_age(self):
        '''检查最大交友年龄'''
        cleaned = super().clean()
        if cleaned['max_dating_age'] < cleaned['min_dating_age']:
            raise forms.ValidationError('max_dating_age 必须大于 min_dating_age')
        else:
            return cleaned['max_dating_age']

    def clean_max_distance(self):
        '''检查最大距离字段'''
        cleaned = super().clean()
        if cleaned['max_distance'] < cleaned['min_distance']:
            raise forms.ValidationError('max_distance 必须大于 min_distance')
        else:
            return cleaned['max_distance']
