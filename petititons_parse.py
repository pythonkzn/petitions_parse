import requests
import re
from bs4 import BeautifulSoup
import json
import codecs


def search_for_date(id):  # функция которая ищет дату создания петиции по ее ID
        date_str_htm = ''
        page_num = 1
        ID = id
        while page_num <= 20:
                URL = 'https://www.petitions247.com/browse.php?page='+ str(page_num) +'&order_by=last_signed&sort_order=desc'
                response = requests.get(URL)
                soup = BeautifulSoup(response.text, 'html.parser')
                page_list = soup.find_all(class_='odd')
                for petition in page_list:
                        pet_str = str(petition)
                        if str(ID) in pet_str:
                                date_str_htm = pet_str
                if date_str_htm == '':
                        page_num += 1
                        date_list = []
                else:
                        date_str = BeautifulSoup(date_str_htm,'lxml').text
                        date_list = date_str.split()
                        page_num = 21
                if date_list == []:
                        page_list = soup.find_all(class_='even')
                        for petition in page_list:
                                pet_str = str(petition)
                                if str(ID) in pet_str:
                                        date_str_htm = pet_str
                        if date_str_htm == '':
                                page_num += 1
                                date_list = []
                        else:
                                date_str = BeautifulSoup(date_str_htm, 'lxml').text
                                date_list = date_str.split()
                                page_num = 21

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
        with codecs.open('output.json', 'w', encoding='utf-8') as json_file:
                json.dump(out_dict, json_file, ensure_ascii=False)
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
                if auth_name.find(author_name_in) != -1:
                        auth_id = re.findall('(\d+)', signs_page[2])[0]
                else:
                        auth_id = author_name_in
        else:
                auth_name = signs_page[4] + ' ' + signs_page[5]
                p = auth_name.find(author_name_in)
                if auth_name.find(author_name_in) != -1:
                        auth_id = re.findall('(\d+)', signs_page[2])[0]
                else:
                        auth_id = author_name_in
        return auth_id

def main():
        URL = input('Введите URL петиции ')
        data = {'page_view_id': '1',
                'time_until_page_fully_loaded': '1409',
                'authenticity_token': '5d2260b26c691988588e9295043b4237'
                }

        response = requests.get(URL, data)
        soup = BeautifulSoup(response.text, 'html.parser')

        id = search_for_id(soup)  # ID петиции
        title = soup.title.get_text()  # заголовок петиции
        full_text = soup.find_all(id='petition_text')[0].get_text().split('\n')  # полный текст петиции
        author_name = search_for_author(soup)  # имя автора петиции
        date = search_for_date(id)  # дата петиции
        sign_count = seacrh_for_signs(soup)  # количество подписавших
        author_id = get_author_id(URL, author_name)
        out_data = exp_to_json(id, title, full_text, author_name, date, sign_count, author_id)
        print (out_data)

if __name__ == "__main__":
        main()
