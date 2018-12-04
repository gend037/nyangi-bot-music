import discord
from discord.ext.commands import Bot
from discord.ext import commands
from discord.voice_client import VoiceClient
import asyncio
import time
import random
import os
from discord import opus
 
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']
 
def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True
 
    for opus_lib in opus_libs:
            try:
                opus.load_opus(opus_lib)
                return
            except OSError:
                pass
 
    raise RuntimeError('Could not load an opus lib. Tried %s' % (', '.join(opus_libs)))
 
load_opus_lib()
bot = commands.Bot("")
for ext in  ["music"]:
    bot.load_extension(ext)
filter = ['cyka blyat', 'fuck', 'ёб твою мать', '씨발', '개새끼', '닥쳐']

rol=[]
ser=[]

@bot.event
async def on_ready():
       print('시작!')
       await bot.change_presence(game=discord.Game(name='보석보다 아름다운 흰둥이와 놀아주는 중이니라'))

@bot.listen()
async def on_message(message):
    if message.content.lower() in filter:
        try:
            await bot.delete_message(message)
            await bot.send_message(message.channel, "흰둥이가 뭘 배우겠느냐! 닥치거라!")
        except discord.errors.NotFound:
            return

        
@bot.command()
async def 냥이야():
    possible_responses = [
        '왜 불렀느냐',
        '왜 그러느냐',
        '무슨 문제있느냐',

    ]
    await bot.say(random.choice(possible_responses))

@bot.command()
async def 안녕():
    possible_responses = [
        '인사를 받아주겠느니라',
        '갑자기 인사를 왜 하는것이냐',
        '흥이니라',

    ]
    await bot.say(random.choice(possible_responses))
   
@bot.command()
async def 냥이():
    possible_responses = [
        '조용히하거라! 우리 보석보다도 소중한 흰둥이가 자고 있지 않느냐!',
        '꺼지거라',
    ]
    await bot.say(random.choice(possible_responses))

@bot.command()
async def 고마워():
    possible_responses = [
        '치...칭찬을 한다고..  내가 널 좋아할..것.. 같으냐..!.',
        '칭찬해준다고 아무것도 나오지 않느니라',
        '너 머리가 잘못된 것이냐 갑자기 이상한 말을 지껄이는 구나',
        '흥, 내가 잘했으니 당연히 칭찬을 받아야 하는 것이니라',
        '왜 그러는것이냐;; 부담되지 않느냐!',

    ]
    await bot.say(random.choice(possible_responses))

@bot.command()
async def 놀아줘():
    possible_responses = [
        '그럴 시간에 우리 흰둥이나 신경쓰거라',
        '쯧 쯧 그러니 니가 머리가 나쁜것이니라',
        '귀찮느니라 혼자서 놀거라',
        '난 내 소중한 흰둥이랑 놀아줘야하니 귀찮게 하지 말거라',

    ]
    await bot.say(random.choice(possible_responses))

  

bot.run(os.environ['BOT_TOKEN'])
  
