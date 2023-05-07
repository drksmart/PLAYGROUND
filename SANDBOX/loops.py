# string="Derek Smart"
#
# def reverse(str):
#     i = len(str) - 1
#     rts = ""
#     while i >= 0:
#         rts = rts + str[i]
#         i -= 1
#     return print(rts)
# reverse(string)

# these both do the same thing. the one above uses a while loop, and the one below uses recursion
# first thing is to figure out what the base case should be for the recursion scenario


string="Derek Smart"

def reverse(str):
    if len(str) <= 1:
        return str
    return str[-1] + reverse(str[:-1])

print(reverse(string))




