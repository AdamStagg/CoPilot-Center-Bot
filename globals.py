import discord

#A class to hold all global variables
class Globals:

    #constructor
    def __init__(self, __bot):
        self._bot = __bot

        self._spreadsheed_id = None
        self._range = None

        self._channels = None

        self._channel_main = None
        self._channel_sched = None
        self._channel_faq = None

        self._o1role = None
        self._o2role = None
        self._o3role = None
        self._o4role = None
        self._ovfrole = None
        self._genrole = None

        self._opening_times = None
        self._closing_times = None

        self._schedules = []

        self._running = None
    
    #Discord bot var
    @property
    def bot(self):
        return self._bot
    @bot.setter
    def bot(self, __bot):
        self._bot = __bot

    #Google spreadsheet data
    @property
    def spreadsheet_id(self):
        return self._spreadsheet_id
    @spreadsheet_id.setter
    def spreadsheet_id(self, __ssid):
        self._spreadsheet_id = __ssid
        
    @property
    def range(self):
        return self._range
    @range.setter
    def range(self, __range):
        self._range = __range

    @property
    def channels(self):
        return self._channels
    @channels.setter
    def channels(self, __channels):
        self._channels = __channels
        
    
    #Discord channel info
    @property
    def channel_main(self):
        return self._channel_main
    @channel_main.setter
    def channel_main(self, __cmain):
        self._channel_main = __cmain
        
    @property
    def channel_sched(self):
        return self._channel_sched
    @channel_sched.setter
    def channel_sched(self, __csched):
        self._channel_sched = __csched
        
    @property
    def channel_faq(self):
        return self._channel_faq
    @channel_faq.setter
    def channel_faq(self, __cfaq):
        self._channel_faq = __cfaq

    
    def init_channels(self):
        if (self.channels == None):
            self.channels = self.bot.get_all_channels()

        self.channel_main = discord.utils.get(self.channels, name="copilot-open-hours")
        self.channel_faq = discord.utils.get(self.channels, name="frequently-asked-questions")
        self.channel_sched = discord.utils.get(self.channels, name="todays-tutor-hours")

    
    #Tutoring roles
    @property
    def o1role(self):
        return self._o1role
    @o1role.setter
    def o1role(self, __role):
        self._o1role = __role
        
    @property
    def o2role(self):
        return self._o2role
    @o2role.setter
    def o2role(self, __role):
        self._o2role = __role

    @property
    def o3role(self):
        return self._o3role
    @o3role.setter
    def o3role(self, __role):
        self._o3role = __role

    @property
    def o4role(self):
        return self._o4role
    @o4role.setter
    def o4role(self, __role):
        self._o4role = __role
    
    @property
    def ovfrole(self):
        return self._ovfrole
    @ovfrole.setter
    def ovfrole(self, __role):
        self._ovfrole = __role

    @property
    def genrole(self):
        return self._genrole
    @genrole.setter
    def genrole(self, __role):
        self._genrole = __role

    def init_roles(self):
        if (self.channels == None):
            self.channels = self.bot.get_all_channels()
        
        self.o1role = discord.utils.get(self.channel_main.guild.roles, name="Student - Online - 1")
        self.o2role = discord.utils.get(self.channel_main.guild.roles, name="Student - Online - 2")
        self.o3role = discord.utils.get(self.channel_main.guild.roles, name="Student - Online - 3")
        self.o4role = discord.utils.get(self.channel_main.guild.roles, name="Student - Online - 4")
        self.ovfrole = discord.utils.get(self.channel_main.guild.roles, name="Student - Overflow Room")
        self.genrole = discord.utils.get(self.channel_main.guild.roles, name="Student - GenEd Course")

    #Schedule hours
    @property
    def opening_times(self):
        return self._opening_times
    @opening_times.setter
    def opening_times(self, __time):
        self._opening_times = __time
        
    @property
    def closing_times(self):
        return self._closing_times
    @closing_times.setter
    def closing_times(self, __time):
        self._closing_times = __time
        
    @property
    def schedules(self):
        return self._schedules
    @schedules.setter
    def schedules(self, __array):
        self._schedules = __array

    @property
    def running(self):
        return self._running
    @running.setter
    def running(self, __run):
        self._running = __run

    
