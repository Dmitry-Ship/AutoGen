import matplotlib.pyplot as plt

# assume the yielded result is stored in a variable called 'result'
result = [
    {"type": "RECTANGLE", "count": 6908},
    {"type": "STICKER", "count": 1177},
    {"type": "ARROW", "count": 68},
    {"type": "TEXT", "count": 10},
    {"type": "DIAMOND", "count": 9},
    {"type": "STAR", "count": 9},
    {"type": "CIRCLE", "count": 9},
    {"type": "TRIANGLE", "count": 9},
    {"type": "DRAWING", "count": 7},
    {"type": "IMAGE", "count": 4},
    {"type": "EMOJI", "count": 1}
]

# extract the types and counts from the result
types = [item["type"] for item in result]
counts = [item["count"] for item in result]

# create the bar graph
plt.bar(types, counts)
plt.xlabel("Element Type")
plt.ylabel("Count")
plt.title("Element Type Distribution")
plt.show()