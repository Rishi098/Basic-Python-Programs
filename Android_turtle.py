import turtle
turtle.speed(20)
turtle.bgcolor("Black")
for i in range(5):
    for colours in ('red', 'magenta', 'blue', 'yellow', 'green', 'white'):
        turtle.color(colours)
        turtle.pensize(10)
        turtle.left(3)
        turtle.forward(200)
        turtle.left(90)
        turtle.forward(200)
        turtle.left(90)
        turtle.forward(200)
        turtle.left(90)
        turtle.title("KING")
app = Tk()
app.geometry("500x500")
app.title("Own Mail send app")
heading = Label(text="Own Python mail sending app", bg="Green", fg="black", font="10", width="500", height="3")
