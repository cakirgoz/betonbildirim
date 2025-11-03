# Beton Bildirim Sistemi

Yapı denetim kuruluşlarının günlük beton dökümlerine ilişkin bildirimde bulunacağı web tabanlı yönetim sistemi.

## Özellikler

### Kullanıcı Özellikleri
- Güvenli giriş sistemi (kullanıcı adı ve şifre ile)
- İlk girişte zorunlu şifre değiştirme
- Günlük beton bildirimi ekleme, düzenleme ve silme
- Kendi bildirimlerini görüntüleme ve yönetme
- Şifre değiştirme

### Admin Özellikleri
- Kullanıcı yönetimi (ekleme, düzenleme, silme, aktif/pasif)
- Laboratuvar yönetimi
- Beton santrali yönetimi
- Tüm bildirimleri görüntüleme
- Gelişmiş filtreleme sistemi (firma, YİBF, laboratuvar, santral, tarih)
- Kullanıcı şifrelerini sıfırlama

## Teknoloji Stack

- **Backend:** Flask 3.0.0
- **Database:** SQLite (dosya bazlı)
- **Authentication:** Flask-Login
- **Forms:** Flask-WTF, WTForms
- **Frontend:** Bootstrap 5, DataTables.js
- **Security:** CSRF koruması, Bcrypt şifre hashleme

## Kurulum

### Gereksinimler
- Python 3.8 veya üzeri

### Adımlar

1. **Depoyu klonlayın veya indirin**
```bash
git clone <repository-url>
cd betonbildirim
```

2. **Virtual environment oluşturun (önerilen)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Bağımlılıkları yükleyin**
```bash
pip install -r requirements.txt
```

4. **Uygulamayı çalıştırın**
```bash
python app.py
```

İlk çalıştırmada veritabanı otomatik olarak oluşturulacak ve başlangıç verileri eklenecektir.

5. **Tarayıcıda açın**
```
http://localhost:5000
```

## Varsayılan Giriş Bilgileri

### Admin Hesabı
- **Kullanıcı Adı:** admin
- **Şifre:** Admin123!

### Yapı Denetim Hesapları
- **Şifre:** Ydk123! (tüm kullanıcılar için aynı)
- **Kullanıcı Adları (Alfabetik sırada):**
  - aladag => Aladağ Yapı Denetim
  - ayc => Ayç Yapı Denetim
  - bolum => Bolum Yapı Denetim
  - elit => Bolu Elit Yapı Denetim
  - kar => Bolu Kar Yapı Denetim
  - koroglu => Bolu Köroğlu Yapı Denetim
  - teknik => Bolu Teknik Yapı Denetim
  - etab => Etab Yapı Denetim
  - evin => Evin Bolu Yapı Denetim
  - kent => Kent Bolu Yapı Denetim
  - koza => Koza Yapı Denetim

### Başlangıç Verileri
- **Laboratuvarlar (3):** Güneş, Kalites, Yea
- **Beton Santralleri (9):** Abant Beton, Allar Nakliyat, Allar Petrol, Bhb Bolu Hazır Beton, Bolu Bel., Güven Hazır Beton, Köroğlu Beton, Şenyürek Beton, Yiğit Hazır Beton

> **Not:** İlk girişte tüm kullanıcılar şifrelerini değiştirmek zorundadır.

## Dosya Yapısı

```
betonbildirim/
│
├── app.py                      # Ana uygulama
├── config.py                   # Konfigürasyon
├── models.py                   # Veritabanı modelleri
├── forms.py                    # Form sınıfları
├── decorators.py               # Custom decorator'lar
├── requirements.txt            # Python bağımlılıkları
├── README.md                   # Bu dosya
│
├── instance/
│   └── database.db            # SQLite veritabanı (otomatik oluşturulur)
│
├── static/
│   ├── css/
│   │   └── style.css          # Custom CSS
│   ├── js/
│   │   └── main.js            # Custom JavaScript
│   └── images/
│
└── templates/
    ├── base.html              # Ana template
    ├── login.html             # Giriş sayfası
    ├── change_password.html   # Şifre değiştirme
    │
    ├── user/                  # Kullanıcı sayfaları
    │   ├── dashboard.html
    │   ├── notification_form.html
    │   └── my_notifications.html
    │
    ├── admin/                 # Admin sayfaları
    │   ├── dashboard.html
    │   ├── users.html
    │   ├── user_form.html
    │   ├── reset_password.html
    │   ├── labs.html
    │   ├── lab_form.html
    │   ├── plants.html
    │   ├── plant_form.html
    │   └── all_notifications.html
    │
    └── errors/                # Hata sayfaları
        ├── 404.html
        └── 500.html
```

## Production Deployment

### Hetzner Shared Hosting için

1. **Dosyaları sunucuya yükleyin**

2. **Virtual environment oluşturun**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Environment variables ayarlayın**
```bash
export SECRET_KEY="your-production-secret-key-here"
export FLASK_ENV=production
```

4. **WSGI server ile çalıştırın (Gunicorn önerilen)**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

5. **Apache/Nginx ile reverse proxy ayarlayın**

### Güvenlik Notları (Production)

- `SECRET_KEY`'i mutlaka değiştirin
- HTTPS kullanın
- Güçlü şifreler belirleyin
- Düzenli yedekleme yapın
- Log dosyalarını kontrol edin

## Kullanım

### Kullanıcı İşlemleri

1. **Giriş yapın** - Kullanıcı adı ve şifreniz ile
2. **İlk girişte şifre değiştirin** - Güvenlik için zorunlu
3. **Yeni bildirim ekleyin** - "Yeni Bildirim" butonuna tıklayın
4. **Bildirimleri görüntüleyin** - Ana sayfada bugünün, "Bildirimlerim" sayfasında tüm bildirimleri görebilirsiniz
5. **Bildirim düzenleyin/silin** - Her bildirim satırındaki butonları kullanın

### Admin İşlemleri

1. **Admin olarak giriş yapın**
2. **Kullanıcı ekleyin/düzenleyin** - Kullanıcı Yönetimi'nden
3. **Laboratuvar/Santral yönetin** - İlgili menülerden
4. **Bildirimleri filtreleyin** - Bildirimler sayfasında filtreleme bölümünü kullanın
5. **Kullanıcı şifrelerini sıfırlayın** - Gerektiğinde

## Destek

Sorularınız veya sorunlarınız için lütfen iletişime geçin.

## Lisans

Bu proje özel kullanım içindir.

## Versiyon

**v1.0.0** - İlk sürüm (Kasım 2025)

