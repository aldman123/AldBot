from discord import *

class ReplyTrigger:

    def __init__(self, triggers: tuple[str], exceptTriggers: tuple[str] = []):
        self.triggers = triggers
        self.exceptTriggers = exceptTriggers

    def isTriggered(self, messageContent: str) -> bool:
        messageContent = messageContent.lower()

        for trigger in self.exceptTriggers:
            if (trigger.lower() in messageContent):
                return False

        for trigger in self.triggers:
            if (trigger.lower() in messageContent):
                return True
        return False


class ImageReplyTrigger(ReplyTrigger):
    def __init__(self, triggers: tuple[str], imageURL: str, exceptTriggers: tuple[str] = []):
        super().__init__(type, triggers, exceptTriggers)
        self.imageURL = imageURL

class TextReplyTrigger(ReplyTrigger):
    def __init__(self, triggers: tuple[str], reply: str, exceptTriggers: tuple[str] = []):
        super().__init__(type, triggers, exceptTriggers)
        self.reply = reply

    