#!/usr/bin/env python3
import requests
import datetime
import os
import time
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

def get_yesterday_date():
    """Get yesterday's date in YYYY-MM-DD format."""
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def get_cubs_game(date_str):
    """Check if the Cubs played on the given date and return game data if so."""
    # MLB Stats API endpoint
    url = f"https://statsapi.mlb.com/api/v1/schedule"
    params = {
        "sportId": 1,  # MLB
        "date": date_str,
        "teamId": 112,  # Cubs team ID
        "hydrate": "game,team"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error fetching game data: {response.status_code}")
        return None
    
    data = response.json()
    if not data["dates"]:
        print(f"No games found for date: {date_str}")
        return None
    
    # Check if Cubs played
    for date in data["dates"]:
        for game in date["games"]:
            teams = game["teams"]
            if (teams["away"]["team"]["id"] == 112 or teams["home"]["team"]["id"] == 112) and game["status"]["statusCode"] == "F":
                return game
    
    return None

def get_game_recap_url(game_data):
    """Construct the game recap URL based on game data."""
    if not game_data:
        return None
    
    # Extract game date
    game_date_str = game_data["officialDate"]
    game_date = datetime.datetime.strptime(game_date_str, "%Y-%m-%d")
    date_part = game_date.strftime("%Y/%m/%d")
    
    # Get team names - only use team name without city
    away_team_full = game_data["teams"]["away"]["team"]["name"].lower()
    home_team_full = game_data["teams"]["home"]["team"]["name"].lower()
    
    # Extract just the team nickname
    away_team = away_team_full.split()[-1]
    home_team = home_team_full.split()[-1]
    
    # Game ID
    game_id = game_data["gamePk"]
    
    # Construct URL
    recap_url = f"https://www.mlb.com/gameday/{away_team}-vs-{home_team}/{date_part}/{game_id}/final/video"
    
    return recap_url

def send_email_sms(message):
    """Send text message using email-to-SMS gateway."""
    try:
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_EMAIL_PASSWORD")
        recipient_number = os.getenv("RECIPIENT_PHONE_NUMBER")
        carrier_gateway = os.getenv("CARRIER_GATEWAY")
        
        print(f"Using sender: {sender_email}")
        print(f"Sending to: {recipient_number}@{carrier_gateway}")
        
        # Recipient's email-to-SMS address
        recipient = f"{recipient_number}@{carrier_gateway}"
        
        # Set up the email - using simple MIMEText instead of MIMEMultipart
        # Some carriers have message size limits for SMS gateway
        msg = MIMEText(message)
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = ""  # Empty subject for SMS
        
        # Connect to Gmail SMTP server and send email
        print("Connecting to SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("Logging in...")
        server.login(sender_email, sender_password)
        text = msg.as_string()
        print("Sending message...")
        server.sendmail(sender_email, recipient, text)
        server.quit()
        
        # Add delay between messages to avoid carrier rate limiting
        time.sleep(2)
        
        print(f"Text message sent successfully via email gateway")
        return True
    except Exception as e:
        print(f"Error sending text message via email gateway: {e}")
        return False

def main():
    # Get yesterday's date
    yesterday = get_yesterday_date()
    print(f"Checking for Cubs game on {yesterday}")
    
    # Check if Cubs played yesterday
    game_data = get_cubs_game(yesterday)
    
    if game_data:
        # Get teams
        away_team = game_data["teams"]["away"]["team"]["name"]
        home_team = game_data["teams"]["home"]["team"]["name"]
        
        # Get scores
        away_score = game_data["teams"]["away"]["score"]
        home_score = game_data["teams"]["home"]["score"]
        
        # Determine if Cubs won or lost
        cubs_team = "away" if game_data["teams"]["away"]["team"]["id"] == 112 else "home"
        opponent = home_team if cubs_team == "away" else away_team
        cubs_score = away_score if cubs_team == "away" else home_score
        opponent_score = home_score if cubs_team == "away" else away_score
        result = "won" if ((cubs_team == "away" and away_score > home_score) or 
                           (cubs_team == "home" and home_score > away_score)) else "lost"
        
        # Get recap URL
        recap_url = get_game_recap_url(game_data)
        
        if recap_url:
            # Send just the URL by itself
            send_email_sms(recap_url)
        else:
            print("Couldn't generate recap URL")
    else:
        print("No Cubs game found for yesterday")

if __name__ == "__main__":
    main()