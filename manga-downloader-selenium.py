from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
from PIL import Image
import os
import shutil
import time


def download_episode(driver, episode_num):
    """Tek bir bölümü indir"""
    try:
        # Web sitesini aç
        url = f"https://turkcemangaoku.com.tr/manga/solo-leveling-ragnarok/bolum-{episode_num}/"
        driver.get(url)
        print(f"Bölüm {episode_num} yükleniyor: {url}")

        # Sayfa yüklenmesini bekle
        time.sleep(10)

        # Resimleri bul
        resimler = driver.find_elements(By.CLASS_NAME, "wp-manga-chapter-img")

        if not resimler:
            print(f"Bölüm {episode_num} için resim bulunamadı!")
            return False

        print(f"Bölüm {episode_num}: {len(resimler)} resim bulundu")

        # Bölüm klasörünü oluştur
        bolum_klasoru = f"episode{episode_num}"
        if not os.path.exists(bolum_klasoru):
            os.mkdir(bolum_klasoru)

        imgIndex = 0
        belgeList = []

        # Her resmi indir
        for resim in resimler:
            try:
                # Resim URL'sini al
                imgUrl = resim.get_attribute("src")
                if not imgUrl:
                    imgUrl = resim.get_attribute("data-src")  # Lazy loading için

                if imgUrl:
                    # Resmi indir
                    responseImg = requests.get(imgUrl, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })

                    if responseImg.status_code == 200:
                        fileName = f"{imgIndex}.jpg"
                        dosya_yolu = f'{bolum_klasoru}/{fileName}'

                        with open(dosya_yolu, "wb") as file:
                            file.write(responseImg.content)

                        print(f"  {fileName} kaydedildi")
                        belgeList.append(imgIndex)
                        imgIndex += 1

            except Exception as e:
                print(f"  Resim indirme hatası: {e}")
                continue

        # PDF oluştur
        if belgeList:
            belgeList.sort()
            imgPathList = []
            imgList = []

            for i in belgeList:
                try:
                    img_path = f'{bolum_klasoru}/{i}.jpg'
                    img = Image.open(img_path)

                    if i == 0:
                        img0 = img.convert('RGB')
                    else:
                        imgList.append(img.convert('RGB'))

                except Exception as e:
                    print(f"  Resim açma hatası: {e}")
                    continue

            # PDF olarak kaydet
            if 'img0' in locals():
                pdf_yolu = f'manga/{episode_num}.pdf'
                if imgList:
                    img0.save(pdf_yolu, save_all=True, append_images=imgList)
                else:
                    img0.save(pdf_yolu)
                print(f"  {episode_num}.pdf kaydedildi")

            # Geçici klasörü sil
            shutil.rmtree(bolum_klasoru)
            return True
        else:
            print(f"  Bölüm {episode_num} için indirilebilir resim bulunamadı")
            if os.path.exists(bolum_klasoru):
                shutil.rmtree(bolum_klasoru)
            return False

    except Exception as e:
        print(f"Bölüm {episode_num} hatası: {e}")
        return False


# Ana manga klasörünü oluştur
if not os.path.exists("manga"):
    os.mkdir("manga")

# Chrome driver'ı otomatik olarak indir ve kur
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    # İndirilecek bölüm aralığı
    baslangic_bolum = 1
    bitis_bolum = 47  # Örnek olarak 5 bölüm

    for episode in range(baslangic_bolum, bitis_bolum + 1):
        print(f"\n--- Bölüm {episode} indiriliyor ---")

        success = download_episode(driver, episode)

        if success:
            print(f"Bölüm {episode} başarıyla indirildi")
        else:
            print(f"Bölüm {episode} indirilemedi")

        # Bölümler arası bekleme süresi (site yükünü azaltmak için)
        time.sleep(3)

except Exception as e:
    print(f"Genel hata: {e}")

finally:
    # Browser'ı kapat
    driver.quit()
    print("\nTüm işlemler tamamlandı ve tarayıcı kapatıldı")