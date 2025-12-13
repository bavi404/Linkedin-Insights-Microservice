# AI Summary Service

Optional AI-powered summary service for LinkedIn pages using OpenAI API.

## Features

- ✅ Generates concise summaries covering:
  - **Page Type**: Enterprise, Startup, Agency, Non-Profit, etc.
  - **Audience**: Size and characteristics
  - **Engagement**: Level and activity patterns
- ✅ Gracefully degrades if OpenAI is not configured
- ✅ Isolated service that doesn't affect core functionality
- ✅ Environment variable configuration

## Setup

### 1. Install OpenAI Package

```bash
pip install openai
```

### 2. Set Environment Variable

Add to your `.env` file:

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo  # Optional, default: gpt-3.5-turbo
OPENAI_MAX_TOKENS=300       # Optional, default: 300
```

### 3. Get OpenAI API Key

1. Sign up at https://platform.openai.com/
2. Create an API key
3. Add it to your `.env` file

## Usage

### Via Service

```python
from linkedin_insights.services.linkedin_page_service import LinkedInPageService
from sqlalchemy.orm import Session

service = LinkedInPageService(db_session)
summary = service.generate_ai_summary("acme-corp")

if summary:
    print(summary["summary"])
    print(f"Page Type: {summary['page_type']}")
    print(f"Audience: {summary['audience']}")
    print(f"Engagement: {summary['engagement']}")
else:
    print("AI Summary Service is not available")
```

### Via API Endpoint

#### Get Summary for Existing Page

```bash
GET /api/v1/pages/{page_id}/summary
```

**Example:**
```bash
curl http://localhost:8000/api/v1/pages/acme-corp/summary
```

**Response:**
```json
{
    "summary": "Acme Corporation is a large enterprise technology company with a substantial following of 50,000+ professionals. The company demonstrates strong engagement with an average of 1,250 likes and 89 comments per post, indicating an active and responsive audience primarily in the technology sector.",
    "page_type": "Enterprise",
    "audience": "Large",
    "engagement": "High",
    "generated_at": "2024-01-15T12:00:00Z"
}
```

#### Generate Summary from Stats

```bash
POST /api/v1/summary/generate
Content-Type: application/json

{
    "name": "Tech Startup Inc",
    "industry": "Technology",
    "total_followers": 5000,
    "head_count": 50,
    "description": "Innovative startup",
    "total_posts": 20,
    "avg_likes": 150,
    "avg_comments": 25,
    "engagement_rate": 3.5
}
```

## Service Behavior

### When Enabled

- Service is fully functional
- Generates AI summaries on request
- Returns structured summaries with extracted metadata

### When Disabled

- Service gracefully degrades
- Returns `None` instead of raising errors
- Core application continues to work normally
- No OpenAI calls are made

## Error Handling

The service handles errors gracefully:

- **Missing API Key**: Service is disabled, returns `None`
- **OpenAI API Error**: Logs error, returns `None`
- **Invalid Response**: Logs error, returns `None`

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes* | None | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-3.5-turbo` | OpenAI model to use |
| `OPENAI_MAX_TOKENS` | No | `300` | Maximum tokens for response |

*Required only if you want to use the AI summary feature

## Response Format

```python
{
    "summary": "Generated summary text...",
    "page_type": "Enterprise",  # or "Startup", "Agency", "Non-Profit", "Business"
    "audience": "Large",        # or "Growing", "Niche", "Moderate"
    "engagement": "High",       # or "Moderate", "Low"
    "generated_at": "2024-01-15T12:00:00Z"
}
```

## Cost Considerations

- Uses OpenAI API which charges per token
- Default model: `gpt-3.5-turbo` (cost-effective)
- Default max tokens: 300 (keeps costs low)
- Each summary request consumes API credits

## Best Practices

1. **Cache Summaries**: Don't regenerate summaries for the same page frequently
2. **Monitor Usage**: Track API usage to control costs
3. **Error Handling**: Always check if summary is `None` before using
4. **Optional Feature**: Design your application to work without AI summaries

## Example Integration

```python
from linkedin_insights.services.linkedin_page_service import LinkedInPageService

def get_page_with_summary(page_id: str, db: Session):
    service = LinkedInPageService(db)
    
    # Get page data
    page = service.get_page_by_page_id(page_id)
    
    # Try to get AI summary (optional)
    summary = service.generate_ai_summary(page_id)
    
    return {
        "page": page,
        "ai_summary": summary  # None if service is disabled
    }
```

## Testing

The service can be tested with mocked OpenAI client:

```python
from unittest.mock import patch, MagicMock

@patch('linkedin_insights.services.ai_summary_service.OpenAI')
def test_ai_summary(mock_openai):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value.choices[0].message.content = "Test summary"
    mock_openai.return_value = mock_client
    
    service = AISummaryService()
    summary = service.generate_summary({"name": "Test Company"})
    
    assert summary is not None
```

