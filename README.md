# EC2 Deployment

# install python > 3.11 via pyenv
First, the project requires python version above 3.11. If not, install pyenv:

sudo yum update
sudo yum install gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel

git clone https://github.com/pyenv/pyenv.git ~/.pyenv

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
source ~/.bashrc

pyenv install 3.11.5
pyenv global 3.11.5

python --version

# install git & poetry

sudo yum install git
git --version

After python version above 3.11 is installed, install poetry:

# Poetry 1.6.1 설치
curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.6.1 python3 -

# 환경 변수 설정
echo 'export PATH="$HOME/.poetry/bin:$PATH"' >> ~/.bashrc

# 변경사항 적용
source ~/.bashrc

# 설치 확인
poetry --version


Then navigate to backend root and run:

`poetry install`

# On adding new dependencies

- Use `poetry add <package-name>` instead of `pip install <package-name>`
- After package is added by others, run `poetry install` to install the new package

# Migrate
`poetry run python manage.py migrate`

# Run
`poetry run python manage.py runserver`

# .env
fix .env file manually 

## Gunicorn 
`https://velog.io/@jiyoung/GunicornNginx-%EB%A6%AC%EB%88%85%EC%8A%A4-%EC%84%9C%EB%B2%84%EC%97%90%EC%84%9C-%EB%B0%B0%ED%8F%AC%ED%95%98%EA%B8%B0` 참고

Gunicorn service setting is at `/etc/systemd/system/gunicorn.service`. This is currently configured as following:

```conf
[Unit]
Description=gunicorn daemon for the artant project
After=network.target

[Service]
User=ec2-user
Group=nginx
WorkingDirectory=/home/ec2-user/artant-BE
ExecStart=/home/ec2-user/.local/bin/poetry run gunicorn --workers 3 --bind 0.0.0.0:8000 config.wsgi:applica>
Restart=always

[Install]
WantedBy=multi-user.target

```

In case this is changed, please run: `sudo systemctl daemon-reload && sudo systemctl restart gunicorn`

## nginx

nginx service setting is at `/etc/nginx/nginx.conf`. This is currently configured as following:

```conf
  server {
    listen 80;
    server_name ec2-13-125-251-12.ap-northeast-2.compute.amazonaws.com;  # EC2 인스턴스의 도메인 주소

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias /home/ec2-user/artant-BE/staticfiles/;  # Django 프로젝트의 정적 파일 경로
    }

    location / {
        include proxy_params;
        proxy_pass http://0.0.0.0:8000;  # Gunicorn TCP 소켓 주소
    }
}


```


## Static files
To serve static files required by e.g. admin sites, one has to first run `poetry run python manage.py collectstatic`.
Then, the static files will be collected to `backend/staticfiles` as specified in `config/settings.py`.

In case of `403 Forbidden` from nginx, one has to run something like below to ensure nginx can access the static files:
```bash
sudo chmod 711 /home/ec2-user/
sudo chown -R ec2-user:nginx /home/ec2-user/artant-BE/staticfiles/
sudo chmod 755 /home/ec2-user//artant-BE/
sudo chmod -R 755 /home/ec2-user/artant-BE/staticfiles/

sudo systemctl restart nginx


# gpt link 참고 'https://chat.openai.com/share/bfa4ebbf-2611-451d-8602-bdcf0c68aad2'