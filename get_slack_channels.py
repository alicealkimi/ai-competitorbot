#!/usr/bin/env python3
"""
Helper script to list all Slack channels and get their IDs.
Run this to find the exact channel IDs for your .env file.
"""

import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_channel_list():
    """List all channels in the workspace with their IDs."""
    load_dotenv()

    slack_token = os.getenv("SLACK_BOT_TOKEN")

    if not slack_token:
        print("❌ Error: SLACK_BOT_TOKEN not found in .env file")
        print("Please add your Slack bot token to the .env file first.")
        return

    if not slack_token.startswith("xoxb-"):
        print("❌ Error: Invalid SLACK_BOT_TOKEN format")
        print("Bot tokens should start with 'xoxb-'")
        return

    client = WebClient(token=slack_token)

    try:
        print("\n" + "="*60)
        print("🔍 Fetching Slack Channels...")
        print("="*60 + "\n")

        # Get public channels
        response = client.conversations_list(types="public_channel,private_channel")
        channels = response["channels"]

        # Separate public and private channels
        public_channels = [ch for ch in channels if not ch.get("is_private")]
        private_channels = [ch for ch in channels if ch.get("is_private")]

        # Display public channels
        if public_channels:
            print("📢 PUBLIC CHANNELS:")
            print("-" * 60)
            for channel in sorted(public_channels, key=lambda x: x["name"]):
                member_status = "✓ Bot is member" if channel.get("is_member") else "✗ Bot not added"
                print(f"  #{channel['name']:<30} {member_status}")
                print(f"    ID: {channel['id']}")
                print()

        # Display private channels (only ones bot is member of)
        if private_channels:
            print("\n🔒 PRIVATE CHANNELS (bot has access):")
            print("-" * 60)
            for channel in sorted(private_channels, key=lambda x: x["name"]):
                print(f"  #{channel['name']:<30} ✓ Bot is member")
                print(f"    ID: {channel['id']}")
                print()

        # Look for CI-Bot channels specifically
        print("\n" + "="*60)
        print("🎯 CI-BOT CHANNELS:")
        print("="*60 + "\n")

        ci_channels = [ch for ch in channels if "competitor-intel" in ch["name"] or "product-competitor" in ch["name"]]

        if ci_channels:
            for channel in ci_channels:
                member_status = "✓" if channel.get("is_member") else "✗ NOT ADDED"
                privacy = "🔒 Private" if channel.get("is_private") else "📢 Public"

                print(f"  #{channel['name']}")
                print(f"    ID: {channel['id']}")
                print(f"    Status: {member_status} | {privacy}")

                if not channel.get("is_member"):
                    print(f"    ⚠️  Action needed: Invite bot with /invite @CI-Bot")
                print()
        else:
            print("⚠️  No CI-Bot channels found!")
            print("\nExpected channels:")
            print("  • #product-competitor-intel-slt")
            print("  • #competitor-intel-alerts")
            print("\nPlease create these channels and invite the bot.")

        print("\n" + "="*60)
        print("📋 COPY TO YOUR .ENV FILE:")
        print("="*60)

        leadership = next((ch for ch in channels if ch["name"] == "product-competitor-intel-slt"), None)
        alerts = next((ch for ch in channels if ch["name"] == "competitor-intel-alerts"), None)

        if leadership:
            print(f'\nSLACK_CHANNEL_LEADERSHIP={leadership["id"]}')
        else:
            print('\n# SLACK_CHANNEL_LEADERSHIP=<create #product-competitor-intel-slt first>')

        if alerts:
            print(f'SLACK_CHANNEL_ALERTS={alerts["id"]}')
        else:
            print('# SLACK_CHANNEL_ALERTS=<create #competitor-intel-alerts first>')

        print()

    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
        if e.response['error'] == 'invalid_auth':
            print("\nYour SLACK_BOT_TOKEN may be invalid or expired.")
            print("Please check your token at: https://api.slack.com/apps")
        elif e.response['error'] == 'missing_scope':
            print("\nMissing required permissions!")
            print("Add these scopes at https://api.slack.com/apps → OAuth & Permissions:")
            print("  • channels:read")
            print("  • groups:read")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    get_channel_list()
