import random

import discord
from discord.ext import commands

class PronounView(discord.ui.View):
    @discord.ui.button(label="She/Her", row=0, style=discord.ButtonStyle.blurple) 
    async def she_button_callback(self, button, interaction):
        user = interaction.user
        role = discord.utils.get(interaction.guild.roles, name="She/Her")
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.edit_message(content="Removed Role " + role.name)
        else:
            await user.add_roles(role)
            await interaction.response.edit_message(content="Added Role " + role.name)

    @discord.ui.button(label="He/Him", row=0, style=discord.ButtonStyle.blurple)
    async def he_button_callback(self, button, interaction):
        user = interaction.user
        role = discord.utils.get(interaction.guild.roles,name="He/Him")
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.edit_message(content="Removed Role " + role.name)
        else:
            await user.add_roles(role)
            await interaction.response.edit_message(content="Added Role " + role.name)

    @discord.ui.button(label="They/Them", row=0, style=discord.ButtonStyle.blurple)
    async def they_button_callback(self, button, interaction):
        user = interaction.user
        role = discord.utils.get(interaction.guild.roles,name="They/Them")
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.edit_message(content="Removed Role " + role.name)
        else:
            await user.add_roles(role)
            await interaction.response.edit_message(content="Added Role " + role.name)

    @discord.ui.button(label="Done", row=1, style=discord.ButtonStyle.blurple)
    async def submit_button_callback(self, button, interaction):
        self.clear_items()
        await interaction.response.edit_message(content="Done", view=self)