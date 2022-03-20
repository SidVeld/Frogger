from frogger.controller import Controller


controller = Controller()
controller.load_scripts()
for number, script in enumerate(controller.scripts):
    print(f"{number + 1}: {script.name}\n{script.description}\nMade by: {script.author}\n\n")

choice = int(input("?\tNumber. Which script we want to run: ")) - 1

controller.scripts[choice].run()
