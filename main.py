from pprint import pprint
import json
import requests
import yadisk

#ВК часть

class VK:

   def __init__(self, access_token, user_id, version='5.131'):
       self.token = access_token
       self.id = user_id
       self.version = version
       self.params = {'access_token': self.token, 'v': self.version}

   def users_info(self):
       url = 'https://api.vk.com/method/photos.get'
       params = {'owner_id': self.id, 'album_id': 'profile', 'extended': 1, 'photo_sizes': 1}
       response = requests.get(url, params={**self.params, **params})
       pprint(response.json())


access_token = 'aaa'
user_id = '2114792'
vk = VK(access_token, user_id)
pprint(vk.users_info())


y.mkdir("/test/Hello Word") # Создать папку
y.upload("file1.txt", "/test/file1.txt") # Загружает первый файл
y.upload("file2.txt", "/test/file2.txt") # Загружает второй файл

#Yandex Disk часть
ya_token = 'aaa'
class Yandex:

    def __init__(self, token):
        self.token = token
        self.host = 'https://cloud-api.yandex.net/v1/disk/resources/upload'

    def get_headers(self):
        return {'Content-Type': 'application/json',
                'Authorization': f'OAuth {self.token}'}

    def YandexUpload(self, file):
        upload_link = 'D:\кодики\Kursovaya1'
        headers = self.get_headers()
        response = requests.post(upload_link, data=open(file, 'rb'), headers=headers)
        response.raise_for_status()
        if response.status_code == 201:
            print('Success')

#if __name__ == '__main__':
    #yaya = Yandex(ya_token)
    #yaya.YandexUpload('Ссылки.txt')
