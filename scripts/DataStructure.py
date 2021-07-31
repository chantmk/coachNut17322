import logging
import enum

class MessageState(enum.Enum):
    CREATED = 0
    DELETED = 1
    SELECTED = 2
    SENT = 3

class ServerData() :
    def __init__(self):
        self.channel = ""
        self.message = ""
        self.messageFlag = MessageState.DELETED
        self.game_emoji = []
        self.count_emoji = []
        self.tag_emoji = []
        self.tag_message = dict()
        self.logger = logging.getLogger()