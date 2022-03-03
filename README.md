# Sue - A Discord Bot

## About

Sue is a multi-purpose bot for Discord. It's made for use by Sutekh, the University of Sydney's pop culture and gaming society.

Sue performs three critical tasks for the society:

- She manages polls.
- She rolls dice.
- She tells dad jokes.

## Commands

Commands addressed to Sue should start with the word `$ue`, using a dollar sign instead of an S (so people don't accidentally trigger her).

The following commands are valid:

- `help`: Display a list of commands.
- `roll`: Roll some dice (see Rolling Dice below).
- `dadjoke`: Tell a random dad joke.
- `poll`: Manage polls (see Polls below).

For example, sending the message `$ue dadjoke` in a server where Sue lives will prompt her to respond with a dad joke.

## Rolling Dice

For use with TRPGs and other online games, Sue can perform various dice-rolling functions.

When using the `$ue roll` command, enter dice using standard dice notation. Uppercase Ds and lowercase ds are both fine. Sue will respond with a pseudorandom (python builtin) result. For instance, if you send `$ue roll d20`, she will respond with a random integer from 1 to 20.

You can enter as many dice as you like. This can be achieved through standard notation; for example, `$ue roll 3d8` works fine. You can also enter multiple different kinds of dice space-separated, like `$ue roll d6 2d10 d12`. When rolling multiple dice, Sue will count each individual result *and* add them all up for you. Aren't computers amazing?

If there are too many results to show, Sue will let you know and just tell you the total sum.

## Polls

Sue's biggest feature is her poll-managing capability.

When using `$ue poll`, you should follow up with a valid action for Sue to take. All of them are listed here:

- `make`: Make a new poll.
- `add`: Add a new option to an existing poll.
- `remove`: Remove an existing option from a poll.
- `changeq`: Change the question/description of an existing poll.
- `changeop`: Change the name of an existing poll option.
- `call`: Set a poll as 'called', which updates the poll with all votes and declares the winner/s.
- `delete`: Delete an existing poll.

Polls are identified with a string decided by the user. You can call your poll anything you like; people responding to the poll won't see it unless they read your commands. The purpose of this is to make it easy to distinguish polls from each other, even polls with the same questions and options. (Message IDs aren't exactly user-friendly.)

Options are identified by the reaction (emoji) chosen by the user to represent them. Users respond to polls by adding to the appropriate reaction/s on the poll message.

### make

Syntax: `$ue poll make [poll name] [open/exclusive/binary] <votes> [channel] [question]`

If a poll is open, users may vote for any number of options. If it is exclusive, users may only vote up to a maximum number specified by the `<votes>` field (which should be ignored if the poll is not exclusive). In both of these cases, options can then be specified with `add`.

Binary is a preset type of poll which is already built with two options, 'yes' and 'no'. Users can only vote for one option. Options in binary polls cannot be added, removed or otherwise modified.

The `[channel]` field should not include the hash symbol '#' unless this is actually part of the channel name.

The `[question]` may contain any content that can actually be reproduced in a Discord message.

Examples:

- `$ue poll make games open board-gaming What are your favourite board games?`
- `$ue poll make movie binary movie-voting Did you like the new Marvel film?`
- `$ue poll make rpgs exclusive 1 trpgs Which tabletop RPG have you played the most overall?`

### add

Syntax: `$ue poll add [poll name] [reaction code] [option]`

The reaction code should be an actual, valid reaction that any normal user in the server (and therefore Sue) has permission to use. If it's usable by you, it'll appear as the respective emoji in your message. If you're still having problems, make sure you're not using animated emojis or emojis from other servers.

Example: `$ue poll add games :gem: Azul`

### remove

Syntax: `$ue poll remove [poll name] [reaction code]`

Example: `$ue poll remove games :gem:`

### changeq

Syntax: `$ue poll changeq [poll name] [new question]`

This completely replaces the original question. It does not append the new text to the existing message.

Example: `$ue poll changeq games Which games do you want to play this Friday?`

### changeop

Syntax: `$ue poll changeop [poll name] [reaction code] [new option]`

Note that this by default preserves current votes on the given option.

Example: `$ue poll changeop game :house_abandoned: Betrayal`

### call

Syntax: `$ue poll call [poll name]`

This command is available as a sort of security measure to preserve the question, options and votes on a poll at a particular time. It also reports and displays the final results. For example, if everyone votes to watch *Shrek* one Wednesday night, and you're worried that everyone will change their votes to *Ratatouille* halfway through the movie for some reason (thus making you look very silly), you can call the poll, thus marking upon the poll for all eternity that the actual winner was, in fact, *Shrek*.

That said, executing `call` on a poll again will enable it to be modified and voted upon once again.

Example: `$ue poll call games`

### delete

Syntax: `$ue poll delete [poll name]`

Polls should preferably be deleted when they are no longer needed. This frees up the name of the poll for future use, and lets Sue know that the data associated with the poll is no longer needed.

Note that this action is irreversible (though the message itself isn't deleted).

Example: `$ue poll delete games`
