# ScanBot

A simple Discord bot whose function is to generate PDFs from a series of images given to it via attachments.
If possible, it will return the generated PDF as an attachment, so long as it does not exceed the 8MB attachment limit.
If this is not possible, the generated PDF will still remain on the filesystem of the server running the bot. (This can be your own device if you so please.) Thus there is also a mode of operation which allows you to specify what permanent directory the PDF should be saved into, thereby allowing a user running the bot on their own machine to access its output directly without relying on the attachment feature of Discord, throttled by the 8MB size limit.

## Commands
The prefix is set to `$` by default, but can be modified trivially in the source file. Any text that starts with the prefix has the potential to be interpreted as a command, but only the following commands result in an action: 
`$start`: Begins a new PDF scan. This may be given an argument, which is a filepath under which to save the PDF on the host's system. Note that this path is relative to the OUTPUT_DIR environment variable, although specifying an absolute path should be possible too.
With no arguments, the PDF generated is saved to the `temp` folder of the bot's working directory. This is then potentially uploaded as an attachment as applicable.

`$im`: Adds up to 10 images to the bot's list of images to compile. The images must be given as attachments to the command message. (Note that this limit of 10 is imposed by the Discord API, and not the bot. Although generating the PDF of 10+ images is technically wholly feasible, it is highly improbable that the resultant filesize will not exceed 8MB, so this should only ever be done with a fixed path and using the local filesystem to retrieve what was generated; alternatively, exceedingly small image files are also possible.)

`$end`: Begins the generation process and thus saves the PDF to the respective location on disk. This may be the `temp` directory, or whatever path was specified by the user. It will upload the PDF as an attachment if it doesn't surpass 8MB; you get the drill.

## .env
There must be a `.env` file present in the bot's directory in order for it to function. It requires the following values:
`DISCORD_TOKEN`: The bot account's token. If you want to run this using your own bot account, you will need to copy its token here.

`OUTPUT_DIR`: The base path, relative to which PDFs are saved if an argument to $start is provided. For example, if `OUTPUT_DIR` is `/home/username/Documents/`, and you type `$start "Homework/Day 1"`, then the PDF will be output to the directory `/home/username/Documents/Homework/Day 1`. This can be set to whatever you like, and inputting absolute paths is entirely acceptable as well.

`NAME_CONVENTION`: A suffix that is appended to all PDF filenames generated, perhaps to identify yourself or something about the scan. May include personal information, so it is better kept in the `.env` file.