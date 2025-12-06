import os
import secrets
from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

# Password from environment variable
SHORTEN_PASSWORD = os.getenv('SHORTEN_PASSWORD', 'defaultpassword')

# Database configuration (file in /tmp when on Vercel)
if os.getenv('VERCEL'):
    db_path = 'sqlite:////tmp/urls.db'
else:
    db_path = 'sqlite:///urls.db'

app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class ShortenedURL(db.Model):
    __tablename__ = 'shortened_urls'
    id = db.Column(db.String(64), primary_key=True)
    long_url = db.Column(db.Text, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


def init_db():
    # Ensure we create tables within the application context
    with app.app_context():
        db.create_all()


init_db()


def generate_short_code(length=6):
    """Generate a random short code"""
    return secrets.token_urlsafe(length)[:length]


def get_base_url():
    """Get the base URL for shortened links"""
    if os.getenv('VERCEL_URL'):
        return f"https://{os.getenv('VERCEL_URL')}"
    elif os.getenv('VERCEL'):
        return "https://your-vercel-domain.vercel.app"  # Update with your domain
    else:
        # Use the request context to get the actual host/port dynamically
        return request.host_url.rstrip('/')


@app.route('/', methods=['GET'])
def index():
    """Serve the homepage"""
    return send_from_directory('public', 'index.html')


@app.route('/api/shorten', methods=['POST'])
def shorten():
    """Create a shortened URL using ORM"""
    data = request.json or {}

    # Validate password
    password = data.get('password', '')
    if password != SHORTEN_PASSWORD:
        return jsonify({'error': 'Invalid password'}), 401

    # Validate URL
    long_url = (data.get('url', '') or '').strip()
    if not long_url:
        return jsonify({'error': 'URL is required'}), 400
    if not long_url.startswith(('http://', 'https://')):
        long_url = 'https://' + long_url

    # If this long URL already exists, return the existing short URL
    existing = ShortenedURL.query.filter_by(long_url=long_url).first()
    if existing:
        base_url = get_base_url()
        short_url = f"{base_url}/r/{existing.id}"
        return jsonify({
            'short_url': short_url,
            'short_code': existing.id,
            'long_url': long_url,
            'note': 'already_exists'
        }), 200

    # Generate a unique short code and store in database (retry on id collision)
    attempts = 0
    short_code = None
    while attempts < 5:
        attempts += 1
        candidate = generate_short_code()
        obj = ShortenedURL(id=candidate, long_url=long_url)
        db.session.add(obj)
        try:
            db.session.commit()
            short_code = candidate
            break
        except IntegrityError:
            db.session.rollback()
            # If collision on id (primary key) or duplicate long_url, retry
            continue

    if not short_code:
        return jsonify({'error': 'Failed to create shortened URL'}), 500

    base_url = get_base_url()
    short_url = f"{base_url}/r/{short_code}"
    return jsonify({
        'short_url': short_url,
        'short_code': short_code,
        'long_url': long_url
    }), 201


import urllib.parse

def encode_fragment_param(url: str) -> str:
    """
    Split URL at '#', then split fragment into key=value.
    Fully URL-encode the value part. Return final URL.
    """
    if "#" not in url:
        return url  # nothing to encode

    base, fragment = url.split("#", 1)

    # fragment like: "project={...long...json...}"
    if "=" not in fragment:
        # encode whole fragment
        encoded = urllib.parse.quote(fragment, safe="")
        return f"{base}#{encoded}"

    key, value = fragment.split("=", 1)
    encoded_value = urllib.parse.quote(value, safe="")

    return f"{base}#{key}={encoded_value}"

@app.route('/r/<short_code>')
def redirect_url(short_code):
    """Redirect to the original URL"""
    row = ShortenedURL.query.get(short_code)
    if row:
        long_url = encode_fragment_param(row.long_url)
        return redirect(long_url)


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
