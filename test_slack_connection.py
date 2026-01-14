#!/usr/bin/env python3
"""
Test script to verify Slack bot connectivity and send test messages.
Run this after configuring your .env file to ensure everything works.
"""

import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime

def test_slack_connection():
    """Test Slack bot connection and send test messages."""
    load_dotenv()

    # Load environment variables
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    channel_leadership = os.getenv("SLACK_CHANNEL_LEADERSHIP")
    channel_alerts = os.getenv("SLACK_CHANNEL_ALERTS")

    print("\n" + "="*60)
    print("🤖 CI-Bot Slack Connection Test")
    print("="*60 + "\n")

    # Check if required variables are set
    missing_vars = []
    if not slack_token:
        missing_vars.append("SLACK_BOT_TOKEN")
    if not channel_leadership:
        missing_vars.append("SLACK_CHANNEL_LEADERSHIP")
    if not channel_alerts:
        missing_vars.append("SLACK_CHANNEL_ALERTS")

    if missing_vars:
        print("❌ Missing environment variables in .env file:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\nPlease configure these variables and try again.")
        return False

    # Validate token format
    if not slack_token.startswith("xoxb-"):
        print("❌ Invalid SLACK_BOT_TOKEN format")
        print("   Bot tokens should start with 'xoxb-'")
        return False

    print("✓ Environment variables loaded")
    print(f"  • Bot Token: {slack_token[:10]}...{slack_token[-4:]}")
    print(f"  • Leadership Channel: {channel_leadership}")
    print(f"  • Alerts Channel: {channel_alerts}")
    print()

    # Initialize Slack client
    client = WebClient(token=slack_token)

    # Test 1: Auth test
    print("📡 Test 1: Authenticating with Slack...")
    try:
        auth_response = client.auth_test()
        print(f"✓ Authentication successful!")
        print(f"  • Bot User: @{auth_response['user']}")
        print(f"  • Team: {auth_response['team']}")
        print(f"  • Bot User ID: {auth_response['user_id']}")
        print()
    except SlackApiError as e:
        print(f"❌ Authentication failed: {e.response['error']}")
        return False

    # Test 2: Check channel access
    print("🔍 Test 2: Verifying channel access...")

    channels_to_test = [
        ("Leadership", channel_leadership),
        ("Alerts", channel_alerts)
    ]

    accessible_channels = []

    for name, channel_id in channels_to_test:
        try:
            # Try to get channel info
            response = client.conversations_info(channel=channel_id)
            channel_info = response["channel"]

            print(f"✓ {name} channel accessible: #{channel_info['name']}")

            # Check if bot is a member
            if not channel_info.get("is_member"):
                print(f"  ⚠️  Bot is NOT a member of this channel!")
                print(f"  → Run: /invite @CI-Bot in #{channel_info['name']}")
            else:
                accessible_channels.append((name, channel_id))
        except SlackApiError as e:
            print(f"❌ {name} channel error: {e.response['error']}")
            if e.response['error'] == 'channel_not_found':
                print(f"  → Channel '{channel_id}' doesn't exist or bot lacks access")
            elif e.response['error'] == 'missing_scope':
                print(f"  → Add 'channels:read' permission to bot")

    print()

    if not accessible_channels:
        print("❌ No channels accessible. Please:")
        print("  1. Create the channels if they don't exist")
        print("  2. Invite the bot with /invite @CI-Bot")
        print("  3. Verify the channel IDs in .env are correct")
        return False

    # Test 3: Send test messages
    print("📨 Test 3: Sending test messages...")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for name, channel_id in accessible_channels:
        try:
            test_message = f"""
🧪 **Test Message** from CI-Bot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is a connectivity test for the Competitive Intelligence Bot.

✓ Slack SDK connection successful
✓ Channel access verified
✓ Message formatting working

_Test sent at: {timestamp}_

If you see this message, your CI-Bot is configured correctly! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """.strip()

            response = client.chat_postMessage(
                channel=channel_id,
                text=f"CI-Bot Test Message - {timestamp}",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": test_message
                        }
                    }
                ]
            )

            print(f"✓ Test message sent to {name} channel")
            print(f"  • Message timestamp: {response['ts']}")

        except SlackApiError as e:
            print(f"❌ Failed to send to {name}: {e.response['error']}")
            if e.response['error'] == 'not_in_channel':
                print(f"  → Invite bot to channel with: /invite @CI-Bot")
            elif e.response['error'] == 'missing_scope':
                print(f"  → Add 'chat:write' permission to bot")

    print()
    print("="*60)
    print("✅ Slack Connection Test Complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Check your Slack channels for test messages")
    print("  2. If messages appear, your setup is complete!")
    print("  3. Run 'python main.py' to start the bot scheduler")
    print("  4. Run 'python run_daily_pipeline.py' to test the full pipeline")
    print()

    return True

if __name__ == "__main__":
    try:
        success = test_slack_connection()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
