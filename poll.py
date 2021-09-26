import discord

class Poll:
    def __init__(self, message, question, type, votes, owner):
        self.message = message
        self.question = question
        self.type = type
        self.options = {}
        self.disabled = False
        self.owner = owner
        if type == "exclusive":
            self.votes = votes
        elif type == "binary":
            self.votes = 1
        else:
            self.votes = -1

    async def init_binary(self):
        self.options["👍"] = "Yes"
        self.options["👎"] = "No"
        await self.message.add_reaction("👍")
        await self.message.add_reaction("👎")

    async def set_question(self, question):
        try:
            old_content = self.message.content.split("\n")
            new_content = "Poll:\n" + question
            if len(old_content) > 2:
                new_content += "\n" + "\n".join(old_content[2:])
            await self.message.edit(content=new_content)
            return "Question successfully changed."
        except:
            return "There was some error in editing the message. Sorry!"

    async def change_option(self, reaction_code, option):
        if reaction_code not in self.options:
            return "Option not found in poll."

        try:
            self.options[reaction_code] = option
            old_content = self.message.content.split("\n")
            i = 1
            for line in old_content[2:]:
                i += 1
                if line.startswith(reaction_code):
                    old_content[i] = reaction_code + ": " + option
                    new_content = "\n".join(old_content)
                    await self.message.edit(content=new_content)
                    return "Option successfully change."
        except:
            return "There was some error in editing the message. Sorry!"

    async def add_option(self, reaction_code, option):
        try:
            try:
                await self.message.add_reaction(reaction_code)
            except NotFound:
                return "That emoji can't be used by the bot in this server."
            except:
                return "There was some error in adding the reaction. Sorry!"
            self.options[reaction_code] = option
            new_content = self.message.content + "\n" + reaction_code + ": " + self.options[reaction_code]
            await self.message.edit(content=new_content)
            return "Option successfully added."
        except discord.errors.HTTPException:
            return "There was a HTTP Exception while editing the message. That emoji might not be available."
        except discord.errors.Forbidden:
            return "There was a Forbidden error while editing the message."
        except:
            return "There was some error in editing the message. Sorry!"

    async def remove_option(self, reaction_code, client_user):
        if reaction_code not in self.options:
            return "Option not found in poll."

        try:
            try:
                await self.message.remove_reaction(reaction_code, client_user)
            except:
                return "There was some error in removing the reaction. Sorry!"

            old_content = self.message.content.split("\n")
            for i in range(len(old_content) - 2):
                if old_content[i+2].startswith(reaction_code):
                    new_content = "\n".join(old_content[:i+2] + old_content[i+3:])
                    await self.message.edit(content=new_content)
                    del self.options[reaction_code]
                    return "Option successfully removed."
            return "Option not found in message."
        except discord.errors.HTTPException:
            return "There was a HTTP Exception while editing the message. That emoji might not be available."
        except discord.errors.Forbidden:
            return "There was a Forbidden error while editing the message."
        except:
            return "There was some error in editing the message. Sorry!"

    async def call(self):
        if len(self.options) == 0:
            return "Cannot call a poll with no options."

        self.disabled = not self.disabled
        if self.disabled:
            reacts = [react for react in self.message.reactions if react.emoji in self.options]
            reacts.sort(key=lambda x: x.count, reverse=True)
            highest = reacts[0].count
            winners = [react for react in reacts if react.count == highest]
            output = ""
            if len(winners) == 1:
                output += "Winner: " + self.options[reacts[0].emoji]
            else:
                output += "There was a {0}-way tie. Winners:".format(len(winners))
                for winner in winners:
                    output +=  " " + self.options[winner.emoji] + ","
                output = output[:-1]

            new_content = "Poll:\n" + self.question + "\n**" + output + "**"
            output += "\nTotal votes:"
            is_bin = self.type == "binary"

            for react in reacts:
                output += "\n" + self.options[react.emoji] + ": " + str(react.count - 1)
                if not is_bin:
                    new_content += "\n" + react.emoji + ": " + self.options[react.emoji] + " - **" + str(react.count - 1) + "**"

            await self.message.edit(content=new_content)
            return output

        else:
            new_content = "Poll:\n" + self.question
            for code in self.options:
                new_content += "\n" + code + ": " + self.options[code]
            await self.message.edit(content=new_content)
            return "Poll now enabled again."
