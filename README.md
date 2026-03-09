# FarmDirect - Farm-to-Table Marketplace

A production-grade marketplace platform connecting local farmers directly with consumers.
FarmDirect eliminates the middleman, ensuring farmers receive fair prices while consumers
get fresh, seasonal produce delivered to their doorstep.

## Features

- **Seasonal Product Listings** -- Browse products organized by season and availability, with real-time harvest status updates from farmers.
- **Subscription Boxes** -- Customizable weekly or biweekly subscription boxes with seasonal produce, curated by local farms.
- **Farm Profiles** -- Detailed profiles for each farm including location, certifications, growing practices, and photo galleries.
- **Delivery Scheduling** -- Flexible delivery windows with route optimization and real-time tracking.
- **Organic Certification Tracking** -- Verified organic, pesticide-free, and other certifications displayed on every product and farm profile.
- **Harvest Calendar** -- Interactive calendar showing what is in season, expected harvest dates, and pre-order availability.
- **Reviews and Ratings** -- Community-driven reviews for farms and individual products.
- **Farmer Dashboard** -- Full inventory management, order tracking, and sales analytics for farmers.

## Tech Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Backend      | Django 5.x + Django REST Framework |
| Frontend     | React 18 + Redux Toolkit          |
| Database     | PostgreSQL 16                      |
| Cache/Broker | Redis 7                            |
| Task Queue   | Celery 5                           |
| Reverse Proxy| Nginx                              |
| Containers   | Docker + Docker Compose            |

## Project Structure

```
farmdirect/
├── backend/
│   ├── apps/
│   │   ├── accounts/      # User management, farmer/consumer profiles
│   │   ├── farms/          # Farm profiles, certifications, harvest calendar
│   │   ├── products/       # Product catalog, categories, seasonal availability
│   │   ├── orders/         # Orders, order items, delivery scheduling
│   │   ├── subscriptions/  # Subscription boxes, plans, recurring orders
│   │   └── reviews/        # Product and farm reviews
│   ├── config/             # Django settings, URLs, WSGI, Celery
│   └── utils/              # Shared utilities, pagination, exception handling
├── frontend/
│   ├── public/
│   └── src/
│       ├── api/            # API client and service modules
│       ├── components/     # Reusable UI components
│       ├── pages/          # Route-level page components
│       ├── store/          # Redux store and slices
│       ├── hooks/          # Custom React hooks
│       └── styles/         # Global CSS
├── nginx/                  # Nginx reverse proxy configuration
├── docker-compose.yml
└── .env.example
```

## Getting Started

### Prerequisites

- Docker Engine 24+ and Docker Compose v2
- Git

### Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/farmdirect.git
   cd farmdirect
   ```

2. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your values (database credentials, secret key, etc.)
   ```

3. **Build and start the services**

   ```bash
   docker compose up --build -d
   ```

4. **Run database migrations**

   ```bash
   docker compose exec backend python manage.py migrate
   ```

5. **Create a superuser**

   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

6. **Access the application**

   - Frontend: http://localhost
   - API: http://localhost/api/
   - Admin: http://localhost/api/admin/
   - API Docs: http://localhost/api/docs/

### Development Without Docker

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py migrate
python manage.py runserver
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

## API Overview

| Endpoint                    | Methods              | Description                   |
|-----------------------------|----------------------|-------------------------------|
| `/api/auth/register/`       | POST                 | User registration             |
| `/api/auth/login/`          | POST                 | Obtain JWT token pair         |
| `/api/auth/token/refresh/`  | POST                 | Refresh access token          |
| `/api/accounts/profile/`    | GET, PUT, PATCH      | User profile management       |
| `/api/farms/`               | GET, POST            | List / create farms           |
| `/api/farms/{id}/`          | GET, PUT, PATCH, DEL | Farm detail                   |
| `/api/products/`            | GET, POST            | Product catalog               |
| `/api/products/{id}/`       | GET, PUT, PATCH, DEL | Product detail                |
| `/api/orders/`              | GET, POST            | Order management              |
| `/api/orders/{id}/`         | GET, PUT, PATCH      | Order detail                  |
| `/api/subscriptions/plans/` | GET                  | List subscription plans       |
| `/api/subscriptions/boxes/` | GET, POST            | Subscription box management   |
| `/api/reviews/`             | GET, POST            | Reviews                       |

## Environment Variables

See [.env.example](.env.example) for the full list of configurable environment variables.

## Testing

```bash
# Run backend tests
docker compose exec backend python manage.py test

# Run frontend tests
docker compose exec frontend npm test
```

## Deployment

For production deployments:

1. Set `DJANGO_SETTINGS_MODULE=config.settings.production` in your `.env`.
2. Set `DEBUG=False` and configure a strong `SECRET_KEY`.
3. Configure your domain in `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`.
4. Set up SSL/TLS certificates and update the Nginx config accordingly.
5. Configure a production-grade PostgreSQL instance with proper backup policies.
6. Set up monitoring and log aggregation (Sentry, Prometheus, ELK, etc.).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
