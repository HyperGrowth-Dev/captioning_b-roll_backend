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

PYTHONPATH=$PYTHONPATH:. uvicorn backend.api:app --reload

## Remotion Lambda Setup and Usage

1. After making any changes to the Remotion components, redeploy the site:
```bash
cd remotion
npx remotion lambda functions deploy
npx remotion lambda sites create src/index.ts --site-name=caption-video
```
n
2. To render a video using Remotion Lambda:
```bash
npx remotion lambda render https://remotionlambda-useast2-bvf5c7h3eb.s3.us-east-2.amazonaws.com/sites/caption-video/index.html CaptionVideo
```

Note: The serve URL will be provided after running the `sites create` command. Make sure to use the URL from your deployment.

Important considerations:
- Always redeploy the site after making changes to any Remotion components
- The serve URL is specific to your AWS deployment
- You can add additional render options like `--concurrency` and `--frames-per-lambda` to optimize rendering

## EC2 Instance
when changes are made, go to download folder and ssh into ec2 instance
```bash
ssh -i "hyper-key.pem" ubuntu@ec2-18-224-63-78.us-east-2.compute.amazonaws.com
```
Then, go to application:
```bash
cd /var/www/vid_editor/
```
Pull changes from Github and merge them
```bash
git checkout main
git fetch origin
git checkout ec2
git merge origin/[branchname]
```
fix merge issues then use git add and commit


Next, to actually push the changes to the website:
if changes were made on front end, first run the build:
```bash 
cd frontend
npm run build
```
then run this:
```bash
sudo systemctl daemon-reload
sudo systemctl restart vid_editor
sudo journalctl -u vid_editor -f
```
