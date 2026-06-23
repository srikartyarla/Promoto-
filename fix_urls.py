import os

files = [f for f in os.listdir('.') if f.endswith('.html')]
old = 'http://127.0.0.1:5000'
new = 'https://promoto-glx0.onrender.com'

for filename in files:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    if old in content:
        content = content.replace(old, new)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {filename}")

print("All done!")