import requests
from bs4 import BeautifulSoup
import os

episode = 1
while(episode<=179):
    url = "https://mangakeyfi.net/manga/solo-leveling/bolum-{}/".format(episode)

    response = requests.get(url)  # Web sayfasını çekme
    html = response.content  # Sayfa içeriği
    soup = BeautifulSoup(html, "html.parser")  # Sayfa parçalandı

    imgIndex = 0
    os.mkdir("episode{}".format(episode))
    print("episode{} klasörü oluşturuldu".format(episode))
    for i in soup.find_all("img", {"class": "wp-manga-chapter-img"}):
        imgUrl = i.get("src")
        responseImg = requests.get(imgUrl)
        fileName = "{}.{}".format(imgIndex, "jpg")

        file = open('episode{}/{}'.format(episode, fileName), "wb")
        file.write(responseImg.content)
        file.close()

        print("{} Kaydedildi".format(fileName))
        imgIndex += 1
    episode+=1