"""Скрипт поиска пользователя в Active Directory"""

from ldap3 import Server, Connection, SUBTREE

# Определяем сервер и считываем учётные данные
AD_SERVER = 'dc1.domain.com'
AD_SERVER_RESERV = 'dc2.domain.com'
domain_name = 'DOMAIN'
# файл ini  логин:пароль
your_name = open('ini', encoding='UTF-8').read().split(':')[0]
AD_USER = f'{domain_name}\{your_name}'
AD_PASSWORD = open('ini', encoding='UTF-8').read().split(':')[1]
AD_SEARCH_TREE = 'dc=roscap,dc=com'

# Проверяем и устанавливаем соединение с сервером
server = ''
if Connection(AD_SERVER).bind() is True:
    server = Server(AD_SERVER)
else:
    server = Server(AD_SERVER_RESERV)
conn = Connection(server, user=AD_USER, password=AD_PASSWORD)
conn.bind()

while True:
    try:
        print(f'Домен {domain_name}.\nМожно искать по ФИО, логину, почте, рабочему или мобильному телефону.')
        search_params = input('Кого ищем?'+'\n\n')
        search_string = ''
        # Условие поиска, исходя из введённых символов
        if "@" in search_params:
            search_string = f'(extensionAttribute140={search_params})'
        elif search_params.count('.') == 1:
            search_string = f'(sAMAccountName={search_params})'
        elif '+' in search_params or search_params.isdigit() and len(search_params) > 5:
            search_string = f'(mobile={search_params})'
        elif search_params.isdigit() and len(search_params) <= 5:
            search_string = f'(telephoneNumber={search_params})'
        else:
            search_string = f'(cn={search_params})'

        # Поиск по введённому условию, с деревом, возврат атрибутов
        conn.search(AD_SEARCH_TREE, f'(&(objectCategory=Person)(|{search_string}))', SUBTREE,
                    attributes=['cn', 'extensionAttribute140', 'department', 'sAMAccountName', 'whenCreated',
                                'displayName', 'telephoneNumber', 'mobile', 'title', 'manager', 'lastLogon',
                                'extensionAttribute10', 'extensionAttribute40', 'UserAccountControl',
                                'distinguishedName'])

        # Проверка статуса УЗ и вывод на экран результата
        status = ''
        for entry in conn.entries:
            if entry.UserAccountControl == 512:
                status = 'Включена'
            elif entry.UserAccountControl == 514:
                status = 'Отключена'
            else:
                status = ' '
            print(' ФИО: ', entry.cn, '\n', 'Логин: ', entry.sAMAccountName, '\n',
                  'Почта: ', entry.extensionAttribute140, '\n', 'Рабочий тел: ', entry.telephoneNumber, '\n',
                  'Мобильный тел.: ', entry.mobile, '\n', 'Отдел: ', entry.department, '\n',
                  'Должность: ', entry.title, '\n', 'Дата рождения: ', entry.extensionAttribute10, '\n',
                  'Последний вход: ', str(entry.lastLogon)[:19], '\n', 'СНИЛС: ',
                  entry.extensionAttribute40, '\n', 'Статус УЗ: ', status, '\n', 'Место в AD: ',
                  ', '.join(str(entry.distinguishedName).split(',')[1:-2]), '\n')
        print('Чтобы продолжить - нажми Enter, чтобы выйти - что угодно и Enter\n')

        if input() == '':
            continue
        else:
            break

    except:
        print('Что-то пошло не так\n')
        if input() == '':
            continue
        else:
            break
