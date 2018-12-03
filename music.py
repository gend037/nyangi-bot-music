import discord
from discord.ext.commands import Bot
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord import opus 
import asyncio
import time
import random
import os
import functools, youtube_dl
from discord.ext import commands
if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')

def __init__(self, bot):
        self.bot = bot

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = ' {0.title} 작성자 {0.uploader}  {1.display_name}(이)가  신청했느니라'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [길이: {0[0]}분 {0[1]}초]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()
        
    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, '현재 노래는' + str(self.current) + '이니라')
            self.current.player.start()
            await self.play_next_song.wait()
class Music:
    """몰라
    """
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel : discord.Channel):
        """뭘 보느냐"""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('채널에서 기다리고 있느니라...')
        except discord.InvalidArgument:
            await self.bot.say('음성 채널이 아니로구나!')
        else:
            await self.bot.say('음악을 틀수있느니라 **' + channel.name)
            
    @commands.command(pass_context=True, no_pm=True)
    async def 와(self, ctx):
        """나를 부를수 있느니라"""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('어디있는 것이느냐 ㅡㅡ')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True
    
    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """나를 부를수 있느니라"""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('어디있는 것이느냐 ㅡㅡ')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def 까미(self, ctx, *, song : str):
        """내 이름 뒤에 노래이름을 쓰거라
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = '오류;;: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say("노래 준비 중이니라")
            await self.bot.say('노래신청이니라! ' + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def bumi(self, ctx, *, song : str):
        """put the link or name of the song~
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = '오류 났느니라;;: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say("노래 준비 중이니라")
            await self.bot.say('노래신청이니라! ' + str(entry))
            await state.songs.put(entry)            
            
    @commands.command(pass_context=True, no_pm=True)
    async def 까미(self, ctx, *, song : str):
        """내 이름 뒤에 노래이름을 쓰거라
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = '오류가 났느니라;;: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say("노래 준비중이니라")
            await self.bot.say('노래신청이니라! ' + str(entry))
            await state.songs.put(entry)
    
    @commands.command(pass_context=True, no_pm=True)
    async def vol(self, ctx, value : int):
        """볼륨을 설정할 수 있느니라."""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('볼륨을 {:.0%} 바꿨느니라 이제 좀 났느냐?'.format(player.volume))
    @commands.command(pass_context=True, no_pm=True)
    
    async def resume(self, ctx):
        """계속 틀겠느니라"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    async def 그만(self, ctx):
        """날 끌수 있느니라
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
            await self.bot.say("흥이 깨졌느니라!")
        except:
            pass
        
    @commands.command(pass_context=True, no_pm=True)
    async def 그만(self, ctx):
        """날 끌수 있느니라
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
            await self.bot.say("흥이 깨졌느니라!")
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """스킵하고 싶으면 3개 이상의 찬성을 받아야 하느니라. 신청자는 원하면 스킵이 가능하니라
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('으냣? 틀고있는게 없느니라....')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say('신청자가 스킵을 하고싶다 하였느니라')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.bot.say('으냐아앗? 결국 스킵했느나?')
                state.skip()
            else:
                await self.bot.say('스킵 할것이느냐? [{}/3] (you really want to skip the song...? [{}/3] )'.format(total_votes) )
        else:
            await self.bot.say('이미 투표하였느니라! 반칙이니라!! (you already had a vote!)')
      
    @commands.command(pass_context=True, no_pm=True)
    async def 스킵(self, ctx):
        """스킵하고 싶으면 3개 이상의 찬성을 받아야 하느니라. 신청자는 원하면 스킵이 가능하느니라
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('틀고 있지 않느니라')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say('신청자가 스킵을 하고싶다 하였느니라')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.bot.say('스킵하겠느니라')
                state.skip()
            else:
                await self.bot.say('스킵을 원하느냐? [{}/3]'.format(total_votes))
        else:
            await self.bot.say('이미 투표하지 않았느냐 ㅡㅡ')

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        """지금 틀고있는 노래이니라.."""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('아무것도 틀고 있지 않느니라')
        else:
            skip_count = len(state.skip_votes)
            await self.bot.say('현재 노래이니라! 현재 스킵 갯수는 이정도이니라 {} [skips: {}/3]'.format(state.current, skip_count))
        
def setup(bot):
    bot.add_cog(Music(bot))
    print('노래ㄱㄱ')
