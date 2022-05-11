import os
import discord
from discord.utils import get
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
import json
import time
from keep_alive import keep_alive #to keep alive on a server

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

load_dotenv()
TOKEN =os.getenv("TOKEN")

# songs=[]


def get_prefix(bot,message):
    with open('prefixs.json','r') as f:
        prefixes=json.load(f)

    return prefixes[str(message.guild.id)]


bot= commands.Bot(command_prefix = get_prefix)

the_last_channel=[]

@bot.event
async def on_guild_join(guild):
    global list
    with open('prefixs.json','r') as f:
         prefixes=json.load(f)
    prefixes[str(guild.id)]='.'
    with open('queues.json','r') as f:
         lista=json.load(f)
    lista[str(guild.id)]=[]
    with open('the_last_channel.json','r') as f:
         the_last_channel=json.load(f)
    the_last_channel[str(guild.id)]="None"

    with open('prefixs.json','w') as f:
        json.dump(prefixes,f,indent=4)
    with open('queues.json','w') as f:
        json.dump(lista,f,indent=4)
    with open('the_last_channel.json','w') as f:
        json.dump(the_last_channel,f,indent=4)


@bot.event
async def on_guild_remove(guild):
    with open('prefixs.json','r') as f:
         prefixes=json.load(f)
    prefixes.pop(str(guild.id))
    
    with open('queues.json','r') as f:
         lista=json.load(f)
    lista.pop(str(guild.id))

    with open('the_last_channel.json','r') as f:
         the_last_channel=json.load(f)
    the_last_channel.pop(str(guild.id))

    with open('prefixs.json','w') as f:
        json.dump(prefixes,f,indent=4)
    with open('queues.json','w') as f:
        json.dump(lista,f,indent=4)
    with open('the_last_channel.json','w') as f:
        json.dump(the_last_channel,f,indent=4)

@bot.command(aliases=['ch'],help='Change the prefix [deafult: .(dot)]')
async def changeprefix(ctx,prefix):
    with open('prefixs.json','r') as f:
         prefixes=json.load(f)

    prefixes[str(ctx.guild.id)]=prefix
    with open('prefixs.json','w') as f:
        json.dump(prefixes,f,indent=4)

        
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command(aliases=['sh'],help='Shows the queue')
async def show(ctx):
    global list
    songs=list[str(ctx.guild.id)]
    if(len(songs)!=0):
        for x in range(len(songs)):
            name_file=songs[x].split('/')
            await ctx.send('Position '+str(x+1)+': '+name_file.pop()+"\n")
    else:
        await ctx.send(str('Empty song queue'))
        return
    await ctx.send(f'-End of queue-')    



@bot.command(aliases=['h'],help='More info about the commands')
async def more_help(ctx):
    await ctx.send(f"""-Add songs to your playlist 
    -join the bot on your voice chat\n 
    -send (.n) to play the next song\n
    .n/.next -> playing the next song\n 
    .j/.join ->join the chat\n 
    .a/.add ->add songs on queue\n
    .l/.leave -> leave the voice chat\n
    .r/.resume ->resume the song\n
    .s/.stop ->stop the song\n
    .p/ .pause ->pause the song\n
    .c / .clear -> clear the queue\n
    .q / .queue -> (.q num) will play the num_th song\n
    .changeprefix -> to change the prefix for commands (default '.'(dot))\n
    .show -> shows the queue""")

file = None
@bot.command(aliases=['a'],help='Adds song in queue')
async def add(ctx):
    global file
    global the_last_channel
    songs=list[str(ctx.guild.id)]
    file = ctx.message.attachments[0].url
    voice = get(bot.voice_clients,guild=ctx.guild)
    if(file.endswith('mp3')):
        print(songs)
        songs.insert(len(songs),file)
        name_file=file.split('/')
        await ctx.send(f'Added the song: '+name_file.pop())
        list[str(ctx.guild.id)]=songs
        if(ctx.message.author.voice.channel!=the_last_channel[str(ctx.guild.id)]): #an einai se kanali na min jana mpei
            await join(ctx) #an den einai se kanali na mpei
        else:
            voice = get(bot.voice_clients, guild=ctx.guild) #an einai se kanali kai den paizei na paijei to ayto poy tha ginei add
            if not voice.is_playing():
                await next(ctx) 
    else:
        await ctx.send(f'This is not a mp3 file')
    print(file+"\n")

@bot.command(aliases=['l'],help='Leave the voice chat')
async def leave(ctx): # Note: ?leave won't work, only ?~ will work unless you change  `name = ["~"]` to `aliases = ["~"]` so both can work.
    global vc
    global list
    global the_last_channel
    print(the_last_channel[str(ctx.guild.id)])
    if(ctx.message.author.voice==None):
        await ctx.send("You have to be connected to a voice channel before you can use this command!")
    elif(ctx.message.author.voice.channel!=the_last_channel[str(ctx.guild.id)]):
        if(the_last_channel[str(ctx.guild.id)]!=None):
            await ctx.send(f"You have to be in the same voice chat: {the_last_channel[str(ctx.guild.id)]}")

    elif(ctx.message.author.voice!=None):
        if(ctx.voice_client):
            await ctx.guild.voice_client.disconnect()
            if(the_last_channel[str(ctx.guild.id)]!=None):
                await ctx.send(f'I left from channel: {ctx.message.author.voice.channel}')

            vc=None
            list[str(ctx.guild.id)]=[]
            the_last_channel[str(ctx.guild.id)]=None
            
        else:
            await ctx.send("i am not in a voice channel")
    


@bot.command(aliases=['p'],help='pause the song')
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")

@bot.command(aliases=['r'],help='resume the song')
async def resume(ctx):
    voice =  get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")

@bot.command(aliases=['s'],help='show the queue')
async def stop(ctx):
    global list
    songs = list[str(ctx.guild.id)]
    global the_last_channel
    voice =  get(bot.voice_clients, guild=ctx.guild)
    voice.stop()
    if(len(songs)==0):
        list[str(ctx.guild.id)]=[]
        the_last_channel[str(ctx.guild.id)]=None


@bot.command(aliases=['j'],help='join in a voice chat')
async def join(ctx):
    global the_last_channel
    global list
    songs=list[str(ctx.guild.id)]
    if(ctx.message.author.voice==None):
        await ctx.send(f'You have to be in a voice chat')
        return
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients,guild=ctx.guild)
    if(the_last_channel[str(ctx.guild.id)] != channel):
        if voice and voice.is_connected(): 
            await voice.move_to(channel)
            if(the_last_channel[str(ctx.guild.id)]!=channel):
                list[str(ctx.guild.id)]=[]
            #na allajei kanali mpainei edw      
        else:
            voice = await channel.connect()
            #prwti fora mpainei edw
            
        await voice.disconnect()

        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
            if(len(songs)!=0): #paizei me tin mia me to poy kanei join
                play_next(ctx)
            print(f"The bot has connected to {channel}\n")

        await ctx.send(f"Joined {channel}\n")
        the_last_channel[str(ctx.guild.id)]=channel #gia na apotrepsw na svinei tin lista an jana kanei join sto idio channel
    else:
        await ctx.send(f'I am already in {channel}\n')


@bot.command(aliases=['q'],help='q [position] or q [name] and skips the songs until find this')
async def queue(ctx):
    global list
    songs=list[str(ctx.guild.id)]
    voice = get(bot.voice_clients,guild=ctx.guild)
    num = ctx.message.content.split(' ')
    num = int(num[1])-1 #dinei 1 ara einai to 0o stin lista
    if(num>len(songs)):
        await ctx.send(f"That song doesn't exist ")
        return
    voice.pause()
    if(num+2<len(songs)):
        voice.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=songs[num]),after= lambda e : play_next(ctx))
    else:
        voice.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=songs[num]))
    song=songs[num].split('/')
    songs=songs[num+1:] #na svisei kai ayto poy paizei
    await ctx.send('Now Playing: '+song[6])
    list[str(ctx.guild.id)]=songs

@bot.command(aliases=['c'],help='clear the queue')
async def clear(ctx):
    global list
    list[str(ctx.guild.id)]=[]
    await ctx.send(f'Removed everything from queue')

@bot.command(aliases=['n'],help='This command plays songs')
async def next(ctx):
    play_next(ctx)
    
#gia na paizei to epomeno
def play_next(ctx):
    global list
    songs=list[str(ctx.guild.id)]
    vc = get(bot.voice_clients, guild=ctx.guild)
    if(len(songs)==0):
        asyncio.run_coroutine_threadsafe(sendEmptyMessage(ctx), bot.loop)
    if len(songs) >= 1:
        vc.play(discord.FFmpegPCMAudio(source=songs[0]), after=lambda e: play_next(ctx))
        asyncio.run_coroutine_threadsafe(sendMessage(ctx,songs[0]), bot.loop) #to bot.loop xreiazetai gia to asygrwto await
        del songs[0]
        list[str(ctx.guild.id)]=songs
    else:
        time.sleep(120) 
        if not vc.is_playing():
            asyncio.run_coroutine_threadsafe(disconnected(ctx), bot.loop) #οτι βαλω εδω μεσα θα μπορει να τρεξει ασυγχρονες συναρτησεις αφου δεν μπορει η play next
        # asyncio.run_coroutine_threadsafe(await ctx.send("No more songs in queue."),loop=None)

async def disconnected(ctx): #na vgainei apo mi asychroni synartsisi
    await leave(ctx)

async def sendMessage(ctx,song): #na leei to epomeno tragoudi se mi asychroni synartisi
    song=song.split('/')
    song=song[6]
    await ctx.send('Now Playing: '+song)

async def sendEmptyMessage(ctx): #na leei to epomeno tragoudi se mi asychroni synartisi
   await ctx.send('The queue is empty.')


with open('queues.json','r') as f:
    list=json.load(f) #pairnw ta id gia na wrisw ta queue
with open('the_last_channel.json','r') as f:
    the_last_channel=json.load(f)
    for x in the_last_channel:
        the_last_channel[x]=None

#keep_alive()
bot.run(TOKEN)