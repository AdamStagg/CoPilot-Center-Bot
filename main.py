import os
from keep_alive import keep_alive
import discord
from discord.ext import tasks
from discord.ext import commands
import discord.utils
import schedule
import asyncio
from datetime import datetime
from pandas import read_csv

#discord api
intents = discord.Intents.default()
intents.members = True

#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="$", intents=intents)

#variables
token = os.environ['TOKEN']

#classes

class Student:

    def __init__(self, _role, _channel):
        self.role = _role
        self.channel = _channel

#fields
global channel_main
global channel_sched
global channel_faq

channel_main = None
channel_sched = None
channel_faq = None

global o1role
global o2role
global o3role
global o4role
global ovfrole
global genrole

o1role = None
o2role = None
o3role = None
o4role = None
ovfrole = None
genrole = None

global opening_times
global closing_times

opening_times = None
closing_times = None

#accessors
def get_channel_main():
    global channel_main
    if channel_main == None:
        channel_main = discord.utils.get(bot.get_all_channels(), name='copilot-open-hours')
    return channel_main

def get_channel_sched():
    global channel_sched
    if channel_sched == None:
        channel_sched = discord.utils.get(bot.get_all_channels(), name='todays-tutor-hours')
    return channel_sched

def get_channel_faq():
    global channel_faq
    if channel_faq == None:
        discord.utils.get(bot.get_all_channels(), name='frequently-asked-questions')
    return channel_faq

def get_online1():
    global o1role
    if o1role == None:
        o1role = discord.utils.get(get_channel_main().guild.roles, name="Student - Online - 1")
    return o1role

def get_online2():
    global o2role
    if o2role == None:
        o2role = discord.utils.get(get_channel_main().guild.roles, name="Student - Online - 2")
    return o2role

def get_online3():
    global o3role
    if o3role == None:
        o3role = discord.utils.get(get_channel_main().guild.roles, name="Student - Online - 3")
    return o3role

def get_online4():
    global o4role
    if o4role == None:
        o4role = discord.utils.get(get_channel_main().guild.roles, name="Student - Online - 4")
    return o4role

def get_overflow():
    global ovfrole
    if ovfrole == None:
        ovfrole = discord.utils.get(get_channel_main().guild.roles, name="Student - Overflow Room")
    return ovfrole

def get_gened():
    global genrole
    if genrole == None:
        genrole = discord.utils.get(get_channel_main().guild.roles, name="Student - GenEd Course")
    return genrole

def get_opening_times():
    global opening_times
    return opening_times

def get_closing_times():
    global closing_times
    return closing_times

#mutators
def set_opening_times(file):
    global opening_times
    opening_times = file

def set_closing_times(file):
    global closing_times
    closing_times = file

@bot.event
async def on_ready():
    global is_closed
    global scheduler
    
    set_opening_times(ReadTimesFromFile("OpeningTimes.csv"))
    set_closing_times(ReadTimesFromFile("ClosingTimes.csv"))
    
    is_closed = False
    
    scheduler = None

    a, b = ESTtoUTC("21:00", 2)
    print("Time: " + str(a) + "\nDay: " + str(b))

    print(datetime.now())


@bot.event
async def on_member_join(member):
    channel_main = get_channel_main()
    channel_sched = get_channel_sched()
    channel_faq = get_channel_faq()
    global is_closed
    
    text = f'Hey {member.mention}, welcome to **CoPilot Tutoring**! CoPilot open doors hours are held Monday - Friday 9am - 9pm (ET) and Saturday 10am - 2pm (ET).\n\nWhen you are ready to work with a tutor, please type your **__name__, __student number__, __degree program__, and __course you need help in__.**\n\nYou can click {channel_sched.mention} for our daily schedule, or {channel_faq.mention} to learn about CoPilot Tutoring.'

    if is_closed:
        await member.send(text)
    else:    
        await channel_main.send(text)


def ESTtoUTC(input_time, input_day) :
    adj_time = int(input_time[:2]) + 5
    output_day = input_day
    if adj_time >= 24:
        adj_time -= 24
        output_day = (output_day + 1) % 7

    if adj_time < 10:
        output_time = "0" + str(adj_time)
    else:
        output_time = str(adj_time)    

    output_time += input_time[2:5] #add the minutes back

    return output_time, output_day
    

@bot.command(name="startschedule")
async def start_schedule(ctx):
    start_schedule_coro.start()
    await ctx.channel.send('The schedule has been started.')

@bot.command(name='stopschedule')
async def stop_schedule(ctx):
    run_schedule.stop()    
    await ctx.channel.send('The schedule has been stopped.')

@bot.command(name='clearschedule')
async def clear_schedule(ctx):
    global scheduler
    if (scheduler != None):
        scheduler.clear()
        await ctx.channel.send('The schedule has been cleared')
        return
    await ctx.channel.send('There was an error clearing the schedule')

@bot.command(name='updateopening')
async def update_opening(ctx, *args):

    WriteToFile("OpeningTimes.csv", *args)
    set_opening_times(ReadTimesFromFile("OpeningTimes.csv"))
    await asyncio.sleep(1)

@bot.command(name='updateclosing')
async def update_closing(ctx, *args):

    WriteToFile("ClosingTimes.csv", *args)
    set_closing_times(ReadTimesFromFile("ClosingTimes.csv"))
    await asyncio.sleep(1)

def ArrayToString(*args):
    output = ""
    print(output)
    for arg in args:        
        output += str(arg[:-1]) + ","
    
    print(output)
    output = output[1:-2]
    print(output)
    return output

def WriteToFile(file_name, *strings):
    with open(file_name, 'w') as file:
        for line in strings:
            file.write(line)
            file.write(',')
    
    with open(file_name, 'rb+') as file:
        file.seek(-1, os.SEEK_END)
        file.truncate()
    
def ReadFromFile(file_name):
    
    return read_csv(file_name)

def ReadTimesFromFile(file_name):

    arr = []

    for i in ReadFromFile(file_name):
        arr.append(str(i)[0:5])

    return arr

@tasks.loop(seconds=1, count=1)
async def start_schedule_coro():
    global scheduler
    scheduler = schedule.Scheduler()
    
    days = [
        scheduler.every().monday,
        scheduler.every().tuesday,
        scheduler.every().wednesday,
        scheduler.every().thursday,
        scheduler.every().friday,
        scheduler.every().saturday,
        scheduler.every().sunday
    ]

    opening_times = get_opening_times()
    closing_times = get_closing_times()

    for i in range(7):
        
        time_open = opening_times[i]
        time_close = closing_times[i]

        if time_open != '00:00':
            time_open, day = ESTtoUTC(time_open, i)
            days[day].at(time_open).do(open_routine)

        if time_close != '00:00':
            time_close, day = ESTtoUTC(time_close, i)
            print(str(time_close) + '\t' + str(day))
            days[day].at(time_close).do(close_routine)

        

    #sleep until next hour 
    #
    #
    #

   
    run_schedule.start(scheduler)  

@tasks.loop(seconds=1)
async def run_schedule(scheduler) :
    scheduler.run_pending()
    await asyncio.sleep(1)

@bot.command(name='openserver')
async def openserver(ctx):
    open_routine()
    await ctx.message.delete()

def open_routine():
    global is_closed
    is_closed = False
    open_coro.start()

@tasks.loop(seconds=1, count=1)
async def open_coro():
    channel_main = get_channel_main()

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
    channel_main = get_channel_main()

    embed = discord.Embed(title="**CoPilot Open Hours Are Now CLOSED**", url="https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events", description = "Open Door Hours are Monday - Friday (9am - 9pm EST), and Saturday's (10am - 2pm EST)  View our tutoring schedule for the week on FSO (https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events)", color=discord.Color.blue())
    embed.set_thumbnail(url="https://simplybook.me/uploads/copilot/image_files/preview/7763022288eca6256d446459bb505b05.jpg")
    
    await channel_main.set_permissions(channel_main.guild.default_role, send_messages=False)
    
    await channel_main.send(embed=embed)


async def remove_role_from_users(student):
    
    for member in student.channel.members:

        if student.role in member.roles:
            await member.remove_roles(student.role)

            if member.voice is not None:
                await member.move_to(None)

            embed = discord.Embed(title="Your tutoring session has ended.", description="Thank you for coming to the CoPilot tutoring center today! Feel free to come back anytime during our online hours.", color = discord.Color.blue())

            embed.add_field(name="Find our schedule online!", value = "Open Door Hours are Monday - Friday (9am - 9pm EST), and Saturday's (10am - 2pm EST)  View our tutoring schedule for the week on FSO (https://one.fullsail.edu/connect/departments/copilot-tutoring-center/119/events)", inline = False)
            embed.set_thumbnail(url="https://simplybook.me/uploads/copilot/image_files/preview/7763022288eca6256d446459bb505b05.jpg")

            await member.send(embed=embed)
            
            return True

    return False

@bot.command(name="open") 
async def open_room(ctx) :
    channel = ctx.channel
    await ctx.message.delete()
    name = channel.name

    dict_roles = {
        'online-1': get_online1(),
        'online-2': get_online2(),
        'online-3': get_online3(),
        'online-4': get_online4(),
        'gen-ed-courses': get_gened(),
        'overflow-room': get_overflow()
    }

    for key in dict_roles:
        if key == name:
            await remove_role_from_users(Student(dict_roles[key], channel))
            break

    
    embed = discord.Embed(title="This room is now open for use.", description="The student associated with this room has been disconnected and this room is available.", color = discord.Color.blue())

    await channel.send(embed=embed)


keep_alive()
bot.run(token)

