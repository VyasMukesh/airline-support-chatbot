# ✈️ Airline Support Chatbot

A comprehensive Django-based airline support chatbot with AI-powered intent classification, natural language understanding, and real-time booking management.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.2.7-green)
![BERT](https://img.shields.io/badge/BERT-Enabled-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

### Core Functionality
- **🤖 AI-Powered Intent Classification**: Uses BERT-based Sentence Transformers for natural language understanding
- **📋 Booking Management**: View, select, and manage flight bookings
- **❌ Flight Cancellation**: Cancel bookings with instant refund calculations
- **✈️ Real-time Flight Status**: Check flight status (On Time, Delayed, Departed, Arrived)
- **💺 Seat Information**: View assigned seats and availability
- **🐕 Pet Travel Policy**: Check pet travel rules and restrictions

### Technical Features
- **Session-based PNR Verification**: One-time PNR verification per session
- **Sticky Booking Selection**: Remembers selected booking throughout conversation
- **Smart Intent Detection**: Fallback to keyword matching if BERT unavailable
- **Cancelled Booking Visualization**: Shows cancelled bookings in red immediately after cancellation
- **Auto-filtering**: Hides cancelled bookings from future queries
- **Comprehensive Audit Trail**: Logs all actions in ProcessLog and CancelledBooking tables

## 🏗️ Architecture

### Backend Stack
- **Framework**: Django 5.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: SQLite (development)
- **AI Model**: Sentence Transformers (all-MiniLM-L6-v2)
- **Python**: 3.12.6

### Frontend Stack
- **UI Framework**: Bootstrap 5
- **JavaScript**: Vanilla JS (ES6+)
- **CSS**: Custom styling with responsive design

### Database Schema
```
┌─────────────────┐
│    Booking      │
├─────────────────┤
│ id              │
│ pnr             │
│ flight_id       │
│ source_airport  │
│ dest_airport    │
│ scheduled_dep   │
│ scheduled_arr   │
│ assigned_seat   │
│ current_status  │
└─────────────────┘
        │
        │ 1:1
        ▼
┌─────────────────┐
│ CancelledBooking│
├─────────────────┤
│ booking         │
│ charges         │
│ refund_amount   │
│ refund_date     │
│ cancelled_at    │
└─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│   ProcessLog    │       │    Message      │
├─────────────────┤       ├─────────────────┤
│ action          │       │ session_key     │
│ booking         │       │ sender          │
│ pnr             │       │ text            │
│ payload         │       │ pnr             │
│ result          │       │ created_at      │
│ created_at      │       └─────────────────┘
└─────────────────┘
```

## 🚀 Installation

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/airline-support-bot.git
cd airline-support-bot
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Load Sample Data (Optional)
```bash
python manage.py shell
>>> from support.models import Booking
>>> Booking.objects.create(
...     pnr='ABC123',
...     flight_id='1111',
...     source_airport_code='JFK',
...     destination_airport_code='LAX',
...     scheduled_departure='2025-10-23T10:00:00Z',
...     scheduled_arrival='2025-10-23T16:00:00Z',
...     assigned_seat='12A',
...     current_status='Scheduled'
... )
>>> exit()
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

## 📖 Usage

### 1. PNR Verification
- Click on the chatbot icon
- Enter your PNR (e.g., `ABC123`)
- PNR is remembered for the entire session

### 2. Natural Language Queries

**Show Bookings:**
- "Show my bookings"
- "I want to see all my flights"
- "What flights do I have?"

**Cancel Booking:**
- "Cancel my flight"
- "I need to cancel my trip"
- "Delete my reservation"

**Check Status:**
- "What's my flight status?"
- "Is my flight on time?"
- "Check my flight"

**Seat Information:**
- "What's my seat number?"
- "Show me available seats"
- "Tell me my seat"

**Pet Policy:**
- "Can I bring my dog?"
- "Are pets allowed?"
- "Pet travel policy"

### 3. Booking Selection
- After querying bookings, click on a flight card to select it
- All subsequent queries will use the selected booking

### 4. Cancellation Flow
- Type "cancel"
- Confirm with "Yes, Cancel"
- Cancelled booking shows in RED
- Future queries won't show the cancelled booking

## 🧠 AI Intent Classification

### How It Works

The bot uses **BERT-based Sentence Transformers** for semantic understanding:

```python
from sentence_transformers import SentenceTransformer, util

# Model: all-MiniLM-L6-v2 (lightweight, fast)
model = SentenceTransformer('all-MiniLM-L6-v2')

# User query
query = "I want to cancel my flight"

# Classifies into intents:
# - booked_flights
# - cancel
# - status
# - seat
# - pets
```

### Fallback Mechanism
If BERT fails to load, the system automatically falls back to keyword matching:
- Fast and reliable
- No AI dependency
- Handles basic queries effectively

## 📁 Project Structure

```
asapp/
├── asapp/                      # Django project settings
│   ├── settings.py            # Configuration
│   ├── urls.py                # Main URL routing
│   └── wsgi.py                # WSGI config
├── support/                    # Main app
│   ├── models.py              # Database models
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API endpoints & logic
│   ├── urls.py                # App URL routing
│   └── intent_classifier.py   # BERT intent classifier
├── templates/
│   └── support/
│       └── chat.html          # Chat UI
├── manage.py                  # Django CLI
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── .gitignore                 # Git ignore rules
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file (optional):
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database
Default: SQLite (`db.sqlite3`)

For production, update `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'airline_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🧪 Testing

### Manual Testing Checklist
- [ ] PNR verification works
- [ ] Booking list displays correctly
- [ ] Booking selection persists
- [ ] Cancellation shows red indicator
- [ ] Cancelled bookings hidden from future queries
- [ ] Flight status shows varied responses
- [ ] Invalid queries rejected
- [ ] BERT intent classification works
- [ ] Fallback keyword matching works

### Sample Test PNR
**PNR**: `ABC123`
**Bookings**:
- Flight 1111: JFK → LAX
- Flight 3333: BOS → SFO

## 📊 API Endpoints

### Public Endpoints
- `GET /` - Home page
- `GET /chat` - Chat interface

### API Endpoints
- `POST /api/verify_pnr` - Verify PNR
- `GET /api/check_session` - Restore session
- `POST /api/process` - Process chat message
- `GET /api/bookings?pnr=ABC123` - List bookings
- `POST /api/flight/cancel` - Cancel booking
- `GET /api/bookings/<id>` - Get single booking

## 🎨 Customization

### Change Bot Name
Edit `templates/support/chat.html`:
```html
<div class="chat-header">
  <strong>Your Airline Name</strong> Support Bot
</div>
```

### Modify Flight Statuses
Edit `support/views.py`:
```python
flight_status = random.choice([
    'On Time', 
    'Departed', 
    'Arrived', 
    'Delayed',
    'Boarding',
    'Cancelled'
])
```

### Add More Intents
Edit `support/intent_classifier.py`:
```python
self.intent_examples = {
    # ... existing intents
    'baggage': [
        'baggage policy',
        'luggage allowance',
        'how much can I bring'
    ]
}
```

## 🐛 Troubleshooting

### BERT Model Not Loading
```bash
# Pre-download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Database Migrations
```bash
python manage.py makemigrations support
python manage.py migrate
```

### Clear Session Data
```bash
python manage.py clearsessions
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure production database
- [ ] Set up static files: `python manage.py collectstatic`
- [ ] Use production WSGI server (Gunicorn, uWSGI)
- [ ] Set up HTTPS
- [ ] Configure CORS if needed
- [ ] Set secure `SECRET_KEY`

### Example: Gunicorn Deployment
```bash
pip install gunicorn
gunicorn asapp.wsgi:application --bind 0.0.0.0:8000
```

## 🙏 Acknowledgments

- Django Framework
- Django REST Framework
- Sentence Transformers (Hugging Face)
- Bootstrap 5


## 🔄 Changelog

### Version 1.0.0 (2025-10-22)
- ✅ Initial release
- ✅ BERT-based intent classification
- ✅ Session-based PNR verification
- ✅ Booking management and cancellation
- ✅ Red indicator for cancelled bookings
- ✅ Real-time flight status
- ✅ Comprehensive error handling

---

