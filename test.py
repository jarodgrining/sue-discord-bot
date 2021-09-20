import random

def roll_dice(dice):
    rolls = []

    for die in dice:
        ind = die.find("d")

        if ind == -1 or len(die) < 2 or ind == len(die)-1:
            return "Invalid dice entered."

        type = die[ind+1:]
        if not type.isdigit():
            return "Invalid dice entered."

        quantity = 1
        if ind > 0:
            quantity_string = die[:ind]
            if not quantity_string.isdigit():
                return "Invalid quantity of dice entered."
            quantity = int(quantity_string)

        for _ in range(quantity):
            rolls.append(random.randrange(1, int(type)+1, 1))

    output = ""
    for roll in rolls:
        output += str(roll) + " "

    output += "\nTotal: " + str(sum(rolls))

    return output

inp = input("Enter dice to be rolled: ")
dice = inp.split(" ")
results = roll_dice(dice)
print(results)
