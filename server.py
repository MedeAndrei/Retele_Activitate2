import socket

HOST = "127.0.0.1"
PORT = 9999
BUFFER_SIZE = 1024

# clientii conectati: { adresa_client: True }
clienti_conectati = {}

# mesajele publicate:
# {
#   id_mesaj: {
#       "autor": adresa_client,
#       "text": "continut mesaj"
#   }
# }
mesaje = {}

# generator simplu de ID-uri unice
id_curent = 1


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print("=" * 50)
print(f"SERVER UDP pornit pe {HOST}:{PORT}")
print("Asteptam mesaje de la clienti...")
print("=" * 50)

while True:
    try:
        date_brute, adresa_client = server_socket.recvfrom(BUFFER_SIZE)
        mesaj_primit = date_brute.decode("utf-8").strip()

        if not mesaj_primit:
            raspuns = "EROARE: Mesaj gol."
            server_socket.sendto(raspuns.encode("utf-8"), adresa_client)
            continue

        parti = mesaj_primit.split(" ", 1)
        comanda = parti[0].upper()
        argumente = parti[1] if len(parti) > 1 else ""

        print(f"\n[PRIMIT] De la {adresa_client}: '{mesaj_primit}'")

        # Verificare permisiune pentru comenzile care necesita conectare
        if comanda in ["PUBLISH", "DELETE", "LIST"] and adresa_client not in clienti_conectati:
            raspuns = "EROARE: Nu esti conectat la server."
            server_socket.sendto(raspuns.encode("utf-8"), adresa_client)
            print(f"[TRIMIS] Catre {adresa_client}: '{raspuns}'")
            continue

        if comanda == "CONNECT":
            if adresa_client in clienti_conectati:
                raspuns = "EROARE: Esti deja conectat la server."
            else:
                clienti_conectati[adresa_client] = True
                nr_clienti = len(clienti_conectati)
                raspuns = f"OK: Conectat cu succes. Clienti activi: {nr_clienti}"
                print(f"[SERVER] Client nou conectat: {adresa_client}")

        elif comanda == "DISCONNECT":
            if adresa_client in clienti_conectati:
                del clienti_conectati[adresa_client]
                raspuns = "OK: Deconectat."
                print(f"[SERVER] Client deconectat: {adresa_client}")
            else:
                raspuns = "EROARE: Nu esti conectat la server."

        elif comanda == "PUBLISH":
            if not argumente.strip():
                raspuns = "EROARE: Mesajul nu poate fi gol."
            else:
                mesaje[id_curent] = {
                    "autor": adresa_client,
                    "text": argumente.strip()
                }
                raspuns = f"OK: Mesaj publicat cu ID={id_curent}"
                id_curent += 1

        elif comanda == "DELETE":
            arg = argumente.strip()

            if not arg:
                raspuns = "EROARE: Trebuie furnizat un ID."
            elif not arg.isdigit():
                raspuns = "EROARE: ID-ul trebuie sa fie un numar intreg valid."
            else:
                id_sters = int(arg)

                if id_sters not in mesaje:
                    raspuns = f"EROARE: Nu exista mesaj cu ID={id_sters}."
                elif mesaje[id_sters]["autor"] != adresa_client:
                    raspuns = "EROARE: Nu poti sterge acest mesaj deoarece nu esti autorul."
                else:
                    del mesaje[id_sters]
                    raspuns = f"OK: Mesajul cu ID={id_sters} a fost sters."

        elif comanda == "LIST":
            if not mesaje:
                raspuns = "Nu exista mesaje publicate."
            else:
                linii = ["Lista mesaje:"]
                for msg_id, detalii in mesaje.items():
                    linii.append(f"[{msg_id}] {detalii['text']}")
                raspuns = "\n".join(linii)

        else:
            raspuns = f"EROARE: Comanda necunoscuta '{comanda}'."

        server_socket.sendto(raspuns.encode("utf-8"), adresa_client)
        print(f"[TRIMIS] Catre {adresa_client}: '{raspuns}'")

    except KeyboardInterrupt:
        print("\n[SERVER] Oprire server...")
        break
    except Exception as e:
        print(f"[EROARE] {e}")

server_socket.close()
print("[SERVER] Socket inchis.")
