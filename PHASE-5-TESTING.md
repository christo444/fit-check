# Phase 5: Quick Testing Guide

## 🚀 Quick Start

### 1. Install LLM Dependencies
```powershell
cd backend
pip install openai anthropic groq
```

### 2. Configure API Key (Choose One)

#### Option A: OpenAI (Recommended)
```env
# Add to backend/.env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4
```

#### Option B: Anthropic Claude
```env
# Add to backend/.env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
LLM_MODEL=claude-3-sonnet-20240229
```

#### Option C: Groq (Fast & Free Tier)
```env
# Add to backend/.env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your-key-here
LLM_MODEL=llama3-70b-8192
```

### 3. Restart Backend
```powershell
cd backend
python app.py
```

## 🧪 Test Endpoint Directly

### Using PowerShell
```powershell
# Replace <outfit_id> with actual ID from your database
$outfitId = "your-outfit-id-here"
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/analyze-style/$outfitId" -Method POST
$response | ConvertTo-Json -Depth 10
```

### Using cURL
```bash
curl -X POST http://localhost:5000/api/analyze-style/<outfit_id>
```

## 📝 Expected Response
```json
{
  "success": true,
  "outfit_id": "...",
  "style": {
    "type": "casual",
    "confidence": 0.89,
    "description": "..."
  },
  "suggestions": [
    {
      "title": "...",
      "description": "...",
      "items": ["...", "...", "..."]
    }
  ],
  "keywords": ["...", "...", "..."],
  "advice": "...",
  "data_sources": {
    "detection": true,
    "pose": true,
    "colors": true,
    "fit": true
  }
}
```

## 🐛 Troubleshooting

### Error: "LLM service not configured"
- ✅ Check `.env` file has `LLM_PROVIDER` and API key
- ✅ Restart backend after adding environment variables
- ✅ Verify API key is valid (no extra spaces or quotes)

### Error: "No analysis data available"
- ✅ Run at least one analysis first (Detection, Pose, Attributes, or Fit)
- ✅ The endpoint requires some input data to analyze

### Error: API Key Invalid
- ✅ Check API key format (starts with `sk-` for OpenAI/Anthropic, `gsk_` for Groq)
- ✅ Verify key is active in provider dashboard
- ✅ Check API usage limits not exceeded

### Error: Module not found
- ✅ Install missing package: `pip install openai anthropic groq`
- ✅ Activate correct virtual environment

### Slow Response
- ⏱️ GPT-4: 5-10 seconds (most accurate)
- ⏱️ Claude: 3-7 seconds (good balance)
- ⏱️ Groq Llama: 1-3 seconds (fastest, free tier available)

## 💡 Tips

### Getting Free API Keys
1. **Groq** - Best for testing, very fast, generous free tier
2. **OpenAI** - $5 free credit for new accounts
3. **Anthropic** - Request access, some free credits available

### Best Models
- **Accuracy**: GPT-4, Claude-3-Opus
- **Speed**: Groq Llama3-70b, GPT-3.5-Turbo
- **Cost**: Groq (free tier), GPT-3.5-Turbo, Claude-3-Haiku

### Testing Workflow
1. Upload an outfit image
2. Run all analyses (Detect → Pose → Attributes → Fit)
3. Click "AI Style Analysis" button
4. Wait 3-10 seconds for results
5. Explore suggestions, keywords, and advice!

## 📊 Check Logs
The backend logs all LLM calls:
```
INFO - Analyzing style with openai (gpt-4)
INFO - YOLO detection: 3 items found
INFO - Pose detection: 33 landmarks found
INFO - Color/pattern extraction: 2 items analyzed
INFO - Fit analysis: 2 items analyzed
INFO - Style analysis successful
```

## 🎯 Next Steps
After verifying Phase 5 works:
1. Test with different outfit types
2. Try different LLM providers
3. Adjust temperature for creative vs. consistent results
4. Consider database caching for repeated queries
5. Add user feedback collection
