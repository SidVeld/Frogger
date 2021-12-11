import os

scripts_dir = "frogger/scripts"

os.system("cls")


scripts = {}
index = 1
for script in os.listdir(scripts_dir):
    if script.startswith("__"):
        continue
    scripts[index] = script[:-3]
    index += 1

while True:
    for index, script in scripts.items():
        print(f"{index}: {script}")

    selected_script = input("\nSelect script's number: ")

    if not selected_script.isdigit():
        os.system("cls")
        print("You must enter a single number!")
        input("Press any key...")
        os.system("cls")
        continue

    selected_script = int(selected_script)

    if selected_script in list(scripts.keys()):
        break
    else:
        os.system("cls")
        print("No script at this number")
        input("Press any key...")

    os.system("cls")


os.system("cls")
print(f"Selected {selected_script}: {scripts[selected_script]}")
input("Press any key...")

os.system(f"python {scripts_dir}/{scripts[selected_script]}.py")
