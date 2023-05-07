# def encrypt_message(str):
#     message = ""
#     alpha = "abcdefghijklmnopqrstuvwxyz"
#     for letter in str:
#         if alpha.index(letter) + 2 <= 25:
#             message += alpha[alpha.index(letter) + 2]
#         else:
#             message += alpha[alpha.index(letter) + 2 - 26]
#     return message
#
# print(encrypt_message("xyz"))

# def word_lengths(str):
#     lengths = []
#     list = str.split(" ")
#     for word in list:
#         lengths.append(len(word))
#     return lengths
#
# print(word_lengths("Somebody stole my donut"))

# def cleanup(list):
#     str = ""
#     cleanlist = []
#     for word in list:
#         if word != "" and word != " ":
#             cleanlist.append(word)
#             str = " ".join(cleanlist)
#     return str
#
# print(cleanup(["cat", " ", "er", "", "pillar"]) )
#
# days = ['Monday', 'Tuesday','Wednesday']
# breakfasts = ['yogurt','donut','biscuit']
# lunches = ['ham sandwich','tacos','salad']
# dinners = ['lasagna','bao','best dinner']
#
# for day, breakfast, lunch, dinner in zip(days, breakfasts, lunches, dinners):
#     print(f'My meals for {day} were {breakfast}, {lunch}, and {dinner}.')

# def destroy_elements(lista, listb):
#     newlist = [num for num in lista if num not in listb]
#     return newlist
#
# print(destroy_elements([1, 2, 3], [4, 5]))






