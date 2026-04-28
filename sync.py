import shutil
import os
import sqlite3

src_dir = r"e:\Приложение диплом\НИИ АЭМ\app"
dst_dir = r"E:\Диплом\Приложение\СовещанияНИИАЭМ\app"

print("Копирование папки app...")
try:
    # Копируем с заменой файлов
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir)
    print("Папка app успешно обновлена.")
except Exception as e:
    print(f"Ошибка при копировании: {e}")

print("Обновление базы данных...")
db_path = r"E:\Диплом\Приложение\СовещанияНИИАЭМ\nii_aem.db"
try:
    conn = sqlite3.connect(db_path)
    conn.execute("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT 1")
    conn.commit()
    conn.close()
    print("Колонка is_active добавлена в БД.")
except Exception as e:
    print("Колонка is_active, вероятно, уже существует или возникла ошибка:", e)

print("Синхронизация завершена.")
