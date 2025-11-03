from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Admin yetkisi gerektiren sayfalar için decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Bu sayfaya erişmek için giriş yapmalısınız.', 'warning')
            return redirect(url_for('login'))
        if not current_user.is_admin():
            flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def password_change_required(f):
    """Şifre değişikliği zorunlu kontrolü için decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.must_change_password:
            # Şifre değiştirme sayfasına izin ver
            if f.__name__ in ['change_password', 'logout']:
                return f(*args, **kwargs)
            flash('Devam etmek için şifrenizi değiştirmelisiniz.', 'warning')
            return redirect(url_for('change_password'))
        return f(*args, **kwargs)
    return decorated_function

