# Диаграмма базы данных Todo List

## Таблицы

### users
| Поле | Тип | Описание |
|------|-----|----------|
| user_id | BIGINT (PK) | ID пользователя |
| username | VARCHAR(255) | Имя пользователя |
| first_name | VARCHAR(255) | Имя |
| last_name | VARCHAR(255) | Фамилия |
| created_at | TIMESTAMP | Дата регистрации |

### tasks
| Поле | Тип | Описание |
|------|-----|----------|
| id | SERIAL (PK) | ID задачи |
| user_id | BIGINT (FK) | ID пользователя |
| title | VARCHAR(500) | Название |
| status | VARCHAR(20) | Статус |
| created_at | TIMESTAMP | Создана |
| updated_at | TIMESTAMP | Обновлена |

## ER-диаграмма
users (1) ----< (many) tasks
