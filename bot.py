# bot.py

#import statements, we use os, discord, and dotenv
import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from statistics import mode

#intents deal with the permissions of our bot, we set members to true so that it can see all members
intents = discord.Intents.all()
intents.members = True

#allows us to give our bot commands, anything with the prefix $
bot = commands.Bot(command_prefix="$", intents = intents)

#parse our associated env file to get the guild and token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#we access the client as well as any permissions we intend to give it
#client = discord.Client(intents = intents)

#event that occurs on bot startup
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


#help command to tell us what we can do
@bot.command()
async def helpme(ctx):
    await ctx.send("Here's what I can do right now! \n"
             + "1. $commonwords---See what words or emojis people use most often! Takes parameters username, "
                + "integer for number of words to look for, and a True or False if you want to filter common words."
             + "\n2. $recommend---Take a random youtube video that has been posted before and recommends" +
             " it back to you; no parameters"
             + "\n3. Some other stuff")

#Command that will find the most commonly said words by a given user, along with settings to determine
#how many words to look up, and whether to filter out common words
@bot.command()
async def commonwords(ctx, member: discord.Member, amount: int = 10, is_filtered: bool = False):
    array_of_all_words = []
    words_blacklist = ["", "the", "of", "and", "a", "to", "in", "is", "you", "that",
                       "it", "he", "was", "for", "on", "are", "as", "with", "his",
                       "they", "i", "at", "be", "this", "have", "from", "or", "one",
                       "had", "by", "word", "but", "not", "what", "all", "were", "we",
                       "when", "your", "can", "said", "there", "use", "an", "each",
                       "which", "she", "do", "how", "their", "if", "will", "up", "other",
                       "about", "out", "many", "then", "them", "these", "so", "some",
                       "her", "would", "make", "like", "him", "into", "time", "has",
                       "look", "two", "more", "write", "go", "see", "number", "no",
                       "way", "could", "people", "my", "than", "first", "water", "been",
                       "call", "who", "oil", "its", "now", "find", "long", "down", "day",
                       "did", "get", "come", "made", "may", "part"]
    counter = 0
    #here we look through and break down every single message sent by a particular user into single words in a list
    for guild in bot.guilds:
        for channel in guild.text_channels:
            async for message in channel.history(limit = None):
                if message.author == member:
                    mini_array = message.content.split(' ')
                    array_of_all_words.extend(mini_array)

    #if the command designated for the list to be filtered, our 100 most common words are filtered from selection
    if is_filtered:
        for word in words_blacklist:
            array_of_all_words = list(filter((word).__ne__, array_of_all_words))

    #to maintain consistency in case, we turn every input to lowercase
    for i in range(len(array_of_all_words)):
        array_of_all_words[i] = array_of_all_words[i].lower()

    #here, we construct a final string for the bot to return
    final_string = member.name + "'s most commonly used words are: \n"
    for i in range(amount):
        counter += 1
        most_common = mode(array_of_all_words)
        most_common_count = array_of_all_words.count(most_common)
        final_string = final_string + "\n" + str(counter) + ". " \
                       + str(most_common) + " (" + str(most_common_count) + ")"
        array_of_all_words = list(filter((most_common).__ne__, array_of_all_words))

    await ctx.send(final_string)

#scours the server for all posted youtube videos, and returns a random one
@bot.command()
async def recommend(ctx):
    list_of_videos = []
    youtube_indicator = "/youtu.be/"
    youtube_indicator2 = ".youtube."
    for guild in bot.guilds:
        for channel in guild.text_channels:
            async for msg in channel.history(limit = None):
                mini_array = msg.content.split(' ')
                for i in range(len(mini_array)):
                    if youtube_indicator in mini_array[i] or youtube_indicator2 in mini_array[i]:
                        list_of_videos.append(mini_array[i])

    value = random.randint(0, len(list_of_videos)-1)
    await ctx.send("Want a recommendation? Here's a video that was posted on the server at some point")
    await ctx.send(list_of_videos[value])

#random message events I added for fun :)
@bot.event
async def on_message(message):
    #generic alonzo reactions
    Alonzo_Reactions = ['ayo', 'nic', 'nb', 'p good']
    if message.author.name == 'azz the marci meat':
        if any(react in message.content for react in Alonzo_Reactions):
            await message.channel.send("@Alonzo#7717 lmao what a bot")

    #call lillian a meatball about once every 20 messages
    if message.author.name == 'lil the meatball':
        random_num = random.randint(0,20)
        if random_num == 10:
            emoji = '\N{FALAFEL}'
            await message.add_reaction(emoji)

    await bot.process_commands(message)


bot.run(TOKEN)
