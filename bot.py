import discord
import os
from dotenv import load_dotenv
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_GUILD')
OUTPUT = os.getenv('OUTPUT_DIR')
NAME_CONVENTION = os.getenv('NAME_CONVENTION')
PREFIX = "$"

if not os.path.exists("temp"):
    os.mkdir("temp")

def parse_args(argstring: str):
    # This separates each argument of a command into separate list items.
    # Although delimited by spaces, space-containing values can be escaped by encapsulating them inside quotation marks, ""
    # e.g. the following: $print a b "c d e" would result in: ["$print", "a", "b", "c d e"] 
    quotation = False
    args = [""]
    for char in argstring:
        if char == '"':
            quotation = not quotation
        elif char == " " and not quotation:
            args.append("")
        else:
            args[len(args)-1] += char
    
    return args

def wipe_scans():
    for path in os.listdir("temp"):
        os.remove(os.path.join("temp", path))

def generate_pdf():
    width_max = height_max = 0
    images = []
    for image in os.listdir("temp"):
        im = Image.open(os.path.join("temp", image))
        if im.height > height_max:
            height_max = im.height
        if im.width > width_max:
            width_max = im.width
        images.insert(0, im)

    if not os.path.exists(os.path.join(OUTPUT, client.scan_name)):
        os.mkdir(os.path.join(OUTPUT, client.scan_name))
    
    title = f"{os.path.basename(os.path.join(OUTPUT, client.scan_name))}{NAME_CONVENTION}"
    canv = canvas.Canvas(os.path.join(OUTPUT, client.scan_name, title), pagesize=(width_max, height_max))
    for im in images:
        canv.drawImage(ImageReader(im), 0, height_max-im.height)
        canv.showPage()

    canv.save()
    return os.path.join(OUTPUT, client.scan_name, title)

client = discord.Client()
client.scanning = False
client.scan_name = ""

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print("It is available on the following servers: " + ", ".join([guild.name for guild in client.guilds]))

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if not message.content.startswith(PREFIX):
        return
    else:
        args = parse_args(message.content)
        cmd = args[0][1:]
        args = args[1:]
    
    if cmd == "start":
        if len(args) < 1:
            await message.channel.send("Error: filepath for scan output not specified, aborting.")
            return
        else:
            client.scan_name = args[0]

        wipe_scans()
        client.scanning = True
        await message.channel.send(f"Initialising new scan with output at {os.path.join(OUTPUT, client.scan_name)}...")
        return

    elif cmd == "im":
        if len(message.attachments) < 1:
            await message.channel.send("Error: no image was attached, please enter again.")
            return
        
        for attachment in message.attachments:
            await attachment.save(os.path.join("temp", attachment.filename))

        await message.channel.send("Successfully saved all attachments.")
    
    elif cmd == "end":
        path = generate_pdf()
        wipe_scans()
        client.scanning = False
        await message.channel.send("Generated PDF", file=discord.File(path))

client.run(TOKEN)