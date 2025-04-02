"""
Online Operations Module

This module provides functions for online operations including:
- Getting IP address
- Getting weather information
- Fetching news, advice, jokes, etc.
- Web search (Google, YouTube, Wikipedia)
- Email and WhatsApp messaging
"""

import os
import re
import sys
import json
import logging
import requests
import webbrowser
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import wikipedia
from newsapi import NewsApiClient
from tmdbv3api import TMDb, Movie
from pyowm import OWM
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger("online_ops")

# Load environment variables
load_dotenv()

# API Keys from .env file
OPENWEATHER_APP_ID = os.getenv("OPENWEATHER_APP_ID", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
EMAIL = os.getenv("EMAIL", "")
PASSWORD = os.getenv("PASSWORD", "")

# Initialize API clients if keys are available
try:
    if NEWS_API_KEY:
        news_api = NewsApiClient(api_key=NEWS_API_KEY)
    else:
        logger.warning("NEWS_API_KEY not set, News API features will not work")
        news_api = None
except Exception as e:
    logger.error(f"Error initializing News API: {e}")
    news_api = None

try:
    if OPENWEATHER_APP_ID:
        owm = OWM(OPENWEATHER_APP_ID)
        mgr = owm.weather_manager()
    else:
        logger.warning("OPENWEATHER_APP_ID not set, Weather API features will not work")
        owm = None
        mgr = None
except Exception as e:
    logger.error(f"Error initializing OpenWeatherMap: {e}")
    owm = None
    mgr = None

try:
    if TMDB_API_KEY:
        tmdb = TMDb()
        tmdb.api_key = TMDB_API_KEY
        movie = Movie()
    else:
        logger.warning("TMDB_API_KEY not set, TMDB API features will not work")
        tmdb = None
        movie = None
except Exception as e:
    logger.error(f"Error initializing TMDB: {e}")
    tmdb = None
    movie = None

# Check if pywhatkit is available (not compatible with Python 3.12+)
try:
    import pywhatkit
    pywhatkit_available = True
except ImportError:
    logger.warning("pywhatkit not available, YouTube and WhatsApp features will use fallbacks")
    pywhatkit_available = False

def get_ip_address():
    """Get the public IP address of the user"""
    try:
        ip_response = requests.get("https://api.ipify.org/?format=json", timeout=5)
        ip_address = ip_response.json()["ip"]
        return ip_address
    except Exception as e:
        logger.error(f"Error getting IP address: {e}")
        return "Unable to get IP address"

def get_weather(city):
    """Get current weather information for a city"""
    try:
        if not owm or not mgr:
            return {"condition": "unavailable", "temperature": "API key not set", "feels_like": "N/A"}
        
        observation = mgr.weather_at_place(city)
        w = observation.weather
        
        # Get weather data
        condition = w.detailed_status
        temperature = w.temperature('celsius')["temp"]
        feels_like = w.temperature('celsius')["feels_like"]
        
        return {
            "condition": condition, 
            "temperature": f"{temperature:.1f}°C", 
            "feels_like": f"{feels_like:.1f}°C"
        }
    except Exception as e:
        logger.error(f"Error getting weather for {city}: {e}")
        return {"condition": "error", "temperature": "unavailable", "feels_like": "unavailable"}

def fetch_latest_news(category="general", count=5):
    """Fetch latest news headlines"""
    try:
        if not news_api:
            return ["News API key not set"]
        
        headlines = news_api.get_top_headlines(category=category, language='en', page_size=count)
        news_articles = headlines['articles']
        
        if not news_articles:
            return ["No news found"]
        
        # Return headlines
        return [article['title'] for article in news_articles]
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return [f"Error fetching news: {str(e)}"]

def fetch_trending_movies(count=5):
    """Fetch trending movies from TMDB"""
    try:
        if not tmdb or not movie:
            return ["TMDB API key not set"]
        
        trending = movie.popular()[:count]
        
        if not trending:
            return ["No trending movies found"]
        
        # Return movie titles
        return [f"{m.title} ({m.release_date[:4] if m.release_date else 'N/A'})" for m in trending]
    except Exception as e:
        logger.error(f"Error fetching trending movies: {e}")
        return [f"Error fetching movies: {str(e)}"]

def get_advice():
    """Get random advice from Advice Slip API"""
    try:
        response = requests.get("https://api.adviceslip.com/advice", timeout=5)
        advice = response.json()["slip"]["advice"]
        return advice
    except Exception as e:
        logger.error(f"Error getting advice: {e}")
        return "I don't have any advice for you right now."

def get_joke():
    """Get a random joke from JokeAPI"""
    try:
        response = requests.get("https://v2.jokeapi.dev/joke/Any?safe-mode", timeout=5)
        joke_data = response.json()
        
        if joke_data["type"] == "single":
            return joke_data["joke"]
        else:
            return f"{joke_data['setup']} ... {joke_data['delivery']}"
    except Exception as e:
        logger.error(f"Error getting joke: {e}")
        return "Why don't scientists trust atoms? Because they make up everything!"

def play_video_on_youtube(video):
    """Play a video on YouTube"""
    try:
        if pywhatkit_available:
            pywhatkit.playonyt(video)
            return f"Playing {video} on YouTube"
        else:
            # Fallback method using webbrowser
            search_query = video.replace(" ", "+")
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
            return f"Opening YouTube search for: {video}"
    except Exception as e:
        logger.error(f"Error playing YouTube video: {e}")
        return f"Error playing video: {str(e)}"

def google_search(query):
    """Search Google for a query"""
    try:
        search_query = query.replace(" ", "+")
        webbrowser.open(f"https://www.google.com/search?q={search_query}")
        return f"Searching Google for: {query}"
    except Exception as e:
        logger.error(f"Error searching Google: {e}")
        return f"Error searching Google: {str(e)}"

def search_wikipedia(topic):
    """Search Wikipedia for a topic and return a summary"""
    try:
        results = wikipedia.summary(topic, sentences=2)
        return results
    except wikipedia.exceptions.DisambiguationError as e:
        # Handle disambiguation
        return f"There are multiple results for {topic}. Please be more specific."
    except wikipedia.exceptions.PageError:
        return f"No information found for {topic} on Wikipedia."
    except Exception as e:
        logger.error(f"Error searching Wikipedia: {e}")
        return f"Error searching Wikipedia: {str(e)}"

def send_email(to, subject, content):
    """Send an email using Gmail"""
    try:
        if not EMAIL or not PASSWORD:
            logger.error("Email credentials not set in .env file")
            return False
        
        # Set up the MIME
        message = MIMEMultipart()
        message['From'] = EMAIL
        message['To'] = to
        message['Subject'] = subject
        
        # Add body to email
        message.attach(MIMEText(content, 'plain'))
        
        # Create SMTP session
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()  # Enable security
        session.login(EMAIL, PASSWORD)  # Login with email and password
        text = message.as_string()
        session.sendmail(EMAIL, to, text)
        session.quit()
        
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def send_whatsapp_msg(number, text):
    """Send a WhatsApp message"""
    try:
        if pywhatkit_available:
            # Format number if needed
            if not number.startswith('+'):
                number = '+' + number
            
            # Get current time to schedule message (1 minute from now)
            now = datetime.now()
            hour = now.hour
            minute = now.minute + 1
            if minute >= 60:
                minute = 0
                hour += 1
            if hour >= 24:
                hour = 0
            
            pywhatkit.sendwhatmsg(number, text, hour, minute, wait_time=10)
            return True
        else:
            # Fallback method for Python 3.12+ using web.whatsapp.com
            # This just opens the website, user must manually send the message
            number = number.replace('+', '')
            webbrowser.open(f"https://web.whatsapp.com/send?phone={number}&text={text}")
            logger.warning("pywhatkit not available, opened web WhatsApp instead")
            return False
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return False

# For testing
if __name__ == "__main__":
    print("IP Address:", get_ip_address())
    print("Weather in London:", get_weather("London"))
    print("Latest News:", fetch_latest_news())
    print("Trending Movies:", fetch_trending_movies())
    print("Advice:", get_advice())
    print("Joke:", get_joke())
    print("Wikipedia Search for Python:", search_wikipedia("Python programming language"))