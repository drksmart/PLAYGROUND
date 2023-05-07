# def factorial(num):
#     x = 1
#     i = 2
#     while i <= num:
#         x = i * x
#         i += 1
#     return x


# def factorial(num):
#     i = num
#     fact = num
#     while i > 1:
#         fact = fact * (i-1)
#         i -= 1
#     return fact


def factorial(num):
    if num == 1:
        return num
    return num * factorial(num - 1)



print(factorial(int(input("Get the factorial of a number (only whole numbers greater than 0, please)! "))))