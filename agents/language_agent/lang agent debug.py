import google.generativeai as genai
import time

# This must be your Gemini API key from https://makersuite.google.com/app/apikey
genai.configure(api_key=r"AIzaSyAYHaKWloNVe4uUtHzjyZZXi8E9eFVA8R4")

# Using a model generally available in the free tier for text tasks.
# 'models/gemini-1.0-pro' is a good choice for general text generation and summarization.
# If 'models/gemini-1.0-pro' is not directly listed or gives errors,
# you could try 'models/gemini-1.5-flash' or 'models/gemini-1.5-flash-latest' from your list.
model_name = 'models/gemini-1.5-flash'

max_retries = 3
retry_delay_seconds = 60 # Start with a 60-second delay for quota errors

for attempt in range(max_retries):
    try:
        model = genai.GenerativeModel(model_name)

        # Craft a clear and specific prompt for better results
        # Note: Free tier models might have older knowledge cutoffs.
        # For "today's" news, they might not have real-time data unless connected to external tools.
        # However, they can summarize based on their training data.
        prompt = "Summarize the latest trends and performance of major Asia tech stocks, including key players like TSMC (Taiwan Semiconductor Manufacturing Company) and Samsung (Samsung Electronics)."

        print(f"Attempt {attempt + 1} using model: {model_name}")
        print(f"Prompt: {prompt}")

        response = model.generate_content(prompt)

        # Check if response.text is available and not empty
        if response.text:
            print("\n--- Summary ---")
            print(response.text)
            break # Exit loop on successful response
        else:
            print(f"Attempt {attempt + 1} received an empty response. Retrying...")

    except genai.types.BlockedPromptException as e:
        print(f"The prompt was blocked: {e}. Please revise your prompt.")
        break # No point in retrying if prompt is blocked
    except genai.types.InvalidAPIKeyException as e:
        print(f"Invalid API Key: {e}. Please check your API key.")
        break # API key issue, no point in retrying
    except Exception as e:
        error_message = str(e).lower()
        if "429 quota exceeded" in error_message or "quota" in error_message or "resourceexhausted" in error_message:
            print(f"Quota or free tier limit exceeded on attempt {attempt + 1}. Error: {e}")
            if attempt < max_retries - 1:
                print(f"Waiting for {retry_delay_seconds} seconds before retrying...")
                time.sleep(retry_delay_seconds)
                # For free tier, consistent 429s might mean you're making requests too frequently
                # or have hit daily limits. Increasing retry_delay_seconds might be needed.
            else:
                print("Max retries reached for quota/free tier error. You might be hitting free tier limits or need to enable billing for higher usage.")
        else:
            print(f"An unexpected error occurred on attempt {attempt + 1}: {e}")

        if attempt == max_retries - 1: # If it's the last attempt and still failed
            print("Failed after multiple attempts.")