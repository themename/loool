import tkinter as tk
from tkinter import messagebox
import urllib.request
import json
import os

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("450x550")
        
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        self.current_user_name = None

        # --- Интерфейс ---
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="GitHub User Finder", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(main_frame, text="Введите логин GitHub:").pack()
        self.search_entry = tk.Entry(main_frame, font=("Arial", 12), width=30)
        self.search_entry.pack(pady=5)

        tk.Button(main_frame, text="Найти пользователя", command=self.search_user, 
                  bg="#2ea44f", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

        self.result_label = tk.Label(main_frame, text="", font=("Arial", 10), justify="left")
        self.result_label.pack(pady=10)

        self.add_fav_btn = tk.Button(main_frame, text="⭐ Добавить в избранное", 
                                     state=tk.DISABLED, command=self.add_to_favorites)
        self.add_fav_btn.pack(pady=5)

        tk.Label(main_frame, text="Избранные пользователи:", font=("Arial", 10, "italic")).pack(pady=(15, 0))
        self.fav_listbox = tk.Listbox(main_frame, width=45, height=8)
        self.fav_listbox.pack(pady=5)
        
        self.update_fav_listbox()

    def search_user(self):
        username = self.search_entry.get().strip()
        
        if not username:
            messagebox.showwarning("Внимание", "Поле поиска не должно быть пустым!")
            return

        url = f"https://github.com{username}"
        
        try:
            # Используем стандартный urllib вместо requests
            req = urllib.request.Request(url)
            # GitHub API иногда требует User-Agent для запросов
            req.add_header('User-Agent', 'Python-Urllib-App')
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                self.current_user_name = data['login']
                info = (f"Логин: {data['login']}\n"
                        f"Имя: {data.get('name') or 'Не указано'}\n"
                        f"Репозиториев: {data['public_repos']}\n"
                        f"Подписчиков: {data['followers']}")
                
                self.result_label.config(text=info, fg="black")
                self.add_fav_btn.config(state=tk.NORMAL)
                
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.result_label.config(text="Пользователь не найден", fg="red")
            else:
                messagebox.showerror("Ошибка API", f"Код ошибки: {e.code}")
            self.add_fav_btn.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Ошибка сети", "Не удалось подключиться к API")

    def add_to_favorites(self):
        if self.current_user_name and self.current_user_name not in self.favorites:
            self.favorites.append(self.current_user_name)
            self.save_favorites()
            self.update_fav_listbox()
            messagebox.showinfo("Успех", f"Пользователь {self.current_user_name} сохранен!")

    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return []
        return []

    def save_favorites(self):
        with open(self.favorites_file, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=4)

    def update_fav_listbox(self):
        self.fav_listbox.delete(0, tk.END)
        for user in self.favorites:
            self.fav_listbox.insert(tk.END, user)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
