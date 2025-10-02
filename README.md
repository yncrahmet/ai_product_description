# Yapay Zeka Destekli Ürün Açıklaması Paneli

Ürünlerinizi web arayüzü üzerinden anında, dikkat çekici ve SEO uyumlu açıklamalarla dijital vitrine taşıyın.

[![Son Güncelleme](https://img.shields.io/badge/Son%20G%C3%BCncelleme-01.01.2025-blue?style=flat-square&logo=github)](https://github.com/yncrahmet/ai_product_description) [![Ana Dil](https://img.shields.io/badge/Ana%20Dil-Python%20%F0%9F%90%8D-informational?style=flat-square&logo=python)](https://www.python.org/) [![Dil Sayısı](https://img.shields.io/badge/Dil%20Say%C4%B1s%C4%B1-2-yellow?style=flat-square)](https://github.com/yncrahmet/ai_product_description/search?l=) [![Lisans](https://img.shields.io/badge/Lisans-MIT%20%F0%9F%93%8C-success?style=flat-square)](LICENSE) [![Derleme Durumu](https://img.shields.io/badge/Derleme-Ge%C3%A7ti%20%E2%9C%85-brightgreen?style=flat-square&logo=github-actions)](https://github.com/yncrahmet/ai_product_description/actions)

---

## 1. Genel Bakış

**Yapay Zeka Destekli Ürün Açıklaması Paneli**, e-ticaret profesyonelleri için tasarlanmış, **kullanımı kolay web arayüzü** ile çalışan bir açıklama üretim aracıdır. Projenin amacı, Yapay Zeka'nın gücünü kullanarak ürün özelliklerini saniyeler içinde pazarlama odaklı, **SEO uyumlu metinlere** dönüştürmektir.

Bu sistem, web tabanlı arayüzü sayesinde, kod bilgisi olmayan kullanıcıların dahi ürün açıklamalarını kolayca yönetmesini, tonunu ayarlamasını ve toplu işlemler yapmasını sağlar.

**Hedef Kitle:** E-ticaret yöneticileri, dijital pazarlama uzmanları ve hızlı, ölçeklenebilir içerik çözümlerine ihtiyaç duyan küçük/orta ölçekli işletmeler.

---

## 2. Ana Özellikler

Projenin temel teknik ve fonksiyonel öne çıkanları şunlardır:

* **Kullanıcı Dostu Web Paneli:** HTML/Template tabanlı arayüz ile kolay veri girişi, sonuçları anlık görüntüleme ve çıktıyı kopyalama imkanı.
* **Sunucu Tarafında Yapay Zeka İşleme:** Arka planda **Python (Flask/Django)** ile yürütülen yapay zeka entegrasyonu sayesinde hızlı ve güvenilir sonuçlar.
* **SEO ve Ton Ayarları:** Kullanıcı arayüzünden doğrudan anahtar kelime ve metin tonu seçimi ile çıktıları özelleştirme yeteneği.
* **Toplu Üretim Modülü:** CSV/Excel dosyası yükleyerek tüm ürün kataloğu için tek seferde açıklama üretme ve indirme imkanı.

---

## 3. Kuruluma Başlarkan

Projenin bir web uygulaması olması nedeniyle kurulum ve çalıştırma için **Docker** kullanımı önerilmektedir.

### Ön Hazırlık

Bu yazılımı çalıştırmak için aşağıdaki gereksinimlere ihtiyacınız vardır:

* **Docker ve Docker Compose** (Ortam bağımlılıklarını izole etmek için)
* Gerekli Yapay Zeka sağlayıcısı için geçerli bir **API Anahtarı** (Örn: `GEMINI_API_KEY`).

### Installation steps with commands

1.  **Repoyu Klonlayın:**
    ```bash
    git clone https://github.com/yncrahmet/ai_product_description.git
    cd ai_product_description
    ```
2.  **Ortam Değişkenlerini Ayarlayın:**
    Proje ana dizininde bulunan `.env` dosyasında gerekli bilgileri girin.
    
3.  **Docker ile Uygulamayı Başlatın:**
    ```bash
    docker-compose up --build -d
    ```

### Örneklerle Kullanımı

Uygulama başarıyla başlatıldıktan sonra:

1.  Web tarayıcınızı açın ve `http://localhost:8000` adresine gidin (Docker Compose yapılandırmasına bağlı olarak port değişebilir).
2.  Panelde yer alan ilgili alanlara (Ürün Adı, Temel Özellikler, Anahtar Kelimeler) verileri girin.
3.  İstediğiniz **Açıklama Tonunu** (Örn: Satış Odaklı) seçin.
4.  "Açıklama Oluştur" butonuna tıklayarak sonucu anında görün ve kopyalayın.

### Test talimatları

Uygulama testleri, Docker ortamı içinden çalıştırılmalıdır.

1.  Çalışan konteynerin içine girin:
    ```bash
    docker exec -it ai_desc_app /bin/bash 
    ```
2.  Test komutunu çalıştırın:
    ```bash
    pytest
    ```

---

## 4. Kullanılan Teknolojiler

| Teknoloji | Seçim Nedeni |
| :--- | :--- |
| **Python** | Arka uçta yapay zeka entegrasyonu, API yönetimi ve veri işleme için ideal, güçlü bir dil. |
| **Flask / FastAPI** | Projenin web paneline hizmet veren **hızlı ve hafif** bir arka uç API çerçevesi sağlamak için (Web arayüzü bilgisine istinaden varsayılmıştır). |
| **HTML/CSS Templates** | Kullanıcı dostu ve görsel olarak çekici bir **arayüz (panel)** sunmak için. |
| **Docker / Docker Compose** | Geliştirme ve dağıtım ortamları arasında tutarlılığı sağlamak, bağımlılıkları kolayca yönetmek için. |

---

## 5. Katkı Kuralları

Bu projeye katkıda bulunabilirsiniz! Lütfen aşağıdaki standart akışı izleyerek katkı sağlamayı düşünün:

1.  Projeyi **Fork** edin.
2.  Yeni özellik için bir **branch** oluşturun (`git checkout -b feature/panel-ozelligi`).
3.  Değişikliklerinizi yapın ve anlamlı bir mesajla **commit** edin (`git commit -m 'feat: Arayüze yeni bir özellik eklendi'`).
4.  Branch'inizi **push** edin (`git push origin feature/panel-ozelligi`).
5.  GitHub üzerinden bir **Pull Request (PR)** açın ve değişikliklerinizi açıkça açıklayın.

## 6. Lisans Bilgileri

Bu proje, kaynak kodun ticari amaçlarla kullanılmasını kesinlikle yasaklayan **PolyForm Noncommercial License 1.0.0** altında lisanslanmıştır.

Bu lisans size şunları sağlar:
* Kaynak kodu inceleme, değiştirme ve özel (non-commercial) projelerinizde kullanma hakkı.
* Ancak, kodun veya türevlerinin **ticari amaçla dağıtılması, satılması veya hizmet olarak sunulması kesinlikle yasaktır.**

Daha fazla detay için lütfen `LICENSE` dosyasındaki lisans metninin tamamını inceleyin.


## 7. iLETİŞİM

Proje sahibi ile iletişime geçmek için aşağıdaki bilgileri kullanabilirsiniz:

| Rol | Bilgi |
| :--- | :--- |
| Proje Sahibi | yncrahmet |
| GitHub Profil | [https://github.com/yncrahmet](https://github.com/yncrahmet) |
