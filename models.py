from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz

db = SQLAlchemy()

# Türkiye saat dilimi
TURKEY_TZ = pytz.timezone('Europe/Istanbul')

def get_turkey_time():
    """Türkiye saatini döndür"""
    return datetime.now(TURKEY_TZ)

class User(UserMixin, db.Model):
    """Kullanıcı modeli - Admin ve Yapı Denetim kullanıcıları"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' veya 'user'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    must_change_password = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=get_turkey_time, nullable=False)
    
    # İlişkiler
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Şifreyi hashleyerek kaydet"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Şifre kontrolü"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Admin kontrolü"""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'


class Notification(db.Model):
    """Beton bildirim modeli"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    yibf_no = db.Column(db.String(100), nullable=False, index=True)
    beton_miktari = db.Column(db.String(100), nullable=False)
    kat_bolge = db.Column(db.String(200), nullable=False)
    beton_santrali_id = db.Column(db.Integer, db.ForeignKey('beton_santralleri.id'), nullable=False)
    laboratuvar_id = db.Column(db.Integer, db.ForeignKey('laboratuvarlar.id'), nullable=False)
    dokum_zamani = db.Column(db.String(5), nullable=False)  # HH:MM formatında
    dokum_tarihi = db.Column(db.Date, nullable=False, index=True)
    aciklama = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_turkey_time, nullable=False)
    updated_at = db.Column(db.DateTime, default=get_turkey_time, onupdate=get_turkey_time, nullable=False)
    
    def __repr__(self):
        return f'<Notification {self.yibf_no} - {self.dokum_tarihi}>'


class Laboratuvar(db.Model):
    """Laboratuvar modeli"""
    __tablename__ = 'laboratuvarlar'
    
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(200), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=get_turkey_time, nullable=False)
    
    # İlişkiler
    notifications = db.relationship('Notification', backref='laboratuvar', lazy='dynamic')
    
    def __repr__(self):
        return f'<Laboratuvar {self.ad}>'


class BetonSantrali(db.Model):
    """Beton santrali modeli"""
    __tablename__ = 'beton_santralleri'
    
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(200), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=get_turkey_time, nullable=False)
    
    # İlişkiler
    notifications = db.relationship('Notification', backref='beton_santrali', lazy='dynamic')
    
    def __repr__(self):
        return f'<BetonSantrali {self.ad}>'

