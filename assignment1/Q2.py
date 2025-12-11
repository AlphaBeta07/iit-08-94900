#10, 21, 4, 7, 8

nums = input("Enter numbers (comma-separated): ")

num_list = [int(x) for x in nums.split(",")]

even = 0
odd = 0

for n in num_list:
    if n % 2 == 0:
        even += 1
    else:
        odd += 1

print("Even numbers:", even)
print("Odd numbers:", odd)
