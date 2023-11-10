import vk_api
import matplotlib.pyplot as plt
import seaborn as sns
import csv

def get_demographic_info(api, source_group_id, limit=60):
    try:
        # Получаем список участников сообщества
        members = api.groups.getMembers(group_id=source_group_id, v='5.95', count=limit)['items']

        # Инициализируем переменные для хранения демографической информации
        total_members = 0
        total_age = 0
        unspecified_age_count = 0
        male_count = 0
        female_count = 0
        unspecified_gender_count = 0
        country_count = {}
        city_count = {}
        unspecified_location_count = 0

        # Проходим по каждому участнику и получаем информацию
        for member_id in members:
            try:
                user_info = api.users.get(user_ids=member_id, v='5.95', fields='sex,bdate,city,country')[0]

                # Общее количество участников
                total_members += 1

                # Возраст
                if 'bdate' in user_info:
                    birthdate = user_info['bdate'].split('.')
                    if len(birthdate) == 3:
                        age = 2023 - int(birthdate[2])
                        total_age += age
                    else:
                        unspecified_age_count += 1
                else:
                    unspecified_age_count += 1

                # Пол
                if 'sex' in user_info:
                    gender = user_info['sex']
                    if gender == 1:
                        female_count += 1
                    elif gender == 2:
                        male_count += 1
                    else:
                        unspecified_gender_count += 1
                else:
                    unspecified_gender_count += 1

                # Место проживания
                if 'country' in user_info:
                    country = user_info['country']['title']
                    if country not in country_count:
                        country_count[country] = 1
                    else:
                        country_count[country] += 1
                else:
                    unspecified_location_count += 1

                if 'city' in user_info:
                    city = user_info['city']['title']
                    if city not in city_count:
                        city_count[city] = 1
                    else:
                        city_count[city] += 1
                else:
                    unspecified_location_count += 1

            except vk_api.exceptions.ApiError as e:
                print(f"Error fetching info for user {member_id}: {e}")

        # Средний возраст
        if total_members > 0:
            average_age = total_age // total_members
        else:
            average_age = 0

        # Процент неуказавших возраст
        if total_members > 0:
            percent_unspecified_age = (unspecified_age_count / total_members) * 100
        else:
            percent_unspecified_age = 0

        # Процент неуказавших место проживания
        if total_members > 0:
            percent_unspecified_location = (unspecified_location_count / total_members) * 100
        else:
            percent_unspecified_location = 0

        # Отображение результатов
        print(f"Total Members: {total_members}")
        print(f"Average Age: {average_age} years")
        print(f"Percent Unspecified Age: {percent_unspecified_age:.2f}%")

        # График пола
        gender_labels = ['Мужчины', 'Женщины', 'Не указано']
        gender_sizes = [male_count, female_count, unspecified_gender_count]
        plt.pie(gender_sizes, labels=gender_labels, autopct='%1.1f%%', startangle=140)
        plt.title('Распределение по полу')
        plt.show()

        # График места проживания
        sns.barplot(x=list(country_count.values()), y=list(country_count.keys()))
        plt.title('Распределение по странам')
        plt.xlabel('Количество участников')
        plt.ylabel('Страна')
        plt.show()

        sns.barplot(x=list(city_count.values()), y=list(city_count.keys()))
        plt.title('Распределение по городам')
        plt.xlabel('Количество участников')
        plt.ylabel('Город')
        plt.show()

        print(f"Percent Unspecified Location: {percent_unspecified_location:.2f}%")

        # Запись результатов в CSV-файл
        with open('demographic_info.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Total Members', 'Average Age', 'Percent Unspecified Age', 'Male', 'Female', 'Unspecified Gender',
                          'Percent Unspecified Location']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow({
                'Total Members': total_members,
                'Average Age': average_age,
                'Percent Unspecified Age': percent_unspecified_age,
                'Male': male_count,
                'Female': female_count,
                'Unspecified Gender': unspecified_gender_count,
                'Percent Unspecified Location': percent_unspecified_location
            })

    except vk_api.exceptions.ApiError as e:
        print(f"Error fetching members of group {source_group_id}: {e}")
        return []

def main():
    # Ваши параметры
    access_token = '' # ВВЕДИ СВОЙ ТОКЕН API VK
    v = '5.95'
    source_group_id = '49907227'  # измененный идентификатор исходного сообщества

    # Подключение к VK API
    vk_session = vk_api.VkApi(token=access_token)
    api = vk_session.get_api()

    # Получаем и анализируем демографическую информацию
    get_demographic_info(api, source_group_id)

if __name__ == "__main__":
    main()
