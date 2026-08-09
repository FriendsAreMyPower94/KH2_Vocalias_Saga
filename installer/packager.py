# -*- coding: utf-8 -*-
"""
===============================================================================
 PACKAGER - CREAZIONE ARCHIVIO CRITTOGRAFATO (patch.pkg)
===============================================================================
 Autore Script: zSavT
 Data Aggiornamento: 2026

 -----------------------------------------------------------------------------
 GUIDA ED ISTRUZIONI D'USO DEL PACKAGER:
 -----------------------------------------------------------------------------
 1. SCOPO DELLO SCRIPT:
    'packager.py' è lo strumento di sviluppo utilizzato dai creatori della mod
    per impacchettare e crittografare i file modificati di Kingdom Hearts II
    in un archivio '.pkg' sicuro (formato ZIP con crittografia AES-256),
    pronto per essere distribuito ed estratto dall'installer.

 2. REQUISITI E FILE NECESSARI:
    - Python 3.9+
    - Librerie elencate in 'requirements.txt' installabili con:
          pip install -r requirements.txt
    - Il file 'chiave.txt' contenente la chiave di cifratura AES-256 in formato testo,
      posizionato nella stessa cartella di 'packager.py'.

 3. COME UTILIZZARE LO SCRIPT (PASSO-PASSO):
    a) Apri il terminale / prompt dei comandi nella cartella dello script.

    b) Per generare un nuovo file 'chiave.txt' con una chiave AES-256 casuale (32 byte):
          python linux/packager.py --gen-key

    c) Per avviare il processo di impacchettamento:
          python linux/packager.py
       - Quando richiesto ("Inserisci il percorso della cartella da zippare:"):
         Inserisci il percorso della cartella contenente i file modificati della mod.
       - Quando richiesto ("Inserisci il nome del file ZIP criptato di output"):
         Premi INVIO per usare il nome di default ('patch.pkg').

 4. NOTE DI COMPILAZIONE EXE DELL'INSTALLER (PYINSTALLER):
    Dopo aver generato 'patch.pkg', l'installer ('installer.py') può essere compilato
    in un file eseguibile stand-alone (.exe / binario Linux) con PyInstaller:
          pyinstaller --noconfirm --onefile --windowed --name "KH2_Vocalias_Saga_Installer" --icon="assets/Logo.ico" --add-data "assets;assets" linux/installer.py
    Consulta le istruzioni dettagliate in 'installer.py' per le opzioni avanzate di compilazione.

===============================================================================
"""

import os       # Per interazioni con il sistema operativo (path, walk, remove)
import sys      # Per terminare lo script in caso di errori critici (sys.exit)
import secrets  # Per la generazione sicura di chiavi crittografiche casuali
import string   # Per la definizione dell'alfabeto della chiave
import pyzipper # La libreria principale per creare archivi ZIP criptati con AES

# Configurazione encoding UTF-8 per console Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# --- Costanti Globali ---
KEY_FILENAME = "chiave.txt"  # Nome del file che deve contenere la chiave di cifratura AES

# --- Funzioni di Utilità ---

def generate_key_file(key_filename=KEY_FILENAME):
    """
    Genera un nuovo file 'chiave.txt' contenente una chiave AES-256 casuale e sicura di 32 caratteri.

    Args:
        key_filename (str): Il nome del file della chiave da creare.

    Returns:
        bytes: La chiave generata codificata in bytes.
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    new_key = ''.join(secrets.choice(alphabet) for _ in range(32))
    with open(key_filename, 'w', encoding='utf-8') as f:
        f.write(new_key + '\n')
    print(f"✨ Nuovo file della chiave '{key_filename}' generato con successo!")
    print(f"🔑 Chiave AES-256 generata (32 caratteri): {new_key}")
    return new_key.encode('utf-8')

def get_input_path(prompt_msg):
    """
    Richiede all'utente di inserire un percorso e continua a chiederlo
    finché non viene fornito un percorso di directory valido.

    Args:
        prompt_msg (str): Il messaggio da mostrare all'utente come prompt.

    Returns:
        str: Il percorso della directory validato fornito dall'utente.
    """
    while True:
        path = input(prompt_msg).strip()
        if os.path.isdir(path):
            return path
        print("❌ Percorso non valido o non è una directory. Riprova.")

def get_output_filename():
    """
    Richiede all'utente il nome base per il file di output e aggiunge
    l'estensione '.pkg'.

    Returns:
        str: Il nome completo del file di output (es. 'mio_archivio.pkg').
    """
    name = input("📦 Nome del file di output (senza estensione): ").strip()
    return f"{name}.pkg"

def confirm(prompt_msg):
    """
    Mostra un messaggio di conferma all'utente e attende una risposta 's' (sì).

    Args:
        prompt_msg (str): Il messaggio di conferma da visualizzare.

    Returns:
        bool: True se l'utente inserisce 's' (ignorando maiuscole/minuscole),
              False altrimenti.
    """
    return input(prompt_msg + " [s/N]: ").lower() == 's'

# --- Funzione Principale di Criptazione ---

def create_encrypted_package(source_folder, output_file, encryption_key):
    """
    Crea un archivio ZIP (.pkg) criptato utilizzando AES-256.

    Comprime i file della cartella sorgente in un file ZIP e lo cifra
    utilizzando la chiave fornita. Gestisce gli errori durante la creazione
    e tenta di rimuovere file parziali in caso di fallimento.

    Args:
        source_folder (str): Il percorso della cartella da archiviare e criptare.
        output_file (str): Il nome completo del file .pkg di output da creare.
        encryption_key (bytes): La chiave AES (come sequenza di byte) da usare
                                per la cifratura. Deve essere adatta per AES-256 (32 byte).
    """
    print(f"\n⚙️  Creazione pacchetto criptato in corso: {output_file}...")
    try:
        with pyzipper.AESZipFile(output_file, 'w',
                                 compression=pyzipper.ZIP_DEFLATED,
                                 encryption=pyzipper.WZ_AES) as zf:
            zf.setencryption(pyzipper.WZ_AES, nbits=256)
            zf.setpassword(encryption_key)

            print("   Aggiunta file all'archivio:")
            for foldername, subfolders, filenames in os.walk(source_folder):
                for filename in filenames:
                    filepath = os.path.join(foldername, filename)
                    arcname = os.path.relpath(filepath, source_folder)
                    print(f"     -> {arcname}")
                    zf.write(filepath, arcname)

        print(f"\n✅ Pacchetto criptato creato con successo: {output_file}")

    except Exception as e:
        print(f"\n❌ Errore critico durante la creazione del pacchetto: {e}")
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
                print(f"   🗑️  File parziale '{output_file}' rimosso.")
            except OSError as remove_error:
                print(f"   ⚠️  Impossibile rimuovere il file parziale '{output_file}': {remove_error}")
        sys.exit(1)


# --- Blocco di Esecuzione Principale ---
if __name__ == "__main__":
    """
    Punto di ingresso dello script. Gestisce il flusso principale:
    - Controllo del flag --gen-key per la creazione diretta di chiave.txt.
    - Lettura / Generazione della chiave AES-256 dal file 'chiave.txt'.
    - Raccolta input ed esecuzione impacchettamento.
    """
    print("\n🔐 Builder CLI per creare un pacchetto criptato (.pkg)")

    # --- Supporto Flag --gen-key ---
    if len(sys.argv) > 1 and sys.argv[1] in ("--gen-key", "-g", "genkey", "--generate-key"):
        generate_key_file(KEY_FILENAME)
        sys.exit(0)

    # --- 1. Lettura o Generazione della chiave dal file ---
    aes_key_from_file = None
    print(f"   Lettura chiave dal file: '{KEY_FILENAME}'...")
    try:
        with open(KEY_FILENAME, 'r', encoding='utf-8') as f_key:
            key_str = f_key.readline().strip()

        if not key_str:
            print(f"⚠️  Attenzione: Il file della chiave '{KEY_FILENAME}' è vuoto.")
            if confirm(f"   Vuoi generare una nuova chiave AES-256 casuale e sovrascrivere '{KEY_FILENAME}'?"):
                aes_key_from_file = generate_key_file(KEY_FILENAME)
            else:
                sys.exit(1)
        else:
            aes_key_from_file = key_str.encode('utf-8')
            key_len = len(aes_key_from_file)
            if key_len != 32:
                print(f"⚠️  Attenzione: La chiave nel file '{KEY_FILENAME}' è lunga {key_len} byte (consigliata: 32 byte per AES-256).")

    except FileNotFoundError:
        print(f"⚠️  File della chiave '{KEY_FILENAME}' non trovato.")
        if confirm(f"   Vuoi generare automaticamente un nuovo file '{KEY_FILENAME}' con una chiave AES-256 casuale?"):
            aes_key_from_file = generate_key_file(KEY_FILENAME)
        else:
            print(f"❌ Errore: Impossibile procedere senza il file '{KEY_FILENAME}'. Operazione annullata.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Errore durante la lettura del file della chiave '{KEY_FILENAME}': {e}")
        sys.exit(1)

    # --- 2. Raccolta input utente ---
    source = get_input_path("📁 Inserisci il percorso della cartella da includere nel pacchetto: ")
    output = "patch.pkg"

    # --- 3. Visualizzazione riepilogo ---
    print(f"\n📋 Riepilogo Operazione:")
    print(f"   - Cartella sorgente:    {source}")
    print(f"   - File pacchetto (.pkg):{output}")
    print(f"   - File chiave usato:    {KEY_FILENAME}")

    # --- 4. Richiesta Conferma ---
    if confirm("\nProcedere con la creazione del pacchetto criptato?"):
        create_encrypted_package(source, output, aes_key_from_file)
    else:
        print("\n⏹️  Operazione annullata dall'utente.")