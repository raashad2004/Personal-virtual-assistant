# Python Voice Assistant

A sophisticated voice assistant built in Python that can perform a wide range of tasks through voice commands, including web searches, playing music, setting reminders, taking notes, controlling system functions, and more.

## Features

- **Voice Recognition**: Understand and respond to voice commands
- **Text-to-Speech**: Provide audible responses
- **GUI Interface**: Clean interface with conversation history
- **Online Operations**:
  - Web searches (Google, Wikipedia)
  - Weather information
  - News headlines
  - Trending movies
  - Email and WhatsApp messaging
- **System Operations**:
  - Open applications (Notepad, Calculator, Discord, etc.)
  - System information and battery status
  - Screenshot capture
  - System control (lock, shutdown, restart)
- **Task Management**:
  - To-do list management
  - Reminders
  - Notes
- **Entertainment**:
  - Music playback
  - Jokes, quotes, and riddles
  - Games like Rock-Paper-Scissors
- **Language Tools**:
  - Text translation
  - Language detection
  - Text-to-speech in multiple languages

## Python Compatibility

This application supports Python 3.8 and higher, with special handling for Python 3.12+:

- **Python 3.8 - 3.11**: Fully compatible with all features
- **Python 3.12+**: Compatible with additional patches and alternative dependencies

The launcher script automatically applies necessary patches for newer Python versions.

## Project Structure

```
Python-Voice-Assistant/
│
├── main.py                  # Main application entry point with core functionality
├── run.py                   # Launcher script with dependency checks
├── test.py                  # Diagnostic script for troubleshooting
├── setup.py                 # Script for creating executable
├── requirements.txt         # Dependencies list
├── .env                     # Environment variables (API keys)
│
├── Functions/               # Modular functionality
│   ├── __init__.py          # Package initialization
│   ├── init.py              # Application launching functions
│   ├── online_ops.py        # Web and online API functions
│   ├── task_manager.py      # To-do, reminder and note management
│   ├── system_utils.py      # System information and control
│   ├── entertainment.py     # Music, games, and fun content
│   └── language_tools.py    # Translation and language services
│
├── assets/                  # Application resources
│   └── icon.ico             # Application icon
│
├── data/                    # Data storage
│   ├── todos.json           # To-do list data
│   ├── notes.json           # Notes data
│   └── reminders.json       # Reminders data
│
├── audio/                   # Audio file storage
├── music/                   # Music files for playback
└── screenshots/             # Saved screenshots
```

## Technologies Used

- **Core Python Libraries**:
  - `speech_recognition` - Voice recognition
  - `pyttsx3` - Text-to-speech engine
  - `tkinter` - GUI framework
  - `pygame` - Audio playback

- **API Integrations**:
  - OpenWeatherMap - Weather information
  - NewsAPI - News headlines
  - TMDB - Movie information
  - Google APIs - Search and translation

- **System Operation**:
  - `psutil` - System information
  - `pyautogui` - Screenshots and automation
  - `platform` - OS detection

- **Package Management**:
  - `python-decouple`/`python-dotenv` - Environment configuration
  - `PyInstaller` - Executable creation

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/raashad2004/Personal-virtual-assistant
   cd python-voice-assistant
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

   **For Python 3.12+ users**:
   The requirements file includes version-specific dependencies based on your Python version. The setup will automatically select the right versions for you.

3. Create a `.env` file in the root directory with your API keys:
   ```
   OPENWEATHER_API_KEY=your_openweather_api_key
   NEWS_API_KEY=your_newsapi_key
   TMDB_API_KEY=your_tmdb_api_key
   EMAIL=your_email@gmail.com
   EMAIL_PASSWORD=your_email_password_or_app_password
   USER=YourName
   BOTNAME=Assistant
   ```

## Usage

### Running the Assistant

1. Use the diagnostic tool to check for issues:
   ```
   python test.py
   ```

2. Run with the launcher script (recommended):
   ```
   python run.py
   ```

3. Or run the main application directly:
   ```
   python main.py
   ```

### Voice Commands

Here are some example commands:
- "Hello" - Greet the assistant
- "What time is it?" - Get current time
- "Open notepad" - Launch Notepad
- "Search Google for Python tutorials" - Perform a Google search
- "Play music" - Play music from the music folder
- "Set a reminder" - Create a reminder
- "Add a task" - Add an item to your to-do list
- "Take a screenshot" - Capture a screenshot
- "What's the weather like?" - Get weather information
- "Tell me a joke" - Hear a joke

### Building an Executable

To create a Windows executable:
```
python setup.py
```
This will create a standalone executable in the `dist` folder.

## Troubleshooting

If you encounter issues:

1. **Import Errors**: Make sure all dependencies are installed
   ```
   pip install -r requirements.txt
   ```

2. **Python 3.12+ Specific Issues**:
   - If you see errors about `pkgutil.ImpImporter`, the application will automatically try to patch this but you may need to downgrade certain packages.
   - For `pywhatkit` errors, the application will use `pywhatkit-fork` on Python 3.12+
   - If you encounter `setuptools` related errors, try:
     ```
     pip install --upgrade setuptools>=68.0.0
     ```

3. **Path Issues**: Ensure that the directory structure is maintained as described above

4. **Microphone Not Working**:
   - Check if your microphone is properly connected
   - Make sure it's set as the default recording device
   - Verify permissions for microphone access

5. **API Errors**:
   - Verify your API keys in the `.env` file
   - Check if you've reached any API limits

6. **Run the diagnostic tool**:
   ```
   python test.py
   ```

## Development

### Adding New Features

1. Create appropriate module in the `Functions` directory
2. Add fallbacks for graceful degradation
3. Import in `Functions/__init__.py`
4. Implement in `main.py`'s `handle_command` function

### Coding Conventions

- Use PEP 8 style guidelines
- Implement proper error handling
- Include docstrings for functions
- Provide fallbacks for missing dependencies

## License

MIT License - See LICENSE file for details.

## Acknowledgements

- This project uses various open-source libraries and APIs
- Inspired by virtual assistants like Siri, Google Assistant, and Alexa

## Logging System

The application includes a comprehensive logging system that organizes logs by component:

- `logs/assistant_*.log`: Main application logs with date-based filenames
- `logs/launcher_*.log`: Launcher script logs
- `logs/modules_*.log`: Function module logs
- `logs/debug_*.log`: Detailed debugging information
- `logs/test_*.log`: Test script logs

### Log Management Features

- **Automatic Log Rotation**: Logs are automatically rotated at midnight
- **Retention Policies**: 
  - Assistant logs: 30 days
  - Debug logs: 7 days
  - Module logs: 14 days 
  - Test logs: 7 days
- **Auto-Cleanup**: The system removes logs older than their retention period
- **Stray Log Detection**: Any log files incorrectly created in the root directory are automatically detected and moved to the logs folder
- **Centralized Storage**: All logs are consolidated in the `logs/` directory for easy access and management

Logs include timestamps, component names, log levels, and detailed file and line tracking for easier debugging. The application also creates different log levels (INFO, DEBUG, WARNING, ERROR) to help with troubleshooting.

## Running Tests

To test if your system has all the required dependencies and components:
```
python test.py
```

This will check:
1. Required Python modules
2. Directory structure
3. Audio components
4. Network connectivity

## Customization

You can customize the assistant by:

1. Editing the `.env` file to set API keys and preferences
2. Adding custom commands in the appropriate modules
3. Modifying the GUI appearance in `gui.py`

## Troubleshooting

If you encounter issues:

1. Check the logs in the `logs/` directory for error messages
2. Run `python test.py` to verify dependencies
3. Ensure your microphone is properly configured
4. Verify you have the required Python version

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python and various open-source libraries
- Icon assets from [source] 