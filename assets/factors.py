### Find all the factors that 1920 and 1080 have in common.

factors_1920 = {num for num in range(1, 1921) if 1920 % num == 0}
factors_1080 = {num for num in range(1, 1081) if 1080 % num == 0}

print(max(factors_1920 & factors_1080))


print(1280/660)