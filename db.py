import sqlite3


# db_file="/Users/evangelinaschnaider/Desktop/programming/IZO_BOT/Poleznye_kartinki.db"
class BotDB:

    def __init__(self, db_file):  # открываем подключение
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def pic_availability(self, pic_numb):  # проверяем наличие рисунка
        availability_result = self.cursor.execute(f"SELECT pic_availability FROM pics_for_sale WHERE pic_number={pic_numb}")
        return availability_result.fetchone()

    def address_adding(self, pic_numb, address):
        self.cursor.execute(f"UPDATE pics_for_sale SET client_address='{address}' WHERE pic_number={pic_numb}")
        self.conn.commit()

    def client_chat_id(self, pic_number, chat_id):
        self.cursor.execute(f"UPDATE pics_for_sale SET client_chat_id='{chat_id}' WHERE pic_number={pic_number}")
        self.conn.commit()

    def client_name_telegram(self, chat_id, client_name_telegram):
        self.cursor.execute(
            f"UPDATE pics_for_sale SET client_name_telegram='{client_name_telegram}' WHERE client_chat_id={chat_id}")
        self.conn.commit()

    def availability_update(self, pic_number):
        self.cursor.execute(f"UPDATE pics_for_sale SET pic_availability=0 WHERE pic_number={pic_number} and status=0")
        self.conn.commit()

    def bill_approved_client_ids(self):
        bill_sent = self.cursor.execute(
            "SELECT client_chat_id FROM pics_for_sale WHERE status=1")
        return bill_sent.fetchall()

    def update_bill_sent_status(self, client_chat_id):
        self.cursor.execute(
            f"UPDATE pics_for_sale SET status=1 WHERE client_chat_id={client_chat_id} and status=0")
        self.conn.commit()

    def update_bill_approved_status(self, client_chat_id):
        self.cursor.execute(
            f"UPDATE pics_for_sale SET status=2 WHERE client_chat_id={client_chat_id} and status=1")
        self.conn.commit()

    def track_number(self):
        bill_sent = self.cursor.execute(
            f"SELECT client_chat_id, track_number FROM pics_for_sale WHERE status=2 and track_number!='no'")
        return bill_sent.fetchall()

    def update_envelope_status(self, client_chat_id):
        self.cursor.execute(
            f"UPDATE pics_for_sale SET status=3 WHERE client_chat_id={client_chat_id} and status=2 and track_number!='no'")
        self.conn.commit()

    def envelop_devilered(self):
        bill_sent = self.cursor.execute(
            f"SELECT client_chat_id FROM pics_for_sale WHERE status=4")
        return bill_sent.fetchall()

    def finalise_purchase(self, client_chat_id):
        self.cursor.execute(
            f"UPDATE pics_for_sale SET status=5 WHERE client_chat_id={client_chat_id} and status=4")
        self.conn.commit()

    def close(self):  # закрываем соденинение
        self.conn.close()
