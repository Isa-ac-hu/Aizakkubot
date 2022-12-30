# bot.py

#import statements, we use os, discord, and dotenv
import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from collections import Counter
from urllib.request import urlopen
import emoji
from fuzzywuzzy import fuzz

#intents deal with the permissions of our bot, we set members to true so that it can see all members
intents = discord.Intents.all()
intents.members = True

#allows us to give our bot commands, anything with the prefix $
bot = commands.Bot(command_prefix="$", intents=intents)

#parse our associated env file to get the guild and token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

complete_dictionary = {}
complete_dictionary_of_emojis = {}
list_of_videos = []
combined_dictionary = Counter()

dictionary_of_every_message = {}
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

    youtube_indicator = "/youtu.be/"
    youtube_indicator2 = ".youtube."

    #populate our dictionary with every word thats ever been said
    for member in guild.members:
        member_dictionary = Counter()
        member_emoji_dictionary = Counter()
        message_list = []
        for channel in guild.text_channels:
            async for message in channel.history(limit=None):
                if message.author.name == member.name:
                    message_list.append(message.content)

                    mini_array = message.content.split(' ')
                    for word in mini_array:
                        word = word.lower()
                        #populate our list of youtube videos
                        for i in range(len(mini_array)):
                            if youtube_indicator in mini_array[i] or youtube_indicator2 in mini_array[i]:
                                list_of_videos.append(mini_array[i])
                        #record popular words
                        if word not in member_dictionary:
                            member_dictionary[word] = 0
                            #populate that emoji dictionary
                            if emoji.distinct_emoji_list(word):
                                member_emoji_dictionary[word] = 0
                        member_dictionary[word] = member_dictionary[word] + 1

                        if word not in combined_dictionary:
                            combined_dictionary[word] = 0
                        combined_dictionary[word] = combined_dictionary[word] + 1

                        #populating an emoji dictionary
                        if emoji.distinct_emoji_list(word):
                            member_emoji_dictionary[word] = member_emoji_dictionary[word] + 1

        complete_dictionary[member.name] = member_dictionary
        complete_dictionary_of_emojis[member.name] = member_emoji_dictionary
        dictionary_of_every_message[member.name] = message_list

#help command to tell us what we can do
@bot.command()
async def helpme(ctx):
    await ctx.send("Here's what I can do right now! \n"
             + "1. $commonwords---See what words or emojis people use most often! Takes parameters username, "
                + "integer for number of words to look for, and a True or False if you want to filter common words."
             + "\n2. $recommend---Take a random youtube video that has been posted before and recommends" +
             " it back to you; no parameters"
             + "\n3. $commonemojis--same as common words but emojis only"
               + "\n4. $talkto-- You've all been simulated in AI! Takes parameters"
                 + " username, followed by a string of your message; you will get a response"
                   + " based on the person you input!"
                     + "\n5. $foodfind--scours dining hall menu for when a food returns;"
                       + " since its currently break, the menus are empty. dont try this one.")

@bot.command()
async def talkto(ctx, member: discord.Member, input_string):
    random_num = random.randint(0,30)
    if(random_num < 7):
        message_list = dictionary_of_every_message[member.name]
        final_string = ""
        max_int = 0
        for message in message_list:
            similarity = fuzz.token_set_ratio(message, input_string)
            if(similarity > max_int):
                max_int = similarity
                final_string = message
        await ctx.send(final_string)
    else:
        message_list = list(complete_dictionary_of_emojis[member.name])
        random_num = random.randint(0, len(message_list) - 1)
        await ctx.send(message_list[random_num])

@bot.command()
async def foodfind(ctx, foodname="Cherry cheesecake tart"):
    class FoodType:
        name = ""
        protein = 0
        appearance_dates = []
        unique_date = ""
        meal = ""
        dining_hall = ""

        def __init__(self, name, protein, unique_date, meal, dining_hall):
            self.name = name
            self.protein = protein
            self.unique_date = unique_date
            self.meal = meal
            self.dining_hall = dining_hall

    marciano = "https://www.bu.edu/dining/location/marciano/#menu"
    west = "https://www.bu.edu/dining/location/west/#menu"
    warren = "https://www.bu.edu/dining/location/warren/#menu"

    locations = [marciano, west, warren]
    list_of_foods = []

    for dining_hall in locations:
        page = urlopen(dining_hall)
        html = page.read().decode("utf-8")
        protein_content = 0
        looking_at_contents = True
        content_line = ""
        current_date = ""
        current_meal = ""
        dining_hall_name = ""
        if (dining_hall == locations[0]):
            dining_hall_name = "Marciano"
        elif (dining_hall == locations[1]):
            dining_hall_name = "West"
        elif (dining_hall == locations[2]):
            dining_hall_name = "Warren Towers"

        for line in html.splitlines():
            # fix any strangely read characters
            if "&#039;" in line:
                line = line.replace("&#039;", "'")
            if "&amp;" in line:
                line = line.replace("&amp;", "&")
            if "&quot;" in line:
                line = line.replace("&quot;", "\"")

            # we're looking at a food item
            if "menu-item-title" in line:
                # cut off extraneous pieces of the string
                line = line.split(">", 1)[1]
                line = line.split("<", 1)[0]
                line = line.replace(' ', "_")
                if looking_at_contents:
                    content_line = line
                    looking_at_contents = False
                else:
                    current_food = FoodType(content_line, protein_content, current_date,
                                            current_meal, dining_hall_name)
                    list_of_foods.append(current_food)
                    looking_at_contents = True

                # reset protein content
                protein_content = 0

            # PROTEIN
            elif "menu-nutrition-protein" in line:
                # cut off extraneous pieces of the string
                line = line.split(">")[2]
                line = line.split("<")[0]
                # remove the final g
                line = line[:-1]
                try:
                    line_int = int(line)
                    protein_content += line_int
                except:
                    protein_content = 0

            # we're looking at the date
            elif "menu-bydate-title" in line:
                # cut off extraneous pieces of the string
                line = line.split(">", 1)[1]
                line = line.split("<", 1)[0]
                current_date = line

            elif "meal-period-breakfast" in line:
                current_meal = "Breakfast"
            elif "meal-period-lunch" in line:
                current_meal = "Lunch"
            elif "meal-period-dinner" in line:
                current_meal = "Dinner"

    # we sort our list, the x. part tells us what parameter to sort by
    list_of_foods.sort(key=lambda x: x.name, reverse=False)

    # new idea, we sort the list of foods by name, so that consecutive items will share a name,
    # thus their different unique dates can be compiled into a full list of appearances

    appearances = []
    for i in range(0, len(list_of_foods) - 1):
        if list_of_foods[i].name == list_of_foods[i + 1].name:
            appearances.append(list_of_foods[i].unique_date + " for " + list_of_foods[i].meal)
        else:
            appearances.append(list_of_foods[i].unique_date)
            list_of_foods[i].appearance_dates = appearances
            appearances = []

    list_of_unique_foods = []
    for obj in list_of_foods:
        if obj.appearance_dates:
            list_of_unique_foods.append(obj)

    # because list of foods was already sorted we dont need to sort list of unique foods
    # unless we'd like to sort by something else like protein or date

    def earliest_appearance(food_name):
        for food in list_of_unique_foods:
            if food.name == food_name:
                return "The food you selected will return on " + food.appearance_dates[0]


        return "This food does not appear in our projected range."

    await ctx.send(earliest_appearance(foodname))


#Command that will find the most commonly said words by a given user, along with settings to determine
#how many words to look up, and whether to filter out common words
@bot.command()
async def commonwords(ctx, member: discord.Member, amount: int = 10, is_filtered: bool = False):
    words_blacklist = {"", "the", "of", "and", "a", "to", "in", "is", "you", "that",
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
                       "did", "get", "come", "made", "may", "part"}

    member_words = complete_dictionary[member.name]
    return_list = member_words.most_common(amount + len(words_blacklist))

    #looking at common words across the server
    if(amount == 69):
        member_words = combined_dictionary
        return_list = member_words.most_common(amount + len(words_blacklist))

    #if the command designated for the list to be filtered, our 100 most common words are filtered from selection
    if is_filtered:
        new_list = []
        for word_tuple in return_list:
            if(word_tuple[0] not in words_blacklist):
                new_list.append(word_tuple)
        return_list = new_list

    #here, we construct a final string for the bot to return
    final_string = member.name + "'s most commonly used words are: \n"
    if(amount == 69):
        final_string = "The entire server's most commonly used words are: \n"
    for i in range(amount):
        most_common = return_list[i][0]
        most_common_count = return_list[i][1]
        count = i+1
        final_string = final_string + "\n" + str(count) + ". " \
                       + str(most_common) + " (" + str(most_common_count) + ")"

    await ctx.send(final_string)

#same but for emojis
@bot.command()
async def commonemojis(ctx, member: discord.Member, amount: int = 5):
    member_words = complete_dictionary_of_emojis[member.name]
    return_list = member_words.most_common(amount)

    #here, we construct a final string for the bot to return
    final_string = member.name + "'s most commonly used emojis are: \n"
    for i in range(amount):
        most_common = return_list[i][0]
        most_common_count = return_list[i][1]
        count = i+1
        final_string = final_string + "\n" + str(count) + ". " \
                       + str(most_common) + " (" + str(most_common_count) + ")"

    await ctx.send(final_string)

#scours the server for all posted youtube videos, and returns a random one
@bot.command()
async def recommend(ctx):
    value = random.randint(0, len(list_of_videos)-1)
    await ctx.send("Want a recommendation? Here's a video that was posted on the server at some point")
    await ctx.send(list_of_videos[value])

#random message events I added for fun :)
@bot.event
async def on_message(message):
    cont = message.content.lower()
    if("cool" in cont or "crazy" in cont or "insane" in cont or "nice" in cont):
        await message.channel.send("Thanks!")

    elif("broken" in cont):
        await message.channel.send("stfu im not broken")


    elif("cock" in cont or "balls" in cont or "cum" in cont or "penis" in cont or "dick" in cont):
        emoji = '🤨'
        await message.add_reaction(emoji)
        await message.channel.send("I'm so happy to be acquainted with these normal individuals")

    #generic alonzo reactions
    Alonzo_Reactions = ['ayo', 'nic', 'nb', 'p good']
    if message.author.name == 'azz the orangutan 🦧':
        if any(react in message.content for react in Alonzo_Reactions):
            await message.channel.send("@Alonzo#7717 lmao what a bot")

    #call lillian a meatball about once every 10 messages
    if message.author.name == 'lil the sloth 🦥':
        random_num = random.randint(0,10)
        if random_num == 5:
            emoji = '\N{FALAFEL}'
            await message.add_reaction(emoji)

    c = message.author.name
    if c == 'chan the deer 🦌' or c == 'loser virgin' or c == 'biology loser' or c == 'Groomer' or \
            c == 'stfu chen':
        message = message.lower()
        if "virgin" in message.content or "virginity" in message.content or "VIRIGN" in message.content:
            await message.channel.send("@Chanbanana#2492 no u")
            await message.author.edit(nick="loser virgin")
        elif "cs" in message.content or "CS" in message.content or "comp sci" in message.content:
            await message.channel.send("@Chanbanana#2492 How can you be in a major comprised of 80%"
                                       + " women yet have no bitches to speak of?")
            await message.author.edit(nick="biology loser")
        elif "bitches" in message.content or "BITCHES" in message.content:
            await message.channel.send("@Chanbanana#2492 Stuy freshmen dont count as bitches 💀")
            await message.author.edit(nick="Groomer")
        elif "codes" in message.content or "code" in message.content or "free time" in message.content:
            await message.channel.send("@Chanbanana#2492 my remaining free time is spent engaged in"
                                       + " fruitful coitus interruptus with your mother")
            await message.author.edit(nick="stfu chen")
        else:
            rand_num = random.randint(0,5)
            if rand_num == 3:
                await message.author.edit(nick="chan the deer 🦌")

        if message.author.name == 'kanwar the duck 🦆' or message.author.name == 'indain person':
            rand_num = random.randint(0,5)
            if rand_num == 3:
                await message.channel.send("@ksingh1#8258 ok kanwar")
                await message.author.edit(nick="indain person")
            elif rand_num == 1:
                await message.author.edit(nick="kanwar the duck 🦆")

        if message.author.name == 'lil the sloth 🦥':
            rand_num = random.randint(0, 5)
            if rand_num == 3:
                await message.channel.send("dont kill me haven't you heard of freedom of speech")
            elif rand_num == 4:
                await message.channel.send("Because people don't have wings, they look for ways to fly")


        if message.author.name == 'kelly the penguin 🐧' or message.author.name == 'jelly the penguin 🐧':
            rand_num = random.randint(0,5)
            if rand_num == 3:
                await message.channel.send("@skeai#7165 bakugo titties")
                await message.author.edit(nick="jelly the penguin 🐧")
            elif rand_num == 1:
                await message.author.edit(nick="kelly the penguin 🐧")

        if message.author.name == 'jiamu the horse🐴' or message.author.name == 'bocchi the cock'\
                or message.author.name == 'USER BANNED FOR SWEARING':
            rand_num = random.randint(0,5)
            if ("shit" in cont or "fuck" in cont or "ass" in cont):
                await message.author.edit(nick="USER BANNED FOR SWEARING")
            if rand_num == 3:
                await message.channel.send("its not about the magic, its about the gathering.")
                await message.author.edit(nick="bocchi the cock")
            elif rand_num == 1:
                await message.author.edit(nick="jiamu the horse🐴")

        if message.author.name == 'kai the bear 🐻' or message.author.name == 'tyrone':
            rand_num = random.randint(0, 5)
            if rand_num == 3:
                await message.channel.send("@LinK#9361 2ND BIGGEST CAT IVE EVER SEEN")
                await message.author.edit(nick="tyrone")
            elif rand_num == 1:
                await message.author.edit(nick="kai the bear 🐻")

        if message.author.name == 'azz the orangutan 🦧' or message.author.name == 'bot':
            rand_num = random.randint(0, 5)
            if rand_num == 3:
                await message.channel.send("ayoooo")
                await message.author.edit(nick="bot")
            elif rand_num == 1:
                await message.author.edit(nick="azz the orangutan 🦧")

    await bot.process_commands(message)

bot.run(TOKEN)