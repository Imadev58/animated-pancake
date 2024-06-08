import discord
from discord.ext import commands, tasks
import asyncio
from collections import deque

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

MASSDM_CHANNEL_ID = 1248669558777057310

ROLE_DM_LIMITS = {
    1248673481751658697: 45,  # bronze
    1248673558931181650: 70,  # silver
    1248673615789035582: 80,  # gold
    1248673669564334100: 100  # premium
}

EXCLUDED_SERVER_ID = 1247994697687765183
LOG_CHANNEL_ID = None

# Set to keep track of DMed users
dmed_users = set()

# Blacklist dictionary with placeholder IDs
BLACKLISTED_USERS = {

}

# Queue to manage mass DM requests
queue = deque()
QUEUE_LIMIT = 15

def is_massdm_channel(ctx):
    return ctx.channel.id == MASSDM_CHANNEL_ID

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="Powerd by Better - members"))
    process_queue.start()

@tasks.loop(seconds=5)
async def process_queue():
    if queue:
        ctx, server_link, dm_limit = queue.popleft()
        await massdm_handler(ctx, server_link, dm_limit)

@bot.command()
async def massdm(ctx, *, server_link: str):
    if ctx.author.id in BLACKLISTED_USERS:
        await ctx.send("You are blacklisted from using this command.", delete_after=10)
        await ctx.message.delete(delay=2)
        return

    if not is_massdm_channel(ctx):
        await ctx.send("This command can only be used in the designated massdm channel.", delete_after=10)
        await ctx.message.delete(delay=2)
        return

    if not server_link.startswith("https://discord.gg/"):
        await ctx.send("Invalid server invite link. Please provide a valid invite link starting with 'https://discord.gg/'.", delete_after=10)
        await ctx.message.delete(delay=2)
        return

    user_roles = ctx.author.roles
    dm_limit = 10

    for role in user_roles:
        if role.id in ROLE_DM_LIMITS:
            dm_limit = max(dm_limit, ROLE_DM_LIMITS[role.id])

    if len(queue) >= QUEUE_LIMIT:
        await ctx.send("The queue is currently full. Please try again later.", delete_after=10)
        await ctx.message.delete(delay=10)
        return

    queue.append((ctx, server_link, dm_limit))
    position = len(queue)

    embed = discord.Embed(
        title="Mass DM",
        description=f"DMing {dm_limit} Member(s) with: {server_link}\nYou're in queue {position}/{QUEUE_LIMIT}",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Powered By  nightmare and better members")
    await ctx.send(embed=embed, delete_after=3)
    await ctx.message.delete(delay=3)

async def massdm_handler(ctx, server_link, dm_limit):
    dmed_count = 0

    log_embed = discord.Embed(
        title="Mass DM Log",
        description=f"DMing {dm_limit} Member(s) with invite link: {server_link}\nRequested by: {ctx.author}",
        color=discord.Color.red()
    )

    for guild in bot.guilds:
        if guild.id == EXCLUDED_SERVER_ID:
            continue

        members = [member for member in guild.members if not member.bot and member.id not in dmed_users]
        for member in members:
            try:
                if dmed_count >= dm_limit:
                    break
                await member.send(f"Join our server: {server_link}")
                dmed_count += 1
                dmed_users.add(member.id)
                print(f"DMed {member.name} in {guild.name}")
                await asyncio.sleep(3)  # Ensuring 3-second delay between each DM
            except discord.errors.Forbidden:
                print(f"Cannot send DM to {member.name}, skipping.")
            except discord.errors.HTTPException as e:
                print(f"Failed to DM {member.name}: {e}")
                await asyncio.sleep(5)  # Reduced wait time for HTTP exceptions
            except Exception as e:
                print(f"Unexpected error with {member.name}: {e}")

        if dmed_count >= dm_limit:
            break

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(embed=log_embed)

    print(f"Successfully DMed {dmed_count} members.")


bot.run("MTI0ODY3MzE1Mzc0NDM3MTcyMw.GrO8c8.TuPW3E062xF7ZAUTuFBW8-0HS7BAH5frTbenyE")
