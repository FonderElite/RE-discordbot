import discord,os,subprocess
from discord.ext import commands
import r2pipe

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

#Process files sent by user
@bot.event
async def on_message(message):
    if message.author == bot.user:  # ignore messages sent by the bot itself
        return

    if message.content.startswith('!hello'):  # check if message is a command
        name = message.content.split(' ')[1]
        await message.channel.send(f'Hello {name}!')
    elif message.content.startswith('!ping'):
        await message.channel.send('Pong!')
    elif message.content.startswith('!files'):
        await message.channel.send('Files Listed: ')
    elif message.content.startswith('!pdf'):
        await message.channel.send('Function: ')
    elif message.content.startswith('!afl'):
     await message.channel.send('[Listed Functions]')
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
async def ping(ctx):
    await ctx.send('pong!')
