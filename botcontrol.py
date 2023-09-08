import asyncio
from disnake.ext import commands
import disnake as discord
# import flet as ft

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix=".")


@bot.event
async def on_ready():
    try:
        await asn_exit()
    except RuntimeWarning as run_warn:
        print("App_module_bot RuntimeWarn:", run_warn)

#
# async def bot_start(token):
#     return await bot.loop.create_task(bot.start(token))


async def test(token):
    try:
        await bot.start(token)
    except Exception as app_error:
        print("App_module_bot:", app_error)


def startup_test(token):
    asyncio.run(test(token))


async def asn_exit():
    print("exit")
    await bot.close()