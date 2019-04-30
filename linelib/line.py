from flask import abort
from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import *
import shlex

class MissingArgument(Exception):
    pass

class Context():
    def __init__(self, event, api):
        self.event = event
        self.api = api
    
    def reply(self, message: str = "", imgurl: str = "", vidurl: str = "", previewurl: str = "",
              audiourl: str = "", duration: int = 0, location: LocationSendMessage = None,
              imagemap: ImagemapSendMessage = None, template: TemplateSendMessage = None):
        if message:
            msg = TextSendMessage(text=message)
        elif imgurl:
            msg = ImageSendMessage(
                original_content_url=imgurl,
                preview_image_url=imgurl if not previewurl else previewurl
            )
        elif vidurl:
            if not previewurl:
                raise MissingArgument("previewurl")
            msg = VideoSendMessage(
                original_content_url=vidurl,
                preview_image_url=previewurl
            )
        elif audiourl:
            if not duration:
                raise MissingArgument("duration")
            msg = AudioSendMessage(
                original_content_url=audiourl,
                duration=duration
            )
        elif location:
            msg = location
        elif imagemap:
            msg = imagemap
        elif template:
            msg = template
        else:
            raise MissingArgument("Needs at least 1 argument")
        self.api.reply_message(self.event.reply_token, msg)

class LineSDK():

    def __init__(self, access_token: str, channel_secret: str, prefix: str = "!"):
        self.lineapi = LineBotApi(access_token)
        self.handler = WebhookHandler(channel_secret)
        self.prefix = prefix
        self.commands = {}
        self._pre_start()

    def handle(self, request) -> str :
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)
        
        try:
            self.handler.handle(body, signature)
        except InvalidSignatureError:
            print("Invalid signature. Please check your channel access token/channel secret.")
            abort(400)
        return "OK"
    
    def on_command(self, cmd):
        command = f"{self.prefix}{cmd}"
        def decorate(function):
            self.commands[command] = function
        return decorate

    def parse_command(self, ctx, cmd, *args) -> bool :
        if cmd in self.commands:
            self.commands[cmd](ctx, *args)
            return True
        return False

    def on_message(self, event):
        ctx = Context(event, self.lineapi)
        splitted = shlex.split(event.message.text)
        self.parse_command(ctx, *splitted)
        return
    
    def on_follow(self, event):
        pass
    
    def on_unfollow(self, event):
        pass
    
    def on_join(self, event):
        pass
    
    def on_leave(self, event):
        pass

    def _pre_start(self):
        @self.handler.add(MessageEvent, message=TextMessage)
        def on_message(event):
            self.on_message(event)
        
        @self.handler.add(FollowEvent)
        def on_follow(event):
            self.on_follow(event)
        
        @self.handler.add(UnfollowEvent)
        def on_unfollow(event):
            self.on_unfollow(event)
        
        @self.handler.add(JoinEvent)
        def on_join(event):
            self.on_join(event)
        
        @self.handler.add(LeaveEvent)
        def on_leave(event):
            self.on_leave(event)
    
    