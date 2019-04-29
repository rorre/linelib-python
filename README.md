# linelib
Another line-bot-sdk wrapper for python, to make some people's life easier.

# Getting Started
## Basic bot
```py
import line
from flask import Flask, request, abort

app = Flask(__name__)
bot = line.LineSDK("Channel access token",
                   "Channel secret")

@bot.on_command("echo")
def echo(ctx, *args):
    ctx.reply(' '.join(args))

@bot.on_command("ping")
def ping(ctx, *):
    ctx.reply("Pong!")

@app.route("/callback", methods=['POST'])
def callback():
    return bot.handle(request)

app.run()
```

will add more stuffs soon(tm) i guess lol