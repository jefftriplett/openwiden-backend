import imaplib
import time

CODE_LENGTH = 6


def search_github_verification_code(user: str, password: str, imap_host: str, timeout: int = 60) -> str:
    """
    Connects to the imap server and returns verification code.
    """
    connection = imaplib.IMAP4_SSL(imap_host)

    while True:
        connection.login(user=user, password=password)
        connection.select(mailbox="INBOX")
        typ, data = connection.search(None, '(SUBJECT "[GitHub] Please verify your device")')

        if typ == "OK":
            messages_ids = data[0].split()

            # Check for a new messages
            if len(messages_ids) == 0:
                if timeout > 0:
                    time.sleep(1)
                    timeout -= 1
                    continue
                else:
                    raise Exception("e-mail search failed (timed out).")

            # Fetch last e-mail
            typ, data = connection.fetch(messages_ids[-1], "(RFC822)")

            if typ == "OK":
                email_text = data[0][1]

                # Parse email for code
                search_text = "Verification code: "
                start = email_text.find(search_text.encode()) + len(search_text)
                end = start + CODE_LENGTH
                code = email_text[start:end]

                # Delete all messages before connection close
                for message_id in messages_ids:
                    connection.store(message_id, "+FLAGS", "\\Deleted")
                connection.expunge()

                # Close connection and logout
                connection.close()
                connection.logout()

                # Return code
                return code.decode()
            else:
                raise Exception("Fetch failed")
