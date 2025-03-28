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