# ShadowNet

**Established 2017 · Programming Education · AI Learning Assistant**

ShadowNet is a programming-learning platform for structured lessons, progress tracking, practical coding, Premium learning and an AI learning assistant.

## Features
- Python, HTML/CSS, C++ and extensible language courses
- Beginner to Semi-pro learning paths
- AI learning assistant with configurable OpenAI model
- Authentication and progress tracking
- Premium learning area
- Privacy and Terms pages
- Developer/Linux-inspired responsive interface
- Gunicorn production support

## Structure
```text
ShadowNet/
├── app.py
├── data.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── auth.html
│   ├── welcome.html
│   ├── dashboard.html
│   ├── language.html
│   ├── ai.html
│   ├── premium.html
│   └── legal.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
python app.py
```
Open `http://127.0.0.1:5000`.

## AI configuration
Set your real key in `.env`:
```env
OPENAI_API_KEY=your-real-key
OPENAI_MODEL=gpt-5.6-luna
```
Never put the API key in HTML, JavaScript, GitHub, screenshots or public documentation.

## Production
```bash
gunicorn app:app
```
With HTTPS, use `COOKIE_SECURE=1` and `FLASK_DEBUG=0`.

## GitHub
```bash
git init
git add .
git commit -m "Initial ShadowNet release"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ShadowNet.git
git push -u origin main
```
The real `.env` is intentionally excluded; commit `.env.example` instead.

## Roadmap
Code playground · quizzes · challenges · XP and streaks · certificates · advanced Premium Master Class · admin dashboard · additional AI modes and languages.

## License
Add a license before public distribution if you intend ShadowNet to be open source.

**ShadowNet — Learn. Build. Master.**
