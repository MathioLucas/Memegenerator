from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import shutil
import uuid

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/processed", StaticFiles(directory="processed"), name="processed")

# Directories for uploaded and processed images
UPLOAD_DIRECTORY = Path("uploads")
PROCESSED_DIRECTORY = Path("processed")
UPLOAD_DIRECTORY.mkdir(exist_ok=True)
PROCESSED_DIRECTORY.mkdir(exist_ok=True)

# Homepage route 
@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    with open("index.html", "r", encoding='utf-8') as f:
        return HTMLResponse(content=f.read())

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), caption: str = Form(...)):
    # Print out the caption to check its actual content
    print(f"Received caption: {repr(caption)}")
    
    # Generate unique filename to prevent overwriting
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_location = UPLOAD_DIRECTORY / unique_filename
    
    # Save uploaded file
    with file_location.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Process the image
        with Image.open(file_location) as image:
            # Create a copy of the image to draw on
            meme_image = image.copy()
            draw = ImageDraw.Draw(meme_image)
            
            # Try to use a Unicode-compatible font that supports multiple languages
            try:
                # Use a system font that should support English characters
                font = ImageFont.truetype("static/fonts/NotoSans-Bold.ttf", 80)
  
            except IOError:
                # Fallback to default if no custom font
                font = ImageFont.load_default()
            
            width, height = meme_image.size
            
            # Calculate text size
            bbox = draw.textbbox((0, 0), caption, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center the text horizontally
            x = (width - text_width) / 2
            
            # Position text near the bottom with some padding
            y = height - text_height - 50
            
            # Add text with a thick black outline for visibility
            outline_width = 3
            outline_color = "black"
            text_color = "white"
            
            # Draw text outline (8-direction)
            for dx in [-outline_width, 0, outline_width]:
                for dy in [-outline_width, 0, outline_width]:
                    draw.text((x+dx, y+dy), caption, font=font, fill=outline_color)
            
            # Draw main text
            draw.text((x, y), caption, font=font, fill=text_color)
            
            # Save processed image
            processed_image_path = PROCESSED_DIRECTORY / f"processed_{unique_filename}"
            meme_image.save(processed_image_path)
        
        processed_image_url = f"/processed/{processed_image_path.name}"
        return HTMLResponse(content=f"""
            <h2>Here is your meme!</h2>
            <img src="{processed_image_url}" alt="Meme" id="processedMeme" style="max-width: 100%;"><br><br>
            <a href="{processed_image_url}" download>Download Meme</a>
        """, status_code=200)
    
    except Exception as e:
        # Print full error for debugging
        import traceback
        traceback.print_exc()
        return HTMLResponse(content=f"Error processing image: {str(e)}", status_code=500)

# Optional: Route for serving processed images directly
@app.get("/processed/{filename}")
async def serve_processed_image(filename: str):
    return FileResponse(PROCESSED_DIRECTORY / filename)

# To run the application directly (optional)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)