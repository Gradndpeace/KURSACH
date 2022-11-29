from pprint import pprint
import json
import requests
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

access_token = 'vk1.a.1lIASctNapb34kcSjpGl1TXkcZWU2OIEAU8XtRPhmAEwsJG3hL1Q7t6vYDXvXljMU_KS4e5zKXQxVVEmV7NF8YYymmt-lzzHGQY_bsWKTldJvxmqbbW9nY6RgoJjp2R8bB7gDkt5sTxwjNNmMUpwNeUSBWRWjks-CRC6ILY6OX6PdPZdo--PhzkrepSgm0GM0cbO-MwJvhySvoitWUCUCA'
user_id = '2114792'
vk = VK(access_token, user_id)
pprint(vk.users_info())

ya_token = 'y0_AgAAAABe-gmCAADLWwAAAADSa_7eCtVzTHroQjCmXjGX-gvwepPsGGQ'
class Yandex:
    def __init__(self, token):
        self.token = token
        self.host = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    def get_headers(self):
        return {'Content-Type': 'application/json',
                'Authorization': f'OAuth {self.token}'}
    def upload(self):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path':'kursovaya.api/aye.jpg', 'url': 'https://sun9-west.userapi.com/sun9-54/s/v1/if1/7ublsydicwPqq3WjsPivCBonG2qwQ9W1rwOdMPUvUP1KNhzDVo6TAXkN_5dbgcwzG_J14QGg.jpg?size=607x1080&quality=96&type=album'}
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()

if __name__ == '__main__':
    yaya = Yandex(ya_token)
    yaya.upload ()
