import customtkinter
def button_event():
    print("button pressed")

app = customtkinter.CTk()
app.geometry("600x500")
app.title("customTkinter GUI demo")


button = customtkinter.CTkButton(app, text="CTkButton", command=button_event)
button.pack()

frame = customtkinter.CTkFrame(master=app, width=200, height=200, fg_color="gray")
customtkinter.CTkLabel(frame,text="This is line 1").pack()
customtkinter.CTkLabel(frame,text="This is line 2").pack()

frame.pack()


entry = customtkinter.CTkEntry(app, placeholder_text="CTkEntry")
entry.pack()
app.mainloop()