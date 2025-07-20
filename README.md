# Discord Verification Bot

A Discord bot that handles user verification through a button-based system with moderator approval.

## Features

- **Verification Button**: Users click a button in the verification channel to start the process
- **Verification Modal**: Users fill out a form with their information
- **Moderator Review**: Responses are sent to a moderator channel for review
- **Approve/Deny System**: Moderators can approve (give role) or deny (kick user) verification requests
- **Automatic Setup**: Bot automatically creates the verification message when it starts

## Setup Instructions

### 1. Create a Discord Bot
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token

### 2. Configure Environment Variables
Create a `.env` file in the project directory with:
```
DISCORD_TOKEN=your_discord_bot_token_here
```

### 3. Configure Channel and Role IDs
Update the following variables in `main.py`:

```python
VERIFY_CHANNEL_ID = 1234567890123456789  # Your verification channel ID
MODERATOR_CHANNEL_ID = 1234567890123456789  # Your moderator channel ID  
VERIFIED_ROLE_ID = 1234567890123456789  # Your verified role ID
```

To get these IDs:
1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
2. Right-click on channels/roles and select "Copy ID"

### 4. Bot Permissions
Make sure your bot has these permissions:
- Send Messages
- Embed Links
- Use Slash Commands
- Manage Roles (for role assignment)
- Kick Members (for denying verification)
- Read Message History

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Run the Bot
```bash
python main.py
```

## How It Works

1. **User joins server** → Bot sends welcome message with verification instructions
2. **User clicks "Verify Yourself" button** → Modal opens with verification questions
3. **User submits form** → Bot sends responses to moderator channel with approve/deny buttons
4. **Moderator clicks Approve** → User gets verified role and access to server
5. **Moderator clicks Deny** → User gets kicked from server

## Commands

- `!hello` - Basic hello command
- `!setup` - Shows setup instructions (Admin only)

## Customization

You can modify the verification questions in the `VerificationModal` class by editing the `ui.TextInput` fields in `main.py`. 