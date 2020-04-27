from .ReactionTracker import ReactionsTracker
from .GlobalDatabase import GlobalDatabase
from .UserDatabase import UserDatabase
from .SBDatabase import SectorBuddyDatabase
from .VatsimOnline import VatsimData
from .TicketsManager import issueTracker
from .BookingsFetcher import BookingHandler

GlobalDatabase().selfCheck()
issueTracker().selfCheck()
ReactionsTracker().selfCheck()
UserDatabase().selfCheck()
SectorBuddyDatabase().selfCheck()
BookingHandler().selfCheck()