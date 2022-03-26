from frogger.controller import Controller


controller = Controller()

if (controller.test_db_connection() is False):
    print("Database connection error. Finishing job.")
    exit(1)

controller.load_scripts()
for number, script in enumerate(controller.scripts):
    print(f"{number + 1}: {script.name}\n{script.description}\nMade by: {script.author}\n\n")

choice = int(input("?\tNumber. Which script we want to run: ")) - 1

controller.create_driver()
controller.scripts[choice].run()
