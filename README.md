# AI Video Caption and Image Generator

This application processes videos by:
1. Extracting audio and generating captions using speech recognition
2. Generating AI images based on the content of the speech
3. Overlaying both captions and images onto the video

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
```

3. Place your input video in the `input` directory

4. Run the application:
```bash
python main.py
```

## Requirements
- Python 3.8+
- OpenAI API key for image generation
- FFmpeg installed on your system

## Directory Structure
- `input/`: Place your input videos here
- `output/`: Generated videos will be saved here
- `temp/`: Temporary files during processing 

## Possible Fonts

"DancingScript-SemiBold" - Semi-bold weight of Dancing Script
"Barlow-Bold" - Bold weight of Barlow
"Barlow-BlackItalic" - Black weight with italic style of Barlow
"Oswald-Regular" - Regular weight of Oswald
"Oswald-SemiBold" - Semi-bold weight of Oswald
"Montserrat-Bold" - Bold weight of Montserrat
"Montserrat-SemiBoldItalic" - Semi-bold weight with italic style of Montserrat

## Example Api Calls

data = {
    "font": "Montserrat-Bold",
    "color": "yellow",
    "font_size": 48
}

# Using hex color
data = {
    "font": "Montserrat-Bold",
    "color": "#FF4500",  # Orange-red
    "font_size": 48
}

# Using RGB
data = {
    "font": "Montserrat-Bold",
    "color": "rgb(106, 155, 51)",  # Orange-red
    "font_size": 44
}