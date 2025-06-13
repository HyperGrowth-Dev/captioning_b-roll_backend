import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# List of required environment variables
required_vars = [
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_REGION',
    'S3_BUCKET_NAME',
    'OPENAI_API_KEY',
    'PEXELS_API_KEY'
]

# Test each variable
print("Testing environment variables...")
print("-" * 50)

all_present = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Show first 4 characters of the value for security
        masked_value = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
        print(f"✓ {var}: {masked_value}")
    else:
        print(f"✗ {var}: Not found")
        all_present = False

print("-" * 50)
if all_present:
    print("All environment variables are loaded correctly!")
else:
    print("Some environment variables are missing. Please check your .env file.")
