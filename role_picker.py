import discord
from discord.ext import commands

async def change_role(interaction, role_name):
    '''
    A function to change a role when a user clicks a button. It will add the role
    if the user does not have it, and remove it if it does have it.
    
    Args:
        interaction: The interaction object
        role_name: The name of the role to change
    '''
    user = interaction.user
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if role in user.roles:
        await user.remove_roles(role)
        await interaction.response.edit_message(content="Removed Role " + role.name)
    else:
        await user.add_roles(role)
        await interaction.response.edit_message(content="Added Role " + role.name)


class PronounView(discord.ui.View):
    @discord.ui.button(label="She/Her", row=0, style=discord.ButtonStyle.blurple) 
    async def she_button_callback(self, button, interaction):
        await change_role(interaction, "She/Her")

    @discord.ui.button(label="He/Him", row=0, style=discord.ButtonStyle.blurple)
    async def he_button_callback(self, button, interaction):
        await change_role(interaction, "He/Him")

    @discord.ui.button(label="They/Them", row=0, style=discord.ButtonStyle.blurple)
    async def they_button_callback(self, button, interaction):
        await change_role(interaction, "They/Them")

    @discord.ui.button(label="Any Pronouns", row=1, style=discord.ButtonStyle.blurple)
    async def any_button_callback(self, button, interaction):
        await change_role(interaction, "Any Pronouns")

    @discord.ui.button(label="Pronouns: Ask Me", row=1, style=discord.ButtonStyle.blurple)
    async def ask_button_callback(self, button, interaction):
        await change_role(interaction, "Pronouns: Ask Me")

    @discord.ui.button(label="Next", row=2, style=discord.ButtonStyle.blurple)
    async def submit_button_callback(self, button, interaction):
        self.clear_items()
        await interaction.response.edit_message(content="Do you want to have the 'AldCo Enthusiast' role? You will get pinged when the server does fun events like movies or online games. You can always run this command again if you change your mind.", view=EnthusiastView())


class EnthusiastView(discord.ui.View):
    @discord.ui.button(label="Yes", row=0, style=discord.ButtonStyle.blurple) 
    async def yes_enthusiant_button_callback(self, button, interaction):
        user = interaction.user
        role = discord.utils.get(interaction.guild.roles, name="AldCo Enthusiast")
        if role in user.roles:
            await interaction.response.edit_message(content="You already have " + role.name)
        else:
            await user.add_roles(role)
            await interaction.response.edit_message(content="Added Role " + role.name)

    @discord.ui.button(label="No", row=0, style=discord.ButtonStyle.blurple)
    async def no_enthusiant_button_callback(self, button, interaction):
        user = interaction.user
        role = discord.utils.get(interaction.guild.roles,name="AldCo Enthusiast")
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.edit_message(content="Removed Role " + role.name)
        else:
            await interaction.response.edit_message(content="You don't have " + role.name)

    @discord.ui.button(label="Next", row=1, style=discord.ButtonStyle.blurple)
    async def submit_button_callback(self, button, interaction):
        self.clear_items()
        await interaction.response.edit_message(content="Last question. What do you believe the best circle constant is? If uncertain, you can just press done.", view=PiTauView())

class PiTauView(discord.ui.View):
    @discord.ui.button(label="π Pi", row=0, style=discord.ButtonStyle.blurple) 
    async def pi_button_callback(self, button, interaction):
        await change_role(interaction, "π gang")

    @discord.ui.button(label="𝜏 Tau", row=0, style=discord.ButtonStyle.blurple)
    async def tau_button_callback(self, button, interaction):
        await change_role(interaction, "𝜏 enjoyer")

    @discord.ui.button(label="𝜏π Pau", row=0, style=discord.ButtonStyle.blurple)
    async def pau_button_callback(self, button, interaction):
        await change_role(interaction, "Pau Heretic")

    @discord.ui.button(label="Done", row=1, style=discord.ButtonStyle.blurple)
    async def submit_button_callback(self, button, interaction):
        self.clear_items()
        await interaction.response.edit_message(content="All done! You can rerun this command at any time if you want to change your roles.", view=self)