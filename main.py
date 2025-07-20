import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from discord import ButtonStyle, ui
from typing import Optional
import webserver

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Configuration - Update these channel IDs and role ID
VERIFY_CHANNEL_ID = 1105671421482512465  # Set this to your verify-yourself channel ID
MODERATOR_CHANNEL_ID = 1080610190619054230  # Set this to your moderator channel ID
NEW_ARRIVALS_CHANNEL_ID = 1139612578549612574  # Set this to your new arrivals channel ID
VERIFIED_ROLE_ID = 1042601936941236254  # Set this to your verified role ID
UNVERIFIED_ROLE_ID = 1249172101999493150  # Set this to your unverified/pending role ID (optional)


class VerificationModal(ui.Modal, title="Server Verification"):
    def __init__(self):
        super().__init__()
        self.reason = ui.TextInput(
            label="Why do you want to join the W4C Community?",
            placeholder="Enter your reason here (max 500 characters)",
            required=True,
            style=discord.TextStyle.paragraph,
            max_length=500
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        # Create embed for moderator review
        embed = discord.Embed(
            title="New Verification Request",
            description=f"User: {interaction.user.mention} ({interaction.user.name})",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Reason", value=self.reason.value, inline=False)
        embed.set_footer(text=f"User ID: {interaction.user.id}")

        # Create approve/deny buttons
        view = VerificationButtons(interaction.user.id)
        
        # Send to moderator channel
        if MODERATOR_CHANNEL_ID:
            moderator_channel = bot.get_channel(MODERATOR_CHANNEL_ID)
            if moderator_channel:
                await moderator_channel.send(embed=embed, view=view)
                await interaction.response.send_message("Your verification request has been submitted! Please wait for moderator approval.", ephemeral=True)
            else:
                await interaction.response.send_message("Error: Moderator channel not found.", ephemeral=True)
        else:
            await interaction.response.send_message("Error: Moderator channel not configured.", ephemeral=True)

class VerificationButtons(ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @ui.button(label="Approve", style=ButtonStyle.green, custom_id="approve_verification")
    async def approve(self, interaction: discord.Interaction, button: ui.Button):
        user = interaction.guild.get_member(self.user_id)
        if user:
            success_messages = []
            
            # Add verified role
            if VERIFIED_ROLE_ID:
                verified_role = interaction.guild.get_role(VERIFIED_ROLE_ID)
                if verified_role:
                    await user.add_roles(verified_role)
                    success_messages.append("given the verified role")
                else:
                    await interaction.response.send_message("Error: Verified role not found.", ephemeral=True)
                    return
            else:
                await interaction.response.send_message("Error: Verified role not configured.", ephemeral=True)
                return
            
            # Remove unverified role if configured
            if UNVERIFIED_ROLE_ID:
                unverified_role = interaction.guild.get_role(UNVERIFIED_ROLE_ID)
                if unverified_role and unverified_role in user.roles:
                    await user.remove_roles(unverified_role)
                    success_messages.append("removed the unverified role")
            
            # Create success message
            if len(success_messages) == 2:
                message = f"✅ {user.mention} has been approved, {success_messages[0]}, and {success_messages[1]}!"
            else:
                message = f"✅ {user.mention} has been approved and {success_messages[0]}!"
            
            await interaction.response.send_message(message, ephemeral=False)
        else:
            await interaction.response.send_message("Error: User not found in server.", ephemeral=True)
        
        # Disable buttons
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

    @ui.button(label="Deny", style=ButtonStyle.red, custom_id="deny_verification")
    async def deny(self, interaction: discord.Interaction, button: ui.Button):
        user = interaction.guild.get_member(self.user_id)
        if user:
            try:
                await user.kick(reason="Verification denied by moderator")
                await interaction.response.send_message(f"❌ {user.mention} has been denied and kicked from the server.", ephemeral=False)
            except discord.Forbidden:
                await interaction.response.send_message("Error: Bot doesn't have permission to kick users.", ephemeral=True)
        else:
            await interaction.response.send_message("Error: User not found in server.", ephemeral=True)
        
        # Disable buttons
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

class VerificationView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Verify Yourself", style=ButtonStyle.primary, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: ui.Button):
        modal = VerificationModal()
        await interaction.response.send_modal(modal)

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")
    
    # Set up verification message if verify channel is configured
    if VERIFY_CHANNEL_ID:
        verify_channel = bot.get_channel(VERIFY_CHANNEL_ID)
        if verify_channel:
            # Check if verification message already exists
            async for message in verify_channel.history(limit=10):
                if message.author == bot.user and message.components:
                    return  # Verification message already exists
            
            # Create verification message
            embed = discord.Embed(
                title="Server Verification",
                description="Welcome! To gain access to this server, please click the button below to start the verification process.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="What happens next?",
                value="1. Click the 'Verify Yourself' button\n2. Fill out the verification form\n3. Wait for moderator approval\n4. Get access to the server!",
                inline=False
            )
            
            view = VerificationView()
            await verify_channel.send(embed=embed, view=view)

@bot.event
async def on_member_join(member):
    if NEW_ARRIVALS_CHANNEL_ID:
        new_arrivals_channel = bot.get_channel(NEW_ARRIVALS_CHANNEL_ID)
        if new_arrivals_channel:
            embed = discord.Embed(
                title="Welcome!",
                description=f"Welcome {member.mention} to the server! Please head over to {new_arrivals_channel.mention} and click the verification button to get started.",
                color=discord.Color.blue()
            )
            await new_arrivals_channel.send(embed=embed)

@bot.command()
async def setup(ctx):
    """Setup command to configure the bot (Admin only)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You need administrator permissions to use this command.")
        return
    
    await ctx.send("Please update the following variables in main.py:\n"
                   "- VERIFY_CHANNEL_ID: Your verification channel ID\n"
                   "- MODERATOR_CHANNEL_ID: Your moderator channel ID\n"
                   "- VERIFIED_ROLE_ID: Your verified role ID\n"
                   "- UNVERIFIED_ROLE_ID: Your unverified/pending role ID (optional)\n\n"
                   "Then restart the bot for changes to take effect.")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.mention}!")

webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
