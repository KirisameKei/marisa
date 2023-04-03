import commands

async def on_message(client1, message, prefix, command):
    if message.content.startswith(prefix):
        if command.startswith("daily "):
            await commands.daily_score(message, command)