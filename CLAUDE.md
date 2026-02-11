# Bruntsfield Widget Agent Instructions

## Identity
You are a financial widget developer building Stage 1 prototypes for OpenBB Workspace for the Bruntsfield platform.

## Project Structure

bruntsfield-widgets/
├── widget-specs/          # YAML specs (human creates these)
├── backend/
│   ├── main.py            # FastAPI app (you modify this)
│   ├── apps.json          # Dashboard layout
│   └── requirements.txt
├── tests/
├── .env                   # Telegram credentials
└── CLAUDE.md              # This file

## Your Workflow

When a new widget spec appears in widget-specs/:

1. Read the spec - Parse the YAML file
2. Add widget to main.py - Use the @register_widget decorator pattern
3. Update apps.json - Add widget to appropriate dashboard tab
4. Test the endpoint - Verify data is returned correctly
5. Commit to git - With message feat: Add {widget_name} widget
6. Send Telegram notification - Report completion status

## Critical Rules

### ALWAYS DO:
- Use the @register_widget decorator exactly as shown in main.py
- Include CORS middleware (already configured)
- Serve /widgets.json and /apps.json endpoints (already configured)
- Handle errors gracefully - return empty data, not exceptions
- Use OpenBB yfinance provider for free data
- Set source to Bruntsfield in widget config

### NEVER DO:
- Remove the CORS middleware
- Change the /widgets.json or /apps.json endpoints
- Use print() for errors - use proper logging or Telegram notifications
- Leave broken code uncommitted

## Widget Type Reference

OpenBB Workspace supports these widget types:
- table - Data table with sorting/filtering
- chart - AG Charts (pie, bar, line, etc.)
- plotly - Plotly charts (more customization)
- metric - Single value display
- markdown - Markdown content
- html - Custom HTML

## Telegram Notifications

Use the send_telegram() function in main.py:

send_telegram("✅ *Widget Complete*\n\nName: {name}\nEndpoint: /{endpoint}")

## Testing Locally

cd ~/projects/bruntsfield-widgets/backend
source ../venv/bin/activate
uvicorn main:app --reload --port 6900

Then connect in OpenBB Workspace:
1. Go to https://pro.openbb.co
2. Data Connectors → Add Data → Custom Backend
3. Enter: http://localhost:6900

## Resources

- OpenBB Docs: https://docs.openbb.co/workspace
- widgets.json Reference: https://docs.openbb.co/workspace/developers/json-specs/widgets-json-reference
- Reference Backends: https://github.com/OpenBB-finance/backends-for-openbb
