@bot.command()
async def history(ctx):
    if ctx.message.author.id == my_user_id:
        await ctx.send("Started fetching messages info...")
        t1 = time.time()
        messages_limit = 10000000
        buffer_limit = 2500
        i = 0
        msg_count = 0
        user_csv_data = "user_csv_data.csv"
        user_csv_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_histories", user_csv_data)
        with open(user_csv_data_path, "a", encoding="utf-8") as fc:
            writer = csv.writer(fc, delimiter=',')
            csv_list = []
            async for message in ctx.channel.history(limit=messages_limit):
                if message.author.bot is False:
                    msg_count += 1
                    csv_list.append([str(message.author.id), message.content])
                    i += 1
                    if i >= buffer_limit:
                        writer.writerows(csv_list)
                        csv_list = []
                        i = 0
                else:
                    pass
            t2 = time.time()
            await ctx.send("Time taken: {0} seconds. Fetched {1} message/s.".format(round(t2 - t1), msg_count))
            print(t2 - t1)
            return
    else:
        await ctx.send("This command can only be called be the bot's owner.")
        return
