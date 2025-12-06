# Personal URL Shortener

A simple, self-hosted URL shortener app built with Flask and deployed on Vercel.

## Features

- 🔗 Create short, shareable links from long URLs
- 🔐 Password-protected URL creation
- 🔀 Long URLs redirects
- 🚀 Deployed on Vercel
- 💾 SQLite database for URL storage

## Project Structure

```
shortener/
├── app.py                 # Flask backend API
├── public/
│   └── index.html        # Frontend UI
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel deployment config
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Local Development

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
cd shortener
```

2. Create a virtual environment (choose one):

**Option A: Using conda**
```bash
conda create -n shortener python=3.11
conda activate shortener
```

**Option B: Using venv**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and set SHORTEN_PASSWORD=your_secure_password
```

5. Run the app:
```bash
python app.py
```

The app will be available at `http://localhost:8000`

## API Endpoints

### POST /api/shorten

Create a shortened URL.

**Request:**
```json
{
  "url": "https://example.com/very/long/url",
  "password": "your_password"
}
```

**Response (201):**
```json
{
  "short_url": "https://your-domain.vercel.app/r/abc123",
  "short_code": "abc123",
  "long_url": "https://example.com/very/long/url"
}
```

**Error Response (401):**
```json
{
  "error": "Invalid password"
}
```

### GET /r/<short_code>

Redirect to the original URL.

Example: `https://your-domain.vercel.app/r/abc123`

### GET /api/health

Health check endpoint.

## Deployment on Vercel

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/shortener.git
git push -u origin main
```

### 2. Connect to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign up or log in
3. Click "Add New..." → "Project"
4. Import your GitHub repository
5. Set environment variables:
   - `SHORTEN_PASSWORD`: Your secure password

### 3. Deploy

Click "Deploy" and Vercel will automatically deploy your app.

## Environment Variables

Create a `.env` file in the root directory:

```
SHORTEN_PASSWORD=your_secure_password
```

For Vercel, add this in Project Settings → Environment Variables.

**Note**: On Vercel, the app automatically uses the `PORT` environment variable assigned by Vercel. Locally, it defaults to port 8000.

## Usage

1. Open the app homepage
2. Enter a long URL in the "Full URL" field
3. Enter the password in the "Password" field
4. Click "Shorten Link"
5. Copy the generated shortened link
6. Share it with anyone!

When someone visits the shortened link, they'll be redirected to the original URL.

## How It Works

- **URL Shortening**: Uses `secrets.token_urlsafe()` to generate random 6-character codes
- **Duplicate Detection**: Returns existing short code if URL already shortened
- **Database**: SQLite with ORM (Flask-SQLAlchemy) stores mappings between short codes and original URLs
- **Redirects**: Support complex URLs with special characters (including JSON fragments)
- **Password Protection**: All shortening requests require the correct password

## Security Considerations

- Change the default password immediately
- Use HTTPS only (Vercel provides this by default)
- Consider rate limiting for production use
- The password is transmitted in the request body; use HTTPS to encrypt

## License

MIT
