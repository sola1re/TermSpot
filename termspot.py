import os
import discord
import asyncio
import language_tool_python
from discord.ext import commands
from discord.ui import Button, View
import datetime

# Initialiser le client discord
intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tool = language_tool_python.LanguageTool('fr')
bot = commands.Bot(command_prefix='!',intents=intents)
validity_duration = 20
command_prefix = '!corrige '
command_stats = '!stats'
command_lang = '!lang '
total_fautes_corrige = 0

class EphemeralButton(discord.ui.Button):
    def __init__(self, label, *, style=discord.ButtonStyle.grey):
        super().__init__(style=style, label=label)

    async def callback(self, interaction: discord.Interaction):
        global mistakes, correct, msg
        if correct==mistakes==0:
            await interaction.response.send_message("Pas d'erreurs, toutes mes félicitations",ephemeral=True)
            await interaction.channel.delete_messages([interaction.message])
        else:
            await interaction.response.send_message(f"{mistakes}Voici ton message automatiquement corrigé:\n{correct}", ephemeral=True)
            await msg.delete()
            await interaction.channel.delete_messages([interaction.message])


# Lorsque le bot se lance
@client.event
async def on_ready():
    print('Connecté en tant que {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name="corriger vos fautes"))
    #general_channel = client.get_channel(1083734674611912754)      #idea: 1083734674611912754
                                                                    #termspot: 1083361373678997675
    #await general_channel.send("Bonjour tout le monde, je suis en ligne !\nVous pouvez me ping avec <@1083359393376120892> et m'envoyer un message et je vous dirai s'il y a une erreur !")


# A chaque message envoyé
@client.event
async def on_message(message):
    global total_fautes_corrige, mistakes, correct, msg, tool

    # Si l'auteur du message est le bot lui-même ne rien faire
    if message.author == client.user:
        return

    # Si le message a bien été envoyé dans un chat textuel
    if not isinstance(message.channel, discord.TextChannel):
        return

    # Vérifier si le message commence par le préfixe de la commande personnalisée (stats)
    if message.content.startswith(command_stats):
        await message.reply(f'Depuis que je suis réveillé il y a eu {total_fautes_corrige} fautes.')

    elif message.content.startswith(command_lang):
        text = message.content[len(command_lang):]
        if text in tool.language.languages:
            tool = language_tool_python.LanguageTool(text)
            await message.reply(f"The language has been changed to {text}")
        else:
            await message.reply("I don't know this language.")

    # Vérifier si le message commence par le préfixe corrige
    elif message.content.startswith(command_prefix):
        text = message.content[len(command_prefix):]
        matches = tool.check(text)
        total_fautes_corrige += len(matches)  # Ajouter le nombre de fautes pour les stats
        if matches:
            corrected_text = tool.correct(text)
            # Afficher les règles oubliées par l'utilisateur
            response = f"{message.author.mention} Voici les règles oubliées dans ton message originel : ''{matches[0].context}''\n"
            for correction in matches:
                response += f"- {correction.message}\n"
            response += "\n"
            mistakes = response
            new_correct = tool.correct(corrected_text)
            correct = tool.correct(new_correct)
        else:
            mistakes=0
            correct=0
        msg=message
        view = discord.ui.View()
        view.add_item(EphemeralButton("Clique ici tu as 20 secondes pas encore mais bientôt t'auras que 20 secondes!"))
        await message.reply("Clique si tu veux savoir s'il y a des erreurs ! S'il y en a, ton message originel sera supprimé.", view=view)

    else:
        # Si aucune commandes alors vérifier le texte et le corriger
        matches = tool.check(message.content)
        total_fautes_corrige += len(matches)
        if matches:
            new_text = tool.correct(message.content)
            new_correct_text = tool.correct(new_text)
            corrected_text = tool.correct(new_correct_text)
            await message.delete()
            await message.channel.send(f"{message.author.display_name.split('#')[0]}: {corrected_text}")

    await asyncio.sleep(1) # Ajouter un délai de 1 seconde entre chaque message traité
