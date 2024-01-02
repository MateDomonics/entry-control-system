from scanner import Nfc

api = "https://eooorfidlkf4wow.m.pipedream.net"

def callback(uuid: str) -> None:
    pass

if __name__ == "__main__":
    nfc_reader = Nfc(callback)
    nfc_reader.start()
    input("Press RETURN to stop.")
    nfc_reader.stop()