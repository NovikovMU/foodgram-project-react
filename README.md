# О проекта:
Foodgram позволяет регистрироваться, создавать рецепты, добавлять рецепты в избранное, подписываться на любимых авторов, а так же добавлять ингредиентыф в список покупок и скачивать его.

# Ссылка на сайт:
https://weloveatastyfoods.ddns.net/

# Разворачиваем проект удалённо:
- Скачайте репозиторий на свой компьютер.
```text
git@github.com:NovikovMU/foodgram-project-react.git
```
-Переходим на удалённый сервер и устанавливаем Docker:
```text
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```
-Устанавливаем nginx:
```text
sudo apt install nginx -y
sudo systemctl start nginx
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```
-Создаем папку foodgram и копируем туда файл docker-compose.yml
-В  папке foodgram создаем файл .env и добавляем туда значение:
```text
POSTGRES_USER=<Your POSTGRES_USER>
POSTGRES_PASSWORD=<Your POSTGRES_PASSWORD>
POSTGRES_DB=django

DB_HOST=db
DB_PORT=5432

DEBUG=False
SECRET_KEY=<Your SECRET_KEY>

ALLOWED_HOSTS=<Your ALLOWED_HOSTS>
```
-Акитивируем докер оркестр:
```text
sudo docker compose -f docker-compose.yml up -d
```
-Делаем миграции, собираемс статику:
```text
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
-Прописываем команду:
```text
sudo nano /etc/nginx/sites-enabled/default
```
-Вставтяем данные:
```text
server {
    server_name <Your ip adress>;

    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000;
    }
}
```
-Перезапускаем nginx:
```text
sudo nginx -t
sudo service nginx reload
```
# Работа с CI/CD
Для работа c CI/CD мы будем использовать Github Actions.
В настройках в разделе actions secrets and variables необходимо заполнить следующие значения:
```text
DOCKER_PASSWORD=<пароль от DockerHub>
DOCKER_USERNAME=<имя пользователя>
HOST=<IP сервера>
SSH_KEY=<ваш SSH ключ>
SECRET_KEY=<секретный ключ проекта django>
SSH_PASSPHRASE=<пароль для сервера, если он установлен>
TELEGRAM_TO=<ID чата, в который придет сообщение>
TELEGRAM_TOKEN=<токен вашего бота>
USER=<username для подключения к серверу>
```
Если все данные заполнены правильно, то после каждого пуша в master ветку вам в телеграмм будет приходить сообщение о пересборке dockerа на удалённом сервере.
# Фото пройденных тесто CI/CD
![alt text](https://github.com/NovikovMU/foodgram-project-react/blob/master/check.png?raw=true)