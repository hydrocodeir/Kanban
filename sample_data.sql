USE kanban_db;

INSERT INTO users (full_name, email, password_hash) VALUES
  ('admin', 'admin@hydrocode.ir', NULL)
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

INSERT INTO projects (user_id, title, description) VALUES
  (1, 'پروژه نمونه', 'این یک پروژه نمونه برای تست برد کانبان است.');

INSERT INTO boards (project_id, title) VALUES
  (1, 'برد کانبان');

INSERT INTO columns (board_id, title, position) VALUES
  (1, 'در انتظار انجام', 0),
  (1, 'در حال انجام', 1),
  (1, 'انجام شده', 2);

INSERT INTO tasks (project_id, column_id, assignee_id, title, description, priority, due_date, status, position) VALUES
  (1, 1, NULL, 'راه‌اندازی پروژه', 'ساخت ساختار اولیه و تنظیمات', 2, DATE_ADD(CURDATE(), INTERVAL 3 DAY), 'در انتظار انجام', 0),
  (1, 2, NULL, 'طراحی UI RTL', 'پیاده‌سازی سایدبار و ناوبری', 3, DATE_ADD(CURDATE(), INTERVAL 5 DAY), 'در حال انجام', 0),
  (1, 3, NULL, 'تست و دیپلوی', 'راهنمای دیپلوی Ubuntu و Nginx', 1, DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'انجام شده', 0);
