import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):
    logging.info('function Invoked')
    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    # TODO: Get connection to database
     
    dbname="techconfdb"
    user="mypgadmin@udazpostgres3"
    password="Jethalal123@"
    host="udazpostgres3.postgres.database.azure.com"
    sslmode = "require"

    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
    conn = psycopg2.connect(conn_string)
    logging.info('after connetion:')
    cursor = conn.cursor()

    try:
        # TODO: Get notification message and subject from database using the notification_id
        cursor.execute("SELECT * FROM notification WHERE id = %s;", (notification_id,))
        notification = cursor.fetchone()

        # TODO: Get attendees email and name
        cursor.execute("SELECT * FROM attendee;")
        attendees = cursor.fetchall()
        attendees_count = str(cursor.rowcount)
        cursor.execute("UPDATE notification SET status = %s, completed_date = %s WHERE id = %s;", ("Notified {} attendees".format(attendees_count), datetime.utcnow(), notification_id))

        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
            send_email(str(attendee[5]), "{} {} {}".format(str(notification[5]), str(attendee[1]), str(attendee[2])), str(notification[2]))

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        cursor.execute("UPDATE notification SET status = %s, completed_date = %s WHERE id = %s;", ("Notified {} attendees".format(attendees_count), datetime.utcnow(), notification_id))

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Connection Closed")


def send_email(email, subject, body):
    logging.info("Sending email: %s", subject)

    admin_email_address = 'test@yopmail.com'
    sendgrid_api_key = '<SENDGRID_API_KEY>'

    message = Mail(
        from_email = admin_email_address,
        to_emails = email,
        subject = subject,
        plain_text_content = body)

    sg = SendGridAPIClient(sendgrid_api_key)
    sg.send(message)