from discord import Message

'''
    Super class for all our message reply triggers
'''
class ReplyTrigger:
    def __init__(self, triggers: list[str], exceptTriggers: list[str] = []):
        self.triggers = tuple(map(lambda s: s.lower(), triggers))
        self.exceptTriggers = tuple(map(lambda s: s.lower(), exceptTriggers))

    def isTriggered(self, messageContent: str) -> bool:
        messageContent = messageContent.lower().strip()

        for trigger in self.exceptTriggers:
            if (trigger in messageContent):
                return False

        for trigger in self.triggers:
            if (trigger in messageContent):
                return True
        return False
    
    async def doReply(self, message: Message):
        pass

'''
    Replies with only an imageUrl (discord will just display the image)
'''
class ImageReplyTrigger(ReplyTrigger):
    def __init__(self, triggers: list[str], imageURL: str, exceptTriggers: list[str] = []):
        super().__init__(triggers, exceptTriggers)
        self.imageUrl = imageURL
    
    async def doReply(self, message: Message):
        await message.reply(self.imageUrl)

'''
    Replies with a text response
'''
class TextReplyTrigger(ReplyTrigger):
    def __init__(self, triggers: list[str], reply: str, exceptTriggers: list[str] = []):
        super().__init__(triggers, exceptTriggers)
        self.reply = reply
    
    async def doReply(self, message: Message):
        await message.reply(self.reply)