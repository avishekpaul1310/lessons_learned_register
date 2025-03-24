# Lessons Learned System

A comprehensive web application for capturing, managing, and sharing project lessons learned within an organization.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![Django Version](https://img.shields.io/badge/django-4.2.7-brightgreen)

## 📋 Overview

The Lessons Learned System enables organizations to:

- Document valuable insights, experiences, and knowledge from projects
- Categorize and search for lessons across multiple dimensions
- Track implementation status of recommendations
- Generate reports for future project planning
- Foster a culture of continuous improvement

## ✨ Features

- **User Management**
  - Customizable user profiles with role-based access control
  - Team member assignment to projects
  
- **Project Management**
  - Create and manage projects with timeline tracking
  - Team composition and role assignment
  - Project-level metrics and dashboards

- **Lessons Learned Tracking**
  - Multi-dimensional categorization (technical, process, communication)
  - Impact assessment (high, medium, low)
  - Implementation status workflow
  - File attachments and commenting system
  
- **Knowledge Sharing**
  - Advanced search and filtering capabilities
  - User tagging and notifications
  - Export functionality (CSV/PDF)
  - "Star" important lessons for quick reference

- **Visual Analytics**
  - Dashboard with key metrics
  - Distribution charts by category, status, and impact
  - Project-specific statistics

## 🔧 Technology Stack

- **Backend**: Django 4.2.7, Python 3.8+
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite (development) / PostgreSQL (production)
- **Libraries**:
  - django-crispy-forms for enhanced forms
  - django-filter for advanced filtering
  - django-summernote for rich text editing
  - Pillow for image processing

## 📦 Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/lessons-learned-system.git
   cd lessons-learned-system
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   - Copy `.env.example` to `.env`
   - Update variables as needed

5. Run migrations
   ```bash
   python manage.py migrate
   ```

6. Create default media directories
   ```bash
   python create_default_jpg.py
   ```

7. Create a superuser
   ```bash
   python manage.py createsuperuser
   ```

8. Start the development server
   ```bash
   python manage.py runserver
   ```

9. Access the application at http://localhost:8000

## 🚀 Getting Started

After installation, you can:

1. Log in with your superuser account
2. Create your first project
3. Add team members to the project
4. Start capturing lessons learned

For demo data, run:
```bash
python create_test_data.py
```

## 🧪 Testing

Run the test suite:
```bash
python run_tests.py
```

Or run individual test modules:
```bash
python manage.py test accounts
python manage.py test projects
python manage.py test lessons
python manage.py test integration_tests
```

## 📚 Documentation

Additional documentation can be found in the [docs](./docs) directory.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📊 Project Structure

```
lessons-learned-system/
├── accounts/               # User authentication and profiles
├── lessons/                # Core lessons learned functionality
├── projects/               # Project management
├── static/                 # Static assets (CSS, JS)
├── templates/              # HTML templates
├── lessons_learned/        # Main project settings
├── docs/                   # Documentation
└── media/                  # User-uploaded files
```

## 📷 Screenshots

Screenshots will be added soon.

## 🌟 Roadmap

- Mobile application support
- Advanced analytics dashboard
- API access for integration with other tools
- Localization support

## 📞 Contact

For questions or feedback, please open an issue on GitHub.
