import discord
import shelve

class Poll:
    def __init__(self, name, question, type, votes, owner_id, channel_id, message_id):

        self.question = question
        self.type = type
        self.options = shelve.open("shelvedoptions/" + name) # closed in main
        self.disabled = False
        self.name = name

        # ids are used to make polls pickleable + not dependent on cache
        self.owner_id = owner_id
        self.channel_id = channel_id
        self.message_id = message_id

        if type == "exclusive":
            self.votes = votes
        elif type == "binary":
            self.votes = 1
        else:
            self.votes = -1

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["options"]
        return state

    def __setstate__(self, d):
        self.__dict__.update(d)
        self.options = shelve.open("shelvedoptions/" + self.name)

    async def init_binary(self, client):
        # in case they don't show up in certain text editors: the below
        # strings are the thumbs up and thumbs down emojis
        self.options["👍"] = "Yes"
        self.options["👎"] = "No"
        # API call not needed to just add reactions => partial message used
        msg = client.get_channel(self.channel_id).get_partial_message(self.message_id)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    async def set_question(self, client, question):
        if self.disabled:
            return "Cannot modify a called poll."

        msg = await client.get_channel(self.channel_id).fetch_message(self.message_id)
        new_content = question
        if len(msg.content) > len(self.question):
            new_content += msg.content[len(self.question):]
        self.question = question
        await msg.edit(content=new_content)
        return "Question successfully changed."

    async def change_option(self, client, reaction_code, option):
        if self.disabled:
            return "Cannot modify a called poll."

        if reaction_code not in self.options:
            return "Option not found in poll."

        try:
            self.options[reaction_code] = option
            msg = await client.get_channel(self.channel_id).fetch_message(self.message_id)
            old_content = msg.content.split("\n")
            i = 1
            for line in old_content[2:]:
                i += 1
                if line.startswith(reaction_code):
                    old_content[i] = reaction_code + ": " + option
                    new_content = "\n".join(old_content)
                    await msg.edit(content=new_content)
                    return "Option successfully change."
        except:
            return "There was some error in editing the message. Sorry!"

    async def add_option(self, client, reaction_code, option):
        if self.disabled:
            return "Cannot modify a called poll."

        if reaction_code in self.options:
            return "That emoji is already in use. Instead, use a different emoji or use '$ue changeop'."

        msg = await client.get_channel(self.channel_id).fetch_message(self.message_id)

        try:
            await msg.add_reaction(reaction_code)
        except NotFound:
            return "That emoji can't be used by the bot in this server."

        self.options[reaction_code] = option
        new_content = msg.content + "\n" + reaction_code + ": " + option
        await msg.edit(content=new_content)
        return "Option successfully added."

    async def remove_option(self, client, reaction_code):
        if self.disabled:
            return "Cannot modify a called poll."

        if reaction_code not in self.options:
            return "Option not found in poll."

        msg = await client.get_channel(self.channel_id).fetch_message(self.message_id)

        await msg.remove_reaction(reaction_code, client.user)

        old_content = msg.content.split("\n")
        for i in range(len(old_content) - 2):
            if old_content[i+2].startswith(reaction_code):
                new_content = "\n".join(old_content[:i+2] + old_content[i+3:])
                await msg.edit(content=new_content)
                del self.options[reaction_code]
                return "Option successfully removed."
        return "Option not found in message."

    async def call(self, client):
        if len(self.options) == 0:
            return "Cannot call a poll with no options."

        msg = await client.get_channel(self.channel_id).fetch_message(self.message_id)
        self.disabled = not self.disabled

        if self.disabled:
            reacts = [react for react in msg.reactions if react.emoji in self.options]
            reacts.sort(key=lambda x: x.count, reverse=True)
            highest = reacts[0].count
            winners = [react for react in reacts if react.count == highest]
            output = ""
            if len(winners) == 1:
                output += "Winner: " + self.options[reacts[0].emoji]
            else:
                output += f"There was a {len(winners)}-way tie. Winners:"
                for winner in winners:
                    output +=  " " + self.options[winner.emoji] + ","
                output = output[:-1]

            new_content = self.question + "\n**" + output + "**"
            output += "\nTotal votes:"
            is_bin = self.type == "binary"

            for react in reacts:
                output += "\n" + self.options[react.emoji] + ": " + str(react.count - 1)
                if not is_bin:
                    new_content += "\n" + react.emoji + ": " + self.options[react.emoji] + " - **" + str(react.count - 1) + "**"

            await msg.edit(content=new_content)
            return output

        else:
            new_content = self.question
            for code in self.options:
                new_content += "\n" + code + ": " + self.options[code]
            await msg.edit(content=new_content)
            return "Poll now enabled again."
