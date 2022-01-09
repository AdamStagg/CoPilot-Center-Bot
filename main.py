import os
import discord

print(discord.__version__)

token = os.environ['TOKEN']
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_member_join(member):
    channel_main = discord.utils.get(client.get_all_channels(), name='copilot-open-hours')
    channel_sched = discord.utils.get(client.get_all_channels(), name='todays-tutor-hours')
    channel_faq = discord.utils.get(client.get_all_channels(), name='frequently-asked-questions')

    await channel_main.send(f'Hey {member.mention}, welcome to **CoPilot Tutoring**! CoPilot open doors hours are held Monday - Friday 9am - 9pm (ET) and Saturday 10am - 2pm (ET).\n\nWhen you are ready to work with a tutor, please type your **__name__, __student number__, __degree program__, and __course you need help in__.**\n\nYou can click {channel_sched.mention} for our daily schedule, or {channel_faq.mention} to learn about CoPilot Tutoring.')


@client.event 
async def on_message(message):
    if message.author == client.user :
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(token)
