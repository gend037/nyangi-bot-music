import asyncio
import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord import opus
import functools, youtube_dl
import random
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
        fmt = ' {0.title} 작성 {0.uploader}   {1.display_name}(이)가 신청했느니라'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [노래 길이: {0[0]}분 {0[1]}초]'.format(divmod(duration, 60))
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
            await self.bot.send_message(self.current.channel, 'Now playing' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()
class Music:
    """Voice related commands.
    Works in multiple servers at once.
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
        """불만 있느냐"""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('이미 채널에 있지 않느냐!')
        except discord.InvalidArgument:
            await self.bot.say('하... 이건 음성 채널이 아니구나')
        else:
            await self.bot.say('음악 틀 수 있느니라 **' + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    async def 와(self, ctx):
        """나를 부를 수 있느니라"""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('왜 들어와있지 않은것이냐?')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def (self, ctx, *, song : str):
        """내 이름 뒤에 듣고 싶은 노래 제목을 쓰거라, 링크도 쓸수 있느니라
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            await self.bot.say("불러오는 중이니라")
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = '에러이니라...: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('노래신청이니라! ' + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def 볼륨(self, ctx, value : int):
        """노래를 볼륨을 설정할 수 있느니라"""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('Set the volume to {:.0%}'.format(player.volume))
    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """몰라"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    async def 그만(self, ctx):
        """꺼지는 커맨드이니라
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
            await self.bot.say("흥이 깨졌느니라")
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def s(self, ctx):
        """노래를 스킵하기 위해선 최소한 3개의 찬성이 필요하느니라. 신청자는 원하면 표 없이 스킵이 가능하니라
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('아무것도 틀고있지 않느니라')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say('넘기겠느니라')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.bot.say('넘기겠느니라')
                state.skip()
            else:
                await self.bot.say('스킵 할 것 같구나... [{}/3]'.format(total_votes))
        else:
            await self.bot.say('이미 투표하지 않았느냐 ㅡㅡ')

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        """지금 틀고있는 노래를 알려주는 커맨드"""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('아무것도 틀고 있지 않느니라')
        else:
            skip_count = len(state.skip_votes)
            await self.bot.say('이번 노래는 {} [현재 스킵은 이 정도이니라: {}/3]'.format(state.current, skip_count))
            
def setup(bot):
    bot.add_cog(Music(bot))
    print('노래 틀 준비 끝났느니라')
