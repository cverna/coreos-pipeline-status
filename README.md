# CoreOS Pipeline Status

A containerized tool for analyzing CoreOS pipeline build status from Slack messages and posting summaries back to Slack channels.

## Overview

This project provides a Python CLI tool that:
- Fetches Slack messages from a specific channel for a given date
- Analyzes CoreOS pipeline build status and failures
- Generates comprehensive reports with build statistics
- Posts formatted summaries back to Slack channels

## Prerequisites

- Python 3.8+ or Docker/Podman
- Slack workspace access
- Slack API tokens (XOXC and XOXD)

## Quick Start

### 1. Get Slack Tokens

Before using this tool, you need to obtain your Slack API tokens. We recommend using the [slack-token-extractor](https://github.com/maorfr/slack-token-extractor) tool:

#### Option A: Browser Extension (Recommended)

1. **Chrome Extension:**
   - Go to `chrome://extensions` in Chrome
   - Enable Developer mode
   - Click "Load unpacked" and select the `chrome` directory from the [slack-token-extractor](https://github.com/maorfr/slack-token-extractor) repository
   - Visit your Slack workspace and click the extension icon to view your tokens

2. **Firefox Add-on:**
   - Go to `about:debugging#/runtime/this-firefox` in Firefox
   - Click "Load Temporary Add-on..." and select the `manifest.json` file from the `firefox` directory
   - Visit your Slack workspace and click the extension icon to view your tokens

### 2. Configure Environment

Create a `.env` file with your Slack tokens:

```bash
# Required Slack tokens (obtained from step 1)
SLACK_XOXC_TOKEN=xoxc-your-token-here
SLACK_XOXD_TOKEN=xoxd-your-token-here

# Slack channel ID (e.g., C1234567890)
SLACK_CHANNEL=C1234567890
```

### 3. Run the Tool

#### Using Docker/Podman (Recommended)

```bash
# Analyze today's builds
podman run --rm --env-file .env quay.io/cverna/coreos-pipeline-status:latest

# Analyze specific date
podman run --rm --env-file .env quay.io/cverna/coreos-pipeline-status:latest --date 2024-01-15

# Pretty print output
podman run --rm --env-file .env quay.io/cverna/coreos-pipeline-status:latest --pretty

# Post summary to Slack
podman run --rm --env-file .env quay.io/cverna/coreos-pipeline-status:latest --summary "🚨 Pipeline Summary: 3/14 builds failed"
```

## Claude Code Integration

This project is designed to work seamlessly with [Claude Code](https://docs.claude.com/en/docs/claude-code/slash-commands) slash commands for automated pipeline analysis.

### Setting up Claude Code Slash Commands

1. **Create a project command** in `.claude/commands/`:

```bash
mkdir -p .claude/commands
```

2. **Create the pipeline analysis command**:
```bash
cp coreos_pipeline_status.md ~/.claude/commands/
```

Then within Claude code you can run the command using `/coreos_pipeline_status`