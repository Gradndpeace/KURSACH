import datetime
import io
import json
import logging
import typing
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('uploader')

VK_ACCESS_TOKEN = "vk1.a.1lIASctNapb34kcSjpGl1TXkcZWU2OIEAU8XtRPhmAEwsJG3hL1Q7t6vYDXvXljMU_KS4e5zKXQxVVEmV7NF8YYymmt-lzzHGQY_bsWKTldJvxmqbbW9nY6RgoJjp2R8bB7gDkt5sTxwjNNmMUpwNeUSBWRWjks-CRC6ILY6OX6PdPZdo--PhzkrepSgm0GM0cbO-MwJvhySvoitWUCUCA"
YANDEX_TOKEN = "y0_AgAAAABe-gmCAAiNqgAAAADZGdVPz5KFIz3fRQW5e3qNg4ZyLoooNW0"
FOLDER_NAME = 'kursovaya.api'
USER_ID = 21142


class PhotoVKDict(typing.TypedDict):
    url: str
    likes: int
    size: str


class PhotoToUploadDict(typing.TypedDict):
    url: str
    likes: int
    size: str
    file_name: str
    content: io.BytesIO


class VKCollector:

    def __init__(self, access_token: str):
        self._token = access_token

    def get_photos_json(self, user_id: int) -> typing.Iterable[PhotoVKDict]:
        """Метод получает информацию о фотографиях опубликованных на странице пользователя

        :param user_id: VK ID пользователя
        """
        offset: int = 0
        count: int = 1000
        while offset < count:
            response = requests.get(
                "https://api.vk.com/method/photos.get",
                params=dict(
                    v='5.131',
                    access_token=self._token,
                    owner_id=user_id,
                    album_id="profile",
                    extended="1",
                    photo_sizes=1,
                    offset=offset,
                    count=1000
                )
            ).json()
            offset += count
            count = response['response']['count']
            for item in response['response']['items']:
                size = sorted(item['sizes'], key=lambda x: (x['height'], x['width']), reverse=True)[0]
                yield dict(
                    url=size['url'],
                    likes=item.get('likes', {}).get('count', 0),
                    size=size['type']
                )

    def get_photos_to_upload(self, user_id: int) -> typing.Iterable[PhotoToUploadDict]:
        """Функция получает и загружает в память фотографии пользователя

        :param user_id: VK ID пользователя
        """
        logger.info(f"Start download files from {user_id}")
        for photo in self.get_photos_json(user_id):
            content = io.BytesIO(requests.get(photo['url']).content)
            content.seek(0)
            yield dict(
                **photo,
                file_name=str(photo['likes']),
                content=content
            )


class YandexUploader:

    def __init__(self, access_token: str):
        self._token = access_token
        self._uploaded_file_names = []

    def refresh_files(self):
        """Функция получает данные о файлах с сервера Yandex.
        Если не существует папки для загрузки, то эта функция создаст её.
        """
        offset = 0
        response = requests.get(
            'https://cloud-api.yandex.net/v1/disk/resources',
            params={
                'path': FOLDER_NAME,
                'limit': 1000,
                'offset': offset,
                'sort': 'name'
            },
            headers={'Authorization': f'OAuth {self._token}'}
        ).json()
        if 'error' in response and response['error'] == 'DiskNotFoundError':
            requests.put(
                'https://cloud-api.yandex.net/v1/disk/resources',
                params={'path': FOLDER_NAME},
                headers={'Authorization': f'OAuth {self._token}'}
            )
        else:
            need_stop = False
            while not need_stop:
                response = requests.get(
                    'https://cloud-api.yandex.net/v1/disk/resources',
                    params={
                        'path': FOLDER_NAME,
                        'limit': 1000,
                        'offset': offset,
                        'sort': 'name'
                    },
                    headers={'Authorization': f'OAuth {self._token}'}
                ).json()
                offset += 1000
                files = list(
                    filter(
                        lambda x: x.get('mime_type') == 'image/jpeg',
                        response.get('_embedded', {}).get('items', [])
                    )
                )
                if not files:
                    break
                for file in files:
                    if file['name'].replace('.jpg', '').isdigit():
                        self._uploaded_file_names.append(file['name'].replace('.jpg', ''))
                    else:
                        need_stop = True
                        break

    def get_upload_url(self, file: PhotoToUploadDict):
        """Функция получает URL для загрузки файла
        """
        response = requests.get(
            'https://cloud-api.yandex.net/v1/disk/resources/upload',
            params=dict(
                path=f'kursovaya.api/{file["file_name"]}.jpg'
            ),
            headers={'Authorization': f'OAuth {self._token}'}
        ).json()
        return response['href']

    def upload_file(self, file: PhotoToUploadDict):
        """Функция загружает файл на сервера Yandex
        """
        if file['file_name'] in self._uploaded_file_names:
            file['file_name'] = f"{file['file_name']}_{datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S.%f')}"
        logger.info(f"Upload file {file['file_name']}.jpg")
        upload_url = self.get_upload_url(file)
        requests.put(
            upload_url,
            data=file['content'],
            headers={
                'Authorization': f'OAuth {self._token}',
                'Slug': file['file_name'],
                'Content-Type': 'image/jpeg'
            }
        )
        self._uploaded_file_names.append(file['file_name'])
        return {
            'file_name': file['file_name'] + ".jpg",
            'size': file['size']
        }


if __name__ == '__main__':
    uploader = YandexUploader(YANDEX_TOKEN)
    uploader.refresh_files()
    uploaded = []
    for upload_file in VKCollector(VK_ACCESS_TOKEN).get_photos_to_upload(user_id=USER_ID):
        uploaded += [uploader.upload_file(upload_file)]
    with open('uploaded.json', 'w', encoding='utf-8') as json_file:
        json_file.write(json.dumps(uploaded, ensure_ascii=False, indent=2))
