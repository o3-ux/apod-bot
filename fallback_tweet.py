"""Send fallback tweet when APOD image cannot be retrieved.

This script expects the following environment variables to be set (e.g. via
GitHub Actions secrets):

TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET

Usage:
    python fallback_tweet.py --message "NASA's APOD is currently unavailable. We'll be back soon!"
"""
from __future__ import annotations

import argparse
import os
import sys

try:
    import tweepy  # type: ignore
except ImportError:
    sys.exit("tweepy not installed; add to requirements.txt")


def tweet(message: str) -> None:
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")

    if not all((api_key, api_secret, access_token, access_secret)):
        sys.exit("Twitter credentials missing. Cannot tweet.")

    client = tweepy.Client(consumer_key=api_key,
                           consumer_secret=api_secret,
                           access_token=access_token,
                           access_token_secret=access_secret)
    client.create_tweet(text=message)
    print("Fallback tweet sent: " + message)


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--message", required=False,
                        default="NASA's APOD is temporarily unavailable. We'll be back soon!")
    args = parser.parse_args(argv)
    tweet(args.message)


if __name__ == "__main__":
    main()
