# 🚀 Quick Setup Guide for AI Features

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd medchart_demo
pip install -r requirements.txt
```

This will install:
- `streamlit` - Web application framework
- `pdfplumber` - PDF processing
- `pandas` - Data analysis
- `google-generativeai` - Gemini API client
- `python-dotenv` - Environment variable management

### 2. Get Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 3. Configure Environment Variables

Create a `.env` file in the `medchart_demo` directory:

```bash
# Option 1: Copy the example file
cp .env.example .env

# Option 2: Create manually
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

Edit the `.env` file and replace `your_actual_api_key_here` with your actual API key:

```
GEMINI_API_KEY=AIzaSyD...your_key_here
```

**Important:** 
- The `.env` file is automatically ignored by git (already in `.gitignore`)
- Never commit your API key to version control
- Keep your API key secure

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### 5. Verify AI Features

1. Navigate to **Tab 4: 🤖 AI Insights**
2. You should see: "✅ Gemini 1.5 Pro connected successfully!"
3. If you see an error, check the troubleshooting section below

## Troubleshooting

### Error: "Gemini API key not found"

**Solution:**
1. Verify `.env` file exists in `medchart_demo` directory
2. Check the file contains: `GEMINI_API_KEY=your_key`
3. Restart the Streamlit application
4. Make sure there are no spaces around the `=` sign

### Error: "models/gemini-1.5-pro is not found"

**Solution:**
- This has been fixed in the implementation
- The code now uses `gemini-1.5-pro-latest` model
- If you still see this error, update your `google-generativeai` package:
  ```bash
  pip install --upgrade google-generativeai
  ```

### Error: "Failed to initialize Gemini"

**Possible causes:**
1. Invalid API key - Get a new one from Google AI Studio
2. No internet connection - Check your network
3. API quota exceeded - Check your usage at Google AI Studio
4. Package not installed - Run `pip install google-generativeai`

### AI Features Not Showing

**Solution:**
1. Make sure you're on **Tab 4: 🤖 AI Insights**
2. Check browser console for errors (F12)
3. Verify the `.env` file is loaded (restart app)
4. Check that `llm_service.py` exists in the directory

## Testing the Setup

### Quick Test

1. Go to **Tab 1: 📋 Validate**
2. Select a sample chart (e.g., `chart_MBR001.txt`)
3. Click "🚀 Run Validation"
4. Go to **Tab 4: 🤖 AI Insights**
5. Click "🔍 Analyze Trends"
6. You should see AI-generated insights

### Feature Checklist

- [ ] Tab 4 shows "✅ Gemini 1.5 Pro connected successfully!"
- [ ] Trend Analysis generates insights
- [ ] Natural Language Query responds to questions
- [ ] Root Cause Analysis works
- [ ] Tab 2 shows "🤖 AI Explanation" buttons
- [ ] Tab 3 has "🔄 Refresh Alerts" button

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GEMINI_API_KEY` | Yes | Your Gemini API key | `AIzaSyD...` |

## File Structure

```
medchart_demo/
├── .env                    # Your API key (create this, not in git)
├── .env.example           # Template for .env file
├── app.py                 # Main application
├── llm_service.py         # Gemini integration
├── analytics_prompts.py   # AI prompt templates
├── db.py                  # Database functions
├── agents.py              # Validation logic
├── requirements.txt       # Python dependencies
└── AI_FEATURES_README.md  # Detailed feature documentation
```

## Security Best Practices

1. ✅ Never commit `.env` file to git
2. ✅ Use `.env.example` for templates only
3. ✅ Rotate API keys periodically
4. ✅ Monitor API usage in Google AI Studio
5. ✅ Set up billing alerts if using paid tier

## Next Steps

Once setup is complete:

1. Read [AI_FEATURES_README.md](AI_FEATURES_README.md) for feature details
2. Run some validations to generate data
3. Explore AI insights in Tab 4
4. Try natural language queries
5. Review automated alerts in Tab 3

## Support

- **Documentation**: See `AI_FEATURES_README.md`
- **Implementation Details**: See `GEMINI_IMPLEMENTATION_PLAN.md`
- **Quick Reference**: See `QUICK_IMPLEMENTATION_GUIDE.md`

---

**Setup Time**: ~5 minutes

**Ready to use!** 🎉