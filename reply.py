from discord import *

class ReplyTrigger:

    def __init__(self, type: str, triggers: tuple[str], reply: str, exceptTriggers: tuple[str] = []):
        self.type = type
        self.triggers = triggers
        self.exceptTriggers = exceptTriggers
        self.reply = reply

    def isTriggered(self, messageContent: str) -> bool:
        messageContent = messageContent.lower()

        for trigger in self.exceptTriggers:
            if (trigger.lower() in messageContent):
                return False

        for trigger in self.triggers:
            if (trigger.lower() in messageContent):
                return True
        return False


