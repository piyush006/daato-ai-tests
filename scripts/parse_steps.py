import sys

text = sys.argv[1]

steps = []
for part in text.replace(">", ",").split(","):
    step = part.strip()
    if step:
        steps.append({"action": "click", "text": step})

print(steps)
