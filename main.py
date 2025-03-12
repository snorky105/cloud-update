import paramiko
import json
import os

# Percorso del file di configurazione
config_file_path = 'config.json'

# Verifica il percorso assoluto del file
print(f"Sto cercando il file di configurazione in: {os.path.abspath(config_file_path)}")

try:
    # Verifica se il file esiste nel percorso specificato
    if not os.path.exists(config_file_path):
        print(f"Errore: Il file di configurazione non è stato trovato in: {os.path.abspath(config_file_path)}")
    else:
        # Carica la configurazione dal file JSON
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
        
        # Itera sui server nella lista
        for server in config['servers']:
            hostname = server['hostname']
            username = server['username']
            password = server['password']
            port = server['port']
            local_path = server['local_path']
            remote_path = server['remote_path']

            # Verifica che il file locale esista
            if not os.path.exists(local_path):
                print(f"Errore: Il file locale {local_path} non esiste.")
                continue  # Passa al prossimo server
            
            # Connessione al server SSH
            print(f"Connessione al server: {hostname}")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, username=username, password=password, port=port)

            # Crea la connessione SFTP per la copia del file
            sftp = ssh.open_sftp()
            
            # Verifica se il file remoto esiste
            try:
                sftp.stat(remote_path)  # Proviamo a ottenere informazioni sul file remoto
                file_exists = True
            except FileNotFoundError:
                file_exists = False

            # Se il file esiste, lo rinominiamo con suffisso "_old" e poi copiamosi il file
            if file_exists:
                print(f"Il file remoto esiste. Rinominando il file remoto...")
                old_remote_path = remote_path.replace(".txt", "_old.txt")
                
                # Verifica se un file con il nome _old esiste già, e se sì, lo cancella
                try:
                    sftp.stat(old_remote_path)
                    print(f"Il file {old_remote_path} esiste già, lo cancello.")
                    sftp.remove(old_remote_path)
                except FileNotFoundError:
                    pass  # Il file non esiste, quindi non facciamo nulla
                
                # Rinominare il file remoto
                sftp.rename(remote_path, old_remote_path)
                print(f"Il file remoto è stato rinominato in: {old_remote_path}")
            
            # Copia il file dal lato locale al lato remoto
            print(f"Sto copiando il file locale nella cartella remota...")
            sftp.put(local_path, remote_path)
            print(f"File copiato con successo sul server {hostname}.")

            # Chiusura della connessione SFTP e SSH
            sftp.close()
            ssh.close()

except FileNotFoundError:
    print(f"Errore: Il file {config_file_path} non è stato trovato.")
except json.JSONDecodeError:
    print("Errore: Il file di configurazione non è valido.")
except KeyError as e:
    print(f"Errore: La chiave {e} non è presente nel file di configurazione.")
except Exception as e:
    print(f"Errore: {e}")