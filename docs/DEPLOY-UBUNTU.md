# 🐧 Ubuntu Deployment Guide (HP EliteDesk / Mini PC)

Complete guide for deploying the Telegram Finance Tracker Bot on Ubuntu for **true 24/7 operation**.

## What You'll Get

After following this guide, your bot will:

- ✅ **Run 24/7 automatically** - Set it and forget it
- ✅ **Start on boot** - PC restarts? Bot starts automatically (no manual intervention needed)
- ✅ **Auto-restart on crash** - Bot crashes? Automatically restarts in 10 seconds
- ✅ **Survive power failures** - Just turn PC back on, bot starts by itself
- ✅ **Run in background** - No need to keep terminal open or stay logged in

**Perfect for always-on deployments on HP EliteDesk, Mini PCs, or servers.**

---

## Prerequisites

- Ubuntu Desktop/Server (20.04 LTS or newer)
- Internet connection
- sudo access
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

## Quick Setup

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install python3 python3-pip python3-venv git -y

# 3. Clone repository
cd ~
git clone https://github.com/diogoviieira/register-track-bot.git
cd register-track-bot

# 4. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 5. Install Python packages
pip install -r requirements.txt

# 6. Set bot token (replace with your token)
echo 'export TELEGRAM_BOT_TOKEN="8244177385:AAHKrL0Cu-_JllKZdTIqgy8PRl9JE4WN7Jw"' >> ~/.bashrc
source ~/.bashrc

# 7. Test the bot
python run_bot.py
```

Press `Ctrl+C` after verifying it works, then continue with auto-start setup below.

---

## Detailed Setup

### Step 1: Update System

```bash
# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Optional: Install useful tools
sudo apt install curl wget nano htop -y
```

### Step 2: Install Python and Git

```bash
# Install Python 3, pip, and virtual environment support
sudo apt install python3 python3-pip python3-venv -y

# Install Git
sudo apt install git -y

# Verify installations
python3 --version
# Should show: Python 3.8 or newer

git --version
# Should show: git version 2.x
```

### Step 3: Clone Repository

```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/diogoviieira/register-track-bot.git

# Enter directory
cd register-track-bot
```

### Step 4: Setup Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Your prompt should now show (.venv) at the beginning

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure Bot Token

**Get your token:**
1. Open Telegram, search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions
3. Copy the token provided

**Set the token permanently:**

```bash
# Add to .bashrc for permanent storage
echo 'export TELEGRAM_BOT_TOKEN="your_actual_token_here"' >> ~/.bashrc

# Reload .bashrc
source ~/.bashrc

# Verify it's set
echo $TELEGRAM_BOT_TOKEN
# Should show your token
```

### Step 6: Test the Bot

```bash
# Make sure you're in the project directory
cd ~/register-track-bot

# Activate virtual environment
source .venv/bin/activate

# Run the bot
python run_bot.py
```

You should see:
```
Database initialized: /home/YOUR_USER/register-track-bot/data/finance_tracker.db
Bot is running... Press Ctrl+C to stop.
```

Test it in Telegram by sending `/start` to your bot. If it responds, press `Ctrl+C` to stop.

---

## 24/7 Auto-Start with systemd

### Create systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/telegram-bot.service
```

Paste this content (replace `YOUR_USER` with your actual username):

```ini
[Unit]
Description=Telegram Finance Tracker Bot
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/home/YOUR_USER/register-track-bot
Environment="TELEGRAM_BOT_TOKEN=8244177385:AAHKrL0Cu-_JllKZdTIqgy8PRl9JE4WN7Jw"
ExecStart=/home/YOUR_USER/register-track-bot/.venv/bin/python run_bot.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=telegram-bot

[Install]
WantedBy=multi-user.target
```

**To find your username:**
```bash
whoami
```

**Save and exit nano:**
- Press `Ctrl+O` to save
- Press `Enter` to confirm
- Press `Ctrl+X` to exit

### Enable and Start Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable telegram-bot

# Start the service now
sudo systemctl start telegram-bot

# Check status
sudo systemctl status telegram-bot
```

You should see `Active: active (running)` in green.

**✅ That's it! Your bot is now configured for 24/7 operation.**

The service will:
- ✅ **Start automatically on boot** - No need to do anything after PC restart
- ✅ **Restart automatically if it crashes** - Self-healing (waits 10 seconds then restarts)
- ✅ **Run in the background** - Always active, even when you're not logged in
- ✅ **Survive reboots** - PC goes down? Just turn it on and bot starts automatically

**Test it:**
```bash
# Reboot your PC to verify auto-start
sudo reboot

# After reboot, check if bot is running
sudo systemctl status telegram-bot
# Should show "active (running)"
```

### Manage the Service

```bash
# Start the bot
sudo systemctl start telegram-bot

# Stop the bot
sudo systemctl stop telegram-bot

# Restart the bot
sudo systemctl restart telegram-bot

# View status
sudo systemctl status telegram-bot

# Disable auto-start on boot
sudo systemctl disable telegram-bot

# View real-time logs
sudo journalctl -u telegram-bot -f

# View last 50 log lines
sudo journalctl -u telegram-bot -n 50
```

---

## Alternative: Using Screen (Simpler but less robust)

If you prefer a simpler approach without systemd:

```bash
# Install screen
sudo apt install screen -y

# Create a screen session
screen -S telegrambot

# Inside the screen session:
cd ~/register-track-bot
source .venv/bin/activate
python run_bot.py

# Detach from screen: Press Ctrl+A then D

# Reattach to screen later:
screen -r telegrambot

# List all screen sessions:
screen -ls

# Kill a screen session:
screen -S telegrambot -X quit
```

---

## Database Backups

### Manual Backup

```bash
# Create backups directory
mkdir -p ~/register-track-bot/backups

# Manual backup
cp ~/register-track-bot/data/finance_tracker.db ~/register-track-bot/backups/finance_$(date +%Y%m%d).db
```

### Automatic Daily Backups

Create a backup script:

```bash
nano ~/register-track-bot/backup.sh
```

Paste this content:

```bash
#!/bin/bash

# Backup script for Telegram Finance Bot

SOURCE="$HOME/register-track-bot/data/finance_tracker.db"
BACKUP_DIR="$HOME/register-track-bot/backups"
DATE=$(date +%Y%m%d)
BACKUP_FILE="$BACKUP_DIR/finance_$DATE.db"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Copy database
cp "$SOURCE" "$BACKUP_FILE"

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "finance_*.db" -type f -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
```

Make it executable:

```bash
chmod +x ~/register-track-bot/backup.sh
```

Schedule with cron:

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 2 AM:
0 2 * * * /home/YOUR_USER/register-track-bot/backup.sh >> /home/YOUR_USER/register-track-bot/backup.log 2>&1
```

Replace `YOUR_USER` with your username.

---

## Database Management

### View Database

```bash
cd ~/register-track-bot
source .venv/bin/activate

# Quick view
python utils/view_db.py

# Interactive browser
python utils/db_browser.py

# Cleanup utility
python utils/cleanup_db.py
```

### Install SQLite Browser (GUI)

```bash
sudo apt install sqlitebrowser -y

# Open database
sqlitebrowser ~/register-track-bot/data/finance_tracker.db
```

---

## Updating the Bot

When you push updates to GitHub:

```bash
# Navigate to bot directory
cd ~/register-track-bot

# Stop the service
sudo systemctl stop telegram-bot

# Pull latest changes
git pull

# Activate virtual environment
source .venv/bin/activate

# Update dependencies (if requirements.txt changed)
pip install -r requirements.txt --upgrade

# Restart the service
sudo systemctl start telegram-bot

# Check status
sudo systemctl status telegram-bot
```

---

## Monitoring

### Check if Bot is Running

```bash
# Check systemd service status
sudo systemctl status telegram-bot

# Check if Python process is running
ps aux | grep python

# View real-time logs
sudo journalctl -u telegram-bot -f

# View last 100 log lines
sudo journalctl -u telegram-bot -n 100

# View logs from today
sudo journalctl -u telegram-bot --since today

# View logs with errors only
sudo journalctl -u telegram-bot -p err
```

### System Resource Usage

```bash
# Install htop (if not already installed)
sudo apt install htop -y

# View resources
htop

# Check disk usage
df -h

# Check bot directory size
du -sh ~/register-track-bot
```

---

## Power Settings (Ubuntu Desktop)

If using Ubuntu Desktop, prevent sleep:

```bash
# Disable automatic suspend
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 0

# Disable screen blank
gsettings set org.gnome.desktop.session idle-delay 0
```

**Or use GUI:**
- Settings → Power
- Set "Automatic suspend" to "Off"
- Set "Blank screen" to "Never"

---

## Troubleshooting

### Bot Not Starting

**Check service status:**
```bash
sudo systemctl status telegram-bot
```

**View detailed logs:**
```bash
sudo journalctl -u telegram-bot -n 100 --no-pager
```

**Check if token is set:**
```bash
echo $TELEGRAM_BOT_TOKEN
# Should show your token
```

**Test manually:**
```bash
cd ~/register-track-bot
source .venv/bin/activate
python run_bot.py
# Check for errors
```

### Database Permission Issues

```bash
# Fix ownership
chown -R $USER:$USER ~/register-track-bot

# Fix permissions
chmod -R 755 ~/register-track-bot
chmod 644 ~/register-track-bot/data/finance_tracker.db
```

### Port/Network Issues

```bash
# Check internet connection
ping -c 4 api.telegram.org

# Check DNS resolution
nslookup api.telegram.org

# Check if firewall is blocking (Ubuntu uses ufw)
sudo ufw status

# If ufw is active and blocking, allow outgoing connections:
sudo ufw default allow outgoing
```

### Service Won't Start

**Check for syntax errors in service file:**
```bash
sudo systemd-analyze verify /etc/systemd/system/telegram-bot.service
```

**Check file paths:**
```bash
# Verify Python path
ls -la ~/register-track-bot/.venv/bin/python

# Verify run_bot.py exists
ls -la ~/register-track-bot/run_bot.py
```

---

## Security Best Practices

### 1. Protect Your Token

```bash
# Never commit tokens to Git
# Token is only in .bashrc and systemd service file

# Check .bashrc permissions (should be 644 or 600)
ls -la ~/.bashrc

# Make it more secure if needed
chmod 600 ~/.bashrc
```

### 2. Keep System Updated

```bash
# Update system regularly
sudo apt update && sudo apt upgrade -y

# Enable automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### 3. Firewall Configuration

```bash
# Enable firewall
sudo ufw enable

# Allow SSH (important if accessing remotely!)
sudo ufw allow ssh

# Check status
sudo ufw status
```

### 4. User Permissions

```bash
# Bot runs as your user (not root) - this is good!
# Verify service user
sudo systemctl show telegram-bot | grep User
```

---

## Remote Access

### Option 1: SSH Access

```bash
# Install OpenSSH server (if not already installed)
sudo apt install openssh-server -y

# Enable SSH service
sudo systemctl enable ssh
sudo systemctl start ssh

# Check SSH status
sudo systemctl status ssh

# Find your IP address
ip addr show | grep inet

# From another computer:
# ssh YOUR_USER@IP_ADDRESS
```

**Secure SSH:**
```bash
# Disable root login
sudo nano /etc/ssh/sshd_config
# Change: PermitRootLogin no

# Restart SSH
sudo systemctl restart ssh
```

### Option 2: TeamViewer

```bash
# Download and install TeamViewer
wget https://download.teamviewer.com/download/linux/teamviewer_amd64.deb
sudo apt install ./teamviewer_amd64.deb -y

# Start TeamViewer
teamviewer
```

### Option 3: Tailscale VPN

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Connect to Tailscale network
sudo tailscale up

# Get your Tailscale IP
tailscale ip -4
```

---

## Performance Optimization

### Disable Unnecessary Services (Ubuntu Desktop)

```bash
# Check what's using resources
systemctl list-units --type=service --state=running

# Disable CUPS (printing) if not needed
sudo systemctl disable cups
sudo systemctl stop cups

# Disable Bluetooth if not needed
sudo systemctl disable bluetooth
sudo systemctl stop bluetooth
```

### Resource Usage

**Typical usage for this bot:**
- RAM: ~30-50 MB
- CPU: <1% when idle
- Disk I/O: Minimal

**Monitor resources:**
```bash
# Real-time monitoring
htop

# Check bot process specifically
ps aux | grep python | grep run_bot
```

---

## Cost & Power Consumption

**HP EliteDesk with Ubuntu:**
- Idle power: ~8-12W (lower than Windows!)
- Active power: ~15-25W
- Monthly cost (at €0.30/kWh): ~€2-4

**Comparison:**
- Ubuntu vs Windows: ~20-30% less power usage
- Raspberry Pi: Still cheaper (~€1-2/month)
- Cloud hosting: ~€5/month

---

## Quick Reference

**Common Commands:**

```bash
# Start bot manually
cd ~/register-track-bot && source .venv/bin/activate && python run_bot.py

# Service management
sudo systemctl start telegram-bot
sudo systemctl stop telegram-bot
sudo systemctl restart telegram-bot
sudo systemctl status telegram-bot

# View logs
sudo journalctl -u telegram-bot -f

# Backup database
cp ~/register-track-bot/data/finance_tracker.db ~/register-track-bot/backups/backup.db

# Update bot
cd ~/register-track-bot && git pull && source .venv/bin/activate && pip install -r requirements.txt --upgrade
```

---

## Verification Checklist

Verify your 24/7 setup is working correctly:

### ✅ Initial Test
```bash
# 1. Check service is running
sudo systemctl status telegram-bot
# Should show: "Active: active (running)" in green

# 2. Test bot in Telegram
# Send /start to your bot - should respond immediately

# 3. Check logs for errors
sudo journalctl -u telegram-bot -n 50
# Should see "Bot is running..." message
```

### ✅ Boot Test (Critical!)
```bash
# Reboot your PC
sudo reboot

# After PC restarts, SSH in or open terminal and check:
sudo systemctl status telegram-bot
# Should show "Active: active (running)"

# Test bot in Telegram again
# Send /start - bot should respond (proves auto-start works!)
```

### ✅ Crash Recovery Test
```bash
# Kill the bot process to simulate crash
sudo pkill -9 -f run_bot.py

# Wait 10-15 seconds, then check status
sudo systemctl status telegram-bot
# Should show bot restarted automatically

# Check logs to verify restart
sudo journalctl -u telegram-bot -n 20
# Should see restart messages
```

### ✅ Power Failure Simulation
```bash
# 1. Just power off the PC (simulate power cut)
sudo poweroff

# 2. Turn PC back on (press power button)

# 3. After boot completes, check bot is running:
sudo systemctl status telegram-bot

# 4. Test in Telegram - should work with no manual intervention!
```

**If all 4 tests pass → Your bot is truly 24/7! 🎉**

---

## Next Steps

After successful deployment:

- [ ] ✅ Test bot in Telegram
- [ ] ✅ Verify service starts on reboot (`sudo reboot`)
- [ ] ✅ Test crash recovery (kill process, verify auto-restart)
- [ ] ✅ Simulate power failure (power off, power on, verify bot starts)
- [ ] Set up daily backups (cron)
- [ ] Configure SSH for remote access
- [ ] Monitor for first 24 hours
- [ ] Consider setting up Tailscale for easy remote access

---

## Ubuntu vs Windows: Why Ubuntu is Better for 24/7 Bots

✅ **Advantages:**
- Lower resource usage (~30% less RAM, CPU)
- More stable for long-running processes
- Better systemd service management
- Free and open source
- Excellent terminal/SSH access
- Lower power consumption
- No forced updates/reboots

❌ **Potential Disadvantages:**
- Learning curve if new to Linux
- No GUI tools by default (Server edition)
- Requires command-line comfort

---

**Your bot is now running 24/7 on Ubuntu! 🚀**

For issues or questions, check the [main README](../README.md) or open an [issue on GitHub](https://github.com/diogoviieira/register-track-bot/issues).
