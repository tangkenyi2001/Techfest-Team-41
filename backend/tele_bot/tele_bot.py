from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp
import base64
import os
from dotenv import load_dotenv
import logging
import sys

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
# Update contains info about incoming msg and context provides context for the callback
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  logger.info(f"User {update.effective_user.id} started a new session")
  await update.message.reply_text("Hello, I will tell you whether what you heard is fake news or not. Send me what you heard with /verify")
  
# reply on /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text("add /verify to the text you want to send")
  
# do on /clear
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear any stored conversation data for this user
    if context.user_data:
        context.user_data.clear()
        
    await update.message.reply_text("Chat context has been cleared.")

# reply with results on /verify {text}
async def verify_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # if message is preceeded with /verify
  if context.args:
    message = " ".join(context.args)
    
  # if message is replied to using /verify 
  elif update.message.reply_to_message:
    message = update.message.reply_to_message.text
  
  else:
    await update.message.reply_text("Provide text to verify")
    return
  
  # Show typing
  await context.bot.send_chat_action(
    chat_id=update.effective_chat.id, 
    action=ChatAction.TYPING
  )
  
  # Backend looks for List[str]
  messages = [message]
  
  try:
    async with aiohttp.ClientSession() as session:
      async with session.post("http://localhost:3000/tele", json=messages) as response:
        if response.status == 200:
          
          # Get results
          results = await response.json()
          
          # Reply user
          await update.message.reply_text(results['text'])
          
          # Process audio file
          if 'audio' in results and results["audio"]:
            # Decode base64 to binary
            audio_binary = base64.b64decode(results['audio'])
            
            # Write to file
            with open('results.mp3', 'wb') as f:
              f.write(audio_binary)
            
            # Send audio to user
            await context.bot.send_voice(
              chat_id=update.effective_chat.id,
              voice=open('results.mp3', 'rb')
            )

        else:
          await update.message.reply_text("Sorry, something went wrong")
          
  except Exception as e:
    await update.message.reply_text(f'Error connecting to server: {str(e)}')     
    
    
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
            sources_text = "\n- ".join(response_data['sources'])
            answer = f"Verdict: {response_data['verdict']} \n \nExplanation: {response_data['explanation']}\n \nSources: \n- {sources_text}"
            
            return answer
          
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
    
    logger.info(f"Received message from user {update.effective_user.id} in {message_type} chat")
    
    # Show typing while bot processes input
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )
    except Exception:
        pass
      
    if message_type in ["group", "supergroup"]:
      if BOT_USERNAME.lower() in message.lower():
        message = message.lower().replace(BOT_USERNAME.lower(), '').strip()
        response = await handle_response(message)    
        
      else:
        # Messages not directed to bot
        return
      
    else:
      # Private chat 
      response = await handle_response(message)
      
    # Reply user
    await update.message.reply_text(response)
        
  except Exception as e:
    logger.error(f"Error in handle_message: {str(e)}")
    try:
      await update.message.reply_text("Sorry, an error occurred while processing your message.")
    except:
      pass
    
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
  application.add_handler(CommandHandler("clear", clear))
  application.add_handler(CommandHandler("verify", verify_news))
  
  # Message handler
  application.add_handler(MessageHandler(filters.TEXT, handle_message))
  
  # Run bot until CTRL + C
  application.run_polling(allowed_updates=Update.ALL_TYPES)
  logger.info("Bot started, polling for messages")
  
if __name__ == '__main__':
  main()