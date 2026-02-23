# کانبان فارسی (RTL) — FastAPI + HTMX + MySQL + Redis

این پروژه یک نرم‌افزار Kanban مینیمال، سبک و مدرن با UI داشبوردی شبیه قالب‌های ادمین (سبک Frest) است.
همه‌ی متن‌ها فارسی هستند و کل UI RTL می‌باشد.

## ویژگی‌ها
- ایجاد پروژه
- هر پروژه یک برد کانبان
- ستون‌ها قابل تنظیم (افزودن/ویرایش/حذف نرم)
- تسک‌ها: عنوان، توضیح، اولویت، تاریخ سررسید، وضعیت، ترتیب
- Drag & Drop کارت‌ها بین ستون‌ها (با SortableJS) و ذخیره در دیتابیس
- HTMX برای ایجاد/حذف/جابجایی بدون رفرش
- کش داده‌ی برد با Redis (با invalidation پس از تغییرات)
- REST API کامل برای `projects`, `columns`, `tasks`

---


## اجرای پروژه با Docker (پیشنهادی برای ویندوز/لینوکس)

### پیش‌نیاز
- Docker Desktop (یا Docker Engine + docker compose)

### اجرا
```bash
# داخل پوشه پروژه
docker compose up --build

> نکته مهم (ویندوز): برای جلوگیری از خطای دسترسی/رزرو پورت‌ها، پورت‌های **MySQL** و **Redis** به‌صورت پیش‌فرض روی Host منتشر نشده‌اند.
> اپلیکیشن داخل شبکه‌ی Docker به سرویس‌ها وصل می‌شود و مشکلی ندارد.
>
> اگر نیاز دارید از خود ویندوز به MySQL وصل شوید، می‌توانید در `docker-compose.yml` بخش `ports` را برای mysql اضافه کنید؛
> مثال:
> ```yaml
> ports:
>   - "4306:3306"
> ```
> سپس با `localhost:4306` متصل شوید.
>
> برای اجرای دستورهای MySQL بدون Publish کردن پورت:
> ```bash
> docker exec -i kanban-mysql mysql -ukanban -pkanban kanban_db
> ```

```

سپس:
- اپ: `http://localhost:8000/`
- MySQL: `localhost:3306` (user: `kanban` / pass: `kanban`)
- Redis: `localhost:6379`

> نکته: در اولین اجرا، فایل‌های `schema.sql` و `sample_data.sql` به صورت خودکار داخل MySQL ایمپورت می‌شوند.

### توقف
```bash
docker compose down
```


### اگر خطای احراز هویت MySQL (cryptography) دیدید
اگر در لاگ `kanban-web` خطای زیر را دیدید:
`cryptography package is required for sha256_password or caching_sha2_password`
این نسخه با افزودن پکیج `cryptography` مشکل را حل می‌کند.

اگر قبلاً کانتینر را اجرا کرده‌اید و Volume دیتابیس ساخته شده، پیشنهاد می‌شود یکبار ریست کنید:
```bash
docker compose down -v
docker compose up --build
```

### ریست کامل دیتابیس (حذف Volume)
```bash
docker compose down -v
```


## اجرای سریع (Local)

### پیش‌نیازها
- Python 3.11+
- MySQL
- Redis

### 1) ساخت محیط با uv
```bash
# نصب uv (اگر ندارید)
curl -LsSf https://astral.sh/uv/install.sh | sh

cd kanban_fa
uv venv
source .venv/bin/activate

# نصب وابستگی‌ها
uv pip install -r requirements.lock
# یا:
# uv pip install fastapi uvicorn sqlalchemy pymysql redis jinja2 python-multipart pydantic-settings
```

### 2) تنظیم محیط
```bash
cp .env.example .env
# DATABASE_URL و REDIS_URL را تنظیم کنید
```

### 3) ساخت دیتابیس و اعمال نمونه داده
```bash
mysql -u root -p < schema.sql
mysql -u root -p < sample_data.sql
```

### 4) اجرای برنامه
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
سپس:
- داشبورد: `http://127.0.0.1:8000/`

---

## ساختار پروژه
```
app/
 ├── main.py
 ├── core/
 ├── db/
 ├── models/
 ├── schemas/
 ├── services/
 ├── routes/
 ├── templates/
 ├── static/
```

---

## Endpoints مهم (وب + HTMX)
- `GET /` داشبورد پروژه‌ها
- `POST /htmx/projects` ایجاد پروژه (partial)
- `GET /projects/{project_id}` صفحه برد
- `GET /htmx/projects/{project_id}/board` بارگذاری برد (partial)
- `POST /htmx/projects/{project_id}/tasks` ایجاد تسک (partial)
- `DELETE /htmx/tasks/{task_id}` حذف تسک (partial)
- `PUT /htmx/tasks/{task_id}/move` جابجایی با Drag&Drop

## REST API
پایه: `/api/v1`
- `GET/POST /projects`
- `GET/PUT/DELETE /projects/{id}`
- `GET/POST /columns`
- `GET/PUT/DELETE /columns/{id}`
- `GET/POST /tasks`
- `GET/PUT/DELETE /tasks/{id}`

---

# راهنمای دیپلوی روی Ubuntu (مخصوص Production)

> این راهنما روی Ubuntu 22.04/24.04 تست‌پذیر است.

## 1) نصب پکیج‌های سیستم
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip build-essential   mysql-server redis-server nginx
```

## 2) ساخت دیتابیس و کاربر
```bash
sudo mysql
```
داخل MySQL:
```sql
CREATE DATABASE kanban_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'kanban'@'localhost' IDENTIFIED BY 'kanban';
GRANT ALL PRIVILEGES ON kanban_db.* TO 'kanban'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```
سپس:
```bash
mysql -u root -p < schema.sql
mysql -u root -p < sample_data.sql
```

## 3) نصب uv و وابستگی‌ها
```bash
# ایجاد مسیر نصب
sudo mkdir -p /opt/kanban
sudo chown -R $USER:$USER /opt/kanban

# کپی پروژه
cp -r . /opt/kanban
cd /opt/kanban

# نصب uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# ساخت venv و نصب
uv venv
source .venv/bin/activate
uv pip install -r requirements.lock
```

## 4) تنظیم env
```bash
cp .env.example .env
nano .env
```
در Production پیشنهاد می‌شود فایل env را در مسیر جدا قرار دهید:
`/etc/kanban.env`

نمونه `/etc/kanban.env`:
```
APP_NAME="کانبان فارسی"
ENV="prod"
SECRET_KEY="یک-کلید-قوی"
DATABASE_URL="mysql+pymysql://kanban:kanban@127.0.0.1:3306/kanban_db?charset=utf8mb4"
REDIS_URL="redis://127.0.0.1:6379/0"
DEFAULT_USER_EMAIL="demo@example.com"
DEFAULT_USER_NAME="کاربر نمونه"
```

## 5) ساخت سرویس systemd
فایل:
`/etc/systemd/system/kanban.service`
```ini
[Unit]
Description=Kanban Farsi (FastAPI)
After=network.target mysql.service redis-server.service

[Service]
Type=simple
WorkingDirectory=/opt/kanban
EnvironmentFile=/etc/kanban.env
ExecStart=/opt/kanban/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

فعال‌سازی:
```bash
sudo systemctl daemon-reload
sudo systemctl enable kanban
sudo systemctl start kanban
sudo systemctl status kanban --no-pager
```

## 6) تنظیم Nginx (Reverse Proxy)
فایل:
`/etc/nginx/sites-available/kanban`
```nginx
server {
  listen 80;
  server_name _;

  client_max_body_size 20m;

  location /static/ {
    alias /opt/kanban/app/static/;
    expires 7d;
    add_header Cache-Control "public";
  }

  location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

فعال‌سازی:
```bash
sudo ln -s /etc/nginx/sites-available/kanban /etc/nginx/sites-enabled/kanban
sudo nginx -t
sudo systemctl reload nginx
```

## 7) دامنه (اختیاری) + SSL
برای SSL می‌توانید از Certbot استفاده کنید:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx
```

---

## نکات
- برای نسخه مینیمال، احراز هویت پیاده‌سازی نشده و یک کاربر پیش‌فرض ایجاد می‌شود.
- کش برد: کلید `board:{project_id}` با TTL کوتاه و invalidation بعد از تغییرات.



## نکته
- برای SessionMiddleware، پکیج `itsdangerous` به وابستگی‌ها اضافه شده است.


## رفع هشدار bcrypt
- برای جلوگیری از هشدار Passlib/Bcrypt، نسخه `bcrypt==3.2.2` پین شده است.


## رفع مشکل Mixed Content روی HTTPS
اگر صفحه روی HTTPS بالا می‌آید ولی فایل‌های `/static` با HTTP درخواست می‌شوند،
این نسخه لینک‌های استاتیک را **relative** می‌کند و Uvicorn را با `--proxy-headers` اجرا می‌کند.


## نکته برای برخی سرورها با CPU قدیمی
اگر موقع بالا آمدن MySQL خطای زیر را دیدید:
`Fatal glibc error: CPU does not support x86-64-v2`
یعنی CPU سرور شما با ایمیج‌های جدید MySQL ناسازگار است. این پروژه روی سرور با **MariaDB 10.11** تنظیم شده که سازگارتر است.

## هشدار Redis: overcommit_memory
اگر هشدار `Memory overcommit must be enabled` دیدید، روی Ubuntu اجرا کنید:
```bash
sudo sysctl vm.overcommit_memory=1
echo 'vm.overcommit_memory=1' | sudo tee -a /etc/sysctl.conf
```
