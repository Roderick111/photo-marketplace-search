## FEATURE:

Build a web application that converts photos into marketplace search links. The workflow:

1. **Image Upload**: User uploads a photo (book, clothing, electronics, etc.) via web interface
2. **Object Detection & Analysis**: Use Claude Vision API to:
   - Identify what object is in the photo
   - Determine the object type/category (book, clothing, electronics, etc.)
   - Generate 1-3 descriptive search queries for the object
3. **Smart Marketplace Routing**: Based on object type, search in appropriate marketplaces:
   - Books → Abebooks.fr
   - Clothing/Fashion → Vinted
   - Everything else (electronics, tools, etc.) → Leboncoin
4. **Results Display**: Show a list of clickable marketplace search links for the user to browse

**Tech Stack Preferences**:
- FastAPI or Streamlit for the web framework (choose the simpler option)
- Claude Vision API (Anthropic) for image analysis
- Pydantic for data validation and structured outputs
- Beautiful Soup or Playwright for any web scraping if needed
- Python 3.10+

**Key Requirements**:
- Single-page interface with drag-and-drop or button upload
- Fast response time (< 5 seconds from upload to links)
- Support common image formats (JPG, PNG, JPEG, WebP)
- Generate 3-5 marketplace search URLs as output
- Clean, minimal UI - focus on functionality over design

## EXAMPLES:

### 1. FastAPI + Vision API Product Detection (Pydantic)
**Source**: [Building a product search API with GPT-4 Vision, Pydantic, and FastAPI](https://pydantic.dev/articles/llm-vision)

This example shows how to:
- Create FastAPI endpoint that receives image URLs
- Use vision API to extract product information
- Structure outputs with Pydantic models
- Validate and parse JSON responses from vision models

**Key patterns to follow**:
- Using `model_json_schema()` to embed validation rules in prompts
- Async endpoint design for vision API calls
- Pydantic models for request/response validation

### 2. FastAPI File Upload Handler
**Source**: [FastAPI Request Files Documentation](https://fastapi.tiangolo.com/tutorial/request-files/)

Simple example for handling image uploads:
```python
from fastapi import FastAPI, File, UploadFile
import aiofiles

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    # Read and process uploaded file
    contents = await file.read()
    # Process image with vision API
    return {"filename": file.filename}
```

**Key patterns**:
- Use `UploadFile` for efficient large file handling
- Install `python-multipart` for form data support
- Async file operations with `aiofiles`

### 3. E-commerce Web Scraper
**Source**: [GitHub - lastuchiha/ecommerce-scraper](https://github.com/lastuchiha/ecommerce-scraper)

Shows how to extract product information from marketplace websites using Beautiful Soup:
- Batch URL processing from text files
- Product name, price, and rating extraction
- Modular design for different marketplace platforms

**Useful for**: Understanding how to construct marketplace search URLs and potentially scrape results

### 4. Streamlit Image Upload Alternative
**Source**: [GitHub - jw782cn/Claude-Streamlit](https://github.com/jw782cn/Claude-Streamlit)

If FastAPI feels too complex, this shows a simpler Streamlit approach:
- Simple file uploader with `st.file_uploader()`
- Direct Claude API integration
- Minimal code for rapid prototyping

## DOCUMENTATION:

### Claude Vision API
- **Official Docs**: [Claude Vision Documentation](https://docs.claude.com/en/docs/build-with-claude/vision)
- **Key info**: Three methods for image input (Files API, base64, URL)
- **Best model**: Claude 3.5 Sonnet for vision tasks
- **Image formats**: PNG, JPEG, WebP, GIF (non-animated)
- **Important**: Use beta header `anthropic-beta: files-api-2025-04-14` for Files API

### FastAPI & File Handling
- **File Upload Guide**: [FastAPI Request Files](https://fastapi.tiangolo.com/tutorial/request-files/)
- **Complete File Handling**: [Uploading Files Using FastAPI](https://betterstack.com/community/guides/scaling-python/uploading-files-using-fastapi/)
- **UploadFile Reference**: [FastAPI UploadFile Class](https://fastapi.tiangolo.com/reference/uploadfile/)

### Pydantic
- **Official Docs**: [Pydantic Documentation](https://docs.pydantic.dev/)
- **Use for**: Structured outputs from Claude, request/response validation

### Web Scraping (if needed)
- **Beautiful Soup**: [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- **Playwright**: [Playwright Python](https://playwright.dev/python/) - for dynamic content

### Marketplace URLs
- **Abebooks.fr**: `https://www.abebooks.fr/servlet/SearchResults?kn={query}&sts=t`
- **Vinted**: `https://www.vinted.fr/catalog?search_text={query}`
- **Leboncoin**: `https://www.leboncoin.fr/recherche?text={query}`

## OTHER CONSIDERATIONS:

### Common Gotchas

1. **Claude API Image Format**:
   - Images must be base64-encoded or uploaded via Files API
   - Don't forget the `anthropic-beta` header for Files API
   - Max image size considerations

2. **Vision Prompt Engineering**:
   - Be very specific in system prompts about output format
   - Request JSON output explicitly
   - Include the Pydantic schema in the system prompt for structured outputs
   - Use prefill technique (`"role": "assistant", "content": "```json"`) to encourage proper formatting

3. **Marketplace Search URLs**:
   - URL-encode search queries (use `urllib.parse.quote()`)
   - Test that generated URLs actually work in browsers
   - Some marketplaces have rate limiting - be respectful

4. **File Upload Security**:
   - Validate file types (only allow images)
   - Set max file size limits (e.g., 10MB)
   - Don't trust user-provided filenames
   - Clean up uploaded files after processing

5. **Error Handling**:
   - What if Claude can't identify the object? (provide fallback)
   - What if image is too blurry/unclear? (give user feedback)
   - Handle API rate limits and failures gracefully

6. **Response Time**:
   - Vision API calls can take 2-5 seconds
   - Consider adding loading indicator in UI
   - Maybe cache results for same image hash

7. **Object Type Classification**:
   - Define clear categories in prompt (book, clothing, electronics, furniture, tools, etc.)
   - Have a "general" fallback category that goes to Leboncoin
   - Consider edge cases (what if photo contains multiple objects?)

8. **Dependencies**:
   - `anthropic` - Claude API client
   - `fastapi` or `streamlit` - web framework
   - `python-multipart` - for FastAPI file uploads
   - `pydantic` - data validation
   - `aiofiles` - async file operations
   - `pillow` - image processing if needed

9. **Environment Variables**:
   - Store `ANTHROPIC_API_KEY` in `.env` file
   - Use `python-dotenv` to load env vars
   - Never commit API keys to git
   
Important: use Serena and Context7 MCPs for better performance and reliability.
