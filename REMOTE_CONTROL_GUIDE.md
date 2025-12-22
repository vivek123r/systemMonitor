# 🎮 Remote Control Setup Guide

## ✅ What's Been Added

### Server (server.py)
- `/api/command` - Send remote commands to PC
- `/api/commands` - Agent polls for pending commands
- `/api/command/ack/{id}` - Acknowledge command execution
- Command queue system for reliable delivery

### Agent (agent.py)
- Polls server every 2 seconds for commands
- Executes commands safely with confirmations
- Supports 10+ command types

### Flutter App
- New "Remote Control" page (icon in app bar)
- Beautiful UI with categorized commands
- Confirmation dialogs for dangerous actions
- Real-time feedback

## 📋 Available Commands

### Power Management
- **Shutdown** - Turn off PC (5 second countdown)
- **Restart** - Reboot PC (5 second countdown)
- **Sleep** - Suspend to RAM
- **Logoff** - Log out current user

### Power Profiles
- **High Performance** - Maximum CPU/GPU performance
- **Balanced** - Balance between performance and energy
- **Power Saver** - Maximize battery life

### Display
- **Brightness Control** - Adjust screen brightness (0-100%)

### Quick Actions
- **Screenshot** - Capture screen and save locally
- **Open Apps** - Launch notepad, chrome, etc.
- **Close Apps** - Terminate running applications

## 🚀 How to Use

### 1. Install Optional Dependencies

For brightness control:
```bash
pip install screen-brightness-control
```

For screenshots:
```bash
pip install pillow
```

### 2. Deploy Updated Server

```bash
cd c:\Users\vivek\projects\systemMonitor
git add .
git commit -m "Add remote control features"
git push
```

Vercel will auto-deploy the updates.

### 3. Run the Agent

```bash
python agent.py
```

The agent will now:
- Send system stats every 2 seconds
- Check for remote commands every 2 seconds
- Execute commands and report back

### 4. Use Flutter App

```bash
cd systemmonitor
flutter run
```

1. Tap the **Remote Control icon** (📡) in the app bar
2. Choose a command
3. Confirm if it's a dangerous action
4. Command is sent to server → Agent executes it

## 🎯 Command Flow

```
Flutter App → Vercel Server → Agent on PC → Execution → Acknowledgment
   (Send)      (Queue)        (Poll)       (Action)    (Confirm)
```

## 🔒 Security Notes

⚠️ **Important**: This system has NO authentication!

**To add security:**
1. Add API key in server.py
2. Require password in Flutter app
3. Use HTTPS only (Vercel provides this)
4. Add rate limiting
5. Log all command attempts

## 🐛 Troubleshooting

**Commands not executing?**
- Check agent is running
- Check internet connection
- Verify Vercel deployment is live
- Look at agent console for errors

**Brightness control not working?**
```bash
pip install screen-brightness-control
```

**Screenshot failing?**
```bash
pip install pillow
```

## 🎨 Customization Ideas

Add more commands in `agent.py`:
```python
elif cmd_type == "open_spotify":
    subprocess.Popen(["spotify.exe"])
    return True
```

Add buttons in Flutter:
```dart
_buildControlCard(
  icon: Icons.music_note,
  title: 'Open Spotify',
  subtitle: 'Launch Spotify app',
  color: Colors.green,
  onTap: () => sendCommand('open_spotify'),
),
```

## 📊 Features Added

✅ Shutdown/Restart/Sleep/Logoff
✅ Power profile switching
✅ Brightness control
✅ Screenshot capture
✅ App launcher
✅ Command queue system
✅ Confirmation dialogs
✅ Real-time feedback
✅ Error handling

## 🚀 Next Features to Add

- 🔐 Authentication & API keys
- 📸 View screenshots remotely
- 📁 File browser
- 🎥 Remote desktop streaming
- 📝 Scheduled commands
- 🔔 Command history
- 👥 Multi-PC support
- 🤖 AI assistant integration

Enjoy your remote-controlled PC! 🎮
