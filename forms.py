from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField, TimeField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from datetime import date, datetime
import re

class LoginForm(FlaskForm):
    """Giriş formu"""
    username = StringField('Kullanıcı Adı', validators=[DataRequired(message='Kullanıcı adı gereklidir')])
    password = PasswordField('Şifre', validators=[DataRequired(message='Şifre gereklidir')])


class ChangePasswordForm(FlaskForm):
    """Şifre değiştirme formu"""
    old_password = PasswordField('Mevcut Şifre', validators=[DataRequired(message='Mevcut şifre gereklidir')])
    new_password = PasswordField('Yeni Şifre', validators=[
        DataRequired(message='Yeni şifre gereklidir'),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır')
    ])
    confirm_password = PasswordField('Yeni Şifre (Tekrar)', validators=[
        DataRequired(message='Şifre tekrarı gereklidir'),
        EqualTo('new_password', message='Şifreler eşleşmiyor')
    ])


class FirstLoginPasswordForm(FlaskForm):
    """İlk giriş şifre değiştirme formu"""
    new_password = PasswordField('Yeni Şifre', validators=[
        DataRequired(message='Yeni şifre gereklidir'),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır')
    ])
    confirm_password = PasswordField('Yeni Şifre (Tekrar)', validators=[
        DataRequired(message='Şifre tekrarı gereklidir'),
        EqualTo('new_password', message='Şifreler eşleşmiyor')
    ])


class NotificationForm(FlaskForm):
    """Beton bildirim formu"""
    yibf_no = StringField('YİBF No', validators=[DataRequired(message='YİBF No gereklidir')])
    beton_miktari = StringField('Beton Miktarı', validators=[DataRequired(message='Beton miktarı gereklidir')])
    kat_bolge = StringField('Kat/Bölge', validators=[DataRequired(message='Kat/Bölge gereklidir')])
    beton_santrali_id = SelectField('Beton Santrali', coerce=int, validators=[DataRequired(message='Beton santrali seçiniz')])
    laboratuvar_id = SelectField('Laboratuvar', coerce=int, validators=[DataRequired(message='Laboratuvar seçiniz')])
    dokum_tarihi = DateField('Döküm Tarihi', format='%Y-%m-%d', validators=[DataRequired(message='Döküm tarihi gereklidir')])
    dokum_zamani = StringField('Döküm Zamanı (HH:MM)', validators=[DataRequired(message='Döküm zamanı gereklidir')])
    aciklama = TextAreaField('Açıklama')
    
    def validate_dokum_zamani(self, field):
        """Döküm zamanı formatı kontrolü (HH:MM)"""
        pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(pattern, field.data):
            raise ValidationError('Geçersiz zaman formatı. HH:MM formatında giriniz (örn: 14:30)')


class UserForm(FlaskForm):
    """Kullanıcı ekleme/düzenleme formu (Admin)"""
    username = StringField('Kullanıcı Adı', validators=[DataRequired(message='Kullanıcı adı gereklidir')])
    company_name = StringField('Firma Adı', validators=[DataRequired(message='Firma adı gereklidir')])
    password = PasswordField('Şifre', validators=[Length(min=6, message='Şifre en az 6 karakter olmalıdır')])
    role = SelectField('Rol', choices=[('user', 'Kullanıcı'), ('admin', 'Admin')], validators=[DataRequired()])


class LaboratuvarForm(FlaskForm):
    """Laboratuvar ekleme/düzenleme formu (Admin)"""
    ad = StringField('Laboratuvar Adı', validators=[DataRequired(message='Laboratuvar adı gereklidir')])


class BetonSantraliForm(FlaskForm):
    """Beton santrali ekleme/düzenleme formu (Admin)"""
    ad = StringField('Santral Adı', validators=[DataRequired(message='Santral adı gereklidir')])


class ResetPasswordForm(FlaskForm):
    """Admin tarafından şifre sıfırlama formu"""
    new_password = PasswordField('Yeni Şifre', validators=[
        DataRequired(message='Yeni şifre gereklidir'),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır')
    ])
    confirm_password = PasswordField('Yeni Şifre (Tekrar)', validators=[
        DataRequired(message='Şifre tekrarı gereklidir'),
        EqualTo('new_password', message='Şifreler eşleşmiyor')
    ])

