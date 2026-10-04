import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import exifread
import piexif
import shutil
from PIL import Image, ImageTk
import os

class EXIFAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("OSINT Metadata Analyzer & Cleaner")
        self.root.geometry("700x650")
        self.root.configure(bg='#2c3e50')
        
        # Заголовок
        title = tk.Label(root, text="Анализатор и очиститель метаданных", 
                        font=('Arial', 16, 'bold'), bg='#2c3e50', fg='white')
        title.pack(pady=15)
        
        # Кнопка выбора файла
        self.btn_select = tk.Button(root, text="📁 Выбрать изображение", 
                                    command=self.select_file,
                                    font=('Arial', 12), bg='#3498db', fg='white',
                                    width=22, height=2)
        self.btn_select.pack(pady=5)
        
        # Кнопка удаления метаданных (изначально отключена)
        self.btn_clean = tk.Button(root, text="🗑️ Удалить метаданные", 
                                   command=self.remove_metadata,
                                   font=('Arial', 12), bg='#e74c3c', fg='white',
                                   width=22, height=2, state=tk.DISABLED)
        self.btn_clean.pack(pady=5)
        
        # Область для отображения изображения
        self.image_label = tk.Label(root, bg='#2c3e50')
        self.image_label.pack(pady=10)
        
        # Текстовое поле для результатов
        self.result_text = scrolledtext.ScrolledText(root, height=12, width=70,
                                                      font=('Consolas', 10),
                                                      bg='#ecf0f1', fg='#2c3e50')
        self.result_text.pack(pady=10, padx=20)
        
        self.current_file = None
    
    def select_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg")]
        )
        if filepath:
            self.current_file = filepath
            self.btn_clean.config(state=tk.NORMAL) # Включаем кнопку очистки
            self.analyze(filepath)
    
    def remove_metadata(self):
        if not self.current_file:
            return
        
        # Запрос подтверждения
        confirm = messagebox.askyesno(
            "Подтверждение", 
            "Вы уверены, что хотите удалить все метаданные?\n"
            "Будет создана безопасная копия файла с суффиксом '_clean'."
        )
        
        if not confirm:
            return
        
        try:
            # Создаем имя для нового файла
            base, ext = os.path.splitext(self.current_file)
            clean_file = f"{base}_clean{ext}"
            
            # Копируем оригинал, чтобы не испортить его
            shutil.copy2(self.current_file, clean_file)
            
            # Удаляем EXIF из копии
            piexif.remove(clean_file)
            
            messagebox.showinfo(
                "Успех!", 
                f"Метаданные успешно удалены!\n\n"
                f"Оригинал сохранен.\n"
                f"Чистая копия сохранена как:\n{clean_file}"
            )
            
            self.result_text.insert(tk.END, f"\n✅ Файл очищен: {os.path.basename(clean_file)}\n")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить метаданные:\n{e}")

    def analyze(self, filepath):
        self.result_text.delete(1.0, tk.END)
        
        try:
            img = Image.open(filepath)
            img.thumbnail((250, 250))
            photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
        except Exception:
            pass
        
        self.result_text.insert(tk.END, f"📄 Файл: {os.path.basename(filepath)}\n")
        self.result_text.insert(tk.END, "="*60 + "\n\n")
        
        try:
            with open(filepath, 'rb') as f:
                tags = exifread.process_file(f, details=False)
            
            if tags:
                self.result_text.insert(tk.END, f"✅ Найдено параметров: {len(tags)}\n\n")
                
                important_tags = {
                    'Image Model': '📱 Модель устройства',
                    'Image Make': '🏭 Производитель',
                    'Image DateTime': '📅 Дата изменения',
                    'EXIF DateTimeOriginal': '📷 Дата съемки',
                    'GPS GPSLatitude': ' Широта',
                    'GPS GPSLongitude': '🌍 Долгота',
                    'Image ImageWidth': '📏 Ширина',
                    'Image ImageLength': '📐 Высота'
                }
                
                for tag, description in important_tags.items():
                    if tag in tags:
                        self.result_text.insert(tk.END, f"{description}: {tags[tag]}\n")
                
                self.result_text.insert(tk.END, "\n" + "="*60 + "\n")
                self.result_text.insert(tk.END, "⚠️ РЕКОМЕНДАЦИЯ:\n")
                self.result_text.insert(tk.END, "Нажмите красную кнопку выше, чтобы создать\n")
                self.result_text.insert(tk.END, "безопасную копию без этих данных!\n")
            else:
                self.result_text.insert(tk.END, "⚠️ Метаданные не найдены.\n")
                self.result_text.insert(tk.END, "Файл уже безопасен для публикации.\n")
                
        except Exception as e:
            self.result_text.insert(tk.END, f"❌ Ошибка анализа: {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = EXIFAnalyzer(root)
    root.mainloop()