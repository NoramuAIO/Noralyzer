# Noralyzer - Kişisel Finans ve Bütçe Takip Uygulaması

Noralyzer, kişisel gelir ve giderlerinizi takip etmenizi, bütçenizi yönetmenizi ve finansal durumunuzu görselleştirmenizi sağlayan modern, kullanıcı dostu bir web uygulamasıdır.

![Noralyzer Dashboard](https://via.placeholder.com/1200x600?text=Noralyzer+Dashboard+Preview)

## 🚀 Özellikler

### Temel Özellikler
- **Detaylı İşlem Takibi:** Gelir, gider, transfer ve varlık alım/satım işlemlerini kolayca kaydedin
- **Gelişmiş Dashboard:** Anlık bakiye durumu, son işlemler ve kategori bazlı harcama dağılımı
- **Raporlar & Analizler:** Aylık gelir/gider trendleri, kategori bazlı detaylı harcama analizleri
- **Varlık Yönetimi:** Nakit, Banka Hesapları, Kredi Kartları, Kripto Para ve Altın takibi
- **Kişi & Borç Takibi:** Aile bireyleri veya arkadaşlarla olan para trafiğini yönetin
- **Bütçe & Hedefler:** Harcama limitleri belirleyin ve tasarruf hedeflerinizi takip edin
- **Mekan/Yer Yönetimi:** Harcamaların nerede yapıldığını kaydedin
- **Hızlı İşlemler:** Sık kullanılan işlemler için şablon sistemi
- **Veri Yedekleme:** JSON formatında dışa/içe aktarma

### v1.1.0 - Yeni Özellikler

#### 🏗️ Modüler Mimari
Uygulama artık Flask Blueprints kullanarak modüler bir yapıya sahip:
- **Ayrıştırılmış Route'lar:** Her modül kendi blueprint'inde (transactions, banks, cards, vb.)
- **App Factory Pattern:** Test edilebilir ve genişletilebilir yapı
- **Temiz Kod Organizasyonu:** models.py, utils.py, routes/ ayrımı

#### 💾 Veritabanı Konfigürasyonu
Tüm konfigürasyon verileri artık veritabanında:
- **Para Birimleri (Currency):** TRY, USD, EUR, BTC, Altın vb. - dinamik yönetim
- **İşlem Tipleri (TransactionType):** Harcama, Gelir, Transfer vb. - özelleştirilebilir
- **Varsayılan Kategoriler:** Veritabanından yüklenen kategori şablonları

#### 🎨 Abyss Ultra Modern UI
- Koyu tema (Dark Mode)
- Glassmorphism efektleri
- Neon aksanlar ve gradientler
- Responsive tasarım

## 🛠️ Teknolojiler

| Kategori | Teknoloji |
|----------|-----------|
| Backend | Python 3.x, Flask 3.0.0 |
| Veritabanı | SQLite, Flask-SQLAlchemy 3.1.1 |
| Frontend | HTML5, CSS3, JavaScript |
| Grafikler | Chart.js |
| İkonlar | Bootstrap Icons |
| Fontlar | Google Fonts (Outfit, Inter) |

## ⚙️ Kurulum

1. **Repoyu Klonlayın:**
   ```bash
   git clone https://github.com/kullaniciadi/noralyzer.git
   cd noralyzer
   ```

2. **Sanal Ortam Oluşturun:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Bağımlılıkları Yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Uygulamayı Çalıştırın:**
   ```bash
   python run.py
   ```

5. **Tarayıcıda Açın:**
   ```
   http://127.0.0.1:5000
   ```

## 📊 Veritabanı Modelleri

### Ana Modeller
- `Bank` - Banka hesapları
- `Card` - Kredi/Banka kartları
- `Person` - Kişiler (borç/alacak takibi)
- `Place` - Mekanlar
- `Transaction` - İşlemler
- `Category` - Kategoriler
- `Tag` - Etiketler
- `Budget` - Bütçeler
- `SavingGoal` - Tasarruf hedefleri
- `QuickTransaction` - Hızlı işlem şablonları

### Konfigürasyon Modelleri
- `Currency` - Para birimleri (code, name, symbol, type)
- `TransactionType` - İşlem tipleri (code, name)
- `Setting` - Uygulama ayarları

## 📸 Ekran Görüntüleri

| Dashboard | İşlem Ekleme |
|-----------|--------------|
| ![Dashboard](https://via.placeholder.com/400x300?text=Dashboard) | ![Add Transaction](https://via.placeholder.com/400x300?text=Islem+Ekle) |

| Raporlar | Ayarlar |
|----------|---------|
| ![Reports](https://via.placeholder.com/400x300?text=Raporlar) | ![Settings](https://via.placeholder.com/400x300?text=Ayarlar) |

## 🗺️ Yol Haritası

- [ ] Kullanıcı kimlik doğrulama (Login/Register)
- [ ] Flask-Migrate ile veritabanı migrasyonları
- [ ] REST API endpoints
- [ ] Döviz kuru API entegrasyonu
- [ ] PWA desteği (offline çalışma)
- [ ] Mobil uygulama

## 🤝 Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/YeniOzellik`)
3. Commit'leyin (`git commit -m 'Yeni özellik eklendi'`)
4. Push'layın (`git push origin feature/YeniOzellik`)
5. Pull Request açın

## 📝 Lisans

Bu proje [MIT](LICENSE) lisansı ile lisanslanmıştır.

---

_Noralyzer - Finansal Özgürlüğünüzü Yönetin._
