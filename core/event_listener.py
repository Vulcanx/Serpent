import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class EventListener(commands.Cog):
    def __init__(self, bot, db_connection):
        self.bot = bot
        self.db_connection = db_connection
        self.commands = {
            'online': {
                'title': 'Players Online',
                'callback': self.command_finish,
                'channelId': 616497056147701767
            },
            'uptime': {
                'title': 'Server Uptime',
                'callback': self.command_finish,
                'channelId': 616497056147701767
            }
        }

        self.start(interval=1)

    def start(self, interval):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.exec_listener,
                               'interval',
                               seconds=interval)
        self.scheduler.start()

    async def exec_listener(self):
        queue = self.get_queue()
        if queue:
            for row in queue:
                # unpack tuple
                id, cmd, args = row
                if self.commands.get(cmd):
                    finish = self.commands[cmd]
                    await finish['callback'](args,
                                             finish['title'],
                                             finish['channelId'])
                query = 'DELETE FROM `server_listener` WHERE `id` = ' + str(id)
                self.db_connection.query(query)

    async def command_finish(self, result, title, channelId):
        embed = discord.Embed(color=0xff0000, title=title, description=result)
        await self.bot.get_channel(id=channelId).send(embed=embed)

    def get_queue(self):
        return self.db_connection.query("""SELECT * FROM `server_listener`""")
