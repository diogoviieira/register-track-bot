# Raspberry Pi Deployment Guide

## Prerequisites
- Raspberry Pi with Raspberry Pi OS installed
- Internet connection
- SSH access to your Raspberry Pi
- Telegram Bot Token from @BotFather

## Step 1: Initial Setup

SSH into your Raspberry Pi:
```bash
ssh pi@your-pi-ip-address
```

Update system packages:
```bash
sudo apt update
sudo apt upgrade -y
```

Install Python 3 and pip (if not already installed):
```bash
sudo apt install python3 python3-pip git -y
```

## Step 2: Clone and Setup Bot

Navigate to home directory and clone the repository:
```bash
cd ~
git clone https://github.com/diogoviieira/register-track-bot.git
cd register-track-bot
```

Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

The project structure:
```
register-track-bot/
├── src/bot.py              # Main bot code
├── utils/                  # Database management tools
├── data/                   # Database storage (auto-created)
├── config/                 # Configuration files
├── run_bot.py              # Bot launcher
└── requirements.txt
```

## Step 3: Configure Bot Token

Set your Telegram bot token as an environment variable:
```bash
# Temporary (for testing)
export TELEGRAM_BOT_TOKEN="your_bot_token_here"

# Or edit the service file (for permanent setup - see Step 4)
```

## Step 4: Test the Bot

Test run the bot to make sure everything works:
```bash
python3 run_bot.py
```

If you see "Bot is running... Press Ctrl+C to stop.", the bot is working correctly. Test it in Telegram, then press Ctrl+C to stop.

## Step 5: Setup Systemd Service (24/7 Operation)

Edit the service file to add your bot token:
```bash
nano config/register-bot.service
```

Replace `your_token_here` with your actual Telegram bot token, then save and exit (Ctrl+X, Y, Enter).

Copy service file to systemd directory:
```bash
sudo cp config/register-bot.service /etc/systemd/system/
```

Reload systemd to recognize the new service:
```bash
sudo systemctl daemon-reload
```

Enable the service to start on boot:
```bash
sudo systemctl enable register-bot.service
```

Start the service:
```bash
sudo systemctl start register-bot.service
```

## Step 6: Verify Service Status

Check if the service is running:
```bash
sudo systemctl status register-bot.service
```

You should see "active (running)" in green.

View live logs:
```bash
sudo journalctl -u register-bot.service -f
```

Press Ctrl+C to exit log view.

## Managing the Bot Service

### Start the bot:
```bash
sudo systemctl start register-bot.service
```

### Stop the bot:
```bash
sudo systemctl stop register-bot.service
```

### Restart the bot:
```bash
sudo systemctl restart register-bot.service
```

### View logs:
```bash
# Last 50 lines
sudo journalctl -u register-bot.service -n 50

# Follow live logs
sudo journalctl -u register-bot.service -f

# Logs from today
sudo journalctl -u register-bot.service --since today
```

### Disable auto-start on boot:
```bash
sudo systemctl disable register-bot.service
```

## Database Management

The bot uses SQLite database stored in `data/finance_tracker.db`.

### View database with utilities:
```bash
# Interactive browser
python3 utils/db_browser.py

# Quick view
python3 utils/view_db.py

# Cleanup utility
python3 utils/cleanup_db.py
```

### Backup database:
```bash
cp ~/register-track-bot/data/finance_tracker.db ~/finance_tracker_backup_$(date +%Y%m%d).db
```

### View database with SQLite (optional):
```bash
sudo apt install sqlite3 -y
sqlite3 ~/register-track-bot/data/finance_tracker.db
```

In SQLite console:
```sql
-- View expenses
SELECT * FROM expenses ORDER BY date DESC LIMIT 10;

-- View incomes  
SELECT * FROM incomes ORDER BY date DESC LIMIT 10;

-- Exit
.quit
```

## Updating the Bot

When you make changes to the code:

1. Stop the service:
```bash
sudo systemctl stop register-bot.service
```

2. Pull latest changes:
```bash
cd ~/register-track-bot
git pull
```

3. Restart the service:
```bash
sudo systemctl start register-bot.service
```

## Troubleshooting

### Bot not responding?
1. Check service status: `sudo systemctl status register-bot.service`
2. Check logs: `sudo journalctl -u register-bot.service -n 100`
3. Verify token is correct in service file
4. Ensure internet connection is working

### Database errors?
1. Check file permissions: `ls -l ~/register-track-bot/data/finance_tracker.db`
2. Ensure the bot has write permissions to the directory
3. Try restarting the service

### Service won't start?
1. Check syntax of service file: `sudo systemd-analyze verify register-bot.service`
2. Check Python path: `which python3`
3. Ensure all dependencies are installed: `pip3 list`

## Security Recommendations

1. **Never commit your bot token to git**
   - Add `.env` to `.gitignore` if using environment files
   - Use the systemd service Environment variable

2. **Backup your database regularly**
   ```bash
   # Add to crontab for daily backups
   crontab -e
   # Add this line:
   0 2 * * * cp ~/register-track-bot/data/finance_tracker.db ~/backups/finance_$(date +\%Y\%m\%d).db
   ```

3. **Keep your system updated**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Monitor disk space**
   ```bash
   df -h
   ```

## Performance Notes

- SQLite is lightweight and perfect for Raspberry Pi
- Database file will grow slowly (typically <100MB per year of data)
- No external database server needed
- Bot uses minimal resources (~20-30MB RAM)
- Can handle multiple concurrent users

## Next Steps

- Set up automatic database backups
- Configure log rotation if needed
- Monitor bot performance with `htop`
- Consider setting up a reverse proxy for web interface (future feature)

---

**Your bot is now running 24/7 on your Raspberry Pi!** 🎉

Test it in Telegram with `/start` or `/help`
