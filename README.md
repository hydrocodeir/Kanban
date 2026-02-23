# سامانه کانبان سازمانی (FastAPI + HTMX + MySQL)

## معرفی پروژه
این پروژه نسخه بازطراحی‌شده و توسعه‌یافته‌ی کانبان با تمرکز بر نیازهای سازمانی است:
- احراز هویت چندکاربره
- کنترل دسترسی مبتنی بر نقش (مدیر/کاربر)
- ثبت لاگ فعالیت (Audit Trail)
- REST API کامل
- رابط HTMX با طراحی RTL فارسی و حالت تاریک
- اعلان تلگرام
- استقرار Docker + Nginx + MySQL

## نقش‌ها
- **مدیر (admin):** مدیریت کامل کاربران، بوردها، ستون‌ها، وظایف و مشاهده همه لاگ‌ها.
- **کاربر (user):** مدیریت داده‌های متعلق به خودش و مشاهده لاگ شخصی.

## Activity Log
رویدادهای زیر ثبت می‌شود:
- ایجاد/ویرایش/حذف وظیفه
- تغییر وضعیت وظیفه
- ورود/ثبت‌نام کاربر
- ایجاد/ویرایش/حذف بورد و ستون

فیلدهای لاگ:
`id`, `user_id`, `action`, `target_type`, `target_id`, `created_at`

## REST API
### Authentication
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`

### Users
- `GET /api/users/` (مدیر)
- `GET /api/users/me`
- `PATCH /api/users/{user_id}`

### Boards
- `GET /api/boards/`
- `POST /api/boards/`
- `PUT /api/boards/{board_id}`
- `DELETE /api/boards/{board_id}`

### Columns
- `GET /api/columns/{board_id}`
- `POST /api/columns/`

### Tasks
- `GET /api/tasks/column/{column_id}`
- `POST /api/tasks/`
- `PATCH /api/tasks/{task_id}`
- `DELETE /api/tasks/{task_id}`

### Activity Logs
- `GET /api/logs/`

## Telegram Notifications
تنظیمات کاربر:
- `telegram_chat_id`
- `notify_enabled`

پیام‌های فارسی پشتیبانی‌شده:
- «یک وظیفه جدید به شما اختصاص داده شد»
- «وضعیت یک وظیفه تغییر کرد»
- «یک وظیفه حذف شد»
- «یک بورد جدید ایجاد شد»

> توکن ربات باید با متغیر محیطی `TELEGRAM_BOT_TOKEN` تنظیم شود.

## رابط کاربری (HTMX + RTL)
- `dir="rtl"` و Bootstrap RTL
- فونت Vazirmatn
- داشبورد با سایدبار و نشان نقش
- ستون‌های استاندارد فارسی:
  - برای انجام
  - در حال انجام
  - انجام‌شده
- کلید تغییر حالت روشن/تاریک

## امنیت و عملکرد
- هش رمز عبور با bcrypt (passlib)
- JWT برای API
- محافظت اولیه brute-force روی ورود
- ORM parameterized query (SQLAlchemy)
- استفاده از ایندکس‌ها و کلیدهای خارجی

## اجرای پروژه با Docker
```bash
docker compose up --build
```

سرویس‌ها:
- `app` (FastAPI)
- `mysql` (MySQL 8)
- `nginx` (Reverse Proxy)

## ساختار پروژه
```text
app/
  core/
  models/
  routers/
  schemas/
  services/
  static/
  templates/
alembic/
nginx/
Dockerfile
docker-compose.yml
```
