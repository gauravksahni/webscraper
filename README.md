# Web Scraper Application

A production-level web scraping application that allows users to scrape any webpage and store the results in a PostgreSQL database. The application consists of a Python backend using FastAPI and a React frontend served through Nginx.

## Features

- Scrape any webpage by providing its URL
- Store scraped data in PostgreSQL database
- View history of previously scraped pages
- Search functionality for scraped content
- Nginx as reverse proxy and static file server
- Docker containerized for easy deployment
- Internet-accessible configuration

## Architecture

### Backend
- **Python FastAPI**: RESTful API for web scraping and data management
- **BeautifulSoup4**: HTML parsing and content extraction
- **SQLAlchemy**: ORM for database interactions
- **PostgreSQL**: Database for storing scraped data

### Frontend
- **React**: User interface with component-based architecture
- **React Router**: Client-side routing
- **Axios**: HTTP client for API requests
- **Nginx**: Web server and reverse proxy

## Project Structure

```
web-scraper/
├── .env                         # Environment variables (not in version control)
├── docker-compose.yml           # Docker Compose configuration
│
├── backend/
│   ├── app.py                   # FastAPI application
│   ├── Dockerfile               # Backend Docker configuration
│   ├── requirements.txt         # Python dependencies
│   └── tests/                   # Unit tests
│       └── test_app.py          # API tests
│
├── frontend/
│   ├── public/                  # Static files
│   ├── src/                     # React components
│   │   ├── App.js               # Main application component
│   │   ├── App.css              # Styles
│   │   ├── index.js             # Entry point
│   │   └── reportWebVitals.js   # Performance reporting
│   ├── nginx/                   # Nginx configuration
│   │   └── nginx.conf           # Nginx server config
│   ├── Dockerfile               # Frontend Dockerfile with Nginx
│   └── package.json             # Node.js dependencies
└── README.md                    # Project documentation
```

## Getting Started

### Prerequisites
- Docker and Docker Compose

### Installation and Running

1. Clone the repository
```bash
git clone https://github.com/yourusername/web-scraper.git
cd web-scraper
```

2. Create a `.env` file for database credentials
```
POSTGRES_USER=app_user
POSTGRES_PASSWORD=your_strong_password
POSTGRES_DB=webscraper
```

3. Start the application using Docker Compose
```bash
docker-compose up -d
```

4. Access the application
- Local: http://localhost
- Internet (if deployed on a server): http://your-server-ip

## API Endpoints

- `POST /api/scrape/`: Scrape a new webpage
- `GET /api/pages/`: Get all scraped pages
- `GET /api/pages/{page_id}`: Get a specific scraped page by ID
- `GET /api/search/?query={query}`: Search for pages containing specific content

## Database Commands

### Login to the Database
```bash
docker-compose exec db psql -U postgres -d webscraper
```

### Useful Database Commands
```sql
-- List all tables
\dt

-- View schema for the scraped_pages table
\d scraped_pages

-- Query data from the table
SELECT id, url, title, scraped_at FROM scraped_pages;

-- Exit the PostgreSQL prompt
\q
```

## Development

### Backend Development

The backend code is mounted as a volume, allowing you to make changes without rebuilding:
```bash
# Make changes to app.py or other files
# The server will automatically reload
```

### Frontend Development

For the frontend, you need to rebuild when making changes:
```bash
# After making changes to React code
docker-compose build frontend
docker-compose up -d
```

## Deployment to Internet

The application is configured to be accessible from the internet. Key points:

1. Nginx binds to all network interfaces on port 80
2. CORS is configured to allow access from any origin
3. The database is not directly exposed to the internet
4. All services run in a Docker network isolation

### Server Requirements
- A server with a public IP address
- Docker and Docker Compose installed
- Port 80 open in the firewall

## Troubleshooting

### Common Issues

**Module not found: Error: Can't resolve './reportWebVitals'**  
Make sure the `reportWebVitals.js` file exists in your `/frontend/src` directory.

**Database connection errors**  
Check your environment variables and ensure the database container is running:
```bash
docker-compose ps
```

**Container not starting**  
Check the logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

## Security Considerations

- Use strong database passwords in the `.env` file
- The current setup doesn't include SSL/TLS (HTTPS)
- For production environments, consider adding SSL with Let's Encrypt
- Limit scraping frequency to avoid overwhelming target websites
- Respect robots.txt files when scraping websites

## Example Websites for Scraping

For testing and educational purposes, these websites are generally scraper-friendly:

- https://en.wikipedia.org/wiki/Main_Page
- http://books.toscrape.com/
- http://quotes.toscrape.com/
- https://www.weather.gov/
- https://openlibrary.org/
- https://data.nasa.gov/

## License

This project is licensed under the MIT License.
