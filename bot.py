import discord
import os
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError
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

def wipe_temp():
    for path in os.listdir("temp"):
        os.remove(os.path.join("temp", path))

def generate_pdf():
    width_max = height_max = 0
    images = []
    for image in os.listdir("temp"):
        try:
            im = Image.open(os.path.join("temp", image))
        except UnidentifiedImageError:
            pass
        if im.height > height_max:
            height_max = im.height
        if im.width > width_max:
            width_max = im.width
        images.insert(0, im)

    if client.scan_name:        
        base_path = os.path.join(OUTPUT, client.scan_name)
    else:
        base_path = "temp"

    if not os.path.exists(base_path):
        if os.path.sep not in client.scan_name:
            segments = os.path.split(client.scan_name)[1:]
        else:
            segments = os.path.split(client.scan_name)
        for i in range(len(segments)):
            folder_to_create = segments[:i+1]
            directory = os.path.join(OUTPUT, *(folder_to_create))
            if not os.path.exists(directory):
                os.mkdir(directory)

    title = f"{os.path.basename(base_path)}{NAME_CONVENTION}"
    pdf_path = os.path.join(base_path, title)
    canv = canvas.Canvas(pdf_path, pagesize=(width_max, height_max))
    for im in images:
        canv.drawImage(ImageReader(im), 0, height_max-im.height)
        canv.showPage()

    canv.save()
    return pdf_path

client = discord.Client()
client.scanning = False
client.scan_name = None # str type, but bot can be used without a file path

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
        cmd = args[0][1:].lower()
        args = args[1:]
    
    if cmd == "start":
        client.scanning = True
        wipe_temp()
        if len(args) < 1:
            client.scan_name = None
            await message.channel.send("Initialising new temporary scan, will output to attachment only")
            return
        else:
            client.scan_name = args[0]
            await message.channel.send(f"Initialising new scan with output at {os.path.join(OUTPUT, client.scan_name)}...")
            return

    elif cmd == "im":
        if not client.scanning:
            await message.channel.send("No scan is currently in progress. Use $start to begin a scan.")
            return

        if len(message.attachments) < 1:
            await message.channel.send("Error: no image was attached, please enter again.")
            return
        
        for attachment in message.attachments:
            await attachment.save(os.path.join("temp", attachment.filename))

        await message.channel.send("Successfully saved all attachments.")
    
    elif cmd == "end":
        if not client.scanning:
            await message.channel.send("No scan is currently in progress. Use $start to begin a scan.")
            return

        await message.channel.send("Beginning PDF generation...")
        try:
            path = generate_pdf()
        except Exception as error:
            await message.channel.send("An error occurred in generating the PDF.")
            print(error)
        client.scanning = False
        status = "Generated PDF"
        file_size = os.path.getsize(path) 
        if file_size < 8*1024*1024:
            file = discord.File(path)
        else:
            status += f" (file size too large — {file_size} bytes exceeds the {8*1024*1024}-byte limit.)"
            file = None
        await message.channel.send(status, file=file)

        # Could theoretically wipe the temp folder here again, but it is perhaps a little redundant,
        # since starting a new scan will always do this before appending any images anyway.

client.run(TOKEN)