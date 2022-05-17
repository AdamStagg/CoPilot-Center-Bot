import os
from keep_alive import keep_alive
import discord
from discord.ext import tasks
from discord.ext import commands
import discord.utils
import asyncio
from datetime import datetime
import utils
from globals import Globals
import gspread

## ------------ DEFINES ------------

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="$", intents=intents)

        
## ------------ FIELDS ------------
token = os.environ['TOKEN']
glob = Globals(bot)
is_closed = False

credentials = {
    "installed": {
        "type": os.environ['SA1'],
        "project_id": os.environ['SA2'],
        "private_key_id": os.environ['SA3'],
        "private_key": os.environ['SA4'],
        "client_email": os.environ['SA5'],
        "client_id": os.environ['SA6'],
        "auth_uri": os.environ['SA7'],
        "token_uri": os.environ['SA8'],
        "auth_provider_x509_cert_url": os.environ['SA9'],
        "client_x509_cert_url": os.environ['SA10']
    }
}


# ------------ BOT COMMANDS ------------

@bot.command(name="startschedule")
@commands.has_role('Manager')
async def start_schedule(ctx):
    glob.running = True
    #start_schedule_coro.start()
    await ctx.channel.send('The schedule has been started.')

@bot.command(name='stopschedule')
@commands.has_role('Manager')
async def stop_schedule(ctx):
    glob.running = False
    #run_schedule.stop()    
    await ctx.channel.send('The schedule has been stopped.')

@bot.command(name='updateopening')
@commands.has_role('Manager')
async def update_opening(ctx, *args):

    utils.WriteToFile("OpeningTimes.csv", *args)
    glob.opening_times = utils.ReadTimesFromFile("OpeningTimes.csv")
    await asyncio.sleep(1)

@bot.command(name='updateclosing')
@commands.has_role('Manager')
async def update_closing(ctx, *args):

    utils.WriteToFile("ClosingTimes.csv", *args)
    glob.closing_timesutils.ReadTimesFromFile("ClosingTimes.csv")
    await asyncio.sleep(1)

@bot.command(name='openserver')
@commands.has_role('Manager')
async def openserver(ctx):
    #open_routine()
    await ctx.message.delete()

@bot.command(name='closeserver')
@commands.has_role('Manager')
async def close(ctx):
    #close_routine()
    await ctx.message.delete()

@bot.command(name="open") 
@commands.has_any_role('Manager', 'CoPilot Tutor')
async def open_room(ctx) :
    channel = ctx.channel
    await ctx.message.delete()
    name = channel.name

    dict_roles = {
        'online-1': glob.o1role,
        'online-2': glob.o2role,
        'online-3': glob.o3role,
        'online-4': glob.o4role,
        'gen-ed-courses': glob.genrole,
        'overflow-room': glob.ovfrole
    }

    for key in dict_roles:
        if key == name:
            await utils.remove_role_from_users(utils.Student(dict_roles[key], channel))
            break
    
    embed = discord.Embed(title="This room is now open for use.", description="The student associated with this room has been disconnected and this room is available.", color = discord.Color.blue())

    await channel.send(embed=embed)



# ------------ BOT EVENTS ------------

@bot.event
async def on_ready():
    

    glob.spreadsheet_id = os.environ['SSID']
    glob.range = os.environ['SID'] + '!' + os.environ['SR']
    
    glob.init_channels()
    glob.init_roles()

    #sa = gspread.oauth_from_dict(credentials)
    #sh = sa.open("CoPilot Tutor Tracker")
    
    glob.opening_times = utils.ReadTimesFromFile("OpeningTimes.csv")
    glob.closing_times = utils.ReadTimesFromFile("ClosingTimes.csv")
    
    for i in range(7):
        glob.schedules.append( utils.ScheduleDay(utils.TimeToMinutes(glob.opening_times[i]), utils.TimeToMinutes(glob.closing_times[i])))

    time, day = utils.UTCtoEST(datetime.now().strftime("%H:%M"), datetime.today().weekday())
    is_closed = utils.CheckClosed(time, day, glob.schedules)
    print(is_closed)
    
    #scheduler = None
    print(datetime.now())

    await Run_Schedule()

    utils.SaveSettings(glob)

    
    #start_schedule_coro.start()


@bot.event
async def on_member_join(member):
    
    text = f'Hey {member.mention}, welcome to **CoPilot Tutoring**! CoPilot open doors hours are held Monday - Friday 9am - 9pm (ET) and Saturday 10am - 2pm (ET).\n\nWhen you are ready to work with a tutor, please type your **__name__, __student number__, __degree program__, and __course you need help in__.**\n\nYou can click {glob.channel_sched.mention} for our daily schedule, or {glob.channel_faq.mention} to learn about CoPilot Tutoring.'

    if is_closed:
        await member.send(text)
    else:    
        await glob.channel_main.send(text)

async def Run_Schedule():
    time, day = utils.UTCtoEST(datetime.now().strftime("%H:%M"), datetime.today().weekday())

    is_closed = utils.CheckClosed(time, day, glob.schedules);
    print(time)
    print(day)
    while (True):
        if (is_closed == False):
            time = utils.TimeUntilClose(time, day, glob.closing_times)
            print("Time after calculation: " + str(time / 60))
            await asyncio.sleep(time)
            await close_coro()
        else:
            if (int(time[:2]) < int(glob.opening_times[day][:2])):
                time = utils.TimeUntilOpen(time, day, glob.opening_times) - 1
            else:
                time = utils.TimeUntilOpen(time, (day + 1) % 7, glob.opening_times) - 1
            seconds = 60 - int(datetime.now().strftime("%S"))
            time = (time * 60) + seconds
            print("Time after calculation: " + str(time/60))
            await asyncio.sleep(time)
            await open_coro()
            
        is_closed = not is_closed

        time, day = utils.UTCtoEST(datetime.now().strftime("%H:%M"), datetime.today().weekday())
    
    print(utils.TimeToMinutes(time))
    

@tasks.loop(seconds=1, count=1)
async def open_coro():
    channel_main = glob.channel_main

    embed = discord.Embed(title="**CoPilot Open Hours Are Now OPEN**", url="https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events", description = "Open Door Hours are Monday - Friday (9am - 9pm EST), and Saturday's (10am - 2pm EST)  View our tutoring schedule for the week on FSO (https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events)", color=discord.Color.blue())
    embed.set_thumbnail(url="https://simplybook.me/uploads/copilot/image_files/preview/7763022288eca6256d446459bb505b05.jpg")

    await channel_main.set_permissions(channel_main.guild.default_role, send_messages=True)

    await channel_main.send(embed=embed)

# def close_routine():
#     global is_closed
#     is_closed = True
#     close_coro.start()

@tasks.loop(seconds=1, count=1)
async def close_coro():

    embed = discord.Embed(title="**CoPilot Open Hours Are Now CLOSED**", url="https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events", description = "Open Door Hours are Monday - Friday (9am - 9pm EST), and Saturday's (10am - 2pm EST)  View our tutoring schedule for the week on FSO (https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events)", color=discord.Color.blue())

    embed.set_thumbnail(url="https://simplybook.me/uploads/copilot/image_files/preview/7763022288eca6256d446459bb505b05.jpg")
    
    await glob.channel_main.set_permissions(glob.channel_main.guild.default_role, send_messages=False)
    
    await glob.channel_main.send(embed=embed)





keep_alive()
bot.run(token)
