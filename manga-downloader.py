import requests #Veri Çekme
from bs4 import BeautifulSoup #Veri Çekme
from PIL import Image #Convert JPG to PDF
import os #Create File
import shutil #Delete File

episode = 1

while(episode<=1):
    url = "https://mangakeyfi.net/manga/seoul-stations-necromancer/bolum-{}/".format(episode)

    response = requests.get(url)  # Web sayfasını çekme
    html = response.content  # Sayfa içeriği
    soup = BeautifulSoup(html, "html.parser")  # Sayfa parçalandı

    imgIndex = 0
    belgeList = []

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
        belgeList.append(imgIndex)
        imgIndex += 1
    belgeList.sort()

    imgPathList = []
    imgList = []
    for i in belgeList:
        imgPathList.append(
            Image.open(r'episode{}/{}.jpg'.format(episode, i)))
        if (i == 0):
            img0 = imgPathList[i].convert('RGB')
            continue
        imgList.append(imgPathList[i].convert('RGB'))
    img0.save(r'manga\{}.pdf'.format(episode), save_all=True, append_images=imgList)
    print("{}.pdf kaydedildi".format(episode))
    shutil.rmtree('episode{}'.format(episode))
    episode = episode + 1