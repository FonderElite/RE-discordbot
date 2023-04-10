import discord
import os
from discord.ext import commands
import r2pipe

#test command

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
@bot.event
async def on_message(message):
    if message.author == bot.user:  # ignore messages sent by the bot itself
        return

    if message.content.startswith('!hello'):  # check if message is a command
        name = message.content.split(' ')[1]
        await message.channel.send(f'Hello {name}!')
    elif message.content.startswith('!ping'):
        await message.channel.send('Pong!')
    elif not message.attachments:
        return
    else:
        attachment = message.attachments[0]
        filename = attachment.filename
        file_ext = os.path.splitext(filename)
        content = await attachment.read()

        if file_ext[1] == ".c":
            print(content)
        elif b"ELF" in content:
            # Check if content is hex-encoded
            if content.startswith(b'0x'):
                # Decode hex-encoded content
                content = bytes.fromhex(content.decode('utf-8'))

            # Write binary content to a new file
            new_filename = filename + '.bin'
            with open(new_filename, 'wb') as f:
                f.write(content)

            r2 = r2pipe.open(new_filename)
            await message.channel.send(f"Successfully wrote binary content to {new_filename}")
            r2.cmd('aaa')
            strings_result = r2.cmd("iz")
            await message.channel.send(strings_result)
            info_result = r2.cmd("ii")
            await message.channel.send(info_result)

    await bot.process_commands(message)  # process any bot commands in the message

@bot.command()
async def ping(ctx):
    await ctx.send('pong!')

bot.run("")
