import commands

async def on_message(client1, message, prefix, command):
    if message.content.startswith(prefix):
        if command.startswith("break "):
            await commands.total_break(message, command)

        elif command.startswith("build "):
            await commands.total_build(message, command)

        elif command.startswith("daily "):
            await commands.daily_score(message, command)

        elif command.startswith("last_login "):
            await commands.last_login(message, command)

        elif command.startswith("mcavatar "):
            await commands.mcavatar(message, command)

        elif command.startswith("stack_eval "):
            await commands.stack_eval64(message, command)

        elif command.startswith("stack_eval64 "):
            await commands.stack_eval64(message, command)

        elif command.startswith("stack_eval16 "):
            await commands.stack_eval16(message, command)

        elif command.startswith("stack_eval1 "):
            await commands.stack_eval1(message, command)

        elif command.startswith("info "):
            await commands.info(client1, message, command)