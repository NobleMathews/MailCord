import os
import sys

import discord
from discord.ext.commands import CheckFailure, CommandNotFound
from dotenv import load_dotenv
from discord.ext import commands
from collections import defaultdict
# script_dir = os.path.abspath(os.path.dirname(sys.argv[0]) or '.')
# credentials_path = os.path.join(script_dir, '../smtp_alt_server/confidential/workerkey.json')
faculty_check = defaultdict(lambda: " ")
faculty_check["noble"] = "elbonleon@gmail.com"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # if discord.utils.get(message.author.roles, name="moderator") is None:
    #     return
    if message.content.startswith('!@'):
        splitMessage = message.content.split(" ")
        target_user = splitMessage[0][2:]
        check = faculty_check[target_user]
        if check != " ":
            response = "@SuperMod Please approve an e-mail to " + check
        else:
            response = "Please add user and email to dictionary before using command"
        messages = await message.channel.history(limit=2).flatten()
        if messages[1].author == message.author:
            response = response + "\n" + messages[1].jump_url
        else:
            response = "Your previous message was lost 😢"
        botMess = await message.channel.send(response)
        await message.delete()
        await botMess.add_reaction("👍")

    await bot.process_commands(message)


@bot.event
@commands.has_role("SuperMod")
async def on_reaction_add(reaction, member):
    if (reaction.emoji == '👍') and (member != bot.user):
        messageContent = reaction.message.content
        if messageContent.startswith('@'):
            try:
                [messageHead, messageUrl] = messageContent.split('\n')
                message = await reaction.message.channel.fetch_message(messageUrl.split("/")[-1])
                print(messageHead.split(" ")[-1], "| Update from Discord Server |", message.content)
            except Exception as error:
                print(error)

        await reaction.message.delete()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


@bot.command()
@commands.has_role("Moderator")
async def ping(ctx):
    # (ctx, user: discord.Member)
    # role = discord.utils.find(lambda r: r.name == 'Member', ctx.message.server.roles)
    # if role in user.roles:
    #     await bot.say("{} is not mapped".format(user))
    # else:
    #     await bot.add_roles(user, role)
    await ctx.channel.send("pong")


@ping.error
async def ping_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("You are lacking a required role")
    else:
        raise error


@bot.command()
async def cprint(ctx, arg):
    await ctx.channel.send(arg)


bot.run(TOKEN)
