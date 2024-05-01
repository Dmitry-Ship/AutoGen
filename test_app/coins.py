def min_coins(total):
    # Coins available
    coins = [1, 2, 5, 10]
    # Array to store the minimum coins needed for each amount from 0 to total
    dp = [float('inf')] * (total + 1)
    # No coins are needed to make the sum 0
    dp[0] = 0
    # Iterate over each amount from 1 to total
    for amount in range(1, total + 1):
        # Check each coin
        for coin in coins:
            if coin <= amount:
                dp[amount] = min(dp[amount], dp[amount - coin] + 1)
    # Return the result for the total amount
    return dp[total]

# Example usage
print(min_coins(11))  # Output: 2 (one 1 coin and one 10 coin)

def min_coins_and_coins_used(total):
    # Coins available
    coins = [1,2,5,10, 50, 100, 500, 1000, 2000, 5000, 10000, 50000]
    # Array to store the minimum coins needed for each amount from 0 to total
    dp = [float('inf')] * (total + 1)
    # Array to store the coins used to make each amount
    coin_used = [0] * (total + 1)
    # No coins are needed to make the sum 0
    dp[0] = 0
    # Iterate over each amount from 1 to total
    for amount in range(1, total + 1):
        # Check each coin
        for coin in coins:
            if coin <= amount and dp[amount - coin] + 1 < dp[amount]:
                dp[amount] = dp[amount - coin] + 1
                coin_used[amount] = coin
    # Reconstruct the coins used to make the total
    result = []
    t = total
    while t > 0:
        result.append(coin_used[t])
        t -= coin_used[t]
    return dp[total], result

# Example usage
min_coins_needed, coins_used = min_coins_and_coins_used(23)
print(f"Minimum coins needed: {min_coins_needed}, Coins used: {coins_used}")

