import vk_api
import csv

def get_groups(api, source_group_id, limit=10):
    try:
        # Получаем список пользователей входящих в исходное сообщество
        members = api.groups.getMembers(group_id=source_group_id, v='5.95', count=limit)['items']

        # Создаем пустой словарь для хранения информации о группах и их участниках
        groups_info = {}

        # Проходим по каждому участнику и получаем список групп, в которых он состоит
        for member_id in members:
            try:
                user_groups = api.groups.get(user_id=member_id, v='5.95')['items']

                # Обновляем информацию о группах
                for group_id in user_groups:
                    if group_id != source_group_id:
                        if group_id not in groups_info:
                            groups_info[group_id] = 1
                        else:
                            groups_info[group_id] += 1
            except vk_api.exceptions.ApiError as e:
                # Обрабатываем ошибку для приватных профилей
                if e.code == 30:
                    print(f"User {member_id} has a private profile.")
                elif e.code == 18:
                    print(f"User {member_id} was deleted or banned.")
                else:
                    print(f"Error fetching groups for user {member_id}: {e}")

        # Сортируем группы по количеству участников в порядке убывания
        sorted_groups = sorted(groups_info.items(), key=lambda x: x[1], reverse=True)

        return sorted_groups

    except vk_api.exceptions.ApiError as e:
        print(f"Error fetching members of group {source_group_id}: {e}")
        return []

def main():
    # Параметры:
    access_token = '' # ВВЕДИ СВОЙ ТОКЕН API VK
    v = '5.95'
    source_group_id = '49907227'  # измененный идентификатор исходного сообщества

    # Подключение к VK API
    vk_session = vk_api.VkApi(token=access_token)
    api = vk_session.get_api()

    # Получаем список сообществ и ранжируем их по количеству участников (ограничено 10 пользователями для тестирования)
    groups_info = get_groups(api, source_group_id, limit=10)

    # Выводим результаты
    for group_id, members_count in groups_info:
        print(f"Group ID: {group_id}, Members Count: {members_count}")

    # Сохраняем результаты в CSV-файл
    filename = f"groups_{source_group_id}.csv"
    with open(filename, 'w', newline='') as f:
        fieldnames = ['group_id', 'members_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for group_id, members_count in groups_info:
            writer.writerow({'group_id': group_id, 'members_count': members_count})

if __name__ == "__main__":
    main()
