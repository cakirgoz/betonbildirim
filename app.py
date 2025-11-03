from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import generate_csrf
from config import Config
from models import db, User, Notification, Laboratuvar, BetonSantrali
from forms import (LoginForm, ChangePasswordForm, FirstLoginPasswordForm, 
                   NotificationForm, UserForm, LaboratuvarForm, 
                   BetonSantraliForm, ResetPasswordForm)
from decorators import admin_required, password_change_required
from datetime import date, datetime
import os

# Flask uygulaması oluştur
app = Flask(__name__)
app.config.from_object(Config)

# CSRF token'ı tüm template'lerde kullanılabilir hale getir
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

# Instance klasörünü oluştur
os.makedirs(os.path.join(app.config['BASE_DIR'], 'instance'), exist_ok=True)

# Database başlat
db.init_app(app)

# Flask-Login başlat
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Bu sayfaya erişmek için giriş yapmalısınız.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==================== GENEL ROUTE'LAR ====================

@app.route('/')
def index():
    """Ana sayfa - login'e yönlendir"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Hesabınız devre dışı bırakılmış. Lütfen yönetici ile iletişime geçin.', 'danger')
                return redirect(url_for('login'))
            
            login_user(user)
            
            if user.must_change_password:
                flash('Güvenlik nedeniyle şifrenizi değiştirmeniz gerekmektedir.', 'warning')
                return redirect(url_for('change_password'))
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('admin_dashboard') if user.is_admin() else url_for('dashboard')
            
            return redirect(next_page)
        else:
            flash('Geçersiz kullanıcı adı veya şifre.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Çıkış işlemi"""
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('login'))


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Şifre değiştirme"""
    # İlk giriş ise farklı form
    if current_user.must_change_password:
        form = FirstLoginPasswordForm()
        if form.validate_on_submit():
            current_user.set_password(form.new_password.data)
            current_user.must_change_password = False
            db.session.commit()
            flash('Şifreniz başarıyla değiştirildi.', 'success')
            return redirect(url_for('index'))
    else:
        form = ChangePasswordForm()
        if form.validate_on_submit():
            if not current_user.check_password(form.old_password.data):
                flash('Mevcut şifreniz yanlış.', 'danger')
                return redirect(url_for('change_password'))
            
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Şifreniz başarıyla değiştirildi.', 'success')
            return redirect(url_for('index'))
    
    return render_template('change_password.html', form=form, 
                         first_login=current_user.must_change_password)


# ==================== KULLANICI ROUTE'LARI ====================

@app.route('/dashboard')
@login_required
@password_change_required
def dashboard():
    """Kullanıcı ana sayfası - Bugünün bildirimleri"""
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    
    today = date.today()
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        dokum_tarihi=today
    ).order_by(Notification.dokum_zamani).all()
    
    return render_template('user/dashboard.html', notifications=notifications, today=today)


@app.route('/notification/add', methods=['GET', 'POST'])
@login_required
@password_change_required
def add_notification():
    """Yeni bildirim ekleme"""
    if current_user.is_admin():
        flash('Admin kullanıcıları bildirim ekleyemez.', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    form = NotificationForm()
    
    # Dropdown'ları doldur (sadece aktif olanlar)
    form.laboratuvar_id.choices = [(lab.id, lab.ad) for lab in 
                                     Laboratuvar.query.filter_by(is_active=True).order_by(Laboratuvar.ad).all()]
    form.beton_santrali_id.choices = [(santral.id, santral.ad) for santral in 
                                       BetonSantrali.query.filter_by(is_active=True).order_by(BetonSantrali.ad).all()]
    
    if form.validate_on_submit():
        notification = Notification(
            user_id=current_user.id,
            yibf_no=form.yibf_no.data,
            beton_miktari=form.beton_miktari.data,
            kat_bolge=form.kat_bolge.data,
            beton_santrali_id=form.beton_santrali_id.data,
            laboratuvar_id=form.laboratuvar_id.data,
            dokum_tarihi=form.dokum_tarihi.data,
            dokum_zamani=form.dokum_zamani.data,
            aciklama=form.aciklama.data
        )
        db.session.add(notification)
        db.session.commit()
        flash('Bildirim başarıyla eklendi.', 'success')
        return redirect(url_for('dashboard'))
    
    # Bugünün tarihini default olarak ayarla
    if request.method == 'GET':
        form.dokum_tarihi.data = date.today()
    
    return render_template('user/notification_form.html', form=form, title='Yeni Bildirim')


@app.route('/notification/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@password_change_required
def edit_notification(id):
    """Bildirim düzenleme"""
    notification = Notification.query.get_or_404(id)
    
    # Sadece kendi bildirimleri düzenleyebilir
    if notification.user_id != current_user.id and not current_user.is_admin():
        flash('Bu bildirimi düzenleme yetkiniz yok.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = NotificationForm(obj=notification)
    
    # Dropdown'ları doldur
    form.laboratuvar_id.choices = [(lab.id, lab.ad) for lab in 
                                     Laboratuvar.query.filter_by(is_active=True).order_by(Laboratuvar.ad).all()]
    form.beton_santrali_id.choices = [(santral.id, santral.ad) for santral in 
                                       BetonSantrali.query.filter_by(is_active=True).order_by(BetonSantrali.ad).all()]
    
    if form.validate_on_submit():
        notification.yibf_no = form.yibf_no.data
        notification.beton_miktari = form.beton_miktari.data
        notification.kat_bolge = form.kat_bolge.data
        notification.beton_santrali_id = form.beton_santrali_id.data
        notification.laboratuvar_id = form.laboratuvar_id.data
        notification.dokum_tarihi = form.dokum_tarihi.data
        notification.dokum_zamani = form.dokum_zamani.data
        notification.aciklama = form.aciklama.data
        notification.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Bildirim başarıyla güncellendi.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('user/notification_form.html', form=form, 
                         notification=notification, title='Bildirim Düzenle')


@app.route('/notification/delete/<int:id>', methods=['POST'])
@login_required
@password_change_required
def delete_notification(id):
    """Bildirim silme"""
    notification = Notification.query.get_or_404(id)
    
    # Sadece kendi bildirimleri silebilir
    if notification.user_id != current_user.id and not current_user.is_admin():
        flash('Bu bildirimi silme yetkiniz yok.', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(notification)
    db.session.commit()
    flash('Bildirim başarıyla silindi.', 'success')
    
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/my-notifications')
@login_required
@password_change_required
def my_notifications():
    """Kullanıcının tüm bildirimleri"""
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.dokum_tarihi.desc(), Notification.dokum_zamani.desc()).all()
    
    return render_template('user/my_notifications.html', notifications=notifications)


# ==================== ADMIN ROUTE'LARI ====================

@app.route('/admin/dashboard')
@login_required
@admin_required
@password_change_required
def admin_dashboard():
    """Admin ana sayfası"""
    total_users = User.query.filter_by(role='user').count()
    total_notifications = Notification.query.count()
    today_notifications = Notification.query.filter_by(dokum_tarihi=date.today()).count()
    active_labs = Laboratuvar.query.filter_by(is_active=True).count()
    active_plants = BetonSantrali.query.filter_by(is_active=True).count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_notifications=total_notifications,
                         today_notifications=today_notifications,
                         active_labs=active_labs,
                         active_plants=active_plants)


# ==================== KULLANICI YÖNETİMİ ====================

@app.route('/admin/users')
@login_required
@admin_required
@password_change_required
def admin_users():
    """Kullanıcı listesi"""
    users = User.query.order_by(User.role.desc(), User.company_name).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/user/add', methods=['GET', 'POST'])
@login_required
@admin_required
@password_change_required
def admin_user_add():
    """Kullanıcı ekleme"""
    form = UserForm()
    
    if form.validate_on_submit():
        # Kullanıcı adı kontrolü
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'danger')
            return redirect(url_for('admin_user_add'))
        
        if not form.password.data:
            flash('Şifre gereklidir.', 'danger')
            return redirect(url_for('admin_user_add'))
        
        user = User(
            username=form.username.data,
            company_name=form.company_name.data,
            role=form.role.data,
            must_change_password=True
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Kullanıcı "{user.username}" başarıyla eklendi.', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/user_form.html', form=form, title='Yeni Kullanıcı')


@app.route('/admin/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@password_change_required
def admin_user_edit(id):
    """Kullanıcı düzenleme"""
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        # Kullanıcı adı kontrolü (kendisi hariç)
        existing_user = User.query.filter(User.username == form.username.data, User.id != id).first()
        if existing_user:
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'danger')
            return redirect(url_for('admin_user_edit', id=id))
        
        user.username = form.username.data
        user.company_name = form.company_name.data
        user.role = form.role.data
        
        # Şifre değişikliği varsa
        if form.password.data:
            user.set_password(form.password.data)
            user.must_change_password = True
        
        db.session.commit()
        flash(f'Kullanıcı "{user.username}" başarıyla güncellendi.', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/user_form.html', form=form, user=user, title='Kullanıcı Düzenle')


@app.route('/admin/user/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
@password_change_required
def admin_user_delete(id):
    """Kullanıcı silme"""
    user = User.query.get_or_404(id)
    
    # Admin kendini silemez
    if user.id == current_user.id:
        flash('Kendinizi silemezsiniz.', 'danger')
        return redirect(url_for('admin_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'Kullanıcı "{username}" başarıyla silindi.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/user/toggle/<int:id>', methods=['POST'])
@login_required
@admin_required
@password_change_required
def admin_user_toggle(id):
    """Kullanıcı aktif/pasif"""
    user = User.query.get_or_404(id)
    
    # Admin kendini pasif yapamaz
    if user.id == current_user.id:
        flash('Kendi hesabınızı devre dışı bırakamazsınız.', 'danger')
        return redirect(url_for('admin_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'aktif' if user.is_active else 'pasif'
    flash(f'Kullanıcı "{user.username}" {status} hale getirildi.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/user/reset-password/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@password_change_required
def admin_user_reset_password(id):
    """Admin tarafından şifre sıfırlama"""
    user = User.query.get_or_404(id)
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        user.must_change_password = True
        db.session.commit()
        flash(f'Kullanıcı "{user.username}" şifresi sıfırlandı. Kullanıcı ilk girişte şifre değiştirmek zorunda kalacak.', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/reset_password.html', form=form, user=user)


# ==================== LABORATUVAR YÖNETİMİ ====================

@app.route('/admin/labs')
@login_required
@admin_required
@password_change_required
def admin_labs():
    """Laboratuvar listesi"""
    labs = Laboratuvar.query.order_by(Laboratuvar.ad).all()
    return render_template('admin/labs.html', labs=labs)


@app.route('/admin/lab/add', methods=['GET', 'POST'])
@login_required
@admin_required
@password_change_required
def admin_lab_add():
    """Laboratuvar ekleme"""
    form = LaboratuvarForm()
    
    if form.validate_on_submit():
        existing_lab = Laboratuvar.query.filter_by(ad=form.ad.data).first()
        if existing_lab:
            flash('Bu laboratuvar zaten mevcut.', 'danger')
            return redirect(url_for('admin_lab_add'))
        
        lab = Laboratuvar(ad=form.ad.data)
        db.session.add(lab)
        db.session.commit()
        flash(f'Laboratuvar "{lab.ad}" başarıyla eklendi.', 'success')
        return redirect(url_for('admin_labs'))
    
    return render_template('admin/lab_form.html', form=form, title='Yeni Laboratuvar')


@app.route('/admin/lab/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@password_change_required
def admin_lab_edit(id):
    """Laboratuvar düzenleme"""
    lab = Laboratuvar.query.get_or_404(id)
    form = LaboratuvarForm(obj=lab)
    
    if form.validate_on_submit():
        existing_lab = Laboratuvar.query.filter(Laboratuvar.ad == form.ad.data, Laboratuvar.id != id).first()
        if existing_lab:
            flash('Bu laboratuvar adı zaten kullanılıyor.', 'danger')
            return redirect(url_for('admin_lab_edit', id=id))
        
        lab.ad = form.ad.data
        db.session.commit()
        flash(f'Laboratuvar "{lab.ad}" başarıyla güncellendi.', 'success')
        return redirect(url_for('admin_labs'))
    
    return render_template('admin/lab_form.html', form=form, lab=lab, title='Laboratuvar Düzenle')


@app.route('/admin/lab/toggle/<int:id>', methods=['POST'])
@login_required
@admin_required
@password_change_required
def admin_lab_toggle(id):
    """Laboratuvar aktif/pasif"""
    lab = Laboratuvar.query.get_or_404(id)
    lab.is_active = not lab.is_active
    db.session.commit()
    
    status = 'aktif' if lab.is_active else 'pasif'
    flash(f'Laboratuvar "{lab.ad}" {status} hale getirildi.', 'success')
    return redirect(url_for('admin_labs'))


@app.route('/admin/lab/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
@password_change_required
def admin_lab_delete(id):
    """Laboratuvar silme"""
    lab = Laboratuvar.query.get_or_404(id)
    
    # İlişkili bildirim var mı kontrol et
    if lab.notifications.count() > 0:
        flash(f'Bu laboratuvarla ilişkili {lab.notifications.count()} bildirim bulunmaktadır. Önce bildirimleri siliniz veya laboratuvarı pasif yapınız.', 'danger')
        return redirect(url_for('admin_labs'))
    
    lab_name = lab.ad
    db.session.delete(lab)
    db.session.commit()
    flash(f'Laboratuvar "{lab_name}" başarıyla silindi.', 'success')
    return redirect(url_for('admin_labs'))


# ==================== BETON SANTRALİ YÖNETİMİ ====================

@app.route('/admin/plants')
@login_required
@admin_required
@password_change_required
def admin_plants():
    """Beton santrali listesi"""
    plants = BetonSantrali.query.order_by(BetonSantrali.ad).all()
    return render_template('admin/plants.html', plants=plants)


@app.route('/admin/plant/add', methods=['GET', 'POST'])
@login_required
@admin_required
@password_change_required
def admin_plant_add():
    """Beton santrali ekleme"""
    form = BetonSantraliForm()
    
    if form.validate_on_submit():
        existing_plant = BetonSantrali.query.filter_by(ad=form.ad.data).first()
        if existing_plant:
            flash('Bu santral zaten mevcut.', 'danger')
            return redirect(url_for('admin_plant_add'))
        
        plant = BetonSantrali(ad=form.ad.data)
        db.session.add(plant)
        db.session.commit()
        flash(f'Beton santrali "{plant.ad}" başarıyla eklendi.', 'success')
        return redirect(url_for('admin_plants'))
    
    return render_template('admin/plant_form.html', form=form, title='Yeni Beton Santrali')


@app.route('/admin/plant/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@password_change_required
def admin_plant_edit(id):
    """Beton santrali düzenleme"""
    plant = BetonSantrali.query.get_or_404(id)
    form = BetonSantraliForm(obj=plant)
    
    if form.validate_on_submit():
        existing_plant = BetonSantrali.query.filter(BetonSantrali.ad == form.ad.data, BetonSantrali.id != id).first()
        if existing_plant:
            flash('Bu santral adı zaten kullanılıyor.', 'danger')
            return redirect(url_for('admin_plant_edit', id=id))
        
        plant.ad = form.ad.data
        db.session.commit()
        flash(f'Beton santrali "{plant.ad}" başarıyla güncellendi.', 'success')
        return redirect(url_for('admin_plants'))
    
    return render_template('admin/plant_form.html', form=form, plant=plant, title='Beton Santrali Düzenle')


@app.route('/admin/plant/toggle/<int:id>', methods=['POST'])
@login_required
@admin_required
@password_change_required
def admin_plant_toggle(id):
    """Beton santrali aktif/pasif"""
    plant = BetonSantrali.query.get_or_404(id)
    plant.is_active = not plant.is_active
    db.session.commit()
    
    status = 'aktif' if plant.is_active else 'pasif'
    flash(f'Beton santrali "{plant.ad}" {status} hale getirildi.', 'success')
    return redirect(url_for('admin_plants'))


@app.route('/admin/plant/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
@password_change_required
def admin_plant_delete(id):
    """Beton santrali silme"""
    plant = BetonSantrali.query.get_or_404(id)
    
    # İlişkili bildirim var mı kontrol et
    if plant.notifications.count() > 0:
        flash(f'Bu santral ile ilişkili {plant.notifications.count()} bildirim bulunmaktadır. Önce bildirimleri siliniz veya santrali pasif yapınız.', 'danger')
        return redirect(url_for('admin_plants'))
    
    plant_name = plant.ad
    db.session.delete(plant)
    db.session.commit()
    flash(f'Beton santrali "{plant_name}" başarıyla silindi.', 'success')
    return redirect(url_for('admin_plants'))


# ==================== BİLDİRİM GÖRÜNTÜLEME (ADMIN) ====================

@app.route('/admin/notifications')
@login_required
@admin_required
@password_change_required
def admin_notifications():
    """Tüm bildirimleri görüntüleme (filtreleme)"""
    # Filtre parametreleri
    user_id = request.args.get('user_id', type=int)
    yibf_no = request.args.get('yibf_no', '').strip()
    lab_id = request.args.get('lab_id', type=int)
    plant_id = request.args.get('plant_id', type=int)
    show_today = request.args.get('show_today', 'false') == 'true'
    
    # Query oluştur
    query = Notification.query
    
    # Filtreler
    if user_id:
        query = query.filter_by(user_id=user_id)
    if yibf_no:
        query = query.filter(Notification.yibf_no.contains(yibf_no))
    if lab_id:
        query = query.filter_by(laboratuvar_id=lab_id)
    if plant_id:
        query = query.filter_by(beton_santrali_id=plant_id)
    if show_today:
        query = query.filter_by(dokum_tarihi=date.today())
    
    notifications = query.order_by(Notification.dokum_tarihi.desc(), 
                                   Notification.dokum_zamani.desc()).all()
    
    # Dropdown'lar için veriler
    users = User.query.filter_by(role='user').order_by(User.company_name).all()
    labs = Laboratuvar.query.filter_by(is_active=True).order_by(Laboratuvar.ad).all()
    plants = BetonSantrali.query.filter_by(is_active=True).order_by(BetonSantrali.ad).all()
    
    return render_template('admin/all_notifications.html',
                         notifications=notifications,
                         users=users,
                         labs=labs,
                         plants=plants,
                         filters={
                             'user_id': user_id,
                             'yibf_no': yibf_no,
                             'lab_id': lab_id,
                             'plant_id': plant_id,
                             'show_today': show_today
                         })


# ==================== HATA YÖNETİMİ ====================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


# ==================== VERİTABANI İNİTİALİZASYON ====================

def init_db():
    """Veritabanını başlat ve seed data ekle"""
    with app.app_context():
        db.create_all()
        
        # Admin kontrolü
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Seed data ekleniyor...")
            
            # Admin hesabı
            admin = User(
                username='admin',
                company_name='Yönetici',
                role='admin',
                must_change_password=True
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            
            # Yapı Denetim Kuruluşları (Alfabetik sırada)
            yapi_denetimler = [
                ('aladag', 'Aladağ Yapı Denetim'),
                ('ayc', 'Ayç Yapı Denetim'),
                ('bolum', 'Bolum Yapı Denetim'),
                ('elit', 'Bolu Elit Yapı Denetim'),
                ('kar', 'Bolu Kar Yapı Denetim'),
                ('koroglu', 'Bolu Köroğlu Yapı Denetim'),
                ('teknik', 'Bolu Teknik Yapı Denetim'),
                ('etab', 'Etab Yapı Denetim'),
                ('evin', 'Evin Bolu Yapı Denetim'),
                ('kent', 'Kent Bolu Yapı Denetim'),
                ('koza', 'Koza Yapı Denetim'),
            ]
            
            for username, company_name in yapi_denetimler:
                user = User(
                    username=username,
                    company_name=company_name,
                    role='user',
                    must_change_password=True
                )
                user.set_password('Ydk123!')
                db.session.add(user)
            
            # Laboratuvarlar (Alfabetik sırada)
            lab_names = ['Güneş', 'Kalites', 'Yea']
            for name in lab_names:
                lab = Laboratuvar(ad=name)
                db.session.add(lab)
            
            # Beton Santralleri (Alfabetik sırada)
            santral_names = [
                'Abant Beton',
                'Allar Nakliyat',
                'Allar Petrol',
                'Bhb Bolu Hazır Beton',
                'Bolu Bel.',
                'Güven Hazır Beton',
                'Köroğlu Beton',
                'Şenyürek Beton',
                'Yiğit Hazır Beton'
            ]
            for name in santral_names:
                plant = BetonSantrali(ad=name)
                db.session.add(plant)
            
            db.session.commit()
            print("Seed data başarıyla eklendi!")
            print("\n" + "="*60)
            print("GİRİŞ BİLGİLERİ")
            print("="*60)
            print("\nAdmin Hesabı:")
            print("  Kullanıcı Adı: admin")
            print("  Şifre: Admin123!")
            print("\nYapı Denetim Hesapları:")
            print("  Şifre (Hepsi için): Ydk123!")
            print("  Kullanıcı Adları:")
            for username, company_name in yapi_denetimler:
                print(f"    {username:10} => {company_name}")
            print("="*60)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

