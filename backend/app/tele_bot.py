from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp
from io import BytesIO
import os
from dotenv import load_dotenv
import logging
import sys
from jigsawstack import JigsawStack
import base64

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    handlers=[
        logging.FileHandler("telegram_bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.INFO)

logger = logging.getLogger(__name__)


load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "http://localhost:8000/rag"
BOT_USERNAME = "@FakeOrNotBot"

# Command Handlers

# reply on /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  logger.info(f"User {update.effective_user.id} started a new session")
  await update.message.reply_text("Hello, are you sure if a news you heard is real or not. Send it to me and I will check for you.")
  
# reply on /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  message_type = update.message.chat.type
  
  if message_type == ["group", "supergroup"]:
    return await update.message.reply_text("Tag me in the message with the news and I will check for you")
  else:
    return await update.message.reply_text("Send me the message and I check for you")

# generate audio playback of response
def get_TTS_file(text):
  # voice for tts
  voice = "en-SG-female-1"
  
  try:
    # Get TTS from api
    jigsawstack = JigsawStack(api_key=os.getenv("JIGSAWSTACK_API_KEY"))
    response = jigsawstack.audio.text_to_speech({
      "text": text,
      "accent": voice
    })
    
  except Exception as e:
    print(f"Error generating Speech from API: {str(e)}")
    return None
  
  audio_binary = response.content
  
  # Encode binary audio as base64
  audio_base64 = base64.b64encode(audio_binary).decode('utf-8')
  
  return audio_base64
  
async def handle_response(message: str):
  
  logger.info(f"Received message to send: {message}")
  
  try:
    request = {
      "message": message
    }
    
    logger.info(f"Sending request: {request}")
    
    async with aiohttp.ClientSession() as session:
      try:
        async with session.post(API_URL, json=request) as response:
          if response.status == 200:
            response_data = await response.json()
            
            # Format reply
            sources_text = "\n- ".join(response_data['sources'])
            answer = f"Verdict: {response_data['verdict']} \n \nExplanation: {response_data['explanation']}\n \nSources: \n- {sources_text}"
            
            # Generate audio reply
            audio_b64 = get_TTS_file(response_data['explanation'])
            
            # Decode audio into file
            audio_binary = base64.b64decode(audio_b64)
            with open('results.mp3', 'wb') as f:
              f.write(audio_binary)
              
            audio_filepath = 'results.mp3'
            
            return answer, audio_filepath
          
          else:
            return f"Error: Received Status Code {response.status}"
      
      except aiohttp.ClientError as e:
        return f"Sorry, I couldn't connect to the API."
          
  except Exception as e:
    return f"Sorry, an error occurred. Please try again later."
    

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    if not update.message or not update.message.text:
      return

    message_type = update.message.chat.type
    message = update.message.text
    
      
    if message_type in ["group", "supergroup"]:
      if BOT_USERNAME.lower() in message.lower():
        message = message.lower().replace(BOT_USERNAME.lower(), '').strip()
        response, audio_filepath = await handle_response(message)    
        
      else:
        # Messages not directed to bot
        return
      
    else:
      # Private chat 
      response, audio_filepath = await handle_response(message)
      
    logger.info(f"Received message from user {update.effective_user.id} in {message_type} chat")
      
    # Show typing while bot processes input
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )
    except Exception:
        pass
      
    # Reply user
    await update.message.reply_text(response)
    await context.bot.send_voice(
      chat_id=update.effective_chat.id,
      voice=open(audio_filepath, 'rb')
    )
    
        
  except Exception as e:
    logger.error(f"Error in handle_message: {str(e)}")
    try:
      await update.message.reply_text("Sorry, an error occurred while processing your message.")
    except:
      pass
    

async def handle_photo(update:Update, context:ContextTypes.DEFAULT_TYPE):
  logger.info("Processing photo")
  photo = update.message.photo[-1]
  file_id = photo.file_id
  
  file_info = await context.bot.get_file(file_id)
  photo_bytes = BytesIO()
  await file_info.download_to_memory(photo_bytes)
  photo_bytes.seek(0)
  
  try:
    async with aiohttp.ClientSession() as session:
      url = "http://localhost:8000/image"
      
      form = aiohttp.FormData()
      form.add_field('file',
                     photo_bytes,
                     filename='photo_from_bot.jpg',
                     content_type='image/jpeg')
      
      logger.info("Sending file to API")
      async with session.post(url, data=form) as response:
        if response.status == 200:
          json_response = await response.json()
          ai_score = str(json_response["type"]["ai_generated"])
          await update.message.reply_text(f"AI generated score: {ai_score}")

        else:
          error_text = await response.text()
          await update.message.reply_text(f"API error: {response.status} - {error_text}")
          
  except Exception as e:
    await update.message.reply_text(f"Error: {str(e)}")
    
async def error_handler(update, context):
  """Log errors caused by updates."""
  
  logger.error(f"Update caused error: {context.error}")
  if update and update.effective_message:
      await update.effective_message.reply_text("An error occurred while processing your request.")

# Run bot
def main():
  logger.info("Starting telegram bot")
  
  # Create application and give token
  application = Application.builder().token(TOKEN).build()
  
  # Register error handler
  application.add_error_handler(error_handler)
  
  # Add commands
  application.add_handler(CommandHandler("start", start))
  application.add_handler(CommandHandler("help", help_command))
  
  # Message handler
  application.add_handler(MessageHandler(filters.TEXT, handle_message))
  
  # Photo handler
  application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
  
  # Run bot until CTRL + C
  application.run_polling(allowed_updates=Update.ALL_TYPES)
  logger.info("Bot started, polling for messages")
  
if __name__ == '__main__':
  main()
    