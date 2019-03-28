import requests
import re
from bs4 import BeautifulSoup



def search_for_date(id): # функция которая ищет дату создания петиции по ее ID
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

def main():
        URL = input('Введите URL петиции ')
        data = {'page_view_id': '1',
                'time_until_page_fully_loaded': '1409',
                'authenticity_token': '5d2260b26c691988588e9295043b4237'
                }

        response = requests.get(URL, data)
        soup = BeautifulSoup(response.text, 'html.parser')

        # ID петиции
        ID = soup.find_all(class_='btn btn-block btn-social btn-facebook facebook_share_button')
        ID = str(ID[0])
        ID = ID.split()
        ID = re.findall('(\d+)', ID[7])
        ID = ID[0]

        # заголовок петиции
        title = soup.title.get_text()

        # полный текст петиции
        full_text = soup.find_all(id='petition_text')[0].get_text()

        # имя автора петиции
        author_text = soup.find_all(id='contact_person')[0].get_text()
        author_list = author_text.split()
        for i in range (0,4):
                author_list.pop()
        author_name = ' '.join(author_list)

        # дата петиции
        date = search_for_date(ID)

        print(date)

main()
