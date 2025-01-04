# Twitter/X AI Agent 🤖

An intelligent Twitter bot that generates and posts tweets using AI, with scheduling capabilities and style matching based on reference tweets.

## Features

- 🧠 AI-powered tweet generation using OpenAI GPT
- 🎯 Style matching based on reference tweets
- ⏰ Schedule tweets for later (coming soon)
- 📊 Analytics and monitoring (coming soon)
- 🔄 Automatic posting with error handling
- 🎨 Customizable tweet styles and options

## Prerequisites

- Python 3.8+
- Twitter Developer Account with API v2 access
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/paresh795/twitter_x_ai_agent.git
cd twitter_x_ai_agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API credentials:
```env
OPENAI_API_KEY=your_openai_key
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run src/app.py
```

2. Enter a topic and customize generation options
3. Generate and preview tweets
4. Post immediately or schedule for later

## Project Structure

```
twitter_ai_agent/
├── src/
│   ├── components/      # UI components
│   ├── services/        # Core services
│   ├── data/           # Data files
│   └── app.py          # Main application
├── tests/              # Test files
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for GPT API
- Twitter for API v2 access
- Streamlit for the UI framework

## Contact

Paresh - [@YourTwitterHandle](https://twitter.com/YourTwitterHandle)

Project Link: [https://github.com/paresh795/twitter_x_ai_agent](https://github.com/paresh795/twitter_x_ai_agent) 