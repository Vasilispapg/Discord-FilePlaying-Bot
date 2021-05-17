import os
import discord
from discord.utils import get
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
import json


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


list={ 639525815201169447:[] , 843598275147595807:[] } #to thewrei command

@bot.event
async def on_guild_join(guild):
    global list
    list[guild.id]=[]
    with open('prefixs.json','r') as f:
         prefixes=json.load(f)
    prefixes[str(guild.id)]='.'

    with open('prefixs.json','w') as f:
        json.dump(prefixes,f,indent=4)

@bot.event
async def on_guild_remove(guild):
    with open('prefixs.json','r') as f:
         prefixes=json.load(f)
    prefixes.pop(str(guild.id))

    with open('prefixs.json','w') as f:
        json.dump(prefixes,f,indent=4)

@bot.command()
async def changeprefix(ctx,prefix):
    with open('prefixs.json','r') as f:
         prefixes=json.load(f)

    prefixes[str(ctx.guild.id)]=prefix
    with open('prefixs.json','w') as f:
        json.dump(prefixes,f,indent=4)

        
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def show(ctx):
    global list
    print(list[ctx.guild.id])
    songs=list[ctx.guild.id]
    if(len(songs)!=0):
        for x in range(len(songs)):
            name_file=songs[x].split('/')
            await ctx.send('Position '+str(x+1)+': '+name_file.pop()+"\n")
    else:
        await ctx.send(str('Empty song queue'))
        return
    await ctx.send(f'-End of queue-')    



@bot.command(aliases=['h'])
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
@bot.command(aliases=['a'])
async def add(ctx):
    global file
    songs=list[ctx.guild.id]
    file = ctx.message.attachments[0].url
    if(file.endswith('mp3')):
        print(songs)
        songs.insert(len(songs),file)
        name_file=file.split('/')
        await ctx.send(f'Added the song: '+name_file.pop())
        list[ctx.guild.id]=songs
    else:
        await ctx.send(f'This is not a mp3 file')
    print(file+"\n")

@bot.command(aliases=['l'])
async def leave(ctx): # Note: ?leave won't work, only ?~ will work unless you change  `name = ["~"]` to `aliases = ["~"]` so both can work.
    global vc
    global list
    global the_last_channel

    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send('I left')
        vc=None
        list[ctx.guild.id]=[]
        the_last_channel=None
    else:
        await ctx.send("i am not in a voice channel")


@bot.command(aliases=['p'])
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")

@bot.command(aliases=['r'])
async def resume(ctx):
    voice =  get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")

@bot.command(aliases=['s'])
async def stop(ctx):
    global list
    songs = list[ctx.guild.id]
    global the_last_channel
    voice =  get(bot.voice_clients, guild=ctx.guild)
    voice.stop()
    if(len(songs)==0):
        list[ctx.guild.id]=[]
        the_last_channel=None

the_last_channel=None

@bot.command(aliases=['j'])
async def join(ctx):
    
    global the_last_channel
    global list
    songs=list[ctx.guild.id]
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients,guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
        if(the_last_channel!=channel):
            list[ctx.guild.id]=[]
        #na allajei kanali mpainei edw      
    else:
        voice = await channel.connect()
        #prwti fora mpainei edw
        the_last_channel=channel #gia na apotrepsw na svinei tin lista an jana kanei join sto idio channel
    await voice.disconnect()

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        if(len(songs)!=0):
            voice.play(discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source=songs[0]),after= lambda e :play_next(ctx))
            song=songs[0].split('/')
            await ctx.send('Playing song: '+song[6])
            songs.remove(songs[0])
            list[ctx.guild.id]=songs #ananewsi listas
        print(f"The bot has connected to {channel}\n")

    await ctx.send(f"Joined {channel}\n")


@bot.command(aliases=['q'])
async def queue(ctx):
    global list
    songs=list[ctx.guild.id]
    voice = get(bot.voice_clients,guild=ctx.guild)
    num = ctx.message.content.split(' ')
    num = int(num[1])-1 #dinei 1 ara einai to 0o stin lista
    if(num>len(songs)):
        await ctx.send(f"That song doesn't exist ")
        return
    voice.pause()
    if(num+2<len(songs)):
        voice.play(discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source=songs[num]),after= lambda e : play_next(ctx))
    else:
        voice.play(discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source=songs[num]))
    song=songs[num].split('/')
    songs=songs[num+1:] #na svisei kai ayto poy paizei
    await ctx.send('Playing song: '+song[6])
    list[ctx.guild.id]=songs

@bot.command(aliases=['c'])
async def clear(ctx):
    global list
    list[ctx.guild.id]=[]
    await ctx.send(f'Removed everything from queue')

@bot.command(aliases=['n'],help='This command plays songs')
async def next(ctx):
    global list
    songs=list[ctx.guild.id]
    vc = get(bot.voice_clients, guild=ctx.guild)
    vc.pause() #gia enallagi
    if(len(songs)==0):
        await ctx.send(str('Empty song queue'))
        return
    else:
        song=songs[0]
        songs.remove(songs[0])
        list[ctx.guild.id]=songs
    print(song)
    if(file==None):
        return
    vc.play(discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source=song,after= lambda e : next(ctx)),after= lambda e : play_next(ctx))
    song=song.split('/')
    await ctx.send(f'Playing song: '+song[6])
    
#gia na paizei to epomeno
def play_next(ctx):
    global list
    songs=list[ctx.guild.id]
    if len(songs) >= 1:
        vc = get(bot.voice_clients, guild=ctx.guild)
        vc.play(discord.FFmpegPCMAudio(source=songs[0]), after=lambda e: play_next(ctx))
        del songs[0]
        list[ctx.guild.id]=songs
        asyncio.run_coroutine_threadsafe(ctx.send("No more songs in queue."),loop=None)
    
bot.run(TOKEN)
