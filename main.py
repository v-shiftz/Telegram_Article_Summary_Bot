import re
import newspaper #pip install newspaper3k
from newspaper import Article
from urllib.parse import urlparse 
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup #pip install python-telegram-bot == 13.15
from telegram.ext import CommandHandler, CallbackContext, Filters, MessageHandler, Updater, CallbackQueryHandler
from telegram.error import TelegramError
from openai import OpenAI #pip install openAI
import tldextract

# Set up your Telegram Bot token, replace the TOKEN portion.
TOKEN = 'ENTER YOUR TELEGRAMBOT TOKEN HERE'
updater = Updater(TOKEN)
dp = updater.dispatcher

latest_summary = ""
latest_title = ""
broadcasted = False


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me an article link, and I will provide summary of the article and give you options to broadcast to broadcast channels.')

#reminder to add yourself to this list as well
def getid(getid):
    id = str(getid)
    with open("admin.txt", 'r') as file:
        # Read existing channels from the file
        valid_users = [line.strip() for line in file.readlines()]

    if id in valid_users:
        return True
    else:
        return False


def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url)


def summarise_by_content(prompt):
    get_summary = ''
    client = OpenAI(
        #update to use your own api_key from openai
        api_key='ENTER YOUR OPENAI KEY HERE'
    )
    while not get_summary:
        response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}         
                    ],
                temperature=0.7,
                max_tokens=200,
                n=1,
                stop=None
            )
        get_summary = response.choices[0].message.content
        if "as an AI text-based assistant" in get_summary or "as an AI text-based model" in get_summary or "as an AI language model" in get_summary:
            get_summary = ''
        else:
            return get_summary
        

def summarise_by_url(prompt):
    get_summary = ''
    client = OpenAI(
        #update to use your own api_key from openai
        api_key='ENTER YOUR OPENAI KEY HERE'
    )
    while not get_summary:
        response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}                
                    ],
                temperature=0.7,
                max_tokens=200,
                n=1,
                stop=None
            )
        get_summary = response.choices[0].message.content
        if "as an AI text-based assistant" in get_summary or "as an AI text-based model" in get_summary or "as an AI language model" in get_summary:
            get_summary = ''
        else:
            break
    return get_summary


def send_to_channel(BROADCAST_ID, summary):
    try:
        updater.bot.send_message(chat_id=BROADCAST_ID, text=summary, parse_mode = 'HTML')
    except:
        updater.bot.message.reply_message("Bot has not been added to " + BROADCAST_ID + ". Please add the bot and make it an admin before trying again.")


def add_admin(update: Update, content: CallbackContext) -> None:
    user = str(update.message.chat.id)
    super_admin = {
        #the key is the telegram id, the value is your name
        "YOUR TELEGRAM ID":"YOUR NAME", "OTHER TRUSTER ID": "OTHER USERNAME"
    }
    if user not in super_admin:
        update.message.reply_text("You are not verified")
        return
    
    admin_id = update.message.text[10:].strip()
    if admin_id == "":
        update.message.reply_text("Nothing is entered. Please try again")
        return
    
    with open("admin.txt", 'r') as file:
        # Read existing admins from the file
        admin_list = [line.strip() for line in file.readlines()]

        # Check if admin already exists
        if admin_id in admin_list:
            update.mesage.reply_text("Admin already exists")
        else:
            # Add admin to the list
            admin_list.append(admin_id)

            # Write the updated admin list to file
            with open ('admin.txt', 'w') as file:
                for i, admin in enumerate(admin_list):
                        file.write(admin)
                        if i < len(admin_list) - 1:
                            file.write("\n")  # Add newline if it's not the last channel

                update.message.reply_text(f"Admin {admin_id} added.")


def remove_admin(update: Update, content: CallbackContext) -> None:
    user = str(update.message.chat.id)
    super_admin = {
        #the key is the telegram id, the value is your name
        "YOUR TELEGRAM ID":"YOUR NAME", "OTHER TRUSTER ID": "OTHER USERNAME"
    }
    if user not in super_admin:
        update.message.reply_text("You are not verified")
        return
    
    admin_remove = update.message.text[13:].strip()
    if admin_remove == "":
        update.message.reply_text("Nothing is entered. Please try again")
        return
    
    with open("admin.txt", 'r') as file:
        admin_list = [line.strip() for line in file.readlines()]
    if admin_remove in admin_list:
        admin_list.remove(admin_remove)
        with open("admin.txt", 'w') as file:
            for i, admin in enumerate(admin_list):
                file.write(admin)
                if i < len(admin_list) - 1:
                    file.write("\n")
        update.message.reply_text(f"Admin {admin_remove} removed.")
    else:
        update.message.reply_text(f"Admin {admin_remove} not found.")

    
def get_channel(update: Update, context:CallbackContext) -> None:
    if not getid(update.message.chat.id):
        update.message.reply_text("You are not verified")
        return
    
    with open("channel_id.txt", 'r') as file:
        channels = [line.strip() for line in file.readlines()]
        if not channels:
            update.message.reply_text("There is currently no channels ")
        else:
            update.message.reply_text(channels)


def add_channel(update: Update, context: CallbackContext) -> None:
    if not getid(update.message.chat.id):
        update.message.reply_text("You are not verified")
        return
    
    channel_id = update.message.text[12:].strip()
    add_id = "@"+channel_id
    with open("channel_id.txt", 'r') as file:
        # Read existing channels from the file
        stored_channels = [line.strip() for line in file.readlines()]

        # Check if the channel already exists
        if add_id in stored_channels:
            update.message.reply_text(f"Channel {channel_id} already exists.")
        else:
             # Add the channel to the list
            stored_channels.append(add_id)

            # Write the updated channels back to the file
            with open("channel_id.txt", 'w') as file:
                for i, channel in enumerate(stored_channels):
                    file.write(channel)
                    if i < len(stored_channels) - 1:
                        file.write("\n")  # Add newline if it's not the last channel

            update.message.reply_text(f"Channel {channel_id} added.")


def remove_channel(update: Update, context: CallbackContext) -> None:
    if not getid(update.message.chat.id):
        update.message.reply_text("You are not verified")
        return
    
    channel_id = update.message.text[15:].strip()
    remove_channel = "@"+channel_id 
    with open("channel_id.txt", 'r') as file:
        stored_channels = [line.strip() for line in file.readlines()]
    if remove_channel in stored_channels:
        stored_channels.remove(remove_channel)
        with open("channel_id.txt", 'w') as file:
            for i, channel in enumerate(stored_channels):
                file.write(channel)
                if i < len(stored_channels) - 1:
                    file.write("\n")
        update.message.reply_text(f"Channel {channel_id} removed.")
    else:
        update.message.reply_text(f"Channel {channel_id} not found.")


def channel_selection():
    with open("channel_id.txt", 'r') as file:
        lines = file.readlines()
        stored_channels = [line.strip() for line in lines]

    if not stored_channels:
        keyboard_1 = [[InlineKeyboardButton("No Channels added. Please add using /add_channel then send the link again.", callback_data='None')]]
        return InlineKeyboardMarkup(keyboard_1)
    keyboard = [
        [InlineKeyboardButton(channel, callback_data=f"{channel}")]
        for channel in stored_channels
    ]
    # Create the reply markup
    return InlineKeyboardMarkup(keyboard)


def button_callback(update: Update, context: CallbackContext) -> None:
    global latest_summary, latest_title, broadcasted

    query = update.callback_query
    query.answer()
    # Check the callback data
    if query.data == 'broadcast':
        if latest_summary and not broadcasted:
            query.edit_message_text(text=latest_summary, parse_mode="HTML",reply_markup=channel_selection())
        elif broadcasted:
            query.edit_message_text(text=latest_summary, parse_mode="HTML",reply_markup=broadcast_button())
        else:
            query.edit_message_text(text='No latest summary available.', reply_markup=broadcast_button())
    else:
        with open("channel_id.txt", 'r') as file:
            lines = file.readlines()
            stored_channels = [line.strip() for line in lines]
        if query.data in stored_channels:
            channel_id = query.data
            # Send the latest summary to the broadcast channel
            send_to_channel(channel_id,latest_summary)
            broadcasted = True
            query.edit_message_text(text=latest_summary, parse_mode="HTML",reply_markup=broadcast_button())


def broadcast_button():
    if not broadcasted:
        keyboard = [[InlineKeyboardButton("Broadcast Latest Summary", callback_data='broadcast')]]
    else:
        keyboard = [[InlineKeyboardButton("Article Broadcasted", callback_data='none')]]
    return InlineKeyboardMarkup(keyboard)


def handle_url_link(update: Update, context: CallbackContext) -> None:
    global latest_summary, latest_title, broadcasted
    
    #simple layer of security
    if not getid(update.message.chat.id):
        update.message.reply_text("You are not verified")
        return
    
    #check if there is channels added
    with open("channel_id.txt", 'r') as file:
        lines = file.readlines()
        stored_channels = [line.strip() for line in lines]
    if not stored_channels:
        update.message.reply_text('Channel list is empty, please add channels using the command: /add_channel.')
        return
    
    url = update.message.text
    # Validate the URL
    if not is_valid_url(url):
        update.message.reply_text('Invalid URL. Please provide a valid URL.')
        return
    
    # Parse the RSS feed
    # Extract text content from the URL using newspaper3k
    article = Article(url)
    article.download()
    article.parse()
    content = article.text
    title = article.title

    domain_info = tldextract.extract(url)
    website_name = domain_info.domain.capitalize()

    # Generate summaries using ChatGPT
    prompt = f"Summarize the content from this Content: {content}, please include the autor if there is any, if not don't mention it. Keep the summary short and sweet."
    if len(prompt)/4 > 4097:
        prompt = f"Summarize the content from this Url: {url}, please include the autor if there is any, if not don't mention it. Keep the summary short and sweet."
        summary = summarise_by_url(prompt)
    else:
        summary = summarise_by_content(prompt)

    latest_title = f"<b>{title}</b>"
    latest_summary= f"<b>{title}</b>"+"\n\n<b>Summary</b>:\n"+summary+"\n\nSummary genereated by ChatGPT, based on the information provided about an article from "f"<a href='{url}'>{website_name}</a>"
    broadcasted = False
    update.message.reply_text(f"<b>{title}</b>"+"\n\n<b>Summary</b>:\n"+summary+"\n\nSummary genereated by ChatGPT, based on the information provided about an article from "f"<a href='{url}'>{website_name}</a>",parse_mode="HTML", reply_markup=broadcast_button())


def error(update: Update, context):
    update.message.reply_text("An error has occured.")
    print('Update "%s" caused error "%s"',update,context.error)


def main():
    # Add handlers to the updater
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_url_link))
    dp.add_handler(CallbackQueryHandler(button_callback))
    dp.add_handler(CommandHandler("add_channel", add_channel))
    dp.add_handler(CommandHandler("remove_channel", remove_channel))
    dp.add_handler(CommandHandler("add_admin", add_admin))
    dp.add_handler(CommandHandler("remove_admin", remove_admin))
    dp.add_handler(CommandHandler("get_channel", get_channel))
    dp.add_error_handler(error)
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()