tech_companies = ["Google", "Microsoft", "Blackberry", "IBM", "Yahoo"]

tech_companies[1:4] = ["Facebook", "Apple"]

print(tech_companies)

def length_match(list, num):
    total = 0
    for str in list:
        if len(str) == num:
            total += 1
    return total

print(length_match([], 5))

def sum_from(num1, num2):
    total = 0
    for num in range(num1, num2 + 1):
        total += num
    return total

print(sum_from(9, 12))

def same_index_values(list1, list2):
    final = []
    for index, item in enumerate(list1):
        if list1[index] == list2[index]:
            final.append(index)
    return final

print(same_index_values(["a", "b", "c", "d"], ["c", "b", "a", "d"]))

def only_evens(list):
    final = []
    for num in list:
        if num % 2 == 0:
            final.append(num)
    return final

print(only_evens([]))

def long_strings(list):
    final = []
    for str in list:
        if len(str) >= 5:
            final.append(str)
    return final

print(long_strings(["Acasdse", "Cat", "Jobbbee"]))

def factors(num):
    final = []
    for number in range(1,num +1):
        final.append(number)
    return final

print(factors(10))

listy = ['a','a','b','c','d','e','f','a','a','g','h','c','d','i']

print(listy)

def work(list):
    for item in list:
        if 'c' in list:
            list.remove('c')
    return list

print(work(listy))

def delete_all(list, target):
      for str in list:
        if target in list:
            list.remove(target)
      return list

print(delete_all([5, 3, 5], 5))

def push_or_pop(list):
    final = []
    for num in list:
        if num > 5:
            final.append(num)
        else:
            final.pop(len(final)-1)
    return final

print(push_or_pop([10, 20, 2, 30]))
















