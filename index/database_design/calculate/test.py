# 原始列表
import random

my_list = [1, 2, 3, 4, 5]

# 抽取 n 个数
n = 10
sampled_numbers = random.choices(my_list, k=n)

print(sampled_numbers)