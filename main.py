import os
from keep_alive import keep_alive
import discord
from discord.ext import tasks
from discord.ext import commands
import discord.utils
import schedule
import asyncio

#discord api
intents = discord.Intents.default()
intents.members = True

#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="$", intents=intents)

#variables
token = os.environ['TOKEN']


@bot.event
async def on_ready():
    global channel_main 
    global channel_sched
    global channel_faq
    global opening_times
    global closing_times
    global is_closed
    global o1role
    global o2role
    global o3role
    global o4role
    global genrole
    global ovfrole
    
    #   Modify here if anything changes
    channel_main = discord.utils.get(bot.get_all_channels(), name='copilot-open-hours')
    channel_sched = discord.utils.get(bot.get_all_channels(), name='todays-tutor-hours')
    channel_faq = discord.utils.get(bot.get_all_channels(), name='frequently-asked-questions')
    
    #   Time in hours (military EST)
    opening_times = ["04:00", "04:00", "04:00", "04:00", "04:00", "05:00", "00:00"]
    closing_times = ["16:00", "16:00", "16:00", "16:00", "16:00", "09:00", "00:00"]
    
    is_closed = False
    
    o1role = discord.utils.get(channel_main.guild.roles, name="Student - Online - 1")
    o2role = discord.utils.get(channel_main.guild.roles, name="Student - Online - 2")
    o3role = discord.utils.get(channel_main.guild.roles, name="Student - Online - 3")
    o4role = discord.utils.get(channel_main.guild.roles, name="Student - Online - 4")
    genrole = discord.utils.get(channel_main.guild.roles, name="Student - GenEd Course")
    ovfrole = discord.utils.get(channel_main.guild.roles, name="Student - Overflow Room")
    
    
    await channel_main.send('Log-in successful')
    


@bot.event
async def on_member_join(member):
    global channel_main
    global channel_sched
    global channel_faq
    global is_closed
    
    text = f'Hey {member.mention}, welcome to **CoPilot Tutoring**! CoPilot open doors hours are held Monday - Friday 9am - 9pm (ET) and Saturday 10am - 2pm (ET).\n\nWhen you are ready to work with a tutor, please type your **__name__, __student number__, __degree program__, and __course you need help in__.**\n\nYou can click {channel_sched.mention} for our daily schedule, or {channel_faq.mention} to learn about CoPilot Tutoring.'

    if is_closed:
        await member.send(text)
    else:    

        await channel_main.send(text)


def start_schedule():
    if opening_times[0] != "00:00":
        schedule.every().monday.at(str(opening_times[0])).do(open_routine)
    if closing_times[0] != "00:00":
        schedule.every().monday.at(str(closing_times[0])).do(close_routine)

    if opening_times[1] != "00:00":
        schedule.every().tuesday.at(str(opening_times[1])).do(open_routine)
    if closing_times[1] != "00:00":
        schedule.every().tuesday.at(str(closing_times[1])).do(close_routine)

    if opening_times[2] != "00:00":
        schedule.every().wednesday.at(str(opening_times[2])).do(open_routine)
    if closing_times[2] != "00:00":
        schedule.every().wednesday.at(str(closing_times[2])).do(close_routine)

    if opening_times[3] != "00:00":
        schedule.every().thursday.at(str(opening_times[3])).do(open_routine)
    if closing_times[3] != "00:00":
        schedule.every().thursday.at(str(closing_times[3])).do(close_routine)

    if opening_times[4] != "00:00":
        schedule.every().friday.at(str(opening_times[4])).do(open_routine)
    if closing_times[5] != "00:00":
        schedule.every().friday.at(str(closing_times[4])).do(close_routine)

    if opening_times[5] != "00:00":
        schedule.every().saturday.at(str(opening_times[5])).do(open_routine)
    if closing_times[5] != "00:00":
        schedule.every().saturday.at(str(closing_times[5])).do(close_routine)

    if opening_times[6] != "00:00":
        schedule.every().sunday.at(str(opening_times[6])).do(open_routine)
    if closing_times[6] != "00:00":
        schedule.every().sunday.at(str(closing_times[6])).do(close_routine)

    update_schedule.start()

@tasks.loop(seconds=1)
async def update_schedule() :
    schedule.run_pending()
    await asyncio.sleep(1)

@bot.command(name='openserver')
async def open(ctx):
    open_routine()
    await ctx.message.delete()

def open_routine():
    global is_closed
    is_closed = False
    open_coro.start()

@tasks.loop(seconds=1, count=1)
async def open_coro():
    global channel_main

    embed = discord.Embed(title="**CoPilot Open Hours Are Now OPEN**", url="https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events", description = "Open Door Hours are Monday - Friday (9am - 9pm EST), and Saturday's (10am - 2pm EST)  View our tutoring schedule for the week on FSO (https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events)", color=discord.Color.blue())
    embed.set_thumbnail(url="https://simplybook.me/uploads/copilot/image_files/preview/7763022288eca6256d446459bb505b05.jpg")

    await channel_main.set_permissions(channel_main.guild.default_role, send_messages=True)

    await channel_main.send(embed=embed)

@bot.command(name="closeserver")
async def close(ctx):
    close_routine()
    await ctx.message.delete()

def close_routine():
    global is_closed
    is_closed = True
    close_coro.start()

@tasks.loop(seconds=1, count=1)
async def close_coro():
    global channel_main

    embed = discord.Embed(title="**CoPilot Open Hours Are Now CLOSED**", url="https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events", description = "Open Door Hours are Monday - Friday (9am - 9pm EST), and Saturday's (10am - 2pm EST)  View our tutoring schedule for the week on FSO (https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events)", color=discord.Color.blue())
    embed.set_thumbnail(url="https://simplybook.me/uploads/copilot/image_files/preview/7763022288eca6256d446459bb505b05.jpg")
    
    await channel_main.set_permissions(channel_main.guild.default_role, send_messages=False)
    
    await channel_main.send(embed=embed)



# def test_func():
#     test_coro.start()

# @tasks.loop(seconds=1, count=1)
# async def test_coro():
#     global channel_main

#     embed = discord.Embed(title="**CoPilot Open Hours Are Now CLOSED**", url="https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events", description = "Open Door Hours are Monday - Friday (9am - 9pm EST), and Saturday's (10am - 2pm EST)  View our tutoring schedule for the week on FSO (https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events)", color=discord.Color.blue())
#     embed.set_thumbnail(url="https://simplybook.me/uploads/copilot/image_files/preview/7763022288eca6256d446459bb505b05.jpg")
    
#     await channel_main.set_permissions(channel_main.guild.default_role, send_messages=False)
    
#     await channel_main.send(embed=embed)
    


@bot.command(name="ping")
async def testFunc(ctx) :
    global channel_main
    await ctx.channel.send("pong")

# @bot.command(name="init") 
# async def init_bot(ctx) :
#     #print('Logged in as {0.user}'.format(client))

#     global channel_main 
#     global channel_sched
#     global channel_faq
#     global opening_times
#     global closing_times
    

#     #   Modify here if anything changes
#     channel_main = discord.utils.get(bot.get_all_channels(), name='copilot-open-hours')
#     channel_sched = discord.utils.get(bot.get_all_channels(), name='todays-tutor-hours')
#     channel_faq = discord.utils.get(bot.get_all_channels(), name='frequently-asked-questions')
#     #   Time in hours (military EST)
#     opening_times = ["09:00", "09:00", "09:00", "09:00", "09:00", "10:00", "00:00"]
#     closing_times = ["21:00", "21:00", "21:00", "21:00", "21:00", "14:00", "00:00"]

#     await ctx.channel.send('Initialization complete.')

async def remove_role_from_users(role):
    global channel_main
    for member in channel_main.guild.members:
        if role in member.roles:
            await member.remove_roles(role)

            if member.voice is not None:
                await member.move_to(None)

@bot.command(name="open") 
async def open_room(ctx) :
    channel = ctx.channel
    await ctx.message.delete()
    global channel_main

    name = channel.name
    roleToRemove = None
    if name == 'online-1':
        global o1role
        roleToRemove = o1role
    elif name == 'online-2':
        global o2role
        roleToRemove = o2role
    elif name == 'online-3':
        global o3role
        roleToRemove = o3role
    elif name == 'online-4':
        global o4role
        roleToRemove = o4role
    elif name == 'gen-ed-courses':
        global genrole
        roleToRemove = genrole
    elif name == 'overflow-room':
        global ovfrole
        roleToRemove = ovfrole
    else:
        return

    await remove_role_from_users(roleToRemove)
    
    embed = discord.Embed(title="This room is now open for use.", description="The student associated with this room has been disconnected and this room is available.", color = discord.Color.blue())

    await channel.send(embed=embed)

@bot.command(name="startschedule")
async def startschedule(ctx):
    start_schedule() 
    await ctx.channel.send('The schedule has been started.')
# @bot.event 
# async def on_message(message):

#     if message.content.startswith('$message') :
#         user = bot.get_user(int(629022176208748544))
#         await user.send('This is a test message')

#     if message.content.startswith('$startschedule') :
#         start_schedule()
#         await message.channel.send('Test')

#     bot.process_commands(message)





keep_alive()
bot.run(token)

