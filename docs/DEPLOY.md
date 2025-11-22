# 🚀 Deployment Guide

Complete guide for deploying the Telegram Finance Tracker Bot on Raspberry Pi for 24/7 operation.

## Prerequisites

- Raspberry Pi (any model with network connectivity)
- Raspberry Pi OS (formerly Raspbian)
- SSH access or direct terminal access
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- Basic command line knowledge

## Quick Deploy

```bash
# 1. Clone repository
cd ~
git clone https://github.com/diogoviieira/register-track-bot.git
cd register-track-bot

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Configure service
sudo nano config/register-bot.service
# Replace 'your_token_here' with your actual token

# 4. Install and start service
sudo cp config/register-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable register-bot.service
sudo systemctl start register-bot.service

# 5. Verify it's running
sudo systemctl status register-bot.service
```

Done! Your bot is now running 24/7.

## Detailed Setup

### Step 1: System Preparation

Update your system:
```bash
sudo apt update && sudo apt upgrade -y
```

Install required packages:
```bash
sudo apt install python3 python3-pip git -y
```

### Step 2: Get the Code

Clone the repository:
```bash
cd ~
git clone https://github.com/diogoviieira/register-track-bot.git
cd register-track-bot
```

Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

### Step 3: Get Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the prompts to create your bot
4. Copy the API token provided

### Step 4: Configure the Service

Edit the service file:
```bash
nano config/register-bot.service
```

Update the `Environment` line with your token:
```ini
Environment="TELEGRAM_BOT_TOKEN=your_actual_token_here"
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

### Step 5: Test Before Installing

Run the bot manually to verify everything works:
```bash
export TELEGRAM_BOT_TOKEN="your_actual_token_here"
python3 run_bot.py
```

You should see:
```
Database initialized: /home/pi/register-track-bot/data/finance_tracker.db
Bot is running... Press Ctrl+C to stop.
```

Test in Telegram by sending `/start` to your bot. If it responds, press `Ctrl+C` to stop.

### Step 6: Install as System Service

Copy service file:
```bash
sudo cp config/register-bot.service /etc/systemd/system/
```

Reload systemd:
```bash
sudo systemctl daemon-reload
```

Enable auto-start on boot:
```bash
sudo systemctl enable register-bot.service
```

Start the service:
```bash
sudo systemctl start register-bot.service
```

### Step 7: Verify Installation

Check status:
```bash
sudo systemctl status register-bot.service
```

You should see `active (running)` in green.

View logs:
```bash
sudo journalctl -u register-bot.service -f
```

Press `Ctrl+C` to exit log view.

## Service Management

### Common Commands

```bash
# Start the bot
sudo systemctl start register-bot.service

# Stop the bot
sudo systemctl stop register-bot.service

# Restart the bot
sudo systemctl restart register-bot.service

# Check status
sudo systemctl status register-bot.service

# View logs (live)
sudo journalctl -u register-bot.service -f

# View last 50 log entries
sudo journalctl -u register-bot.service -n 50

# Disable auto-start
sudo systemctl disable register-bot.service
```

## Database Management

### Location

Database file: `~/register-track-bot/data/finance_tracker.db`

### Viewing Data

Use the included utilities:
```bash
cd ~/register-track-bot

# Interactive browser (most features)
python3 utils/db_browser.py

# Quick overview
python3 utils/view_db.py

# Cleanup tool
python3 utils/cleanup_db.py
```

### Direct SQL Access

Install SQLite (if needed):
```bash
sudo apt install sqlite3 -y
```

Open database:
```bash
sqlite3 ~/register-track-bot/data/finance_tracker.db
```

Example queries:
```sql
-- View recent expenses
SELECT * FROM expenses ORDER BY date DESC LIMIT 10;

-- Monthly totals
SELECT strftime('%Y-%m', date) as month, 
       SUM(amount) as total 
FROM expenses 
GROUP BY month 
ORDER BY month DESC;

-- Exit SQLite
.quit
```

### Backup Strategy

Manual backup:
```bash
cp ~/register-track-bot/data/finance_tracker.db \
   ~/backups/finance_$(date +%Y%m%d).db
```

Automated daily backups:
```bash
# Create backup directory
mkdir -p ~/backups

# Edit crontab
crontab -e

# Add this line for daily 2 AM backups:
0 2 * * * cp ~/register-track-bot/data/finance_tracker.db ~/backups/finance_$(date +\%Y\%m\%d).db
```

Keep last 30 days of backups:
```bash
# Add to crontab
0 3 * * * find ~/backups -name "finance_*.db" -mtime +30 -delete
```

## Updating the Bot

When updates are available:

```bash
# Stop the service
sudo systemctl stop register-bot.service

# Backup current database
cp ~/register-track-bot/data/finance_tracker.db ~/finance_backup.db

# Pull updates
cd ~/register-track-bot
git pull

# Install any new dependencies
pip3 install -r requirements.txt

# Restart service
sudo systemctl start register-bot.service

# Check status
sudo systemctl status register-bot.service
```

## Troubleshooting

### Bot Not Responding

1. Check if service is running:
   ```bash
   sudo systemctl status register-bot.service
   ```

2. View recent logs:
   ```bash
   sudo journalctl -u register-bot.service -n 100
   ```

3. Verify token is correct in service file:
   ```bash
   sudo nano /etc/systemd/system/register-bot.service
   ```

4. Test internet connection:
   ```bash
   ping -c 4 api.telegram.org
   ```

### Service Won't Start

Check for errors:
```bash
sudo journalctl -u register-bot.service -xe
```

Verify Python path:
```bash
which python3
```

Check dependencies:
```bash
pip3 list | grep telegram
```

### Database Issues

Check file permissions:
```bash
ls -la ~/register-track-bot/data/
```

Ensure write access:
```bash
touch ~/register-track-bot/data/test.txt && rm ~/register-track-bot/data/test.txt
```

Check disk space:
```bash
df -h
```

## Performance & Monitoring

Expected performance on Raspberry Pi 4:

| Metric | Value |
|--------|-------|
| RAM Usage | ~20-30 MB |
| CPU Usage | <1% (idle) |
| Disk Space | ~50 MB (app) + database growth |
| Network | Minimal (polling API) |

Database growth rate: ~1-5 MB per year per user

## Security Best Practices

1. **Never commit tokens to git** - Keep them in the service file only
2. **Regular updates** - `sudo apt update && sudo apt upgrade -y`
3. **Monitor logs regularly** - `sudo journalctl -u register-bot.service --since today`
4. **Backup database** - Set up automated daily backups

## Support

Need help? 

- Check the [README](../README.md)
- Review logs: `sudo journalctl -u register-bot.service -n 100`
- Open an issue: [GitHub Issues](https://github.com/diogoviieira/register-track-bot/issues)

---

**Your bot is now deployed! 🎉** Test it by sending `/start` to your bot in Telegram.
