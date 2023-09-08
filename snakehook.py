from disnake import Webhook
from disnake import Embed
from disnake import Colour
import aiohttp
import asyncio
# import logging

# logger = logging.getLogger("disnake")
# handler = logging.FileHandler(filename="module.log", encoding="utf-8", mode="w")
# handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
# logger.setLevel(logging.DEBUG)
# logger.addHandler(handler)


async def embed(url: str, title: str, desc: str, colour, color, amount_fld: int, fld_title, fld_desc):
    async with aiohttp.ClientSession() as session:
        global emb
        webhook = Webhook.from_url(url=url, session=session)
        emb = Embed(title=title,
                    description=desc,
                    colour=colour,
                    color=color)

        if not amount_fld <= 0:
            for i in range(amount_fld):
                print(fld_title, fld_desc)
                emb.add_field(name=fld_title[0], value=fld_desc[0], inline=True)
                fld_title.pop(0)
                fld_desc.pop(0)

        await webhook.send(embed=emb)


async def non_embed(url: str, text: str):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url=url, session=session)

        await webhook.send(text)

        await session.close()


def color_analytics(color: str):
    if color == "Blue":
        return Colour.blue()
    elif color == "Blurple":
        return Colour.blurple()
    elif color == "Dark_blue":
        return Colour.dark_blue()
    elif color == "Green":
        return Colour.green()
    elif color == "Brand_green":
        return Colour.brand_green()
    elif color == "Dark_green":
        return Colour.dark_green()
    else:
        return Colour.default()


def start_embed(url, title, desc, colour=None, color=None, amount_fld=0, fld_list=None):
    global fld_title, fld_desc
    print(fld_list)
    fld_title = []
    fld_desc = []
    if fld_list is not None:
        while len(fld_list) >= 1:
            fld_title.append(fld_list[0])
            fld_list.pop(0)
            fld_desc.append(fld_list[0])
            fld_list.pop(0)

    colour = color_analytics(colour)
    color = color_analytics(color=color)
    print(color, colour)
    asyncio.run(embed(url, title, desc, colour, color, amount_fld, fld_title, fld_desc))


def start_non_embed(url, text):
    asyncio.run(non_embed(url, text))