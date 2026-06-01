# Simple LMS - Progress 4

Project ini merupakan lanjutan dari Simple LMS untuk mata kuliah Pemrograman Server. Pada progress 4, sistem dikembangkan dengan fitur Redis caching, MongoDB activity logging, Celery asynchronous task, RabbitMQ message broker, dan Flower monitoring.

## Fitur Progress 4

### 1. Redis Integration
- Course list caching
- Course detail caching
- Cache invalidation ketika instructor membuat course baru
- Rate limiting sederhana 60 request per menit per IP

### 2. MongoDB Integration
- Activity logs disimpan ke collection `activity_logs`
- Learning analytics disimpan ke collection `learning_analytics`
- Aggregation query untuk laporan statistik course

### 3. Celery Tasks
- `send_enrollment_email`
- `generate_certificate`
- `update_course_statistics`
- `export_course_report`

### 4. RabbitMQ
RabbitMQ digunakan sebagai message broker untuk Celery.

### 5. Flower
Flower digunakan untuk monitoring task Celery.

## Arsitektur Sistem

```mermaid
flowchart TD
    User[User / Client] --> Web[Django Web API]
    Web --> Postgres[(PostgreSQL)]
    Web --> Redis[(Redis Cache)]
    Web --> MongoDB[(MongoDB)]
    Web --> RabbitMQ[RabbitMQ Broker]
    RabbitMQ --> Worker[Celery Worker]
    Worker --> MongoDB
    Worker --> Postgres
    Beat[Celery Beat Scheduler] --> RabbitMQ
    Flower[Flower Monitoring] --> RabbitMQ