from tkinter import *
#from pillow import Image,ImageTk

class Window(Frame):
    
    def __init__(self, master = None):
        Frame.__init__(self, master)

        self.master = master

        self.init_window()

    def init_window(self):
        

        self.master.title("Detect-it")

        self.pack(fill= BOTH, expand=TRUE)

        quitButton = Button(self, text="Quit", command = self.client_exit)

        quitButton.place(x=175,y=230)

        menu = Menu(self.master)
        self.master.config(menu = menu)

        file = Menu(menu)
        file.add_command(label='Save')
        file.add_command(label='Exit',command= self.client_exit)

        menu.add_cascade(label='File',menu=file)

        edit=Menu(menu)

        edit.add_command(label='Undo')
        menu.add_cascade(label='Edit' ,menu=edit)

        run=Menu(menu)
        run.add_command(label='Run    F5')
        menu.add_cascade(label='Run' ,menu=run)

        options=Menu(menu)
        options.add_command(label="Configure")
        menu.add_cascade(label="Options",menu=options)
        
        help=Menu(menu)
        help.add_command(label="Help")
        menu.add_cascade(label="Help",menu=help)

        self.title= Label(self,text="Detect-it")
        self.title.config(font=("Arial Black",25))
        self.title.place(x=self.title.winfo_x()+107,y=self.title.winfo_y()+10)

        self.vno= Label(self,text="version 1.0")
        self.vno.config(font=("Courier",13))
        self.vno.place(x=self.vno.winfo_x()+190,y=self.vno.winfo_y()+52)

        self.own= Label(self,text="By Mohamed Yilmaz")
        self.own.config(font=("Courier",13))
        self.own.place(x=self.own.winfo_x()+219,y=self.own.winfo_y()+260)

        self.url = Label(self,text="Enter the URL:  ")
        self.url.place(x=self.url.winfo_x()+19,y=self.url.winfo_y()+128)
        #self.l1["bg"]="red"
        self.strin=StringVar()
        self.e1=Entry(self,width="37",textvariable=self.strin)
        
        self.e1.insert(0,"Enter the url to be tested for XSS..")
        self.e1.delete(0,END)
        self.e1.grid(row=0,column=1)
        self.e1.place(x=101,y=130)

        

        testButton = Button(self, text="Test",command=self.print_url)
        testButton.place(x=330,y=127)
        
        
    def client_exit(self):
        exit()

    def print_url(self):
        var=self.strin.get()
        if var=='':
            self.url = Label(self,text="Please enter a URL..")
            self.url.place(x=self.url.winfo_x()+95,y=self.url.winfo_y()+168)
        else:
            self.url = Label(self,text="Testing the given URL....")
            self.url.place(x=self.url.winfo_x()+95,y=self.url.winfo_y()+168)

    

root = Tk()
root.geometry("400x300")
app= Window(root)

root.mainloop()
