# Telegram_Article_Summary_Bot
This python telegram bot receives article URLs and utilizes openAI to generate the summary of the article before giving option to send the summary into a broadcast channel.
Before the bot broadcast in a channel, make sure to add the bot into the broadcast channel and give it admin rights. If not the broadcast function will not work.
OpenAI is abit finicky about summarising URL and may take a few attempts for it to send a proper summary. Summary by url will only run if the content of the article is too long for openAI's input.
