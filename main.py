import threading
from customtkinter import *
from socket import *

import base64
import io
from PIL import Image
from tkinter import filedialog


class MainWindow(CTk):
   def __init__(self):
       super().__init__()
       self.geometry('400x300')
       self.label = None
       # menu frame
       self.menu_frame= CTkFrame(self, width=30, height=300)
       self.menu_frame.pack_propagate(False)
       self.menu_frame.place(x=0, y=0)
       self.is_show_menu = False
       self.speed_animate_menu = -5
       self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
       self.btn.place(x=0, y=0)
       #main
       self.chat_field = CTkScrollableFrame(self)
       self.chat_field.place(x=0, y=0)
       self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
       self.message_entry.place(x=0, y=0)
       self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
       self.send_button.place(x=0, y=0)


       self.username = "GEORGE"
       try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("0.tcp.eu.ngrok.io",14160))
            hello = f"TEXT@{self.username}, @[SYSTEM] {self.username} приэднався до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()

       except Exception as e:
           print("ERRO")


       self.adaptive_ui()


   def toggle_show_menu(self):
       if self.is_show_menu:
           self.is_show_menu = False
           self.speed_animate_menu *= -1
           self.btn.configure(text='▶️')
           self.show_menu()
       else:
           self.is_show_menu = True
           self.speed_animate_menu *= -1
           self.btn.configure(text='◀️')
           self.show_menu()
           # setting menu widgets
           self.label = CTkLabel(self.menu_frame, text='Імʼя')
           self.label.pack(pady=30)
           self.entry = CTkEntry(self.menu_frame)
           self.entry.pack()


   def show_menu(self):
       self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
       if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
           self.after(10, self.show_menu)
       elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
           self.after(10, self.show_menu)
           if self.label and self.entry:
               self.label.destroy()
               self.entry.destroy()


   def adaptive_ui(self):
       self.menu_frame.configure(height=self.winfo_height())
       self.chat_field.place(x=self.menu_frame.winfo_width())
       self.chat_field.configure(width=self.winfo_width()-self.menu_frame.winfo_width() - 20,
                                 height=self.winfo_height()-40)
       self.send_button.place(x=self.winfo_width()-50, y=self.winfo_height()-40)
       self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
       self.message_entry.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())


       self.after(50, self.adaptive_ui)

   def recv_message(self):
       buffer = ""

       while True:
           try:
               chunk = self.sock.recv(4096)
               if not chunk:
                   print(2)
                   break
               buffer += chunk.decode("utf-8", errors="ignore")

               while "\n" in buffer:
                   line, buffer = buffer.split("\n", 1)
                   self.handle_line(line.strip())
           except:
               break
       self.sock.close()


   def handle_line(self, line):
        if not line:
            return
        parts = line.split("@",3)
        msg_type = parts[0]
        if msg_type == 'TEXT':
            if len(parts) >= 3:
                autor = parts[1]
                message = parts[2]
                self.add_message(f"{autor}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                b64_img = parts[3]
                try:
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_img = CTkImage(pil_img, size=(300, 300))
                    self.add_message(f"{author} надіслав(ла) зображення: {filename}", img=ctk_img)
                except Exception as e:
                    self.add_message(f"Помилка відображення зображення: {e}")
        else:
            self.add_message(line)

   def add_message(self, text, img = None):
       message_frame = CTkFrame(self.chat_field,fg_color="grey")
       message_frame.pack(pady = 5, anchor =  "w")
       wrap_size = self.winfo_width() - self.menu_frame.winfo_width()-40

       if not img :
           CTkLabel(message_frame, text=text, wraplength=wrap_size, text_color = "white", justify="left").pack(padx = 10, pady = 5)
       else:
           CTkLabel(message_frame, text=text, wraplength=wrap_size, text_color="white", image=img , compound="top", justify="left").pack(padx=10,
                                                                                                             pady=5)


   def send_message(self):
       message = self.message_entry.get()
       if message:
           self.add_message(f"{self.username}: {message}")
           date = f"TEXT@{self.username}@{message}\n"
           try:
                self.sock.sendall(date.encode("utf-8"))
           except:
               pass
       self.message_entry.delete(0,END)

win = MainWindow()
win.mainloop()
