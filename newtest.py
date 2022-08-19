import requests
import json
import os
from dotenv import load_dotenv


class Company:
    headers = {}
    cred = {}
    MAINURL = "https://api3.casebook.ru"

    def __init__(self, inn):
        if not load_dotenv(): raise SystemExit
        self.headers = {"apikey": os.environ.get('APIKEY')}  # сделать глобальной переменной
        self.inn = inn
        self.mistakes = ""
        self.name = None
        self.lchild = None
        self.bro = None
        self.father = None
        self.card = None
        self.all_money_to_pay = 0
        self.unpaid_money = 0
        self.amount_unpaid_money = 0
        self.bankrupt_check = False
        self.pledges_count = 0
        self.check_exec_processes = None
        self.check_bankrupt_messages = None
        self.check_pledges_messages = None

    def get_organization_card(self):  # возвращает карточку организации
        response = requests.get(f"{self.MAINURL}/organizations/{self.inn}", headers=self.headers)
        if response.status_code != 200: return False
        self.card = json.loads(response.text)
        self.name = self.card['shortName']

    def add_node(self, name, data):  # создает экземпляр класса для дальнейшего поиска учредителей
        if self.lchild is None:
            self.lchild = Company(data)
            self.lchild.name = name
            self.lchild.father = self
            return self.lchild  # NEW
        current = self.lchild
        while current.bro is not None: current = current.bro
        current.bro = Company(data)
        current.bro.name = name
        current.bro.father = self
        return current.bro

    def print_founders(self, rezultz=None):
        if rezultz is None: rezultz = set()
        self.get_organization_card()
        self.get_exec_processes(just_check=True)
        self.get_bankrupt_messages(just_check=True)
        self.get_pledges(just_check=True)
        if self.father is not None:
            rezultz.add((self.name, self.inn,
                         self.card['statusInfo']['name']
                         if self.card is not None and self.card['statusInfo']['name'] is not None else '-',
                         'ЕСТЬ' if self.amount_unpaid_money else '-', 'ЕСТЬ' if self.bankrupt_check else '-',
                         'ЕСТЬ' if self.pledges_count else '-'))
        if self.lchild is not None: self.lchild.print_founders(rezultz)
        if self.bro is not None: self.bro.print_founders(rezultz)
        return rezultz

    def print_me(self, counter=0):  # печатает на экран всех учредителей вплоть до физ. лиц
        print("    " * counter, self.name, self.inn, "    Father:", (self.father.name if self.father is not None else "IT IS ROOT"))
        if self.lchild is not None: self.lchild.print_me(counter + 1)
        if self.bro is not None: self.bro.print_me(counter)

    def get_exec_processes(self, just_check=False):  # возвращает инфо обо всех исполнительных процедурах | Теперь с возможностью одноразовой проверки на наличие
        self.all_money_to_pay, self.unpaid_money, i, self.amount_unpaid_money = 0, 0, 1, 0
        response = requests.get(f"{self.MAINURL}/organizations/{self.inn}/executoryProcesses", headers=self.headers,
                                params={'page': 1, 'size': 100})
        if response.status_code != 200: return False
        total_pages = json.loads(response.text)['pages']
        self.check_exec_processes = json.loads(response.text)['total']
        if not total_pages or just_check: return
        while i < total_pages + 1:
            print(f"get_exec_processes, page: {i}, total pages: {total_pages}")
            response = requests.get(f"{self.MAINURL}/organizations/{self.inn}/executoryProcesses", headers=self.headers,
                                    params={'page': i, 'size': 100})
            if response.status_code != 200:
                self.mistakes += f"get_exec_processes failed on page: {i}\n"
                i += 1
                continue
            dict_info = json.loads(response.text)
            for j in dict_info['items']:
                if j['amount'] is not None and j['debtRemainingBalance'] is not None and not j['isFinished']:
                    self.amount_unpaid_money += 1
                    self.all_money_to_pay += j['amount']
                    self.unpaid_money += j['debtRemainingBalance']
            i += 1

    def print_organization_card(self):
        with open("keys_rus.json", 'r', encoding="utf-8") as filer: keys_rus = json.load(filer)
        if self.card is None: self.get_organization_card()
        with open(self.inn + "_card.rtf", 'w', encoding='utf-8') as f:
            for key, val in self.card.items():
                if key in ['phones', 'webSites']:
                    f.write(keys_rus[key] + "\n")
                    for i in val: f.write("    " + i + "\n")
                    f.write("\n")
                elif type(val) is list:
                    f.write(keys_rus[key][0] + "\n")
                    for i in val:
                        for a, b in i.items(): f.write("    " + keys_rus[key][1][a] + ": " + (b if type(b) is str else str(b)) + "\n")
                        f.write("\n")
                    if not len(val): f.write("\n")
                elif type(val) is dict:
                    f.write(keys_rus[key][0] + "\n")
                    for a, b in val.items(): f.write("    " + keys_rus[key][1][a] + ": " + (b if type(b) is str else str(b)) + "\n")
                    f.write("\n")
                else:
                    f.write((keys_rus[key] if type(keys_rus[key]) is str else keys_rus[key][0]) + "\n    " + (val if type(val) is str else str(val)) + "\n\n")

    def get_bankrupt_messages(self, just_check=False):
        response = requests.get(f"{self.MAINURL}/organizations/{self.inn}/bankruptmessages", headers=self.headers,
                                params={'page': 1, 'size': 100})
        if response.status_code != 200: return
        self.check_bankrupt_messages = json.loads(response.text)['total']
        total_pages, i = json.loads(response.text)['pages'], 1
        if not total_pages or just_check: return
        with open(f"Сообщения_о_банкротстве_{self.inn}.rtf", 'w', encoding='utf-8') as f:
            while i < total_pages + 1:
                print(f"get_bankrupt_messages, page: {i}, total pages: {total_pages}")
                response = requests.get(f"{self.MAINURL}/organizations/{self.inn}/bankruptmessages",
                                        headers=self.headers, params={"page": i, 'size': 100})
                if response.status_code != 200:
                    self.mistakes += f"get_bankrupt_messages failed on page {i}\n"
                    i += 1
                    continue
                dict_info = json.loads(response.text)
                for j in dict_info['items']:
                    f.write(f"    Номер сообщения: {j['number']}\nНаименование должника: {j['debtorName']}\nНомер дела:"
                            f" {j['caseNumber']}\nДата публикации: {str(j['publishDate'])}\n"
                            f"Текст сообщения:\n{j['note']}\n\n")
                    self.bankrupt_check = True
                i += 1

    def get_pledges(self, just_check=False, part_type='pledger'):
        self.pledges_count = 0
        all_pledges = []
        response = requests.get(f"{self.MAINURL}/pledges", headers=self.headers,
                                params={'innOrOgrn': self.inn, 'participantType': part_type, 'size': 100})
        if response.status_code != 200: return
        total_pages, i = json.loads(response.text)['pages'], 1
        self.check_pledges_messages = json.loads(response.text)['total']
        if not total_pages or just_check: return
        while i < total_pages + 1:
            print(f"get_pledges, page: {i}, total pages: {total_pages}")
            response = requests.get(f"{self.MAINURL}/pledges", headers=self.headers,
                                    params={'innOrOgrn': self.inn, 'participantType': part_type, 'page': i, 'size': 100})
            dict_info = json.loads(response.text)
            for j in dict_info['pledges']:
                self.pledges_count += 1
                all_pledges.append(j)
            i += 1
        self.get_info_about_pledges(all_pledges)

    def get_info_about_pledges(self, all_pledges):
        with open("keys_rus_pledges.json", "r", encoding="utf-8") as f1: keys_rus = json.loads(f1.read())
        with open(f"Информация_о_залогах_{self.inn}.rtf", "w", encoding="utf-8") as f:
            for i in all_pledges:
                response = requests.get(f"{self.MAINURL}/pledges/{i['noticeNumber']}", headers=self.headers)
                if response.status_code != 200:
                    self.mistakes += f"get_info_about_pledges failed on pledge number {i['noticeNumber']}\n"
                    continue
                dict_info = json.loads(response.text)
                for j in dict_info:
                    if type(dict_info[j]) is not list:
                        f.write(f"{keys_rus[j]}: {dict_info[j] if dict_info[j] is not None else 'информация не найдена'}\n")
                    else:
                        f.write(keys_rus[j] + "\n")
                        for k in dict_info[j]:
                            for m in k:
                                f.write(keys_rus[m] + ": ")
                                if k[m] is None: f.write("информация не найдена\n")
                                elif k[m] in keys_rus: f.write(keys_rus[k[m]] + "\n")
                                else: f.write(k[m] + "\n")
                f.write("\n\n")

    def get_founders(self, visited=None):  # возвращает всех учредителей компании вплоть до физ. лиц
        if visited is None: visited = {self.inn}
        response = requests.get(f"{self.MAINURL}/organizations/{self.inn}/founders/fns",
                                headers=self.headers, params={'page': 1, 'size': 100})
        if response.status_code != 200: return
        total_pages, i, children = json.loads(response.text)['pages'], 1, {}
        while i < total_pages + 1:
            print(f"get_founders, page: {i}, total pages: {total_pages}, name: {self.name}, self inn: {self.inn}")
            response = requests.get(f"{self.MAINURL}/organizations/{self.inn}/founders/fns",
                                    headers=self.headers, params={"page": i, 'size': 100})
            if response.status_code != 200:
                self.mistakes += f"get_founders failed on page {i}"
                i += 1
                continue
            dict_info = json.loads(response.text)
            print(dict_info)
            for j in dict_info['items']:
                if j['inn'] is None: j['inn'] = 'None' + j['name']
                if j['inn'] not in children and j['inn'] != self.inn and j['status'] == 'actual':
                    children[j['inn']] = j['name']
            i += 1
        for inn, name in children.items():
            child = self.add_node(name, inn)
            if child.inn[:4] != 'None' and child.inn not in visited:
                visited.add(child.inn)
                child.get_founders(visited)
            else: child.inn = None


'''
    def get_founders(self, cur_inn=None):  # возвращает всех учредителей компании вплоть до физ. лиц
        if cur_inn is None: self.get_full_name()  # предусмотреть случай, когда pages > 1
        response = requests.get(f"{self.MAINURL}/organizations/{self.inn if cur_inn is None else cur_inn}/founders/fns",
                                headers=self.headers)
        if response.status_code != 200: return
        dict_info = json.loads(response.text)
        children = {}
        for i in dict_info['items']:
            if i['inn'] not in children and i['inn'] != self.inn: children[i['inn']] = i['name']
        for inn, name in children.items():
            child = self.add_node(name, inn)
            if child.inn is not None: child.get_founders(child.inn)
            
    def log_me_in(self):  # создает headers с apikey
        if not load_dotenv(): return False
        self.cred = {"login": os.environ.get('LOGIN'), "password": os.environ.get('PASSWORD')}
        self.headers = {"apikey": os.environ.get('APIKEY')}
        return True
        
    def get_full_name(self):  # возвращает полное наименование компании по ИНН
        response = requests.get(f"{self.MAINURL}/organizations", headers=self.headers, params={'inn': self.inn})
        if response.status_code != 200: return
        self.name = json.loads(response.text)['items'][0]['name']  # Ошибка на ИНН: 771579081330
'''

if __name__ == "__main__":
    aboba = Company("2320013490")  # 2320013490 - много учредителей, 5029073314 - яхт-клуб буревестник в залоге, 1659188878-спец в залоге, 0814099824 - дальняя степь (банкрот), 7718979307-citilink, 5022089668-семерикъ, 2337042629, 7104002407, 7704450922, 9715306321, 7715417853, 7725808905 - жесткая    7707778239,  7734413460 - Текон, 7713140469 - Касперский

    aboba.get_founders()
    aboba.print_me()
    aboba.get_organization_card()
    aboba.print_organization_card()
    #aboba.get_pledges()
    #aboba.get_bankrupt_messages()
    #aboba.get_founders()
    #aboba.print_me()
#    print(aboba.check_exec_processes)
#    aboba.get_exec_processes(True)
#    print(aboba.check_exec_processes)
#    print(aboba.check_bankrupt_messages)
#    aboba.get_bankrupt_messages(True)
#    print(aboba.check_bankrupt_messages)
#    print(aboba.check_pledges_messages)
#    aboba.get_pledges(just_check=True)
#    print(aboba.check_pledges_messages)
    #print(aboba.all_money_to_pay, aboba.unpaid_money)

    #aboba.get_organization_card()
    #aboba.print_organization_card()
    #aboba.get_pledges()
