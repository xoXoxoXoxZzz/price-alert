from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import logging , requests , time , threading , os


#log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot token
TOKEN = os.getenv("TELEGRAM_TOKEN")
#some magic here
application = ApplicationBuilder().token(TOKEN).build()

# TELEGRAM HANDLER FUNCTIONS
#when user sends /strat
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btcpricenow = get_bitcoin_price()
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"Hi! Send me \n /usd for current USD/IRR \n /btc for current BTC/USD \n /settarget e.g /settarget > 60000 \n or /settarget < 30000 for btc price notification  "
    )

#for btc command price check 
async def btc(update , context ):
     btc_price_now = get_bitcoin_price()
     await update.message.reply_text(f"BTC price is {btc_price_now} USD")

#usd to irr price check by bacheha
async def get_dollar_price(update: Update , context):
    r = requests.post('https://www.bonbast.com/converter')  
    if r.status_code == 200 :
        resp = r.json()
        dollar = int(float(resp["IRR"]) * 1.303189846)
        await update.message.reply_text(f"Dollar price is {dollar} IRR")

# Function to handle the target price and filter input
async def settarget(update):

    try:
        target_and_filter = update.message.text.split()
        target_symbol = target_and_filter[1]
        target_price = float(target_and_filter[2])
        chat_id = update.message.chat_id
        await update.message.reply_text(f"Target price set to {target_symbol} ${target_price}.\nI will notify you accordingly.")

       # Start the check_btc_price thread
        check_btc_price_thread = threading.Thread(target=check_btc_price, args=[target_price, target_symbol, chat_id])
        check_btc_price_thread.start()
    
    except ValueError:
        await update.message.reply_text("Invalid input. Please provide the target price (in USD) and optionally a filter (e.g., /settarget > 50000 or /settarget < 45000).")

#HELPER FUNCTIONS
#BTC price check api 
def get_bitcoin_price():
    url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    response = requests.get(url)
    data = response.json()
    
    usd_rate_float = data['bpi']['USD']['rate_float']
    
    return usd_rate_float

#check bitcoin price every 60 secs thread module
def check_btc_price(target_price, target_symbol , chat_id):
    
    while True:
        
        btc_price = get_bitcoin_price()
        if target_price and (target_symbol == ">" and btc_price > target_price or target_symbol == "<" and btc_price < target_price):
            message = f"BTC price is {btc_price} \n YOUR TARGET HAS REACHED."
            url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
            data = {'chat_id': chat_id, 'text': message}
            requests.post(url, data=data)
            break

        time.sleep(60)  

#listen to /start commands
start_handler = CommandHandler('start', start)
application.add_handler(start_handler)

#listen to /settarget command
target_handler = CommandHandler("settarget" , settarget)
application.add_handler(target_handler)

#listen to /usd command
dollar_handler = CommandHandler("usd" , get_dollar_price)
application.add_handler(dollar_handler)

#Listen to /btc command
btc_handler = CommandHandler("btc" , btc)
application.add_handler(btc_handler)

#keep it running
application.run_polling()