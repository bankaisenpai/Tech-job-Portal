# Tech Job Portal

A full-stack web application for searching and saving tech jobs from multiple job boards including Indeed, Glassdoor, and more.

## 🚀 Features

- 🔐 **User Authentication** - Secure registration and login system
- 🔍 **Smart Job Search** - Search across 20+ job boards with a single query
- 💾 **Save Jobs** - Bookmark favorite jobs and access them anytime
- 👤 **User Profile** - Manage preferences and saved jobs
- 🎨 **Modern UI** - Clean, responsive design with smooth animations
- 📧 **Job Alerts** - Get notified about new matching jobs (coming soon)

## 🛠️ Technologies Used

- **Backend:** Python, Flask
- **Database:** MySQL
- **Frontend:** HTML5, CSS3, JavaScript
- **APIs:** JSearch API (RapidAPI)
- **Authentication:** Flask-Session, Werkzeug Security

## 📋 Prerequisites

- Python 3.8+
- MySQL Database
- RapidAPI Account (for JSearch API)

## ⚙️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/bankaisenpai/Tech-job-Portal.git
cd tech-job-portal
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:
- Database credentials (MySQL)
- RapidAPI key
- Flask secret key

4. **Set up the database**

Run the SQL setup script in MySQL:
```bash
mysql -u root -p < database_setup.sql
```

5. **Run the application**
```bash
python app.py
```

6. **Open in browser**
```
http://127.0.0.1:5000
```

## 📁 Project Structure
```
tech-job-portal/
├── app.py              # Main Flask application
├── sc.py               # Job scraping module
├── templates/          # HTML templates
├── static/            # CSS, JavaScript, images
├── .env.example       # Environment variables template
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## 🔒 Security

This project uses environment variables to protect sensitive data. Never commit your `.env` file to version control.

## 📸 Screenshots

<img width="960" height="481" alt="Screenshot 2025-10-21 173254" src="https://github.com/user-attachments/assets/645a0c52-82c3-4b8b-9b86-6e988b84f167" />

## 🚧 Future Enhancements

- [ ] Email notifications for job alerts
- [ ] Advanced filters (salary, company, date)
- [ ] Job application tracking
- [ ] Analytics dashboard

## 👨‍💻 Author

**Rahul**
- GitHub: [bankaisenpai](https://github.com/bankaisenpai)
- LinkedIn: [Rahul U](https://linkedin.com/in/rahul-u-50665937a)

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
