import matplotlib.pyplot as plt

# assume the query result is stored in a variable called 'result'
result = [{"count": 23}]

# extract the count from the result
count = result[0]["count"]

# create a figure and axis object
fig, ax = plt.subplots()

# create a bar graph with a single bar
ax.bar("Daily Elements", count)

# set the title and labels
ax.set_title("Elements Created Daily")
ax.set_xlabel("Day")
ax.set_ylabel("Count")

# show the plot
plt.show()