# SoulNotes 📝✨

**Transform your thoughts into meaningful stories with AI-powered journaling**

SoulNotes is a personal digital journaling application that helps users capture thoughts, organize them by mood, and transform everyday moments into inspiring stories, poems, and reflections using AI technology.

## 🌟 Features

### Core Functionality
- **Personal Journaling**: Write and save personal notes anytime, anywhere
- **Mood Organization**: Sort notes by emotions (Happy, Motivated, Nostalgic, Reflective, etc.)
- **AI Story Generation**: Transform your notes into inspiring stories, poems, letters, and more
- **Voice Agent**: Listen to your AI-crafted stories with text-to-speech functionality
- **Secure & Private**: All notes are personal, secure, and easy to manage

### AI Content Generation
- **Multiple Output Formats**: 
  - Paragraph
  - Story
  - Poem
  - Letter
  - Journal Entry
  - Summary
- **Mood-Based Generation**: Generate content based on selected emotional themes
- **Custom Instructions**: Add specific details or themes for personalized content

### Voice Features
- **Text-to-Speech**: Listen to your generated stories
- **Voice Customization**: Select different voices, adjust speed and pitch
- **Playback Controls**: Play, pause, resume, and stop functionality

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Django 4.0+
- Modern web browser with JavaScript enabled

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Note_taking_project.git
   cd Note_taking_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000/`

## 📂 Project Structure

```
Note_taking_project/
├── application/           # Main Django app
│   ├── __pycache__/
│   ├── migrations/
│   ├── templates/application/
│   │   ├── about.html         # About page
│   │   ├── add_note.html      # Note creation
│   │   ├── ai_agent.html      # AI story generation
│   │   ├── base.html          # Base template
│   │   └── home.html          # Landing page
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py              # Application forms
│   ├── models.py             # Note models
│   ├── tests.py
│   ├── urls.py               # Application URLs
│   └── views.py              # Main application views
├── authentication/           # Authentication app
│   ├── __pycache__/
│   ├── migrations/
│   ├── templates/authentication/
│   │   ├── home.html             # Login page
│   │   ├── new_try.html          # Additional auth page
│   │   ├── new1_try.html         # Additional auth page
│   │   ├── privacy_policy.html   # Privacy policy
│   │   └── terms_of_service.html # Terms of service
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── decorators.py         # Custom decorators
│   ├── forms.py              # Authentication forms
│   ├── models.py             # User models
│   ├── tests.py
│   ├── urls.py               # Authentication URLs
│   └── views.py              # Authentication views
├── Note_taking_project/      # Django project settings
│   ├── __pycache__/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL configuration
│   └── wsgi.py
├── notes/                    # Notes management app
├── venv/                     # Virtual environment
├── db.sqlite3               # SQLite database
├── manage.py                # Django management script
└── README.md                # Project documentation
```

## 💻 Usage

### 1. User Registration & Login
- **Sign Up**: Create a new account with name, email, and password
- **Login**: Access your account with credentials
- **Session Management**: Optional "Remember Me" for extended sessions

### 2. Note Management
- **Create Notes**: Add personal notes with titles and descriptions
- **Organize by Mood**: Categorize notes based on emotional themes
- **View & Edit**: Manage your personal note collection

### 3. AI Story Generation
1. **Select Mood**: Choose from 8 emotional themes:
   - ✨ General
   - 😊 Happy
   - 🌅 Hopeful
   - 🤔 Reflective
   - 💪 Motivation
   - 🧘 Calm
   - 🎭 Dramatic
   - 😂 Funny

2. **Choose Notes**: Select one or more notes to include

3. **Customize Output**: 
   - Add additional details or instructions
   - Choose output format (story, poem, letter, etc.)

4. **Generate & Listen**: Create AI content and use voice features

## 🎨 UI/UX Features

### Design Elements
- **Modern Gradient Design**: Purple-blue gradient theme
- **Glassmorphism Effects**: Transparent cards with blur effects
- **Responsive Layout**: Mobile-friendly design
- **Smooth Animations**: Hover effects and transitions
- **Intuitive Navigation**: Easy-to-use interface

### Interactive Components
- **Step-by-step Form**: Guided AI generation process
- **Real-time Validation**: Form validation with user feedback
- **Dynamic Content**: JavaScript-powered interactions
- **Audio Controls**: Comprehensive text-to-speech interface

## 🔧 Technical Details

### Backend (Django)
- **Authentication System**: Custom user model with session management
- **Password Security**: Hashed password storage
- **Form Handling**: Django forms with validation
- **Session Management**: Configurable session expiry

### Frontend
- **Vanilla JavaScript**: No external JS frameworks
- **CSS3**: Modern styling with gradients and animations
- **HTML5**: Semantic markup structure
- **Web Speech API**: Browser-native text-to-speech

### Security Features
- **CSRF Protection**: Django CSRF tokens
- **Password Hashing**: Secure password storage
- **Session Security**: Configurable session timeouts
- **Input Validation**: Server-side form validation

## 🛠️ Development

### Key Models
```python
# authentication/models.py
class Login_model(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Hashed
    created_at = models.DateTimeField(auto_now_add=True)

# application/models.py (assumed structure)
class Note(models.Model):
    user = models.ForeignKey(Login_model, on_delete=models.CASCADE)
    note_title = models.CharField(max_length=200)
    note_description = models.TextField()
    mood = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
```

### Main Views
**Authentication App:**
- `home()`: Landing page with login form
- `Login_views()`: Handle user authentication
- `SignUp_views()`: User registration process
- `Logout_views()`: Session termination
- `terms_of_service()`: Terms of service page
- `privacy_policy()`: Privacy policy page

**Application App:**
- `add_note()`: Note creation and management
- `ai_agent()`: AI story generation interface
- `about()`: About page with feature overview

### URL Patterns
```python
# Note_taking_project/urls.py (main project URLs)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('app/', include('application.urls')),
]

# authentication/urls.py
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.Login_views, name='login_page'),
    path('signup/', views.SignUp_views, name='signup_page'),
    path('logout/', views.Logout_views, name='logout_page'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
]

# application/urls.py
urlpatterns = [
    path('about/', views.about, name='about'),
    path('add-note/', views.add_note, name='add_note'),
    path('ai-agent/', views.ai_agent, name='ai_agent'),
]
```

## 🎯 Future Enhancements

### Planned Features
- **Note Categories**: Advanced note organization
- **Export Options**: PDF/Word export functionality
- **Social Sharing**: Share generated stories (optional)
- **Mobile App**: Native mobile applications
- **Advanced AI**: More sophisticated content generation
- **Themes**: Multiple UI themes and customization

### Technical Improvements
- **API Integration**: RESTful API for mobile apps
- **Database Optimization**: Query optimization and caching
- **Cloud Storage**: File upload and storage capabilities
- **Analytics**: User engagement tracking
- **Performance**: Load time optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow Django best practices
- Maintain responsive design principles
- Add comments for complex JavaScript functions
- Test across different browsers
- Ensure accessibility standards

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support, email support@soulnotes.com or create an issue in the GitHub repository.

## 🙏 Acknowledgments

- Django community for the excellent web framework
- Web Speech API for text-to-speech functionality
- Modern CSS techniques for beautiful UI design
- Open source community for inspiration and tools

---

**SoulNotes** - *Capture. Reflect. Create. Be inspired.*

Transform your everyday thoughts into extraordinary stories with the power of AI. Start your journey today! ✨
