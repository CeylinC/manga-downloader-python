import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://blueperiodchapters.website"
BASE_OUTPUT_DIR = "manga/Blue-Period"


def update_session_from_driver(driver, session):
    """Tarayıcıdaki güncel çerezleri ve başlıkları requests oturumuna aktarır."""
    for cookie in driver.get_cookies():
        session.cookies.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get("domain")
        )

    session.headers.update({
        "User-Agent": driver.execute_script("return navigator.userAgent"),
        "Referer": driver.current_url
    })


def download_episode(driver, session, episode_num):
    """Belirtilen bölüme ait görselleri indirir."""
    chapter_url = f"{BASE_URL}/manga/blue-period-chapter-{episode_num}/"
    output_dir = os.path.join(BASE_OUTPUT_DIR, f"Chapter-{episode_num}")
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n--- Chapter {episode_num} ---")
    print("İlk URL:", chapter_url)
    driver.get(chapter_url)

    # Sayfanın ve olası yönlendirmelerin tamamlanmasını bekle
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("Son URL:", driver.current_url)

    # Güncel sayfa bilgileriyle oturumu tazele
    update_session_from_driver(driver, session)

    # Lazy loading görsellerinin yüklenmesi için sayfayı kaydır
    images = driver.find_elements(By.CSS_SELECTOR, "img[alt]")
    for img in images:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", img)
        time.sleep(0.3)

    # Yüklenen görsellerin URL'lerini topla
    images = driver.find_elements(By.CSS_SELECTOR, "img[alt]")
    image_data = []
    target_alt_prefix = f"Blue Period Chapter {episode_num} image"

    for img in images:
        src = img.get_attribute("currentSrc") or img.get_attribute("src")
        alt = img.get_attribute("alt") or ""

        if src and target_alt_prefix in alt:
            image_data.append((src, alt))

    print(f"Bulunan görsel sayısı: {len(image_data)}")

    extensions = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif"
    }

    for index, (url, alt) in enumerate(image_data, start=1):
        try:
            response = session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
            extension = extensions.get(content_type)

            if not extension:
                print(f"Atlandı: {alt} ({content_type})")
                continue

            filename = f"{index:03d}{extension}"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "wb") as file:
                file.write(response.content)

            print(f"Kaydedildi: {filename}")
            time.sleep(0.5)

        except requests.RequestException as error:
            print(f"İndirme hatası ({alt}): {error}")


def main():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    session = requests.Session()

    try:
        # 1-93 arası bölümler
        for episode in range(12, 94):
            download_episode(driver, session, episode)
            time.sleep(3)
    finally:
        driver.quit()
        print("\nTüm işlemler tamamlandı.")


if __name__ == "__main__":
    main()