import discord
from discord.ext import commands
import json
import rota
import os
import asyncio
import traceback

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

USER_DATA_FILE = "users.json"

if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        userDatas = json.load(f)
else:
    userDatas = {}

def getSongData(song_id):
    with open("songs.json", "r", encoding="utf-8") as f:
        songs = {song["id"]: song for song in json.load(f)["songs"]}
    return songs[song_id]

def saveUserProfiles():
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(userDatas, f, ensure_ascii=False, indent=4)

def verifyProfile(user_id):
    user_id = str(user_id)
    required_keys = ["server", "objectId"]
    
    if user_id not in userDatas:
        userDatas[user_id] = {}
    
    for key in required_keys:
        if key not in userDatas[user_id]:
            saveUserProfiles()
            return False, f"缺少 {key}"
    
    saveUserProfiles()
    return True, "绑定成功"

async def update_user_data(ctx, key, value):
    user_id = str(ctx.author.id)
    userDatas[user_id][key] = value
    saveUserProfiles()
    
    verified, message = verifyProfile(user_id)
    await ctx.reply(f'{ctx.author} {message}')

def readSongAliases():
    with open("songAliases.json", "r", encoding="utf-8") as f:
        return json.load(f)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')

@bot.command()
async def b40(ctx):
    user_id = str(ctx.author.id)
    
    verified, message = verifyProfile(user_id)
    if not verified:
        await ctx.reply(f'{ctx.author} 尚未完成 Rotaeno 账号绑定 ({message})')
        return
    
    print(f'命令 /b40 被用户 {ctx.author} (ID: {user_id}）触发')
    # if True:
    #     msg = await ctx.reply(f'已加入列表，请等待')
    #     img_path = await asyncio.to_thread(rota.get, userDatas[user_id])
    #     await ctx.reply(f"{ctx.author.mention} 你的 Best 40 数据已生成", file=discord.File(img_path))
    #     await msg.delete()
    try:
        msg = await ctx.reply(f'已加入列表，请等待')
        img_path = await asyncio.to_thread(rota.getBest40, userDatas[user_id])
        await ctx.reply(f"{ctx.author.mention} 你的 Best 40 数据已生成", file=discord.File(img_path))
    except:
        traceback.print_exc()
        try:
            await ctx.reply(f"{ctx.author.mention} 发生错误")
        except:
            await ctx.send(f'{ctx.author.mention} 发生错误 (大概率为无法回复消息)')
    finally:
        await msg.delete()

@bot.command()
async def server(ctx):
    if len(ctx.message.content.split(maxsplit=1)) < 2:
        await ctx.reply("请提供 server 值")
        return
    await update_user_data(ctx, "server", ctx.message.content.split(maxsplit=1)[1])

@bot.command()
async def objectid(ctx):
    if len(ctx.message.content.split(maxsplit=1)) < 2:
        await ctx.reply("请提供 objectId 值")
        return
    await update_user_data(ctx, "objectId", ctx.message.content.split(maxsplit=1)[1])
    
@bot.command()
async def song(ctx, *, song_name):
    user_id = str(ctx.author.id)
    
    verified, message = verifyProfile(user_id)
    if not verified:
        await ctx.reply(f'{ctx.author} 尚未完成 Rotaeno 账号绑定 ({message})')
        return
    
    print(f'命令 /song {song_name} 被用户 {ctx.author} (ID: {user_id}）触发')
    try:
        if song_name in ["设计蚂蚁", "設計螞蟻"]:
            await ctx.reply(f'''恐怖！设计蚂蚁来了😱\n🐜\n                               🐜\n      🐜\n                         🐜\n           🐜\n                   🐜\n                🐜\n            🐜\n                    🐜\n      🐜\n                         🐜\n 🐜\n                              🐜''')
            return
        msg = await ctx.reply(f'已加入列表，请等待')
        song_names = {}
        source_song_aliases = readSongAliases()
        for song_alias in source_song_aliases:
            if song_name.lower() == song_alias.lower():
                song_names = {}
                song_names[song_alias] = source_song_aliases[song_alias]
                break
            if song_name.lower() in song_alias.lower():
                k = True
                for tmp in song_names:
                    if tmp.lower() == song_alias.lower():
                        k = False
                if k:
                    song_names[song_alias] = source_song_aliases[song_alias]
        if len(song_names) != 1:
            await ctx.reply(f"{ctx.author.mention} 该别名有以下歌曲:\n{'\n'.join(song_names.keys())}")
            return
        
        song_id = list(song_names.keys())[0]
        if "211" in song_id:
            tmp = song_names[song_id]
            song_id = "211大学"
            data = await asyncio.to_thread(rota.getSong, userDatas[user_id], song_id)
            song_id = tmp
        else:
            song_id = song_names[song_id]
            data = await asyncio.to_thread(rota.getSong, userDatas[user_id], song_id)

        await ctx.reply(f"{ctx.author.mention} 你的 {getSongData(song_id)["title_localized"]["default"]} 歌曲数据已生成", file=discord.File(data))
    except:
        traceback.print_exc()
        try:
            await ctx.reply(f"{ctx.author.mention} 发生错误")
        except:
            await ctx.send(f'{ctx.author.mention} 发生错误 (大概率为无法回复消息)')
    finally:
        try:
            await msg.delete()
        except:
            ...

@bot.command()
async def alias(ctx, *, song_alisa):
    user_id = str(ctx.author.id)
    
    print(f'命令 /alias {song_alisa} 被用户 {ctx.author} (ID: {user_id}）触发')
    with open("songAliases.add.txt", "a", encoding="utf-8") as f: f.write(f"{song_alisa}\n")
    try:
        await ctx.reply(f"{ctx.author.mention} 已添加 {song_alisa} 到别名库 (请等待管理员的审核)")
    except:
        await ctx.send(f'{ctx.author.mention} 发生错误 (大概率为无法回复消息)')

bot.run("")
