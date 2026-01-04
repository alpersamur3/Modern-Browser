# 🌐 Modern Browser

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**Gelişmiş, modern ve güvenli bir web tarayıcısı**

</div>

---

## 📋 Genel Bakış

Modern Browser, PyQt5 ve QWebEngineView kullanılarak geliştirilen, tam özellikli bir web tarayıcısıdır. Modüler mimarisi sayesinde kolay genişletilebilir ve özelleştirilebilir yapıdadır.

## ✨ Özellikler

### 🔖 Temel Özellikler
- **Sekmeli Tarama**: Çoklu sekme desteği, sekme sabitleme, sessize alma
- **Yer İmleri**: Klasörlerle organize edilebilen yer imi yönetimi
- **Geçmiş**: Kapsamlı tarama geçmişi yönetimi
- **İndirmeler**: Gelişmiş indirme yöneticisi

### 🔒 Gizlilik ve Güvenlik
- **Gizli Mod**: Geçmiş kaydedilmeden gezinme
- **Reklam Engelleyici**: Yerleşik reklam ve izleyici engelleme
- **Parola Yöneticisi**: Şifreli parola saklama
- **HTTPS Göstergesi**: Güvenli bağlantı durumu

### 🎨 Görünüm
- **Karanlık Mod**: Göz yormayan karanlık tema
- **Modern Arayüz**: Şık ve kullanıcı dostu tasarım
- **Özelleştirilebilir**: Tema ve görünüm ayarları

### 🛠️ Araçlar
- **Sayfa İçi Arama**: Ctrl+F ile hızlı arama
- **Zoom Kontrolü**: Yakınlaştırma/uzaklaştırma
- **Okuma Modu**: Dikkat dağıtmayan okuma deneyimi
- **Ekran Görüntüsü**: Sayfa görüntüsü kaydetme
- **Yazdırma**: Sayfa yazdırma desteği
- **Kaynak Görüntüleme**: Sayfa kaynak kodu

### ⌨️ Klavye Kısayolları
| Kısayol | İşlev |
|---------|-------|
| `Ctrl+T` | Yeni sekme |
| `Ctrl+W` | Sekmeyi kapat |
| `Ctrl+Shift+N` | Gizli sekme |
| `Ctrl+Shift+T` | Kapatılan sekmeyi aç |
| `Ctrl+L` | Adres çubuğuna odaklan |
| `Ctrl+F` | Sayfada bul |
| `Ctrl+D` | Yer imi ekle/kaldır |
| `Ctrl+H` | Geçmiş |
| `Ctrl+J` | İndirmeler |
| `Ctrl++` | Yakınlaştır |
| `Ctrl+-` | Uzaklaştır |
| `Ctrl+0` | Zoom sıfırla |
| `F11` | Tam ekran |
| `F5` | Yenile |
| `Ctrl+P` | Yazdır |

## 📁 Proje Yapısı

```
Simple-Browser/
├── browser/
│   ├── __init__.py
│   ├── core/                    # Çekirdek modüller
│   │   ├── __init__.py
│   │   ├── browser_tab.py       # Sekme yönetimi
│   │   ├── browser_engine.py    # Tarayıcı motoru
│   │   └── settings_manager.py  # Ayar yönetimi
│   ├── ui/                      # Kullanıcı arayüzü
│   │   ├── __init__.py
│   │   ├── main_window.py       # Ana pencere
│   │   ├── toolbar.py           # Araç çubuğu
│   │   ├── sidebar.py           # Yan panel
│   │   ├── status_bar.py        # Durum çubuğu
│   │   └── dialogs.py           # Diyalog pencereleri
│   ├── features/                # Özellik modülleri
│   │   ├── __init__.py
│   │   ├── bookmarks.py         # Yer imleri
│   │   ├── history.py           # Geçmiş
│   │   ├── downloads.py         # İndirmeler
│   │   ├── ad_blocker.py        # Reklam engelleyici
│   │   ├── password_manager.py  # Parola yöneticisi
│   │   ├── search.py            # Arama yönetimi
│   │   └── reader_mode.py       # Okuma modu
│   ├── utils/                   # Yardımcı araçlar
│   │   ├── __init__.py
│   │   ├── constants.py         # Sabitler
│   │   └── helpers.py           # Yardımcı fonksiyonlar
│   └── resources/               # Kaynaklar
│       ├── icons/
│       └── styles/
├── main.py                      # Ana giriş noktası
├── browser.py                   # Eski basit sürüm (legacy)
├── requirements.txt             # Bağımlılıklar
└── README.md
```

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- PyQt5
- PyQtWebEngine
- cryptography

### Adım Adım Kurulum

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/alpersamur3/Simple-Browser.git
   cd Simple-Browser
   ```

2. **Sanal ortam oluşturun (önerilir):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # veya
   venv\Scripts\activate     # Windows
   ```

3. **Bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Uygulamayı çalıştırın:**
   ```bash
   python main.py
   ```

## 💡 Kullanım

### Temel Kullanım
1. **URL Navigasyonu**: Adres çubuğuna URL veya arama terimi yazın ve Enter'a basın
2. **Yeni Sekme**: `+` düğmesine tıklayın veya `Ctrl+T` kullanın
3. **Gizli Sekme**: Menüden "Gizli Sekme" seçin veya `Ctrl+Shift+N` kullanın

### Yer İmleri
- Sayfayı yer imlerine eklemek için yıldız simgesine tıklayın
- Yer imlerini görüntülemek için yan paneli açın

### Ayarlar
- Menü butonundan (☰) "Ayarlar" seçeneğine tıklayın
- Ana sayfa, arama motoru, tema ve gizlilik ayarlarını özelleştirin

## 🔧 Geliştirme

### Katkıda Bulunma
1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'i push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

### Yeni Özellik Ekleme
Modüler yapı sayesinde yeni özellikler kolayca eklenebilir:
1. `browser/features/` altında yeni modül oluşturun
2. `browser/features/__init__.py` dosyasını güncelleyin
3. `MainWindow` sınıfına entegre edin

## 📜 Lisans

Bu proje MIT Lisansı altında dağıtılmaktadır.

```
MIT License

Copyright (c) 2025 Alper Samur

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**

</div>
