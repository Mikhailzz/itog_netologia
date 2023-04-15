import requests
from random import randrange
from pprint import pprint
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import json

token = 'vk1.a.z5c2xvqGfGV5atbYwiYMuJqDnPZAEyiwDqcOsyWM7nqb545PyPmH8hRNYyQ8Fhy-14OCyjvMKfIQr8DNEmjygKpWqdCFkav8_N92mvk6n5eG5mnQ9Pt5Yb0A_GYt16mJVr__J1fPXzBTz027dtwWt3wbReUBFL97uE9g8PJh9_iiogjrC3rrfu0eFyeHmMQqmexoDdOUXXmWScjXLu59cA'

token_two = 'vk1.a.GhVbUb7Wy2k3eodQYaspriY5g5si_VOcJBo7eHNsg5fdcA4gWuv07TCqXoIZ1kQrLZxcaNCVUlTp-ex3WWin0JYF8HkMF0_KqZ8jGuU19dKwWKJWO0b5Pj0u1KJaZuAbd_fC0-fGyabBRFa1qKCI2vVblUWksC29M3gyOMOkq6zblLoWsnEMuvkFqcSEN6lclUsAHz7uLE1wW-NRtuKSNA'

vk = vk_api.VkApi(token=token)
session_api = vk.get_api()
longpoll = VkLongPoll(vk)

Base = declarative_base()


class Seeker(Base):
    __tablename__ = 'seeker'

    id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=40), unique=False)
    last_name = sq.Column(sq.String(length=40), unique=False)


class Lover(Base):
    __tablename__ = 'lover'

    id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=40), unique=False)
    last_name = sq.Column(sq.String(length=40), unique=False)
    id_seeker = sq.Column(sq.Integer, sq.ForeignKey("seeker.id"), nullable=False, primary_key=True)

    seeker = relationship(Seeker, backref="Seekers")


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


DSN = 'postgresql://postgres:th2AfrM1n7Dp3@localhost:5432/itog'

engine = sq.create_engine(DSN)
create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()


def write_msg(user_id, message):
    vk.method('messages.send',
              {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), 'chat_id': 11, })


class VK:
    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        paramss = {'fields': 'bdate, sex, city, relation'}
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params, **paramss})
        return response.json()

    def filefoto(self, user_id):
        params = {'owner_id': user_id,
                  'album_id': 'profile',
                  'photo_sizes': 'z',
                  'extended': '1'
                  }
        url = 'https://api.vk.com/method/photos.getAll'
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def search(self, params):
        url = 'https://api.vk.com/method/users.search'
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def city_id_get(self, name_town):
        params = {'q': name_town}
        url = 'https://api.vk.com/method/database.getCities'
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    # def sort_photo(self):
    #     url = 'https://api.vk.com/method/users.search'
    #     response = requests.get(url, params={**self.params, **params})
    #     return response


def super_popular(photo):
    count_like = []
    for elem in photo['response']['items']:
        count_like.append(elem['likes']['count'])
    count_like.sort(reverse=True)
    print('count', count_like)
    return count_like[0:3]


def params_search_func(people_info):
    if 'sex' in people_info:
        sex = people_info['sex']
    else:
        sex = 0
    if 'city' in people_info:
        city = people_info['city']['id']
    else:
        city = ''
    relation = people_info['relation']
    if 'bdate' in people_info:
        bdate = people_info['bdate']
    else:
        bdate = ''
    params_search_dict = dict()

    print(sex, city, bdate, relation)
    bdate_year = bdate.split('.')
    year = 0
    if len(bdate_year) == 3:
        year = 2023 - int(bdate_year[2])
    print(year)
    if sex == 1:
        params_search_dict['sex'] = 2
    elif sex == 2:
        params_search_dict['sex'] = 1
    if city:
        params_search_dict['city'] = city
    if year:
        params_search_dict['age_from'] = year - 2
        params_search_dict['age_to'] = year + 2
    params_search_dict['relation'] = 6
    params_search_dict['count'] = 1000
    return params_search_dict


def check_params(params):
    flag = 0
    if params[event.user_id]['sex'] == 0:
        flag = 1
        write_msg(event.user_id, f"Введите свой пол (Пример: пол мужской)")
    if 'age_from' not in params[event.user_id]:
        flag = 1
        write_msg(event.user_id, f"Введите год первый (Пример: возраст от 20)")
    if 'age_to' not in params[event.user_id]:
        flag = 1
        write_msg(event.user_id, f"Введите год первый (Пример: возраст до 25)")
    if 'city' not in params[event.user_id]:
        flag = 1
        write_msg(event.user_id, f"Введите город (Пример: город Тула)")
    return flag


user_stop = dict()
user_all_dict = dict()
user_flag_in = dict()
user_params_search = dict()
list_pop = []
list_check = []
for event in longpoll.listen():
    print('2')
    if event.type == VkEventType.MESSAGE_NEW:
        info = session_api.users.get(users_id=event.user_id)

        if event.to_me:
            request = event.text

            print('3')

            # создание параметров поиска

            if request.lower() == 'поиск':
                if event.user_id not in user_all_dict:
                    user_all_dict[event.user_id] = VK(token_two, event.user_id)
                inform_user = user_all_dict[event.user_id].users_info()
                people = inform_user['response'][0]
                print(people)

                q = session.query(Seeker).filter(Seeker.id == people['id'])
                if not q.all():
                    people_base_seeker = Seeker(id=people['id'], first_name=people['first_name'],
                                                last_name=people['last_name'])
                    session.add(people_base_seeker)
                    session.commit()

                parametrs_search = params_search_func(people)
                if event.user_id not in user_params_search:
                    user_params_search[event.user_id] = {}
                user_params_search[event.user_id].update(parametrs_search)
                # user_params_search[event.user_id].pop('city')
                # user_params_search[event.user_id]['sex'] = 0
                # user_params_search[event.user_id].pop('age_to')

                if event.user_id not in user_flag_in:
                    user_flag_in[event.user_id] = 0

                flag = check_params(user_params_search)

                if flag == 0:
                    write_msg(event.user_id, f"Параметры успешно созданы, введите: поиск класс")
                    user_flag_in[event.user_id] = 1
                continue

            # задание города
            if request.lower().startswith('город'):
                dict_city = dict()
                city_request = request.split(' ')
                city = city_request[1]
                response = user_all_dict[event.user_id].city_id_get(city)
                if response['response']['count'] == 0:
                    write_msg(event.user_id, f"Введите город снова")
                else:
                    dict_city['city'] = response['response']['items'][0]['id']

                user_params_search[event.user_id].update(dict_city)

                flag = check_params(user_params_search)

                if flag == 0:
                    write_msg(event.user_id, f"Параметры успешно созданы, введите: поиск класс")
                    user_flag_in[event.user_id] = 1
                continue

            # задание пола

            if request.lower().startswith('пол'):
                gender_dict = dict()
                gender = request.split(' ')
                if gender[1] == 'мужской':
                    gender_dict['sex'] = 1
                elif gender[1] == 'женский':
                    gender_dict['sex'] = 2
                else:
                    write_msg(event.user_id, f"Повторите ввод пола")

                user_params_search[event.user_id].update(gender_dict)

                flag = check_params(user_params_search)

                if flag == 0:
                    write_msg(event.user_id, f"Параметры успешно созданы, введите: поиск класс")
                    user_flag_in[event.user_id] = 1
                continue

            # возраст от

            if request.lower().startswith('возраст от'):
                dict_age_from = dict()
                age_from = request.split(' ')
                dict_age_from['age_from'] = int(age_from[2])
                if 'age_to' in user_params_search[event.user_id]:
                    if (user_params_search[event.user_id]['age_to'] > dict_age_from['age_from']) and (80 > dict_age_from['age_from'] > 18):
                        user_params_search[event.user_id].update(dict_age_from)

                        flag = check_params(user_params_search)

                        if flag == 0:
                            write_msg(event.user_id, f"Параметры успешно созданы, введите: поиск класс")
                            user_flag_in[event.user_id] = 1
                    else:
                        write_msg(event.user_id, f"Возраст неверен")
                elif 80 > dict_age_from['age_from'] > 18:
                    user_params_search[event.user_id].update(dict_age_from)
                    flag = check_params(user_params_search)

                    if flag == 0:
                        write_msg(event.user_id, f"Параметры успешно созданы, введите: поиск класс")
                        user_flag_in[event.user_id] = 1
                else:
                    write_msg(event.user_id, f"Возраст неверен")

                continue

            # возраст до

            if request.lower().startswith('возраст до'):
                dict_age_to = dict()
                age_to = request.split(' ')
                dict_age_to['age_to'] = int(age_to[2])
                if 'age_from' in user_params_search[event.user_id]:
                    if (user_params_search[event.user_id]['age_from'] < dict_age_to['age_to']) and (18 < dict_age_to['age_to'] < 100):
                        user_params_search[event.user_id].update(dict_age_to)

                        flag = check_params(user_params_search)

                        if flag == 0:
                            write_msg(event.user_id, f"Параметры успешно созданы, введите: поиск класс")
                            user_flag_in[event.user_id] = 1

                    else:
                        write_msg(event.user_id, f"Возвраст неверен")

                elif 100 > dict_age_to['age_to'] > 18:
                    user_params_search[event.user_id].update(dict_age_to)
                    flag = check_params(user_params_search)

                    if flag == 0:
                        write_msg(event.user_id, f"Параметры успешно созданы, введите: поиск класс")
                        user_flag_in[event.user_id] = 1
                else:
                    write_msg(event.user_id, f"Возвраст неверен")
                continue

                # user_params_search[event.user_id].update(dict_year_from)
                #
                # flag = check_params(user_params_search)
                #
                # if flag == 0:
                #     write_msg(event.user_id, f"Параметры успешно созданы")
                #     user_flag_in[event.user_id] = 1

            if request == "поиск класс":
                if user_flag_in[event.user_id] == 1:
                    parametrs_search = user_params_search[event.user_id]

                    serch_str = user_all_dict[event.user_id].search(parametrs_search)
                    # pprint(serch_str)
                    serch_res = serch_str['response']['items']
                    print('ДЛИННА', len(serch_res))
                    # count = 0
                    list_human = []
                    if event.user_id not in user_stop:
                        user_stop[event.user_id] = []
                    print('TESSSSST', serch_res[5]['id'])

                    for elem in serch_res:
                        if (elem['is_closed'] == False) and (elem['id'] not in user_stop[event.user_id]):
                            print(elem)

                            e = session.query(Lover).filter(Lover.id == elem['id'], Lover.id_seeker == event.user_id)
                            if not e.all():
                                people_base_lover = Lover(id=elem['id'], first_name=elem['first_name'],
                                                          last_name=elem['last_name'], id_seeker=event.user_id)

                                session.add(people_base_lover)

                                session.commit()

                            list_human.append(elem)
                            user_stop.setdefault(event.user_id, []).append(elem['id'])
                            # list_check.append(elem['id'])
                            photo = user_all_dict[event.user_id].filefoto(elem['id'])
                            if photo['response']['count'] == 0:
                                continue
                            photttto = photo['response']['items']
                            newwww = sorted(photttto, key=lambda x: x['likes']['count'], reverse=True)
                            print('Далее будет сортир!')

                            # pprint(newwww)
                            count = 0
                            listochek = []
                            for elementos in newwww:
                                listochek.append(elementos['id'])
                                count += 1
                                if count == 3:
                                    break
                            if len(listochek) == 3:

                                vk.method("messages.send",
                                          {"user_id": event.user_id,
                                           'attachment': f'photo{elem["id"]}_{listochek[0]},photo{elem["id"]}_{listochek[1]},photo{elem["id"]}_{listochek[2]}',
                                           "random_id": 0})
                            elif len(listochek) == 2:
                                vk.method("messages.send",
                                          {"user_id": event.user_id,
                                           'attachment': f'photo{elem["id"]}_{listochek[0]},photo{elem["id"]}_{listochek[1]}',
                                           "random_id": 0})
                            else:
                                vk.method("messages.send",
                                          {"user_id": event.user_id,
                                           'attachment': f'photo{elem["id"]}_{listochek[0]}',
                                           "random_id": 0})
                            write_msg(event.user_id, f'https://vk.com/id{elem["id"]}')
                            break
                else:
                    write_msg(event.user_id, f'Не все параметры заданыб поиск невозможен')
                continue




