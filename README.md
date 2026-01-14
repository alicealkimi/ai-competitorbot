# CI Bot MVP - Competitive Intelligence Bot

Daily AI & AdTech Market Intelligence via Slack

## Overview

The Competitive Intelligence Bot (CI-Bot) MVP delivers daily curated market intelligence on AI capabilities and automation developments in advertising technology. It monitors Tier 1 publications, uses AI to filter relevant content, and delivers executive-ready digests via Slack.

## Features

- **RSS Monitoring**: Automatically monitors 4 Tier 1 AdTech publications
- **AI Classification**: Uses Claude API to identify relevant articles and categorize threats
- **Manual Review**: Editor review interface for threat scoring
- **Slack Integration**: Daily digests and weekly summaries delivered to Slack channels
- **Automated Scheduling**: Runs daily at 6 AM (processing), 8 AM (digest), and 4 PM Friday (weekly summary)

## Setup

### Prerequisites

- Python 3.8+
- Anthropic Claude API key
- Slack workspace with bot token
- Slack channels: `#product-competitor-intel-slt` and `#competitor-intel-alerts`

### Installation

1. Clone or navigate to the project directory:
```bash
cd "Product Competitor Analysis Bot"
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. Run setup script to initialize database and directories:
```bash
python setup.py
```

Alternatively, initialize manually:
```bash
python -c "from database import init_database; init_database()"
```

### Environment Variables

Required variables in `.env`:

- `ANTHROPIC_API_KEY` - Your Anthropic Claude API key
- `SLACK_BOT_TOKEN` - Slack bot OAuth token (starts with `xoxb-`)
- `SLACK_CHANNEL_LEADERSHIP` - Channel ID or name for daily digests
- `SLACK_CHANNEL_ALERTS` - Channel ID or name for high-priority alerts

Optional variables:

- `RELEVANCE_THRESHOLD` - Minimum relevance score (default: 3)
- `MAX_DAILY_ITEMS` - Maximum items per digest (default: 5)
- `TIMEZONE` - Timezone for scheduling (default: America/New_York)

## Usage

### Running the Bot

Start the scheduler to run automated tasks:

```bash
python main.py
```

### Manual Processing

Run the daily pipeline manually:

```bash
python run_daily_pipeline.py
```

### Editor Review Interface

Review and score articles awaiting manual review:

```bash
python review_interface.py
```

## Project Structure

```
.
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── config.py                # Configuration management
├── main.py                  # Entry point and orchestration
├── database.py              # SQLite operations
├── rss_aggregator.py        # RSS feed collection
├── deduplication.py         # Article deduplication
├── llm_processor.py         # Claude API integration
├── prompts.py               # LLM prompt templates
├── classifier.py            # Relevance filtering
├── review_interface.py      # Editor review CLI
├── threat_scorer.py         # Threat level assignment
├── slack_bot.py             # Slack Bolt app
├── message_formatter.py     # Message formatting
├── slack_delivery.py        # Slack message delivery
├── scheduler.py             # Task scheduling
├── run_daily_pipeline.py    # Daily workflow
├── tests/                   # Unit tests
├── data/                    # SQLite database (gitignored)
└── logs/                    # Log files (gitignored)
```

## Scheduled Tasks

- **6:00 AM Daily**: RSS aggregation → LLM classification → Store results
- **7:30 AM Daily**: Editor review reminder (if pending items)
- **8:00 AM Daily (Mon-Fri)**: Send daily digest to `#product-competitor-intel-slt`
- **4:00 PM Friday**: Send weekly summary

## Troubleshooting

### RSS Feed Failures

If feeds fail to parse, check:
- Network connectivity
- Feed URLs in `config.py`
- Feed format changes (may require updates)

### LLM API Errors

If Claude API calls fail:
- Verify `ANTHROPIC_API_KEY` is correct
- Check API rate limits
- Review logs in `logs/ci_bot.log`

### Slack Delivery Issues

If messages don't send:
- Verify `SLACK_BOT_TOKEN` is valid
- Ensure bot is added to target channels
- Check bot has `chat:write` permission
- Review Slack API error messages in logs

## Development

### Running Tests

```bash
pytest tests/
```

### Logging

Logs are written to `logs/ci_bot.log` with configurable log level via `LOG_LEVEL` environment variable.

## License

Internal use only - Alkimi CI Bot MVP

