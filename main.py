import discord,os,subprocess,re,openai
from discord.ext import commands
import r2pipe,requests
from bs4 import BeautifulSoup
from pyExploitDb import PyExploitDb

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
openai.api_key = "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"


# help pages
page1 = discord.Embed(title="Reverse Engineering Commands", description="Use the buttons below to navigate between help pages.", colour=discord.Colour.orange())
page1.set_thumbnail(url="https://rada.re/r/img/r2logo3.png")
page1.set_image(url="https://www.megabeets.net/uploads/packedup_cover.png")
page1.add_field(name="!files", value="List files in system", inline=False)
page1.add_field(name="!pdf", value="Print dissassembly function",inline=False)

page2 = discord.Embed(title="Bot Help 2", description="Page 2", colour=discord.Colour.orange())
page3 = discord.Embed(title="Bot Help 3", description="Page 3", colour=discord.Colour.orange())

bot.help_pages = [page1, page2, page3]

#Process files sent by user
@bot.event
async def on_message(message):
    if message.author == bot.user:  # ignore messages sent by the bot itself
        return
    if message.content.startswith('!searchsploit'):  # check if message is a command
        await message.channel.send("CVE Search:")
    elif message.content.startswith("!guide"):
        print("Guide")
    elif message.content.startswith('!ping'):
        await message.channel.send('Pong!')
    elif message.content.startswith('!files'):
        await message.channel.send('Files Listed: ')
    elif message.content.startswith('!pdf'):
        await message.channel.send('Function: ')
    elif message.content.startswith('!afl'):
     await message.channel.send('[Listed Functions]')
    elif message.content.startswith('!ai'):
        print('AI envoked')
    elif not message.attachments:
        return
    else:
        attachment = message.attachments[0]
        filename = attachment.filename
        file_ext = os.path.splitext(filename)
        content = await attachment.read()

        if file_ext[1] == ".c":
            with open(filename,'wb') as f:
                f.write(content)
                f.close()
            os.system(f"gcc {filename} -o {file_ext[0]}.bin")
            compiled_file = discord.File(f"{file_ext[0]}.bin")
            await message.channel.send(f"{filename} compiled successfully")
            await message.channel.send(file=compiled_file)

        elif b"ELF" in content:
            # Check if content is hex-encoded
            if content.startswith(b'0x'):
                # Decode hex-encoded content
                content = bytes.fromhex(content.decode('utf-8'))

            # Write binary content to a new file
            elif file_ext[1] == "": 
                new_filename = file_ext[0] + '.bin'
                with open(new_filename, 'wb') as f:
                    f.write(content)
                    f.close()
                await message.channel.send(f"Successfully wrote binary content to {new_filename}")
            else:
                with open(filename, 'wb') as f:
                    f.write(content)
                    f.close()
                r2 = r2pipe.open(filename)
                await message.channel.send(f"Successfully wrote binary content to {filename}")
                r2.cmd('aaa')
                strings_result = r2.cmd("iz")
                await message.channel.send(strings_result)
                info_result = r2.cmd("ii")
                await message.channel.send(info_result)
    await bot.process_commands(message)  # process any bot commands in the message


@bot.command()
async def guide(ctx):
    buttons = [u"\u23EA", u"\u2B05", u"\u27A1", u"\u23E9"] # skip to start, left, right, skip to end
    current = 0
    msg = await ctx.send(embed=bot.help_pages[current])

    for button in buttons:
        await msg.add_reaction(button)

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)

        except asyncio.TimeoutError:
            return print("test")

        else:
            previous_page = current
            if reaction.emoji == u"\u23EA":
                current = 0
                

            elif reaction.emoji == u"\u2B05":
                if current > 0:
                    current -= 1

            elif reaction.emoji == u"\u27A1":
                if current < len(bot.help_pages)-1:
                    current += 1

            elif reaction.emoji == u"\u23E9":
                current = len(bot.help_pages)-1

            for button in buttons:
                await msg.remove_reaction(button, ctx.author)

            if current != previous_page:
                await msg.edit(embed=bot.help_pages[current])

@bot.command()
async def files(ctx):
    list_cmd = os.popen('ls').read()
    await ctx.send(list_cmd)

@bot.command()
async def pdf(ctx,filename,function):
    r = r2pipe.open(filename)
    r.cmd('aaa')
    func = r.cmd(f'pdf @ {function}') # disassamble funtion
    if len(func) > 2000:
        # message is too long, create a file object and send it to Discord
        with open(f'{filename}-{function}',"w") as f:
            f.write(func)
            f.close()
        file = discord.File(f'{filename}-{function}')
        await ctx.send(file=file)
    else:
        await ctx.send(func)

@bot.command()
async def afl(ctx,filename):
    r = r2pipe.open(filename)
    r.cmd('aaa')
    function_list = r.cmd('afl')
    await ctx.send(function_list)


@bot.command()
async def searchsploit(ctx,cveid):
    searchdb = os.popen(f"searchsploit --cve {cveid}").read()
    replacestr = searchdb.replace("-","")
    # Create a new embed object
    embed = discord.Embed(title=f"CVE-{cveid}", description=replacestr, color=0xFF5733)
    # Set the thumbnail for the embed
    embed.add_field(name="MITRE Reference", value="https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=2021-44228", inline=True)

    embed.set_thumbnail(url="https://gitlab.com/uploads/-/system/project/avatar/11903608/kali-exploitdb.png")
    # Set the image for the embed
    embed.set_image(url="https://i.pinimg.com/550x/6e/be/06/6ebe060067479e7e51f3e81b934768ab.jpg")

    # Set the footer for the embed
    embed.set_footer(text="")

    await ctx.send(embed=embed)


bot.run("")
