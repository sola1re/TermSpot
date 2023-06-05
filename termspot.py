######################
# Created By Kazulhu #
#    2022 - 2023     #
######################

import discord
from discord.ext import commands
import language_tool_python
from random import randint
import os

tool = language_tool_python.LanguageTool('fr')
global total_fautes_corrige  # Number of mistakes corrected
intents = discord.Intents.default()
intents.message_content = True

# Generation of a forbidden characters list
forbidden_list = []
for i in range(8):
    forbidden_list.append(chr(randint(97, 122)))
forbidden_word = ''.join(forbidden_list)
print(f"Here is the forbidden word : '{forbidden_word}'")

client = discord.Bot(intents=intents)

# Path to the file for storing error count
ERROR_COUNT_FILE = 'error_count.txt'


def load_error_count():
    if os.path.isfile(ERROR_COUNT_FILE):
        with open(ERROR_COUNT_FILE, 'r') as file:
            try:
                return int(file.read())
            except ValueError:
                return 0
    else:
        return 0


def save_error_count(count):
    with open(ERROR_COUNT_FILE, 'w') as file:
        file.write(str(count))


# Load the initial error count
total_fautes_corrige = load_error_count()


@client.event
async def on_ready():
    print('Connecté en tant que {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name="corriger vos fautes"))


def text_correction(text):
    global total_fautes_corrige
    matches = tool.check(text)
    total_fautes_corrige += len(matches)
    save_error_count(total_fautes_corrige)
    if matches:
        corrected_text = tool.correct(text)
        corrected_list = corrected_text.split(' ')
        for i in range(len(corrected_list)):
            corrected_text = tool.correct(corrected_text)
        if corrected_text==None:
            return text
        return corrected_text


def mistakes(text):
    global total_fautes_corrige
    matches = tool.check(text)
    total_fautes_corrige += len(matches)
    save_error_count(total_fautes_corrige)
    if matches:
        # Afficher les règles oubliées par l'utilisateur
        response = f"Voici les règles oubliées dans ton message originel : ''{matches[0].context}''\n"
        for correction in matches:
            response += f"- {correction.message}\n"
        response += "\n"
        mistakes = response
    else:
        mistakes = 0
    return mistakes


@client.slash_command(name='cor', description='Send your message with no mistakes')
async def cor_command(ctx: commands.Context, text: str):
    await ctx.respond("Le message corrigé devrait être envoyé d'ici quelques secondes.",ephemeral=True)
    await ctx.channel.send(f"***{ctx.author.display_name.split('#')[0]} :*** {text_correction(text)}")


@client.slash_command(name='exp', description='Corrects the given text and provides error suggestions')
async def exp_command(ctx: commands.Context, text: str):
    answer = mistakes(text)
    if answer == 0:
        await ctx.respond(content="Pas d'erreurs, toutes mes félicitations",ephemeral=True)
    else:
        await ctx.respond(content=answer,ephemeral=True)


@client.slash_command(name='stats', description='Shows the number of errors corrected by the bot')
async def stats_command(ctx: commands.Context):
    await ctx.respond(f'Depuis que je suis publié il y a eu {total_fautes_corrige} fautes.')


@client.slash_command(name='help', description="Shows all the commands of TermSpot(it's me)")
async def help_command(ctx: commands.Context):
    embed = discord.Embed(
        title="Commandes",
        description="Voici toutes les commandes que tu peux utiliser grâce à moi:",
        color=discord.Colour.blurple(),  # Pycord provides a class with default colors you can choose from
    )
    embed.add_field(name="/cor <insert text>", value="J'envoie ton message à ta place mais corrigé", inline=True)
    embed.add_field(name="/exp <insert text>", value="Explique les erreurs commises dans ton message", inline=True)
    embed.add_field(name="/stats", value="Envoie le nombre d'erreurs corrigées par le bot depuis qu'il est en ligne", inline=True)
    embed.add_field(name="/help", value="Tu viens d'utiliser cette commande", inline=True)
    embed.set_author(name="TermSpot", icon_url="https://imgur.com/iVSj45a.png")
    embed.set_thumbnail(url="https://imgur.com/iVSj45a.png")
    await ctx.respond(embed=embed)

client.run('token')
