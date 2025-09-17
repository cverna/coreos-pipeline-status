#!/usr/bin/env python3
"""
Slack Message Fetcher CLI

A simple CLI script to fetch messages from a Slack channel for a specific day.
Returns messages as JSON.
"""

import os
import sys
import json
import argparse
import ssl
import certifi
from datetime import datetime, timezone
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def load_config():
    """Load configuration from environment variables."""
    load_dotenv()

    xoxc_token = os.getenv('SLACK_XOXC_TOKEN')
    xoxd_token = os.getenv('SLACK_XOXD_TOKEN')
    channel = os.getenv('SLACK_CHANNEL')

    if not xoxc_token or not xoxd_token:
        print("Error: SLACK_XOXC_TOKEN and SLACK_XOXD_TOKEN must be set in .env file", file=sys.stderr)
        sys.exit(1)

    if not channel:
        print("Error: SLACK_CHANNEL not found in environment variables", file=sys.stderr)
        sys.exit(1)

    # Extract just the channel ID (remove any extra text like #channel-name)
    channel_id = channel.split()[0] if ' ' in channel else channel

    return xoxc_token, xoxd_token, channel_id


def parse_date(date_str):
    """Parse date string and return start and end timestamps."""
    try:
        if date_str:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date_obj = datetime.now()

        # Set to start of day (00:00:00)
        start_of_day = date_obj.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        # Set to end of day (23:59:59)
        end_of_day = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)

        return start_of_day.timestamp(), end_of_day.timestamp()
    except ValueError:
        print(f"Error: Invalid date format '{date_str}'. Use YYYY-MM-DD format.", file=sys.stderr)
        sys.exit(1)


def fetch_messages(client, channel_id, oldest, latest):
    """Fetch messages from Slack channel within the specified time range."""
    messages = []
    cursor = None

    while True:
        try:
            history_response = client.conversations_history(
                channel=channel_id,
                oldest=str(oldest),
                latest=str(latest),
                limit=1000,
                cursor=cursor,
            )

            batch_messages = history_response.get('messages', [])
            messages.extend(batch_messages)

            if not history_response.get('has_more'):
                break

            cursor = history_response.get('response_metadata', {}).get('next_cursor')

        except SlackApiError as e:
            print(f"Error from Slack API: {e.response['error']}", file=sys.stderr)
            sys.exit(1)

    return messages


def main():
    parser = argparse.ArgumentParser(description='Fetch Slack messages for a specific day as JSON')
    parser.add_argument(
        '--date',
        type=str,
        help='Date in YYYY-MM-DD format (default: today)',
        default=None
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: print to stdout)',
        default=None
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print JSON output'
    )

    args = parser.parse_args()

    # Load configuration
    xoxc_token, xoxd_token, channel_id = load_config()

    # Setup Slack client
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    client = WebClient(token=xoxc_token, ssl=ssl_context)
    client.headers.update({"Cookie": f"d={xoxd_token};"})

    # Test authentication
    try:
        client.auth_test()
    except SlackApiError as e:
        print(f"Authentication failed: {e.response['error']}", file=sys.stderr)
        sys.exit(1)

    # Parse date and get timestamps
    oldest, latest = parse_date(args.date)

    date_str = datetime.fromtimestamp(oldest).strftime('%Y-%m-%d')

    # Fetch messages
    messages = fetch_messages(client, channel_id, oldest, latest)

    if not messages:
        messages = []

    # Sort messages by timestamp (oldest first)
    messages.sort(key=lambda x: float(x.get('ts', 0)))

    # Filter to include all message types (users and bots)
    filtered_messages = [msg for msg in messages if msg.get('type') == 'message']

    result = {
        'date': date_str,
        'channel': channel_id,
        'message_count': len(filtered_messages),
        'messages': filtered_messages
    }

    # Output JSON
    json_output = json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_output)
    else:
        print(json_output)


if __name__ == '__main__':
    main()
