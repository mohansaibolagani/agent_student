# Student Assistant Agent

An AI assistant agent built using **Google Agent Development Kit (ADK)** and Gemini models to help students with study calculations, file creation, and project management.

## Features

- **Mark Average Calculation**: Compute grade and mark averages.
- **File Management**: Create study notes and structured documents.
- **GitHub Integration**: Direct repository push and code synchronization via GitHub API.

## Project Structure

```text
project/
├── my_agent/
│   ├── __init__.py       # Package entry point
│   ├── agent.py          # Agent initialization and tool configuration
│   ├── config.py         # Agent configuration
│   ├── prompts.py        # System instructions and prompt templates
│   └── tools.py          # Custom agent tools
├── requirements.txt      # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # Project documentation
```

## Setup & Running

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   Create a `.env` file or export environment variables:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key
   GITHUB_TOKEN=your_github_token  # Optional, for GitHub tool operations
   ```
