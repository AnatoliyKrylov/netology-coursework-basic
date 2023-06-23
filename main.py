import time
import requests
import json
from PIL import Image


def yauploaderfromvk(vkid, ya_token, count=5):
    res_data = []
    # получаем токен для ВК из файла
    with open('vk_token.txt', 'r') as file_object:
        token = file_object.read().strip()
    vk_url = 'https://api.vk.com/method/photos.get'
    vk_params = {
        'owner_id': vkid,
        'access_token': token,
        'album_id': 'profile',
        'extended': '1',
        'count': count,
        'v': '5.131'
    }
    vk_res = requests.get(vk_url, params=vk_params).json()
    if vk_res.get('error') is None:
        print(f'Результат от VK получен.')
        ya_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        ya_params = {
            'path': f'VK ID{vkid} {int(time.time())}'
        }
        ya_headers = {
            'Authorization': ya_token
        }
        create_folder_response = requests.put(ya_url, headers=ya_headers, params=ya_params)
        if 200 <= create_folder_response.status_code < 300:
            ya_url += '/upload'
            for item in vk_res['response']['items']:
                max_height = 0
                max_size_url = ''
                size_type = ''
                for size in item['sizes']:
                    time.sleep(0.33)
                    if 200 <= requests.get(size['url']).status_code < 300:
                        if Image.open(requests.get(size['url'], stream=True).raw).size[0] > max_height:
                            max_height = Image.open(requests.get(size['url'], stream=True).raw).size[0]
                            max_size_url = size['url']
                            size_type = size['type']
                    else:
                        print(f'Фото {item["likes"]["count"]}.jpg не будет загружено. '
                              f'Ошибка {requests.get(size["url"]).status_code}')
                        continue
                if max_size_url:
                    file_name = item['likes']['count']
                    ya_params['url'] = max_size_url
                    ya_params['path'] = ya_params['path'].split('/')[0] + f'/{file_name}.jpg'
                    upload_photo_response = requests.post(ya_url, headers=ya_headers, params=ya_params)
                    if 200 <= upload_photo_response.status_code < 300:
                        res_data.append({'file_name': f"{file_name}.jpg", 'size': size_type})
                        print(f'Фото {file_name}.jpg успешно загружено на Яндекс Диск '
                              f'в папку {ya_params["path"].split("/")[0]}')
                    else:
                        print(f'Не удалось загрузить фото {file_name}.jpg в Яндекс Диск. '
                              f'Ошибка {upload_photo_response.status_code}: {upload_photo_response.json()["message"]}')
                    with open('result.json', 'w') as f:
                        json.dump(res_data, f)
        else:
            print(f'Не удалось создать папку в Яндекс Диске. '
                  f'Ошибка {create_folder_response.status_code}: {create_folder_response.json()["message"]}')
    else:
        print(f'Результат от VK не получен. Ошибка {vk_res["error"]["error_code"]}: {vk_res["error"]["error_msg"]}')


# получаем токен для Яндекса из файла
with open('ya_token.txt', 'r') as file_object:
    ya_token = file_object.read().strip()

yauploaderfromvk(14, ya_token)
