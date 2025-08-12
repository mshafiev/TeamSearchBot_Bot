# Matchmaking Telegram Bot

A Telegram bot built with aiogram 3 for viewing and rating user profiles with likes, messages, and basic profile editing. Integrates with an external DB API and a recommendation service, and enqueues like events to RabbitMQ.

## Purpose
- Guide users through profile registration and editing
- Show recommendations and collect likes/dislikes
- Notify users about incoming likes and handle mutual matches

## Inputs
- Telegram updates (messages, contacts, photos)
- Environment variables:
  - `BOT_TOKEN`, `DB_SERVER_HOST`, `DB_SERVER_PORT`
  - `RECSYS_SERVER_HOST`, `RECSYS_SERVER_PORT`
  - `RMQ_USER`, `RMQ_PASS`, `RMQ_HOST`, `RMQ_PORT`

## Outputs
- Telegram messages to users
- HTTP requests to DB API (`api_client.py`) and RecSys (`recsys_client.py`)
- RabbitMQ messages to `likes` queue (`producer.py`)

## Quick start
1. Fill `.env` with required variables
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Structure
- `main.py` – bot entrypoint and router wiring
- `app/routers/*.py` – features (start, registration, update, questionnaires)
- `app/functions.py` – shared bot functions (profile render, menu)
- `app/keyboards.py` – keyboards
- `app/states.py` – FSM states
- `app/texts.py` – centralized user-facing texts (localization ready)
- `app/validators.py` – input validators/parsers
- `app/utils.py` – safe async send helpers
- `api_client.py` – external DB API client
- `recsys_client.py` – recommendation service client
- `producer.py` – RMQ publisher (non-blocking)

## Testing
- Business logic is separated from I/O:
  - Validators (`app/validators.py`) can be unit-tested without Telegram
  - Message sending uses `app/utils.safe_send_message` for predictable behavior
- Suggested tests (pytest):
  - `validate_message_text`, `parse_age`, `parse_date_dmy`
  - `send_like_message` publishes valid payloads and rejects invalid IDs
  - Router handlers can be tested with aiogram test utilities and mocked clients

## Logging & Error handling
- Non-fatal send failures are logged with context
- External service calls are wrapped by dedicated clients; critical errors are user-friendly

## Changelog
- Add centralized texts in `app/texts.py` for localization
- Add validators in `app/validators.py` (IDs, messages, age, date)
- Add safe send helpers in `app/utils.py`
- Refactor routers to use texts, validators, and safe sends
- Optimize RMQ producer by moving blocking publish to a thread; add input validation
- Normalize registration prompts and validation messages
- Remove duplicate imports and redundant state setting in update flows

## Future optimizations
- Add exponential backoff and rate-limit handling for external HTTP calls
- Cache user lookups where safe to reduce duplicate network calls
- Add structured logging and tracing (e.g., OpenTelemetry)
- Introduce feature flags and A/B for recommendation strategies
- Add CI with linting (flake8/ruff) and tests (pytest)