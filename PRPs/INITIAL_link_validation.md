## FEATURE:

let's add a check for likns found before provideing them: if there is nothing found from this link, no need to provide the it

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

   
Important: use Serena and Context7 MCPs for better performance and reliability.
