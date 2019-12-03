# doc-api

# Установка:
git clone https://github.com/frfrrfrrr/doc-api.git
docker build -t doc-api .

# Запуск:
docker run -p 7000:7000 -e LC_ALL=en_US.utf-8 -e LANG=en_US doc-api

# Тестирование:
Самый простой способ протестировать - использовать POSTMAN или любой другой HTTP-клиент.

POST-запрос по адресу
localhost:7000/api/excludeApproval

Content-Type: application/x-www-form-urlencoded

в теле запроса должен быть параметр in_file типа файл, содержащий PDF-файл.
в ответ должен вернуться тот же PDF-файл.