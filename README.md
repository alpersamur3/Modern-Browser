# 🌐 Modern Browser

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-purple.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**Gelişmiş, modern ve güvenli bir web tarayıcısı**

*Python & PyQt5 ile geliştirilmiş, çok dilli, gizli pencere destekli, tam özellikli bir masaüstü tarayıcı.*

</div>

---

## 📋 Genel Bakış

Modern Browser, PyQt5 ve QWebEngineView kullanılarak geliştirilen, tam özellikli bir web tarayıcısıdır. Modüler mimarisi sayesinde kolay genişletilebilir ve özelleştirilebilir yapıdadır. GNU gettext tabanlı çoklu dil desteği, ayrı pencerede açılan gizli tarama modu, gelişmiş indirme yöneticisi ve akıllı reklam engelleyici gibi modern tarayıcı özelliklerini içerir.

## ✨ Özellikler

### 🔖 Temel Özellikler
- **Sekmeli Tarama**: Çoklu sekme desteği, sekme sabitleme, sessize alma, sürükle-bırak
- **Yeni Pencere**: `Ctrl+N` ile yeni tarayıcı penceresi açma
- **Yer İmleri**: Klasörlerle organize edilebilen yer imi yönetimi
- **Geçmiş**: Kapsamlı tarama geçmişi yönetimi ve temizleme
- **İndirmeler**: Gelişmiş indirme yöneticisi (ilerleme takibi, dosya açma, iptal)
- **Sayfa Kaynağı Görüntüleme**: Syntax-highlighted kaynak kodu görüntüleme

### 🔒 Gizlilik ve Güvenlik
- **Gizli Pencere**: `Ctrl+Shift+N` ile ayrı pencerede gizli tarama — tüm sekmeler gizli, görsel olarak belirgin (mor banner ve ikon)
- **Reklam Engelleyici**: Yerleşik reklam ve izleyici engelleme (Google Ads, DoubleClick vb.)
- **Parola Yöneticisi**: Şifreli parola saklama (cryptography kütüphanesi ile)
- **HTTPS Göstergesi**: Güvenli bağlantı durumu kilit ikonu ile gösterim
- **Do Not Track**: İsteğe bağlı izleme engellemesi
- **Çıkışta Veri Temizleme**: Otomatik geçmiş/çerez temizleme seçeneği

### 🌍 Çoklu Dil Desteği (i18n)
- **GNU gettext tabanlı**: `.po` / `.mo` dosyaları ile profesyonel çeviri altyapısı
- **Desteklenen Diller**: Türkçe 🇹🇷, English 🇬🇧, Deutsch 🇩🇪, Français 🇫🇷, Español 🇪🇸
- **Anlık Dil Değiştirme**: Ayarlardan dil değiştirince menüler ve arayüz anında güncellenir
- **Kolay Genişletme**: Yeni dil eklemek için `locales/<dil_kodu>/LC_MESSAGES/messages.po` dosyası oluşturup derlemek yeterli

### 🎨 Görünüm
- **Karanlık Mod**: Göz yormayan karanlık tema (tüm UI bileşenlerinde)
- **Modern Arayüz**: Şık, yuvarlatılmış köşeler, animasyonlu geçişler
- **Özelleştirilebilir**: Tema, yazı tipi, durum çubuğu ve yer imi çubuğu gösterimi ayarları
- **Gizli Pencere Teması**: Mor banner ve özel ikon ile gizli modun açıkça belirtilmesi

### 🛠️ Araçlar
- **Sayfa İçi Arama**: `Ctrl+F` ile hızlı arama (büyük/küçük harf duyarlı)
- **Zoom Kontrolü**: Yakınlaştırma/uzaklaştırma (%25 - %500 arası)
- **Okuma Modu**: Dikkat dağıtmayan, sade okuma deneyimi
- **Ekran Görüntüsü**: Sayfa görüntüsü PNG/JPEG olarak kaydetme
- **Yazdırma**: Sayfa yazdırma desteği
- **Kaynak Görüntüleme**: Karanlık temalı, monospace font ile sayfa kaynak kodu
- **Geliştirici Araçları**: DevTools desteği (`F12`)

### ⌨️ Klavye Kısayolları
| Kısayol | İşlev |
|---------|-------|
| `Ctrl+T` | Yeni sekme |
| `Ctrl+N` | Yeni pencere |
| `Ctrl+Shift+N` | Yeni gizli pencere |
| `Ctrl+W` | Sekmeyi kapat |
| `Ctrl+Shift+T` | Kapatılan sekmeyi aç |
| `Ctrl+Tab` | Sonraki sekme |
| `Ctrl+Shift+Tab` | Önceki sekme |
| `Ctrl+L` | Adres çubuğuna odaklan |
| `Ctrl+F` | Sayfada bul |
| `Ctrl+D` | Yer imi ekle/kaldır |
| `Ctrl+Shift+B` | Yer imleri paneli |
| `Ctrl+H` | Geçmiş paneli |
| `Ctrl+J` | İndirmeler paneli |
| `Ctrl++` | Yakınlaştır |
| `Ctrl+-` | Uzaklaştır |
| `Ctrl+0` | Zoom sıfırla |
| `F5` | Yenile |
| `Ctrl+F5` | Önbellek atla + yenile |
| `F11` | Tam ekran |
| `F12` | Geliştirici araçları |
| `Ctrl+U` | Kaynak görüntüle |
| `Ctrl+P` | Yazdır |
| `Ctrl+Shift+S` | Ekran görüntüsü |
| `Ctrl+Shift+R` | Okuma modu |
| `Ctrl+,` | Ayarlar |
| `Ctrl+Q` | Çıkış |

## 📁 Proje Yapısı

```
Modern-Browser/
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
│   └── utils/                   # Yardımcı araçlar
│       ├── __init__.py
│       ├── constants.py         # Sabitler ve temalar
│       ├── helpers.py           # Yardımcı fonksiyonlar
│       └── i18n.py              # Çoklu dil desteği (gettext)
├── locales/                     # Çeviri dosyaları
│   ├── tr/LC_MESSAGES/          # Türkçe
│   │   ├── messages.po
│   │   └── messages.mo
│   └── en/LC_MESSAGES/          # İngilizce
│       ├── messages.po
│       └── messages.mo
├── resources/
│   └── icons/                   # SVG ikonlar
├── main.py                      # Ana giriş noktası
├── compile_translations.py      # Çeviri derleme aracı
├── requirements.txt             # Bağımlılıklar
└── README.md
```

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- PyQt5 >= 5.15.0
- PyQtWebEngine >= 5.15.0
- cryptography >= 3.4.0

### Adım Adım Kurulum

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/alpersamur3/Modern-Browser.git
   cd Modern-Browser
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

4. **Çevirileri derleyin:**
   ```bash
   python compile_translations.py
   ```

5. **Uygulamayı çalıştırın:**
   ```bash
   python main.py
   ```

## 💡 Kullanım

### Temel Kullanım
1. **URL Navigasyonu**: Adres çubuğuna URL veya arama terimi yazın ve Enter'a basın
2. **Yeni Sekme**: `+` düğmesine tıklayın veya `Ctrl+T` kullanın
3. **Yeni Pencere**: Araç çubuğundaki pencere düğmesine tıklayın veya `Ctrl+N` kullanın
4. **Gizli Pencere**: Menüden "Yeni Gizli Pencere" seçin veya `Ctrl+Shift+N` kullanın — ayrı pencerede açılır, tüm sekmeler gizlidir

### Gizli Tarama
- Gizli pencerede açılan tüm sekmeler otomatik olarak gizli moddadır
- Gizli pencere mor banner ile belirgin şekilde işaretlenir
- Gizli sekmelerde göz ikonu ve mor renk kullanılır
- Tarama geçmişi, çerezler ve site verileri kaydedilmez

### Yer İmleri
- Sayfayı yer imlerine eklemek için yıldız simgesine tıklayın (`Ctrl+D`)
- Yer imlerini görüntülemek için yan paneli açın (`Ctrl+Shift+B`)

### İndirmeler
- Sayfadaki indirme bağlantılarına tıklayın — otomatik olarak indirilir
- İndirme durumu toast bildirimi ile gösterilir
- İndirmeleri yan panelden yönetin (`Ctrl+J`)
- Tamamlanan indirmeleri doğrudan açabilir veya klasörünü görebilirsiniz

### Dil Değiştirme
- Menü → Ayarlar → Genel sekmesinden "Dil" seçeneğini değiştirin
- Dil değişikliği anında uygulanır, menüler ve araç çubuğu güncellenir

### Ayarlar
- Menü butonundan (☰) "Ayarlar" seçeneğine tıklayın (`Ctrl+,`)
- **Genel**: Ana sayfa, arama motoru, dil, başlangıç davranışı
- **Görünüm**: Karanlık mod, yer imi çubuğu, durum çubuğu
- **Gizlilik**: Do Not Track, parola kaydetme, çıkışta temizleme
- **Güvenlik**: Reklam engelleyici, HTTPS zorlama, JavaScript ayarları
- **İndirmeler**: İndirme klasörü, konum sorma seçeneği

## 🌐 Çeviri Ekleme

Yeni bir dil eklemek için:

1. `locales/<dil_kodu>/LC_MESSAGES/` klasörünü oluşturun
2. Mevcut bir `.po` dosyasını kopyalayıp çevirin:
   ```bash
   mkdir -p locales/de/LC_MESSAGES
   cp locales/en/LC_MESSAGES/messages.po locales/de/LC_MESSAGES/messages.po
   ```
3. `messages.po` dosyasındaki `msgstr` değerlerini çevirin
4. Çevirileri derleyin:
   ```bash
   python compile_translations.py
   ```
5. `browser/utils/i18n.py` içindeki `get_available_languages()` fonksiyonuna yeni dili ekleyin

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

### Mimari
- **Singleton Pattern**: `BrowserEngine`, `DownloadManager`, `SettingsManager` tek örnek olarak çalışır
- **Signal/Slot**: PyQt5 sinyal mekanizması ile bileşenler arası iletişim
- **MVC Benzeri**: `core/` (model), `ui/` (view/controller), `features/` (servisler)
- **gettext i18n**: Tüm UI metinleri `tr()` fonksiyonu ile çevrilebilir

### Ekran Görüntüleri

<img width="460" height="453" alt="Ekran görüntüsü 2026-02-11 111841" src="https://github.com/user-attachments/assets/11e1e104-1a47-4f67-af3d-144e7bec0695" />
<img width="1919" height="1140" alt="Ekran görüntüsü 2026-02-11 111830" src="https://github.com/user-attachments/assets/2714f67b-c855-4bcd-a50f-ae711ea08060" />
<img width="1919" height="1139" alt="Ekran görüntüsü 2026-02-11 111800" src="https://github.com/user-attachments/assets/40c8ea12-fc7c-4112-8649-dcfedc6970df" />
<img width="1919" height="1140" alt="Ekran görüntüsü 2026-02-11 111750" src="https://github.com/user-attachments/assets/abe52029-f118-4542-aae8-cdee08c6f006" />



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
