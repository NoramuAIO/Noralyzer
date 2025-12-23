# Noralyzer - Kişisel Finans ve Bütçe Takip Uygulaması

Noralyzer, kişisel gelir ve giderlerinizi takip etmenizi, bütçenizi yönetmenizi ve finansal durumunuzu görselleştirmenizi sağlayan modern, kullanıcı dostu bir web uygulamasıdır.

![Noralyzer Dashboard](https://hizliresim.com/6ajv0rx)

## 🚀 Özellikler

- **Detaylı İşlem Takibi:** Gelir, gider, transfer ve varlık alım/satım işlemlerini kolayca kaydedin.
- **Gelişmiş Dashboard:** Anlık bakiye durumu, son işlemler ve kategori bazlı harcama dağılımını tek ekranda görün.
- **Raporlar & Analizler:**
  - Aylık gelir/gider trendleri.
  - Kategori bazlı detaylı harcama analizleri.
  - Tarih ve kategori filtreleme seçenekleri.
- **Varlık Yönetimi:**
  - Nakit, Banka Hesapları ve Kredi Kartları.
  - Kripto Para ve Altın takibi desteği.
- **Kişi & Borç Takibi:** Aile bireyleri veya arkadaşlarla olan para trafiğini yönetin (Kime/Kimden).
- **Bütçe & Hedefler:** Harcama limitleri belirleyin ve tasarruf hedeflerinizi takip edin.
- **Mekan/Yer Yönetimi:** Harcamaların nerede yapıldığını kaydedin.
- **Veri Yedekleme:** Veritabanını yedekleme, geri yükleme ve sıfırlama özellikleri.
- **Responsive Tasarım:** Mobil ve masaüstü uyumlu modern arayüz (Dark Mode estetiği).

## 🛠️ Teknolojiler

- **Backend:** Python, Flask
- **Veritabanı:** SQLite, SQLAlchemy
- **Frontend:** HTML5, CSS3 (Modern Variables & Flexbox/Grid), JavaScript
- **Grafikler:** Chart.js
- **İkonlar:** Bootstrap Icons (BI)
- **Fontlar:** Google Fonts (Outfit & Inter)

## ⚙️ Kurulum

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin:

1.  **Repoyu Klonlayın:**

    ```bash
    git clone https://github.com/noramuAIO/noralyzer.git
    cd noralyzer
    ```

2.  **Sanal Ortam (Virtual Environment) Oluşturun:**

    ```bash
    python -m venv venv

    # Windows
    venv\Scripts\activate

    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Gerekli Kütüphaneleri Yükleyin:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Uygulamayı Çalıştırın:**

    ```bash
    python app.py
    ```

5.  **Tarayıcıda Açın:**
    Tarayıcınızda `http://127.0.0.1:5000` adresine gidin.

## 📸 Ekran Görüntüleri

| Dashboard                                                        | İşlem Ekleme                                                            |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------- |
| ![Dashboard](https://hizliresim.com/6ajv0rx) | ![Add Transaction](https://hizliresim.com/i7r1r28) |

| Raporlar                                                      | Kişiler                                                      |
| ------------------------------------------------------------- | ------------------------------------------------------------ |
| ![Reports](https://hizliresim.com/oyvah4v) | ![Persons](https://hizliresim.com/55k3bpf) |

## 🤝 Katkıda Bulunma

Katkıda bulunmak isterseniz, lütfen bir "issue" açın veya "pull request" gönderin. Her türlü katkıya açığız!

1.  Forklayın
2.  Feature branch oluşturun (`git checkout -b feature/YeniOzellik`)
3.  Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4.  Branch'inizi pushlayın (`git push origin feature/YeniOzellik`)
5.  Pull Request oluşturun

## 📝 Lisans

Bu proje [MIT](LICENSE) lisansı ile lisanslanmıştır.

---

_Noralyzer - Finansal Özgürlüğünüzü Yönetin._
