import pymysql
import pymysql.cursors
from sshtunnel import SSHTunnelForwarder


# db_file="/Users/evangelinaschnaider/Desktop/programming/IZO_BOT/Poleznye_kartinki.db"
class BotDB:

    def __init__(self):  # открываем подключение
        self.conn = pymysql.connect(
            host='127.0.0.1',
            user='EvaSchneider',
            password='PoleznyeKartinki',
            database='EvaSchneider$default',
            cursorclass=pymysql.cursors.DictCursor
        )

        self.cursor = self.conn.cursor()

    def pic_availability(self, pic_numb):  # проверяем наличие рисунка
        self.cursor.execute(f"SELECT pic_availability FROM pics_for_sale WHERE pic_number={pic_numb}")
        return self.cursor.fetchone()

    def client_to_buy(self, chat_id):
        self.cursor.execute(f"SELECT status FROM pics_for_sale WHERE client_chat_id={chat_id} order by id desc")
        return self.cursor.fetchone()[0]

    def client_to_buy_pic_number(self, chat_id):
        self.cursor.execute(
            f"SELECT pic_number FROM pics_for_sale WHERE client_chat_id={chat_id} and status=0 order by id desc"
        )
        client_status = self.cursor.fetchone()[0]
        if client_status != 0:
            return True
        else:
            return False

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

    def client_name(self, chat_id, name):
        self.cursor.execute(
            f"UPDATE pics_for_sale SET client_name='{name}' WHERE client_chat_id={chat_id}")
        self.conn.commit()

    def availability_update(self, pic_number):
        self.cursor.execute(f"UPDATE pics_for_sale SET pic_availability=0 WHERE pic_number={pic_number} and status=0")
        self.conn.commit()

    def bill_approved_client_ids(self):
        self.cursor.execute("SELECT client_chat_id FROM pics_for_sale WHERE status=1")
        return self.cursor.fetchall()

    def update_bill_sent_status(self, client_chat_id):
        self.cursor.execute(
            f"UPDATE pics_for_sale SET status=1 WHERE client_chat_id={client_chat_id} and status=0")
        self.conn.commit()

    def update_bill_approved_status(self, client_chat_id):
        self.cursor.execute(
            f"UPDATE pics_for_sale SET status=2 WHERE client_chat_id={client_chat_id} and status=1")
        self.conn.commit()

    def track_number(self):
        self.cursor.execute(
            f"SELECT client_chat_id, track_number FROM pics_for_sale WHERE status=2 and track_number!='no'")
        return self.cursor.fetchall()

    def update_envelope_status(self, client_chat_id):
        self.cursor.execute(
            f"UPDATE pics_for_sale SET status=3 WHERE client_chat_id={client_chat_id} and status=2 and track_number!='no'")
        self.conn.commit()

    def envelop_devilered(self):
        self.cursor.execute(f"SELECT client_chat_id FROM pics_for_sale WHERE status=4")
        return self.cursor.fetchall()

    def finalise_purchase(self, client_chat_id):
        self.cursor.execute(
            f"UPDATE pics_for_sale SET status=5 WHERE client_chat_id={client_chat_id} and status=4")
        self.conn.commit()

    # загрузка рисунка на продажу
    def adding_client_pic1(self, client_chat_id):
        self.cursor.execute(
            f"INSERT INTO pics_to_receive (client_chat_id,status) VALUES ('{client_chat_id}', '0')")
        self.conn.commit()

    def checking_client_to_download_pic(self, client_chat_id):
        try:
            self.cursor.execute(
                f"SELECT status FROM pics_to_receive WHERE client_chat_id={client_chat_id} order by id desc")
            if self.cursor.fetchone()[0] == 0:
                return True
            else:
                return False
        except:
            return False

    def adding_client_pic(self, client_chat_id, client_nickname_telergam, client_name, file):
        self.cursor.execute(
            f"UPDATE pics_to_receive SET client_nickname_telergam='{client_nickname_telergam}' WHERE client_chat_id={client_chat_id}")
        self.cursor.execute(
            f"UPDATE pics_to_receive SET client_name='{client_name}' WHERE client_chat_id={client_chat_id}")
        self.cursor.execute(
            f"UPDATE pics_to_receive SET pic='{file}' WHERE client_chat_id={client_chat_id}")

        self.conn.commit()

    def client_name_receive(self, chat_id, name):
        self.cursor.execute(
            f"UPDATE pics_to_receive SET client_name='{name}' WHERE client_chat_id={chat_id}")
        self.conn.commit()

    def photo_pic_from_client_received(self):
        self.cursor.execute("SELECT client_chat_id FROM pics_to_receive WHERE status=1")
        return self.cursor.fetchall()

    def photo_pic_from_client_received_not_approve(self):
        self.cursor.execute("SELECT client_chat_id FROM pics_to_receive WHERE status=10")
        return self.cursor.fetchall()

    def update_photo_received_status(self, client_chat_id):
        self.cursor.execute(
            f"UPDATE pics_to_receive SET status=2 WHERE client_chat_id={client_chat_id} and status=1")
        self.conn.commit()

    def update_photo_received_status_not_approved(self, client_chat_id):
        self.cursor.execute(
            f"UPDATE pics_to_receive SET status=0 WHERE client_chat_id={client_chat_id} and status=10")
        self.conn.commit()

    def check_client_status_for_descr(self, client_chat_id):
        self.cursor.execute(
            f"SELECT status FROM pics_to_receive WHERE client_chat_id={client_chat_id} order by id desc")
        return self.cursor.fetchone()[0]

    def add_pic_info(self, client_chat_id, pic_info):
        self.cursor.execute(
            f"UPDATE pics_to_receive SET pic_info='{pic_info}' WHERE client_chat_id={client_chat_id} and status=2")
        self.conn.commit()

    def update_status_pic_sent(self, client_chat_id):
        self.cursor.execute(
            f"UPDATE pics_to_receive SET status=3 WHERE client_chat_id={client_chat_id} and status=2")
        self.conn.commit()

    def pic_received(self):
        self.cursor.execute(f"SELECT client_chat_id FROM pics_to_receive WHERE status=4")
        return self.cursor.fetchall()

    def update_status_pic_sent_received(self, client_chat_id):
        self.cursor.execute(
            f"UPDATE pics_to_receive SET status=5 WHERE client_chat_id={client_chat_id} and status=4")
        self.conn.commit()

    def pic_received_sold(self):
        self.cursor.execute(f"SELECT client_chat_id FROM pics_to_receive WHERE status=6")
        return self.cursor.fetchall()

    def update_status_pic_sent_received_sold(self, client_chat_id):
        self.cursor.execute(
            f"UPDATE pics_to_receive SET status=7 WHERE client_chat_id={client_chat_id} and status=6")
        self.conn.commit()

    def get_sold_pic_info1(self, client_chat_id):
        self.cursor.execute(f"SELECT pic_name FROM pics_to_receive WHERE client_chat_id={client_chat_id} and status=6")
        return self.cursor.fetchone()

    def get_sold_pic_info2(self, client_chat_id):
        self.cursor.execute(
            f"SELECT pic_price FROM pics_to_receive WHERE client_chat_id={client_chat_id} and status=6")
        return self.cursor.fetchone()

    def get_sold_pic_info3(self, client_chat_id):
        self.cursor.execute(
            f"SELECT pic_location FROM pics_to_receive WHERE client_chat_id={client_chat_id} and status=6")
        return self.cursor.fetchone()

    def get_sold_pic_info4(self, client_chat_id):
        self.cursor.execute(
            f"SELECT money_to_project FROM pics_to_receive WHERE client_chat_id={client_chat_id} and status=6")
        return self.cursor.fetchone()

    def close(self):  # закрываем соденинение
        self.conn.close()
        self.tunnel.close()
