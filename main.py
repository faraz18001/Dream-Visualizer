from openai import OpenAI
import os

# Make sure you've set up your API key in the .env file first
client = OpenAI()

try:
    # Generate the image
    response = client.images.generate(
        model="dall-e-3",
        prompt="A cute baby sea otter",
        n=1,
        size="1024x1024"
    )

    # Get the image URL from the response
    image_url = response.data[0].url

    # Download the image
    import requests

    # Download the image
    image_response = requests.get(image_url)
    
    # Ensure the downloads directory exists
    os.makedirs("downloads", exist_ok=True)

    # Save the image
    with open("downloads/sea_otter.png", "wb") as f:
        f.write(image_response.content)

    print("Image has been saved successfully!")

except Exception as e:
    print(f"An error occurred: {e}")
