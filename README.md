# Cubs Recap Bot

A Python script that checks if the Chicago Cubs played yesterday, and if so, sends a text message with a link to the condensed game recap on MLB.com.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables for Twilio:
   ```
   export TWILIO_ACCOUNT_SID="your_account_sid"
   export TWILIO_AUTH_TOKEN="your_auth_token"
   export TWILIO_FROM_NUMBER="your_twilio_phone_number"
   export TWILIO_TO_NUMBER="your_phone_number"
   ```

## Usage

Run the script manually:
```
python cubs_recap_bot.py
```

For automated daily updates, consider setting up a cron job.

## Features

- Checks if the Cubs played yesterday using the MLB Stats API
- Determines the game result (win/loss)
- Constructs a link to the condensed game recap video
- Sends a text message with the result and recap link using Twilio