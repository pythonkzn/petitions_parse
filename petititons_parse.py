import requests
from bs4 import BeautifulSoup
import json
import codecs
from pprint import pprint
import re
from itertools import chain
import sys
import hashlib


def get_all_last():
        page_num = 1
        url_last = 'https://www.petitions247.com/browse.php?page=' + str(
                page_num) + '&order_by=petition_created&sort_order=desc'
        response = requests.get(url_last)
        pprint('Получили список ссылок на страницу {}'.format(page_num))
        soup = BeautifulSoup(response.text, 'html.parser')
        max_page_num = soup.find_all(class_='pagination flex-wrap')[0].text.split()[-2]
        td_tags = str(soup.find_all('td'))
        soup_sub = BeautifulSoup(td_tags, 'lxml')
        petition_href_list = [[]]
        for a in soup_sub.find_all('a', href=True):
                petition_href_list[0].append(a['href'])
        while page_num < int(max_page_num):
                page_num += 1
                response = requests.get('https://www.petitions247.com/browse.php?page=' + str(
                        page_num) + '&order_by=petition_created&sort_order=desc')
                pprint('Получили список ссылок на страницу {}'.format(page_num))
                soup = BeautifulSoup(response.text, 'html.parser')
                td_tags = str(soup.find_all('td'))
                soup_sub = BeautifulSoup(td_tags, 'lxml')
                sub_petition_href_list = []
                for a in soup_sub.find_all('a', href=True):
                        sub_petition_href_list.append(a['href'])  # получаем ссылки петиций
                petition_href_list.append(sub_petition_href_list)
        out_petition_href_list = list(
                chain.from_iterable(petition_href_list))  # получили уникальную часть ссылок на петиции
        href_list = []
        for href in out_petition_href_list:
                href_list.append('https://www.petitions247.com' + href)
        data_list_petition = []
        count = 0
        for href in href_list:
                try:
                        data_list_petition.append(search_by_url(href))
                        print('Распечатана петиция номер {}'.format(count))
                except Exception as e:
                        print('Петиция закрыта и не может быть распечатана')
                count += 1
        return data_list_petition



def search_by_url(url_in):
        data = {'page_view_id': '1',
                'time_until_page_fully_loaded': '1409',
                'authenticity_token': '5d2260b26c691988588e9295043b4237'
                }

        response = requests.get(url_in, data)
        soup = BeautifulSoup(response.text, 'html.parser')

        id = search_for_id(soup)  # ID петиции
        title = soup.title.get_text()  # заголовок петиции
        full_text = soup.find_all(id='petition_text')[0].get_text().split('\n')  # полный текст петиции
        author_name = search_for_author(soup)  # имя автора петиции
        date = search_for_date(url_in)  # дата петиции
        sign_count = seacrh_for_signs(soup)  # количество подписавших
        author_id = get_author_id(url_in, author_name)
        out_data = exp_to_json(id, title, full_text, author_name, date, sign_count, author_id)
        pprint (out_data)
        return out_data


def search_for_date(url):  # функция которая ищет дату создания петиции по ее ID
        url_p_1 = url[0:29]
        url_p_2 = 'signatures/' + url[29:]
        url_signs = url_p_1 + url_p_2  # URL страницы с подписями петиции
        response = requests.get(url_signs)
        soup = BeautifulSoup(response.text, 'html.parser')
        date_list = soup.find(class_='odd')
        date_list = date_list.text.split()

        return date_list[-1]


def search_for_id(soup_in):
        ID = soup_in.find_all(class_='btn btn-block btn-social btn-facebook facebook_share_button')
        ID = str(ID[0])
        ID = ID.split()
        ID = re.findall('(\d+)', ID[7])
        ID = ID[0]
        return ID


def search_for_author(soup_in):
        author_text = soup_in.find_all(id='contact_person')[0].get_text()
        author_list = author_text.split()
        for i in range (0,4):
                author_list.pop()
        author_name_out = ' '.join(author_list)
        return author_name_out


def seacrh_for_signs(soup_in):
        sign_count_out_2 = ['']
        sign_count = soup_in.find_all(class_='signatureAmount badge badge-primary')
        sign_count = str(sign_count[0])
        sign_count_out = sign_count.split()
        sign_count_out_1 = re.findall('(\d+)', sign_count_out[3])
        if (len(sign_count_out) > 4):  # если количество подписей меньше 1000 то не будет этого параметра
                sign_count_out_2 = re.findall('(\d+)', sign_count_out[4])
        sign_count_out = sign_count_out_1[0] + sign_count_out_2[0]
        return sign_count_out


def exp_to_json(id_in, title_in, full_text_in, author_name_in, date_in, sign_count_in, author_id_in):
        out_dict = {'ID': id_in,
                    'Title': title_in,
                    'Text': full_text_in,
                    'Author': author_name_in,
                    'Date': date_in,
                    'Number of signs': sign_count_in,
                    'Author ID': author_id_in}
        #with codecs.open('output.json', 'w', encoding='utf-8') as json_file:
                #json.dump(out_dict, json_file, ensure_ascii=False)
        return out_dict


def get_author_id(url, author_name_in):
        url_p_1 = url[0:29]
        url_p_2 = 'signatures/' + url[29:]
        url_signs = url_p_1 + url_p_2  # URL страницы с подписями петиции
        response = requests.get(url_signs)
        soup = BeautifulSoup(response.text, 'html.parser')
        signs_page = soup.find_all('tr')
        signs_page = str(signs_page[2])
        signs_page = signs_page.split()
        auth_name = signs_page[6] + ' ' + signs_page[7]  # имя автора первого подписанта петиции
        if len(auth_name) > 10:  # обходим случай когда первый подписавший зареген на сайте
                p = auth_name.count(author_name_in.split()[0])
                if auth_name.count(author_name_in.split()[0]) == 1:
                        auth_id = re.findall('(\d+)', signs_page[2])[0]
                else:
                        auth_id = author_name_in
        else:
                auth_name = signs_page[4] + ' ' + signs_page[5]
                p = auth_name.find(author_name_in)
                if auth_name.count(author_name_in.split()[0]) == 1:
                        auth_id = re.findall('(\d+)', signs_page[2])[0]
                else:
                        auth_id = author_name_in
        return auth_id


def get_votes(url):
        comment_list = []
        page_num = 1
        url_p_1 = url[:29]
        url_p_2 = url[29:-5]
        url_signs = url_p_1 +  'signatures.php?tunnus=' + url_p_2 + '&page_number='+ str(page_num) +'&num_rows=10&a=2' # URL страницы с подписями петиции
        response = requests.get(url_signs)
        soup = BeautifulSoup(response.text, 'html.parser')
        max_page_num = soup.find_all(class_='pagination flex-wrap')[0].text.split()[-2]
        print('Обработка страницы номер {}'.format(page_num))
        table_tag = str(soup.find('tbody'))  # получили таблицу с подписями
        soup_sub = BeautifulSoup(table_tag, 'lxml')
        td_tag = soup_sub.find_all('td')  # получили список значений ячеек таблицы
        output_list = [[]]
        i = 0  # счетчик строк
        j = 0  # счетчик ячеек в строке
        y = 0  # счетчик общего количества ячеек
        while y <= (len(td_tag)-1):
             if (y > 0) and (y % 5 == 0):
                     i += 1
                     output_list.append([])
             output_list[i].append(td_tag[y].text)
             y += 1
        comment_list.append(output_list)
        while page_num < int(max_page_num):
                page_num += 1
                url_p_1 = url[:29]
                url_p_2 = url[29:-5]
                url_signs = url_p_1 + 'signatures.php?tunnus=' + url_p_2 + '&page_number=' + str(page_num) + '&num_rows=10&a=2'  # URL страницы с подписями петиции
                response = requests.get(url_signs)
                soup = BeautifulSoup(response.text, 'html.parser')
                print('Обработка страницы номер {}'.format(page_num))
                table_tag = str(soup.find('tbody'))  # получили таблицу с подписями
                soup_sub = BeautifulSoup(table_tag, 'lxml')
                td_tag = soup_sub.find_all('td')  # получили список значений ячеек таблицы
                output_list = [[]]
                i = 0  # счетчик строк
                j = 0  # счетчик ячеек в строке
                y = 0  # счетчик общего количества ячеек
                while y <= (len(td_tag) - 1):
                        if (y > 0) and (y % 5 == 0):
                                i += 1
                                output_list.append([])
                        output_list[i].append(td_tag[y].text)
                        y += 1
                comment_list.append(output_list)
        comment_list = list(chain.from_iterable(comment_list))
        return comment_list


def get_comments(votes_list):
        comments_out = []
        for item in votes_list:
                if item[3] != '':
                        comments_out.append(item)
                item[2] = item[2].strip()
                key = item[0] + item[1] + item[4]
                hash_line = hashlib.md5(key.encode('utf8'))
                item.append(hash_line.hexdigest())
        #with open('comments.json', 'w', encoding='utf8') as json_file:
                #json.dump(comments_out, json_file, ensure_ascii=False)
        return comments_out


def main():
        in_com = input('Введите:'
                       ' 1 - если нужно получить информацию о последних \n созданных петициях'
                       ' 2 - если нужно получить информацию о петиции по ее URL  ')

        if in_com == '1':
                get_all_last()
        elif in_com == '2':
                url_in = input('Введите URL петиции ')
                search_by_url(url_in)
                in_com = input(
                        'Если необходимо собрать комментарии к петиции и список проголосовавших нажмите Y, если нет - Q  ')
                if in_com == 'Y':
                        voted_list = get_votes(url_in)  # проголосовавшие
                        comments = get_comments(voted_list)  # комментарии к петиции
                        pprint(comments)
                elif in_com == 'Q':
                        sys.exit(0)
                else:
                        print('Вы ввели неверную команду')


if __name__ == "__main__":
        main()
