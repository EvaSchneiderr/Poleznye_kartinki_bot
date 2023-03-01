import sqlite3


# db_file="/Users/evangelinaschnaider/Desktop/programming/IZO_BOT/Poleznye_kartinki.db"
class BotDB:

    def __init__(self, db_file):  # открываем подключение
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def pic_availability(self, pic_numb):  # проверяем наличие рисунка
        availability_result = self.cursor.execute(f"SELECT availability FROM table1 WHERE pic_number={pic_numb}")
        return availability_result.fetchone()

    def close(self):  # закрываем соденинение
        self.conn.close()
