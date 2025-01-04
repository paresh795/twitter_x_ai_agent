# Twitter AI Agent 🤖

An intelligent Twitter bot that generates and schedules personalized tweets using AI, maintaining your unique writing style and voice.

## Features ✨

- **AI-Powered Tweet Generation**: Creates engaging tweets based on your topics while matching your personal writing style
- **Style Personalization**: Uses your previous tweets as reference to maintain consistency in tone and style
- **Smart Scheduling**: Schedule tweets for optimal posting times
- **Interactive UI**: Clean, modern interface for tweet generation and management
- **Real-time Preview**: See how your tweet will look before posting
- **Error Handling**: Robust error handling and rate limit management

## Setup 🚀

1. **Clone the repository**
```bash
git clone https://github.com/paresh795/twitter_x_ai_agent.git
cd twitter_x_ai_agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure your credentials**
Create a `.env` file in the root directory with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
```

4. **Set up your reference tweets**
- Create a file at `src/data/reference_tweets.json`
- Add your previous tweets in this format:
```json
{
    "tweets": [
        {"text": "Your first tweet here"},
        {"text": "Your second tweet here"},
        {"text": "Add more tweets..."}
    ]
}
```
These tweets will be used as reference to maintain your writing style.

5. **Run the application**
```bash
streamlit run src/app.py
```

## Usage 💡

1. **Generate Tweets**
   - Enter your topic
   - Customize style preferences (Professional, Casual, etc.)
   - Add hashtags and emojis as needed
   - Preview and post or schedule

2. **Schedule Tweets**
   - Generate a tweet
   - Click "Schedule Tweet"
   - Select date and time
   - Confirm scheduling

## Project Structure 📁

```
twitter_ai_agent/
├── src/
│   ├── components/         # UI components
│   ├── services/          # Core services (Twitter, OpenAI, etc.)
│   ├── data/             # Reference tweets and other data
│   └── app.py            # Main application
├── .env                  # Environment variables
└── README.md            # Documentation
```

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📝

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- OpenAI for GPT API
- Twitter API
- Streamlit for the UI framework

## Contact 📧

Paresh - https://x.com/pareshranaut

My Youtube Channel - https://www.youtube.com/@paresh-ranaut

My website : https://autolynxai.com
