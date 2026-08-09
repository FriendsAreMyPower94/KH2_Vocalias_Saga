# -*- coding: utf-8 -*-
"""
===============================================================================
 KINGDOM HEARTS II FINAL MIX - MOD VOCALIAS SAGA INSTALLER
===============================================================================
 Mod: Mod di doppiaggio e adattamento in italiano di KINGDOM HEARTS II Final Mix
 Mod By: VOCALIA Studios (https://www.youtube.com/@vocaliastudio)
 Autore Installer: SavT (https://savtchannel.altervista.org/)
 Versione Installer: 3.0

 -----------------------------------------------------------------------------
 GUIDA ED ISTRUZIONI D'USO DELL'INSTALLER:
 -----------------------------------------------------------------------------
 1. PRE-REQUISITI E FILE NECESSARI:
    Affinché l'installer funzioni correttamente, devono trovarsi nella stessa
    cartella dell'eseguibile/script i seguenti file:
    - 'patch.pkg' : L'archivio criptato contenente i file di gioco moddati.
    - 'chiave.txt': Il file di testo contenente la chiave di cifratura AES-256
                    necessaria per decriptare 'patch.pkg'.
    - 'assets/'   : La cartella contenente immagini, font ('Cinzel', 'Exo 2')
                    ed icone dell'interfaccia utente.

 2. ESECUZIONE DA PYTHON (SVILUPPO / AMBIENTE LOCALE):
    - Requisiti: Python 3.9+ e le librerie elencate in 'requirements.txt'.
    - Comando per installare le dipendenze:
          pip install -r requirements.txt
    - Comando per avviare l'installer:
          python linux/installer.py

 3. ESECUZIONE DA ESEGUIBILE COMPILATO:
    - Su Windows / Linux / Steam Deck, è sufficiente avviare l'eseguibile
      compilato (es. 'installer.exe' o l'eseguibile binario Linux).

 4. FLUSSO GUIDATO DI INSTALLAZIONE:
    a) Menu Principale (COMANDI): Premi "▶ INSTALLA" per iniziare.
    b) Controllo File Patch (ELABORATORE): Verifica automatica di 'patch.pkg' e 'chiave.txt'.
    c) Informazioni (DIARIO DI GRILLO): Avvisi sulle fonti ufficiali e supporto.
    d) Licenza (CONFIGURAZIONE): Accettazione dei termini di licenza d'uso.
    e) Selezione Cartella (MAPPA DEI MONDI): Selezione della cartella di installazione
       di Kingdom Hearts II Final Mix e avvio dell'estrazione con backup opzionale.

 5. COME COMPILARE L'ESEGUIBILE (.EXE / BINARIO LINUX) CON PYINSTALLER:
    Per creare l'eseguibile stand-alone distribuiscibile, installa PyInstaller
    ed esegui uno dei seguenti comandi dal terminale:

    a) Installare PyInstaller e Dipendenze:
          pip install -r requirements.txt

    b.1) Comando di Compilazione su Windows (File Singolo .exe):
          pyinstaller --noconfirm --onefile --windowed --name "KH2_Vocalias_Saga_Installer" --icon="assets/Logo.ico" --add-data "assets;assets" linux/installer.py

    b.2) Comando di Compilazione su Linux / Steam Deck (Binario Eseguibile):
          pyinstaller --noconfirm --onefile --windowed --name "KH2_Vocalias_Saga_Installer_Linux" --add-data "assets:assets" linux/installer.py

    N.B.: L'eseguibile generato verrà salvato nella cartella 'dist/'. Ricordati di
    posizionare i file 'patch.pkg' e 'chiave.txt' nello stesso percorso dell'eseguibile.

===============================================================================
"""

import sys
import os
import platform
import webbrowser
import subprocess
import traceback
import shutil
import datetime
import pyzipper
import urllib.request
import json
from packaging import version

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFrame,
    QStackedWidget, QFileDialog, QTextEdit, QLineEdit, QMessageBox,
    QProgressBar, QHBoxLayout, QDialog, QDialogButtonBox, QInputDialog,
    QStyle, QTextBrowser, QCheckBox, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import (
    QPixmap, QFont, QIcon, QCursor, QPalette, QColor, QFontDatabase,
    QPainter
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QSize, QPoint, QTimer, QUrl
)

# --- Funzione per aprire URL in modo sicuro (Fix per Steam Deck / Linux) ---
def apri_url(url):
    print(f"Apertura URL: {url}")
    try:
        if platform.system() == "Linux":
            env = os.environ.copy()
            env.pop("LD_LIBRARY_PATH", None)
            
            subprocess.Popen(['xdg-open', url], env=env)
        else:
            webbrowser.open(url)
    except Exception as e:
        print(f"Impossibile aprire il browser per {url}: {e}")

# --- Funzione Resource Path ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- Costanti Globali & Link ---
CHIAVE = "chiave.txt"
DEFAULT_FOLDER_NAME = ""
LOG_FILE = "install_log.txt"
PACKAGE_FILE = "patch.pkg"
IMG_FILE = resource_path("assets/img.png")
LOGO_ICO = resource_path("assets/Logo.ico")
HEAD_ICON_PATH = resource_path("assets/head_icon.png")
YT_ICON = resource_path("assets/youtube.png")
GH_ICON = resource_path("assets/github.png")
WEB_ICON = resource_path("assets/web.png")
VERSIONE = "v0.1.0"

# --- Link Ufficiali ---
SAVT_SITE_URL = "https://savtchannel.altervista.org/"       # Sito personale di SavT (usato SOLO se si clicca su 'Installer By SavT')
VOCALIA_YT_URL = "https://www.youtube.com/@vocaliastudio"    # Canale YouTube ufficiale di Vocalia Studios
VOCALIA_GH_URL = "https://github.com/FriendsAreMyPower94/KH2_Vocalias_Saga" # Repository GitHub ufficiale Vocalia Studios
VOCALIA_WEB_URL = "https://www.youtube.com/@vocaliastudio"   # Link principale Vocalia Studios

# Costanti di riferimento che puntano tutte a Vocalia Studios
YT_URL = VOCALIA_YT_URL
GH_URL = VOCALIA_GH_URL
WEB_URL = VOCALIA_WEB_URL
ALT_SITE_NAME = "Vocalia Studio"
ALT_SITE_URL = VOCALIA_YT_URL

CREDITI_MOD = "Mod By 𝐕𝐎𝐂𝐀𝐋𝐈𝐀 𝑺𝒕𝒖𝒅𝒊𝒐𝒔"
CREDITI_INSTALLER = "Installer By SavT"
CREDITI = f"{CREDITI_MOD} | {CREDITI_INSTALLER}"
EXE_NAME = "KINGDOM HEARTS II FINAL MIX.exe"
EXE_SUBFOLDER = ""

LICENZA = """1) La presente patch va utilizzata esclusivamente sul gioco originale legittimamente detenuto per il quale è stata creata.
2) Questa patch è stata creata senza fini di lucro.
3) È assolutamente vietato vendere o cedere a terzi a qualsiasi titolo il gioco già patchato;
i trasgressori potranno essere puniti, ai sensi dell'art. 171bis, legge sul diritto d'autore.
4) Si declina la responsabilità derivante dall'uso scorretto di questo programma da parte di terzi.
5) Questa patch non contiene porzioni di codice del programma del gioco;
gli elementi che la formano non sono dotati di autonomia funzionale.
6) Per la creazione di tale patch non è stato necessario violare sistemi di protezione informatica,
   né dalla sua applicazione viene messa in atto tale condotta.
7) La patch è un prodotto amatoriale, pertanto l'autore declina la responsabilità di possibili malfunzionamenti;
   l'utilizzo della stessa è da intendersi a vostro rischio e pericolo.
8) Si ricorda infine che i diritti sul gioco (software) appartengono ai rispettivi proprietari (Disney e Square Enix).
This patch does not contain copyrighted material, has no functional autonomy, and you must have your own original copy to apply it.
All game rights, intellectual property, logo/names and movies/images are property of Disney and Square Enix.
"""
YT_URL = "https://www.youtube.com/@vocaliastudio"
GH_URL = "https://github.com/FriendsAreMyPower94/KH2_Vocalias_Saga"
WEB_URL = "https://www.youtube.com/@vocaliastudio"
DONAZIONI = "https://donazionivocaliastudios.carrd.co/"

def load_custom_fonts():
    try:
        font_dir = resource_path("assets/fonts")
        if os.path.exists(font_dir):
            for font_file in os.listdir(font_dir):
                if font_file.endswith((".ttf", ".otf")):
                    font_path = os.path.join(font_dir, font_file)
                    font_id = QFontDatabase.addApplicationFont(font_path)
                    if font_id != -1:
                        print(f"Font caricato con successo: {QFontDatabase.applicationFontFamilies(font_id)}")
    except Exception as e:
        print(f"Impossibile caricare i font personalizzati: {e}")

def get_dynamic_stylesheet():
    v_icon_path = resource_path("assets/v.png").replace("\\", "/")
    return f"""
/* Kingdom Hearts II Global Theme & Fonts */
QWidget {{
    background-color: transparent;
    color: #f0f4fc;
    font-family: "Exo 2", Cinzel, Garamond, "Palatino Linotype", "Book Antiqua", Georgia, serif;
    font-size: 10pt;
}}

QWidget#InstallerWizard {{
    background: qradialgradient(
        cx: 0.5, cy: 0.38, radius: 0.95,
        fx: 0.5, fy: 0.38,
        stop: 0.0 #143264,
        stop: 0.25 #0d2248,
        stop: 0.55 #071530,
        stop: 0.82 #040d20,
        stop: 1.0 #01050e
    );
}}

QDialog#CustomConfirmDialog, QDialog#CompletionDialog, QDialog#PirateWarningDialog {{
    background-color: #071429;
    border: 2px solid #ffd700;
    border-radius: 8px;
}}

QLabel {{
    background-color: transparent;
    padding: 1px;
}}

QLabel#TitleLabel {{
    font-family: Cinzel, Garamond, "Palatino Linotype", Georgia, serif;
    font-size: 21pt;
    font-weight: bold;
    color: #ffd700;
    letter-spacing: 1.5px;
    margin-bottom: 10px;
    qproperty-alignment: 'AlignCenter';
}}

QLabel#KHMainHeader {{
    font-family: Cinzel, Garamond, "Palatino Linotype", Georgia, serif;
    font-size: 24pt;
    font-weight: bold;
    color: #ffd700;
    letter-spacing: 1.5px;
    qproperty-alignment: 'AlignCenter';
}}

QLabel#KHSubHeader {{
    font-family: Cinzel, "Exo 2", Garamond, Georgia, serif;
    font-size: 13pt;
    font-weight: bold;
    color: #00e5ff;
    letter-spacing: 2px;
    qproperty-alignment: 'AlignCenter';
}}

QLabel#SubtitleLabel {{
    font-family: "Exo 2", Garamond, Georgia, serif;
    font-size: 11pt;
    color: #cce6ff;
    margin-bottom: 8px;
    qproperty-alignment: 'AlignCenter';
}}

QLabel#StatusLabel {{
    color: #00e5ff;
    font-size: 10.5pt;
    font-weight: bold;
    padding: 5px;
    min-height: 3.5em;
    qproperty-alignment: 'AlignCenter';
}}

QLabel#VersionLabel {{
    color: #ffd700;
    font-family: "Exo 2", Cinzel, serif;
    font-size: 10pt;
    font-weight: bold;
    letter-spacing: 1px;
}}

QLabel#ModCreditsLabel {{
    color: #ffd700;
    font-family: "Exo 2", Cinzel, serif;
    font-size: 10pt;
    font-weight: bold;
    letter-spacing: 1px;
}}

QLabel#AuthorLabel {{
    color: #8da4c4;
    font-family: "Exo 2", Cinzel, serif;
    font-size: 7.5pt;
    font-weight: normal;
    letter-spacing: 0.8px;
}}

QLabel#AuthorLabel a {{
    color: #00e5ff;
    text-decoration: none;
    font-weight: bold;
}}

QLabel#AuthorLabel a:hover {{
    color: #ffd700;
    text-decoration: underline;
}}

QLabel#HeadIcon {{
    background-color: transparent;
}}

QLabel#KeyInputLabel {{
    font-size: 9.5pt;
    color: #b3d9ff;
    padding-right: 5px;
}}

QLabel#DialogMainText {{
    font-size: 11pt;
    color: #ffffff;
}}

QLabel#DialogInfoText {{
    color: #b3d9ff;
    font-size: 9.5pt;
    padding-top: 5px;
}}

QLabel#DialogWarningText {{
    color: #ffaa00;
    font-weight: bold;
    font-size: 9.5pt;
    padding-top: 8px;
}}

/* KH Command Menu Style Buttons */
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0a1c38, stop:0.5 #122b52, stop:1 #0a1c38);
    color: #f0f4fc;
    border: 2px solid #0099ff;
    border-radius: 6px;
    padding: 9px 22px;
    font-family: "Exo 2", Cinzel, Garamond, Georgia, serif;
    font-size: 11pt;
    font-weight: bold;
    letter-spacing: 1.2px;
    outline: none;
    min-width: 95px;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #123263, stop:0.5 #1d4585, stop:1 #123263);
    border: 2px solid #ffd700;
    color: #ffd700;
}}

QPushButton:pressed {{
    background: #08142b;
    border: 2px solid #00e5ff;
    color: #ffffff;
}}

QPushButton:disabled {{
    background-color: #0b1424;
    color: #3d506e;
    border-color: #1a2a44;
}}

/* Action Command Primary Button (Avanti / Installa / Accetto) */
QPushButton#NextButton, QPushButton#InstallButton, QPushButton#AcceptButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #005ce6, stop:0.5 #0099ff, stop:1 #00e5ff);
    color: #ffffff;
    border: 2px solid #ffd700;
    border-radius: 6px;
    font-weight: bold;
    font-size: 11pt;
}}

QPushButton#NextButton:hover, QPushButton#InstallButton:hover, QPushButton#AcceptButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0073e6, stop:0.5 #1ab2ff, stop:1 #33f0ff);
    border: 2px solid #ffffff;
    color: #ffffff;
}}

QPushButton#NextButton:pressed, QPushButton#InstallButton:pressed, QPushButton#AcceptButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0044ab, stop:0.5 #007acc, stop:1 #00b3e6);
    border: 2px solid #ffd700;
}}

QPushButton#NextButton:disabled, QPushButton#InstallButton:disabled, QPushButton#AcceptButton:disabled {{
    background-color: #0c203b;
    color: #3b5880;
    border-color: #152d4d;
}}

/* Secondary / Cancel Buttons */
QPushButton#CancelButton, QPushButton#RetryButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0e1a30, stop:1 #172847);
    border: 1.5px solid #0099ff;
    color: #b8d5ff;
    border-radius: 6px;
}}

QPushButton#CancelButton:hover, QPushButton#RetryButton:hover {{
    background: #182e54;
    border: 1.5px solid #00e5ff;
    color: #ffffff;
}}

QPushButton#CancelButton:pressed, QPushButton#RetryButton:pressed {{
    background: #081021;
    border: 1.5px solid #007acc;
    color: #7baae0;
}}

/* Social Link Bar Buttons */
QPushButton#LinkButton {{
    background-color: rgba(10, 28, 56, 0.75);
    border: 1.5px solid #0099ff;
    border-radius: 16px;
    padding: 2px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    qproperty-iconSize: 22px 22px;
}}

QPushButton#LinkButton:hover {{
    background-color: rgba(0, 229, 255, 0.3);
    border: 1.5px solid #ffd700;
}}

QPushButton#LinkButton:pressed {{
    background-color: rgba(0, 229, 255, 0.5);
}}

QPushButton#HiddenKeyButton {{
    background-color: transparent;
    border: none;
    padding: 0px;
    margin: 0px;
    min-width: 10px;
    max-width: 10px;
    min-height: 10px;
    max-height: 10px;
}}

/* Input Fields */
QLineEdit, QTextEdit, QTextBrowser {{
    background-color: rgba(6, 17, 36, 0.85);
    border: 1.5px solid #0099ff;
    color: #f0f4fc;
    border-radius: 6px;
    padding: 8px;
    font-size: 10.5pt;
    selection-background-color: #0073e6;
    selection-color: #ffffff;
}}

QLineEdit:focus, QTextEdit:focus, QTextBrowser:focus {{
    border: 2px solid #ffd700;
    background-color: rgba(9, 24, 51, 0.95);
}}

QLineEdit::placeholder {{
    color: #526f9c;
}}

QLineEdit#KeyInputField {{
    font-size: 9.5pt;
    padding: 6px;
}}

/* KH HP/MP Style Progress Bar */
QProgressBar {{
    border: 2px solid #ffd700;
    border-radius: 6px;
    background-color: #050e1c;
    text-align: center;
    height: 14px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0052cc, stop:0.5 #00a6ff, stop:1 #00f0ff);
    border-radius: 4px;
    margin: 0px;
}}

QPushButton#BrowseButton {{
    padding: 4px;
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0a1c38, stop:1 #122b52);
    border: 1.5px solid #0099ff;
    border-radius: 6px;
    color: #00e5ff;
}}

QPushButton#BrowseButton:hover {{
    background: #163666;
    border: 1.5px solid #ffd700;
    color: #ffd700;
}}

QPushButton#BrowseButton:pressed {{
    background: #08142b;
}}

QMessageBox, QInputDialog {{
    background-color: #071429;
    border: 2px solid #ffd700;
    border-radius: 8px;
}}

QMessageBox QLabel {{
    color: #f0f4fc;
    background-color: transparent;
    font-size: 10pt;
    min-width: 260px;
}}

QFrame#KHCardFrame {{
    background-color: rgba(6, 17, 38, 0.76);
    border: 2px solid #0099ff;
    border-radius: 12px;
}}

/* Checkbox Styling */
QCheckBox {{
    spacing: 8px;
    color: #e0eeef;
    font-size: 10pt;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid #0099ff;
    border-radius: 4px;
    background-color: #071426;
}}

QCheckBox::indicator:hover {{
    border: 2px solid #ffd700;
}}

QCheckBox::indicator:checked {{
    background-color: #0066cc;
    border: 2px solid #00e5ff;
    image: url({v_icon_path});
}}

QCheckBox::indicator:checked:hover {{
    background-color: #0080ff;
    border: 2px solid #ffd700;
}}

QCheckBox::indicator:disabled {{
    background-color: #0b1424;
    border: 1px solid #1a2a44;
}}

/* ScrollBars */
QScrollBar:vertical {{
    border: none;
    background: rgba(5, 14, 28, 0.5);
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: #0099ff;
    min-height: 25px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: #ffd700;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
    background: none;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    border: none;
    background: rgba(5, 14, 28, 0.5);
    height: 8px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background: #0099ff;
    min-width: 25px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #ffd700;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
    background: none;
}}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}

QFrame#KHCardFrame {{
    background-color: rgba(8, 22, 46, 0.75);
    border: 2px solid #0099ff;
    border-radius: 10px;
}}
"""

def leggi_chiave(nome_file):
    try:
        if not os.path.exists(nome_file):
            print(f"Errore: Il file '{nome_file}' non esiste.")
            return None
        if not os.access(nome_file, os.R_OK):
            print(f"Errore: Il file '{nome_file}' non ha i permessi di lettura.")
            return None
        with open(nome_file, 'r') as file:
            chiave = file.readline().strip()
        if not chiave:
            print(f"Avviso: Il file '{nome_file}' è vuoto o non contiene una chiave valida.")
            return None
        print(f"Chiave di decriptazione letta con successo dal file '{nome_file}'.")
        return chiave.encode('utf-8')
    except Exception as e:
        print(f"Si è verificato un errore durante la lettura del file '{nome_file}': {e}")
        return None

class VersionCheckWorker(QThread):
    update_found = pyqtSignal(str, str)

    def __init__(self, current_version, repo_url):
        super().__init__()
        self.current_version = current_version
        self.repo_url = repo_url
        self.api_url = ""

    def _compare_versions(self, v1_str, v2_str):
        try:
            latest_v = version.parse(v1_str)
            current_v = version.parse(v2_str)
            return latest_v > current_v
        except (version.InvalidVersion, AttributeError, TypeError) as e:
            print(f"Avviso: Impossibile analizzare la versione in modo standard ({e}). Fallback a confronto stringa.")
            if "Alpha" in v1_str and "beta" in v2_str.lower(): 
                return False
            if "Alpha" in v2_str and "beta" in v1_str.lower(): 
                return True
            return v1_str.lstrip('vV') > v2_str.lstrip('vV')

    def run(self):
        try:
            parts = self.repo_url.strip("/").split("/")
            owner, repo = parts[-2], parts[-1]
            self.api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
            
            print(f"Controllo aggiornamenti a: {self.api_url}")
            req = urllib.request.Request(self.api_url, headers={'User-Agent': 'SavT-Installer-Updater'})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data_list = json.loads(response.read().decode())
                    if not data_list:
                        print("Controllo aggiornamenti: Nessuna release trovata sul repository.")
                        return

                    latest_release_data = data_list[0] 
                    latest_version_tag = latest_release_data.get('tag_name')
                    download_url = latest_release_data.get('html_url')
                    
                    if not latest_version_tag or not download_url:
                        print("Controllo aggiornamenti: 'tag_name' o 'html_url' non trovati nella risposta.")
                        return
                        
                    print(f"Ultima versione su GitHub: {latest_version_tag}, Versione corrente: {self.current_version}")
                    
                    if self._compare_versions(latest_version_tag, self.current_version):
                        print(f"Nuova versione disponibile: {latest_version_tag}")
                        self.update_found.emit(latest_version_tag, download_url)
                    else:
                        print("La versione corrente è la più recente.")
                else:
                    print(f"Controllo aggiornamenti fallito con codice di stato: {response.status}")
        except Exception as e:
            print(f"Impossibile controllare gli aggiornamenti: {e}")

class InstallWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    backup_status = pyqtSignal(str)
    
    def __init__(self, dest_path, aes_key, do_backup, package_filename):
        super().__init__()
        self.dest_path = dest_path
        self.aes_key = aes_key
        self.do_backup = do_backup
        self.package_filename = package_filename
        self._is_interruption_requested = False
        
    def requestInterruption(self):
        self._is_interruption_requested = True
        
    def isInterruptionRequested(self):
        return self._is_interruption_requested
        
    def run(self):
        try:
            package_path = resource_path(self.package_filename)
            if not os.path.exists(package_path):
                raise FileNotFoundError(f"File della patch non trovato: {self.package_filename}")
            
            with pyzipper.AESZipFile(package_path) as zf:
                zf.setpassword(self.aes_key)
                file_infos = zf.infolist()
                total_files = len(file_infos)
                
                if self.do_backup:
                    self.backup_status.emit("Avvio backup file originali...")
                    backup_folder_name = f"_backup_patch_ita_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    backup_base_path = os.path.join(self.dest_path, backup_folder_name)
                    backup_count = 0
                    
                    try:
                        os.makedirs(backup_base_path, exist_ok=True)
                        print(f"Creata cartella backup: {backup_base_path}")
                        for file_info in file_infos:
                            if self.isInterruptionRequested():
                                self.finished.emit(False, "Backup annullato dall'utente.")
                                return
                            if not file_info.is_dir():
                                source_file_path = os.path.join(self.dest_path, file_info.filename)
                                if os.path.isfile(source_file_path):
                                    backup_file_path = os.path.join(backup_base_path, file_info.filename)
                                    backup_file_dir = os.path.dirname(backup_file_path)
                                    os.makedirs(backup_file_dir, exist_ok=True)
                                    print(f"Backing up: {source_file_path} -> {backup_file_path}")
                                    shutil.copy2(source_file_path, backup_file_path)
                                    backup_count += 1
                                    
                        if backup_count > 0:
                            self.backup_status.emit(f"Backup di {backup_count} file completato in '{backup_folder_name}'.")
                            print(f"Backup completato: {backup_count} file.")
                        else:
                            self.backup_status.emit("Nessun file originale trovato da backuppare.")
                            print("Nessun file da backuppare.")
                            
                    except (shutil.Error, OSError, IOError) as backup_error:
                        error_msg = f"Errore durante il backup:\n{backup_error}"
                        print(f"Errore backup: {error_msg}")
                        with open(LOG_FILE, 'a', encoding='utf-8') as f:
                            f.write(error_msg + "\n")
                        self.finished.emit(False, error_msg + "\nL'installazione è stata interrotta.")
                        return
                        
                if total_files == 0:
                    self.finished.emit(True, "Installazione completata (archivio vuoto).")
                    return
                    
                for i, file_info in enumerate(file_infos):
                    if self.isInterruptionRequested():
                        self.finished.emit(False, "Installazione annullata dall'utente.")
                        return
                        
                    file = file_info.filename
                    target_path = os.path.join(self.dest_path, file)
                    
                    if file_info.is_dir():
                        os.makedirs(target_path, exist_ok=True)
                        self.progress.emit(int(((i + 1) / total_files) * 100))
                        continue
                        
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    try:
                        with zf.open(file_info) as source, open(target_path, "wb") as target:
                            chunk_size = 1024 * 512
                            while True:
                                if self.isInterruptionRequested():
                                    try:
                                        target.close()
                                        os.remove(target_path)
                                    except OSError:
                                        pass
                                    self.finished.emit(False, "Installazione annullata dall'utente.")
                                    return
                                    
                                chunk = source.read(chunk_size)
                                if not chunk: 
                                    break
                                target.write(chunk)
                    except Exception as write_error:
                         raise IOError(f"Errore scrittura file {target_path}: {write_error}") from write_error
                         
                    self.progress.emit(int(((i + 1) / total_files) * 100))
                    
            if not self.isInterruptionRequested():
                self.finished.emit(True, "Installazione completata con successo!")
                
        except FileNotFoundError as e:
             with open(LOG_FILE, 'a', encoding='utf-8') as f:
                 f.write(f"Errore FileNotFoundError: {str(e)}\n")
             self.finished.emit(False, str(e))
        except (pyzipper.BadZipFile, RuntimeError) as e:
            error_msg = f"Errore: {self.package_filename} è corrotto, la chiave AES usata non è valida o file zip non valido."
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{error_msg} Dettaglio: {type(e).__name__}: {str(e)}\n")
            self.finished.emit(False, error_msg)
        except IOError as e:
            error_msg = f"Errore di I/O durante l'estrazione:\n{str(e)}"
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(error_msg + "\n")
            self.finished.emit(False, error_msg + "\nVerifica permessi e spazio disco.")
        except Exception as e:
            error_msg = f"Errore imprevisto durante l'estrazione:\n{type(e).__name__}: {str(e)}"
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(error_msg + "\n")
                traceback.print_exc(file=f)
            self.finished.emit(False, error_msg)

class PirateWarningDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Installazione Bloccata")
        self.setModal(True)
        self.setObjectName("PirateWarningDialog")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 15)
        main_layout.setSpacing(15)
        
        image_label = QLabel()
        img_path = resource_path("assets/pirate.jpg")
        if os.path.exists(img_path):
            image_label.setPixmap(QPixmap(img_path).scaled(640, 569, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(image_label)
        
        text_label = QLabel("È stata rilevata una versione non ufficiale o alterata del gioco.\nCome indicato nei Termini di Licenza, la patch supporta unicamente le copie originali e legittimamente detenute.")
        text_label.setObjectName("DialogMainText")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)
        main_layout.addWidget(text_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        if ok_button:
            ok_button.setText("OK")
            ok_button.setObjectName("AcceptButton")
            ok_button.clicked.connect(self.on_accept_clicked)
        else:
            button_box.accepted.connect(self.on_accept_clicked)
            
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(button_box)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        self.adjustSize()
        
    def on_accept_clicked(self):
        self.accept()
        # Link per l'acquisto del gioco
        apri_url("https://store.steampowered.com/app/2552430/KINGDOM_HEARTS_HD_1525_ReMIX/")
        # Invia un segnale di chiusura per l'intera app dopo 1.5 secondi
        QTimer.singleShot(1500, QApplication.instance().quit)

class CustomConfirmDialog(QDialog):
    def __init__(self, parent=None, title="Conferma", text="", informative_text="", warning_text="", icon_pixmap=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setObjectName("CustomConfirmDialog")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 15)
        main_layout.setSpacing(15)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        if icon_pixmap:
            icon_label = QLabel()
            icon_label.setPixmap(icon_pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            content_layout.addWidget(icon_label, 0)
            
        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)
        
        self.main_text_label = QLabel(text)
        self.main_text_label.setObjectName("DialogMainText")
        self.main_text_label.setWordWrap(True)
        text_layout.addWidget(self.main_text_label)
        
        if informative_text:
            self.info_text_label = QLabel(informative_text)
            self.info_text_label.setObjectName("DialogInfoText")
            self.info_text_label.setWordWrap(True)
            text_layout.addWidget(self.info_text_label)
            
        self.warning_label_container = QWidget()
        self.warning_layout = QVBoxLayout(self.warning_label_container)
        self.warning_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.addWidget(self.warning_label_container)
        
        content_layout.addLayout(text_layout, 1)
        main_layout.addLayout(content_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        yes_button = button_box.button(QDialogButtonBox.StandardButton.Yes)
        if yes_button:
            yes_button.setText("Sì")
            yes_button.setObjectName("AcceptButton")
            yes_button.setDefault(True)
            
        no_button = button_box.button(QDialogButtonBox.StandardButton.No)
        if no_button:
            no_button.setText("No")
            no_button.setObjectName("CancelButton")
            
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(button_box)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        self.setMinimumWidth(450)
        self.adjustSize()
        
        if warning_text:
            self.setWarningText(warning_text)
            
    def setWarningText(self, text):
        for i in reversed(range(self.warning_layout.count())):
            widget = self.warning_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
                
        if text:
            warning_text_label = QLabel(text)
            warning_text_label.setObjectName("DialogWarningText")
            warning_text_label.setWordWrap(True)
            self.warning_layout.addWidget(warning_text_label)
            self.warning_label_container.setVisible(True)
        else:
            self.warning_label_container.setVisible(False)
            
        self.adjustSize()

class CompletionDialog(QDialog):
    def __init__(self, parent=None, title="Completato", text="", url_to_open=None):
        super().__init__(parent)
        self.url_to_open = url_to_open
        self.setWindowTitle(title)
        self.setModal(True)
        self.setObjectName("CompletionDialog")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 15)
        main_layout.setSpacing(15)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        icon_label = QLabel()
        try:
            icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
            icon_label.setPixmap(icon.pixmap(QSize(32, 32)))
        except Exception:
            pass
            
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        content_layout.addWidget(icon_label, 0)
        
        self.main_text_label = QLabel(text)
        self.main_text_label.setObjectName("DialogMainText")
        self.main_text_label.setWordWrap(True)
        self.main_text_label.setMinimumWidth(250)
        content_layout.addWidget(self.main_text_label, 1)
        
        main_layout.addLayout(content_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        
        if ok_button:
            ok_button.setText("OK")
            ok_button.setObjectName("AcceptButton")
            ok_button.setDefault(True)
            ok_button.clicked.connect(self.accept_and_open_url)
        else:
            button_box.accepted.connect(self.accept_and_open_url)
            
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(button_box)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        self.adjustSize()
        self.setMaximumWidth(500)
        
    def accept_and_open_url(self):
        url = self.url_to_open
        self.accept()
        if url:
            try:
                apri_url(WEB_URL)
                apri_url(url)
                QTimer.singleShot(2000, QApplication.instance().quit)
            except Exception as e:
                print(f"Error opening URL {url}: {e}")
        else:
             QTimer.singleShot(2000, QApplication.instance().quit)

class WelcomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setSpacing(12)
        
        # --- Top Bar con stemma KH e link social ---
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)
        
        top_title = QLabel("👑 KINGDOM HEARTS II")
        top_title.setStyleSheet("font-size: 13pt; font-weight: bold; color: #ffd700; font-family: Cinzel, Garamond, serif; letter-spacing: 1.5px;")
        top_title_effect = QGraphicsDropShadowEffect(top_title)
        top_title_effect.setBlurRadius(12)
        top_title_effect.setColor(QColor(255, 215, 0, 180))
        top_title_effect.setOffset(0, 0)
        top_title.setGraphicsEffect(top_title_effect)
        
        top_bar.addWidget(top_title)
        top_bar.addStretch()
        
        for icon_path, url, tip in zip([YT_ICON, GH_ICON, WEB_ICON], [YT_URL, GH_URL, WEB_URL], ["YouTube - Canale Ufficiale", "GitHub - Repository", "Sito Web Ufficiale"]):
            try:
                if not os.path.exists(icon_path):
                    continue
                btn = QPushButton()
                btn.setObjectName("LinkButton")
                btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn.setFlat(True)
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(22, 22))
                btn.setFixedSize(QSize(32, 32))
                btn.setToolTip(tip)
                btn.clicked.connect(lambda _, link=url: apri_url(link))
                top_bar.addWidget(btn)
            except Exception as e:
                print(f"Err icon {icon_path}: {e}")
                
        layout.addLayout(top_bar)
        layout.addSpacing(5)
        
        # --- Layout Centrale: Command Menu a Sinistra + Card Espositiva a Destra ---
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(20)
        
        # --- Command Menu Box (Sinistra) ---
        cmd_box = QFrame()
        cmd_box.setObjectName("KHCommandBox")
        cmd_box.setStyleSheet("""
            QFrame#KHCommandBox {
                background-color: rgba(6, 16, 36, 0.85);
                border: 2px solid #0099ff;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        cmd_layout = QVBoxLayout(cmd_box)
        cmd_layout.setContentsMargins(12, 15, 12, 15)
        cmd_layout.setSpacing(12)
        
        cmd_header = QLabel("COMANDI")
        cmd_header.setStyleSheet("font-family: Cinzel, Garamond, serif; font-size: 11pt; font-weight: bold; color: #00e5ff; letter-spacing: 2px;")
        cmd_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cmd_layout.addWidget(cmd_header)
        cmd_layout.addSpacing(5)
        
        self.next_btn = QPushButton("▶  INSTALLA")
        self.next_btn.setObjectName("NextButton")
        self.next_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.next_btn.setDefault(True)
        
        self.notice_btn = QPushButton("ℹ️  INFO")
        self.notice_btn.setObjectName("CommandMenuBtn")
        self.notice_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        self.license_btn = QPushButton("📜  LICENZA")
        self.license_btn.setObjectName("CommandMenuBtn")
        self.license_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        self.cancel_btn = QPushButton("✖  ESCI")
        self.cancel_btn.setObjectName("CancelButton")
        self.cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        cmd_layout.addWidget(self.next_btn)
        cmd_layout.addWidget(self.notice_btn)
        cmd_layout.addWidget(self.license_btn)
        cmd_layout.addStretch()
        cmd_layout.addWidget(self.cancel_btn)
        
        middle_layout.addWidget(cmd_box, 0)
        
        # --- Card Espositiva (Destra) ---
        card_frame = QFrame()
        card_frame.setObjectName("KHCardFrame")
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)
        
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            if os.path.exists(IMG_FILE):
                image_label.setPixmap(QPixmap(IMG_FILE).scaled(300, 170, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                image_label.setText("Immagine non trovata")
        except Exception as e:
            image_label.setText(f"Err img: {e}")
            
        title = QLabel("KINGDOM HEARTS II")
        title.setObjectName("KHMainHeader")
        title_effect = QGraphicsDropShadowEffect(title)
        title_effect.setBlurRadius(20)
        title_effect.setColor(QColor(255, 215, 0, 200))
        title_effect.setOffset(0, 0)
        title.setGraphicsEffect(title_effect)
        
        subtitle = QLabel("VOCALIA'S SAGA — MOD INSTALLER ITA")
        subtitle.setObjectName("KHSubHeader")
        subtitle_effect = QGraphicsDropShadowEffect(subtitle)
        subtitle_effect.setBlurRadius(16)
        subtitle_effect.setColor(QColor(0, 229, 255, 200))
        subtitle_effect.setOffset(0, 0)
        subtitle.setGraphicsEffect(subtitle_effect)
        
        desc = QLabel("Questo programma installerà la mod di doppiaggio e adattamento in italiano per Kingdom Hearts II Final Mix.")
        desc.setObjectName("SubtitleLabel")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        
        card_layout.addWidget(image_label)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(desc)
        
        middle_layout.addWidget(card_frame, 1)
        
        layout.addLayout(middle_layout, 1)
        layout.addSpacing(5)
        
        # --- Footer Info ---
        bottom_info_layout = QHBoxLayout()
        version_label = QLabel(f"Versione Patch: {VERSIONE}")
        version_label.setObjectName("VersionLabel")
        version_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        autore_label = QLabel(f"Installer By <a href='{SAVT_SITE_URL}'>SavT</a>")
        autore_label.setObjectName("AuthorLabel")
        autore_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        autore_label.setOpenExternalLinks(False)
        autore_label.linkActivated.connect(lambda link: apri_url(link))
        autore_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        mod_label = QLabel(CREDITI_MOD)
        mod_label.setObjectName("ModCreditsLabel")
        mod_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        bottom_info_layout.addWidget(version_label)
        bottom_info_layout.addStretch(1)
        bottom_info_layout.addWidget(autore_label)
        bottom_info_layout.addStretch(1)
        bottom_info_layout.addWidget(mod_label)
        
        layout.addLayout(bottom_info_layout)

class PackageCheckScreen(QWidget):
    def __init__(self, parent_wizard):
        super().__init__()
        self.parent_wizard = parent_wizard
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setSpacing(12)
        
        # --- Top Header: Synthesis & Material Check Theme ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        
        title = QLabel("⚙️ ELABORATORE")
        title.setObjectName("TitleLabel")
        title_effect = QGraphicsDropShadowEffect(title)
        title_effect.setBlurRadius(16)
        title_effect.setColor(QColor(255, 215, 0, 180))
        title_effect.setOffset(0, 0)
        title.setGraphicsEffect(title_effect)
        
        sub_tab = QLabel("[ 🔍 VERIFICA ARCHIVIO E CHIAVE AES ]")
        sub_tab.setStyleSheet("font-family: 'Exo 2', Cinzel, serif; font-size: 10pt; font-weight: bold; color: #00e5ff; letter-spacing: 1.5px;")
        sub_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(sub_tab)
        
        card_frame = QFrame()
        card_frame.setObjectName("KHCardFrame")
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        self.status_label = QLabel("Verifico...")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        
        self.key_input_widget = QWidget()
        self.key_input_layout = QVBoxLayout(self.key_input_widget)
        self.key_input_layout.setContentsMargins(0, 10, 0, 5)
        self.key_input_layout.setSpacing(5)
        
        key_input_label = QLabel("Chiave AES non valida. Inserisci una chiave alternativa:")
        key_input_label.setObjectName("KeyInputLabel")
        key_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.key_input_field = QLineEdit()
        self.key_input_field.setObjectName("KeyInputField")
        self.key_input_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input_field.setPlaceholderText("Inserisci chiave e premi Riprova (o lascia vuoto per default)")
        self.key_input_field.returnPressed.connect(self.check_package)
        
        self.key_input_layout.addWidget(key_input_label)
        self.key_input_layout.addWidget(self.key_input_field)
        self.key_input_widget.setVisible(False)
        
        self.retry_btn = QPushButton("🔄  RIPROVA CONTROLLO")
        self.retry_btn.setObjectName("RetryButton")
        self.retry_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.retry_btn.clicked.connect(self.parent_wizard.go_to_check)
        self.retry_btn.setVisible(False)
            
        retry_layout = QHBoxLayout()
        retry_layout.addStretch()
        retry_layout.addWidget(self.retry_btn)
        retry_layout.addStretch()
        
        card_layout.addWidget(self.status_label)
        card_layout.addWidget(self.key_input_widget)
        card_layout.addLayout(retry_layout)
        
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("✖  ESCI")
        self.cancel_btn.setObjectName("CancelButton")
        self.cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            
        self.next_btn = QPushButton("▶  AVANTI")
        self.next_btn.setObjectName("NextButton")
        self.next_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.next_btn.setEnabled(False)
        self.next_btn.setDefault(True)
            
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.next_btn)
        
        layout.addLayout(header_layout)
        layout.addSpacing(5)
        layout.addWidget(card_frame, 1)
        layout.addSpacing(8)
        layout.addLayout(btn_layout)
        
    def check_package(self, package_to_check=PACKAGE_FILE):
        if self.key_input_widget.isVisible():
            new_key_text = self.key_input_field.text()
            key_changed = False
            if new_key_text:
                try:
                    new_key_bytes = new_key_text.encode('utf-8')
                    if new_key_bytes != self.parent_wizard.current_aes_key:
                        self.parent_wizard.current_aes_key = new_key_bytes
                        print("Chiave AES aggiornata (da input).")
                        key_changed = True
                except Exception as e:
                    QMessageBox.warning(self, "Errore Chiave", f"Chiave non valida: {e}")
                    print(f"Err key enc: {e}")
            else:
                 chiave_default = leggi_chiave(resource_path(CHIAVE))
                 if self.parent_wizard.current_aes_key != chiave_default:
                     self.parent_wizard.current_aes_key = chiave_default
                     print("Chiave AES reimpostata (da input vuoto).")
                     key_changed = True
                     
        aes_key_to_use = self.parent_wizard.current_aes_key
        package_path = resource_path(package_to_check)
        self.key_input_widget.setVisible(False)
        self.retry_btn.setVisible(False)
        self.status_label.setText("Verifico...")
        QApplication.processEvents()
        
        if not aes_key_to_use:
            self.status_label.setText(f"<font color='#ff8080'>❌ Errore: Chiave AES non disponibile.</font><br><font color='#bbccd0' size='-1'>Impossibile leggere {CHIAVE} e nessuna chiave inserita.</font>")
            self.next_btn.setEnabled(False)
            self.retry_btn.setVisible(True)
            self.key_input_widget.setVisible(True)
            self.key_input_field.setFocus()
            return
            
        if os.path.isfile(package_path):
            try:
                with pyzipper.AESZipFile(package_path) as zf:
                    zf.setpassword(aes_key_to_use)
                    test = zf.testzip()
                    
                if test is None:
                    self.status_label.setText(f"<font color='#228B22'>✔️ File '{package_to_check}' valido.</font>")
                    self.next_btn.setEnabled(True)
                    self.retry_btn.setVisible(False)
                    self.key_input_widget.setVisible(False)
                else:
                    self.status_label.setText(f"<font color='#ffd880'>⚠️ File '{package_to_check}' corrotto (file: {test}).</font><br><font color='#bbccd0' size='-1'>Riscrivi la patch.</font>")
                    self.next_btn.setEnabled(False)
                    self.retry_btn.setVisible(True)
                    self.key_input_widget.setVisible(False)
            except (pyzipper.BadZipFile, RuntimeError) as e:
                 print(f"Package check bad key/zip error: {type(e).__name__}")
                 self.status_label.setText(f"<font color='#ffd880'>⚠️ Chiave AES non valida o archivio corrotto.</font><br><font color='#bbccd0' size='-1'>Inserisci chiave corretta e riprova.</font>")
                 self.next_btn.setEnabled(False)
                 self.retry_btn.setVisible(True)
                 self.key_input_widget.setVisible(True)
                 self.key_input_field.setFocus()
            except Exception as e:
                 self.status_label.setText(f"<font color='#ff8080'>❌ Errore verifica: {type(e).__name__}</font>")
                 self.next_btn.setEnabled(False)
                 self.retry_btn.setVisible(True)
                 self.key_input_widget.setVisible(False)
                 print(f"Pkg check err: {e}")
                 traceback.print_exc()
        else:
            self.status_label.setText(f"<font color='#ff8080'>❌ File '{package_to_check}' non trovato.</font><br><font color='#bbccd0' size='-1'>Controlla cartella installer.</font>")
            self.next_btn.setEnabled(False)
            self.retry_btn.setVisible(False)
            self.key_input_widget.setVisible(False)

class NoticeScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setSpacing(12)
        
        # --- Top Header: Jiminy's Journal Theme ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        
        title = QLabel("📜 DIARIO DEL GRILLO")
        title.setObjectName("TitleLabel")
        title_effect = QGraphicsDropShadowEffect(title)
        title_effect.setBlurRadius(16)
        title_effect.setColor(QColor(255, 215, 0, 180))
        title_effect.setOffset(0, 0)
        title.setGraphicsEffect(title_effect)
        
        sub_tab = QLabel("[ 📘 NOTA BENE E FONTI UFFICIALI ]")
        sub_tab.setStyleSheet("font-family: 'Exo 2', Cinzel, serif; font-size: 10pt; font-weight: bold; color: #00e5ff; letter-spacing: 1.5px;")
        sub_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(sub_tab)
        
        card_frame = QFrame()
        card_frame.setObjectName("KHCardFrame")
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)
        
        notice_area = QTextBrowser()
        notice_area.setReadOnly(True)
        notice_area.setOpenExternalLinks(False)
        notice_area.setOpenLinks(False)
        notice_area.anchorClicked.connect(lambda qurl: apri_url(qurl.toString()))
        
        html_content = f"""<body style='color: #f0f4fc; font-family: "Exo 2", Garamond, serif; font-size: 10.5pt;'>
        <style> p {{ margin-bottom: 12px; }} b {{ color: #ffd700; }} a {{ color: #00e5ff; text-decoration: none; font-weight: bold; }} a:hover {{ text-decoration: underline; color: #ffffff; }} </style>
        <p><b>1. La patch è GRATUITA e Open Source.</b><br>Se hai pagato per ottenere questo software, sei stato truffato. Chiedi <b>immediatamente i soldi indietro</b>. Il progetto è e sarà sempre gratuito.</p>
        <p><b>2. Scarica solo da fonti ufficiali.</b><br>Ottieni la patch esclusivamente dalle nostre fonti ufficiali:
            <ul>
                <li>Repository GitHub: <a href="{GH_URL}"><b>Clicca qui</b></a></li>
                <li>Canale YouTube: <a href="{YT_URL}"><b>Clicca qui</b></a></li>
                <li>Sito Web Ufficiale: <a href="{WEB_URL}"><b>Clicca qui</b></a></li>
                <li>{ALT_SITE_NAME}: <a href="{ALT_SITE_URL}"><b>Clicca qui</b></a></li>
            </ul>
            Non ci assumiamo alcuna responsabilità per problemi, virus o malfunzionamenti derivanti da versioni scaricate da siti non ufficiali.</p>
        <p><b>3. Segnala problemi o errori di traduzione.</b><br>Se riscontri un bug o un errore, il tuo aiuto è prezioso. Puoi <a href="{GH_URL}/issues/new?template=errore-nella-traduzione.yml"><b>cliccare qui per aprire una segnalazione su GitHub</b></a>.</p>
        <p><b>4. Supporta il progetto (Opzionale).</b><br>Mantenere e migliorare questo progetto richiede tempo e dedizione. Se il nostro lavoro ti è piaciuto, puoi supportarci con una piccola <a href="{DONAZIONI}"><b>donazione cliccando qui</b></a>. Grazie di cuore!</p></body>"""
        notice_area.setHtml(html_content)
        card_layout.addWidget(notice_area)
        
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("✖  ESCI")
        self.cancel_btn.setObjectName("CancelButton")
        self.cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.back_btn = QPushButton("◀  INDIETRO")
        self.back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        self.next_btn = QPushButton("▶  AVANTI")
        self.next_btn.setObjectName("NextButton")
        self.next_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.next_btn.setDefault(True)
            
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.next_btn)
        
        layout.addLayout(header_layout)
        layout.addSpacing(5)
        layout.addWidget(card_frame, 1)
        layout.addSpacing(8)
        layout.addLayout(btn_layout)

class LicenseScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setSpacing(12)
        
        # --- Top Header: System Config Theme ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        
        title = QLabel("⚖️ CONFIGURAZIONE")
        title.setObjectName("TitleLabel")
        title_effect = QGraphicsDropShadowEffect(title)
        title_effect.setBlurRadius(16)
        title_effect.setColor(QColor(255, 215, 0, 180))
        title_effect.setOffset(0, 0)
        title.setGraphicsEffect(title_effect)
        
        sub_tab = QLabel("[ 🛡️ TERMINI DI LICENZA D'USO ]")
        sub_tab.setStyleSheet("font-family: 'Exo 2', Cinzel, serif; font-size: 10pt; font-weight: bold; color: #00e5ff; letter-spacing: 1.5px;")
        sub_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(sub_tab)
        
        card_frame = QFrame()
        card_frame.setObjectName("KHCardFrame")
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(15, 15, 15, 15)
        
        self.license_text = QTextEdit()
        self.license_text.setPlainText(LICENZA)
        self.license_text.setReadOnly(True)
        self.license_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.license_text.setObjectName("LicenseText")
        card_layout.addWidget(self.license_text)
        
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("✖  ESCI")
        self.cancel_btn.setObjectName("CancelButton")
        self.cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            
        self.next_btn = QPushButton("▶  ACCETTO E CONTINUA")
        self.next_btn.setObjectName("AcceptButton")
        self.next_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.next_btn.setDefault(True)
            
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.next_btn)
        
        layout.addLayout(header_layout)
        layout.addSpacing(5)
        layout.addWidget(card_frame, 1)
        layout.addSpacing(8)
        layout.addLayout(btn_layout)

class InstallScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(25, 15, 25, 15)
        self.layout.setSpacing(12)
        
        # --- Top Header: World Destination & Drive Gauge Theme ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        
        title = QLabel("🏰 MAPPA DEI MONDI")
        title.setObjectName("TitleLabel")
        title_effect = QGraphicsDropShadowEffect(title)
        title_effect.setBlurRadius(16)
        title_effect.setColor(QColor(255, 215, 0, 180))
        title_effect.setOffset(0, 0)
        title.setGraphicsEffect(title_effect)
        
        sub_tab = QLabel("[ 📍 SELEZIONE CARTELLA & INSTALLAZIONE ]")
        sub_tab.setStyleSheet("font-family: 'Exo 2', Cinzel, serif; font-size: 10pt; font-weight: bold; color: #00e5ff; letter-spacing: 1.5px;")
        sub_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(sub_tab)
        
        card_frame = QFrame()
        card_frame.setObjectName("KHCardFrame")
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        path_label = QLabel("Seleziona la cartella principale di KINGDOM HEARTS -HD 1.5+2.5 ReMIX-:")
        path_label.setObjectName("SubtitleLabel")
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Es: C:/.../Steam/steamapps/common/KINGDOM HEARTS -HD 1.5+2.5 ReMIX-")
        
        self.browse_btn = QPushButton("📁")
        self.browse_btn.setObjectName("BrowseButton")
        self.browse_btn.setFixedSize(36, 36)
        self.browse_btn.setToolTip("Sfoglia cartelle")
        self.browse_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.browse_btn.clicked.connect(self.select_folder)
        
        path_input_layout = QHBoxLayout()
        path_input_layout.addWidget(self.path_input, 1)
        path_input_layout.addSpacing(6)
        path_input_layout.addWidget(self.browse_btn)
        
        self.backup_checkbox = QCheckBox("Crea backup dei file originali prima dell'installazione")
        self.backup_checkbox.setChecked(True)
        self.backup_checkbox.setToolTip("Se selezionato, i file che verranno sovrascritti dalla patch\nsaranno prima copiati in una sottocartella '_backup_patch_ita_...'")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        
        self.status_label = QLabel("Pronto per l'installazione.")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.head_icon = QLabel(self)
        self.head_icon.setObjectName("HeadIcon")
        try:
            if os.path.exists(HEAD_ICON_PATH):
                self.head_icon.setPixmap(QPixmap(HEAD_ICON_PATH).scaled(22, 22, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                self.head_icon.setText("»")
                self.head_icon.setStyleSheet("color: #ff8030; font-size: 16pt; font-weight: bold;")
                
            self.head_icon.setFixedSize(24, 24)
            self.head_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.head_icon.hide()
            self.head_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.progress_bar.valueChanged.connect(self.update_icon_position)
        except Exception as e:
            print(f"Err head icon: {e}")
            
        card_layout.addWidget(path_label)
        card_layout.addLayout(path_input_layout)
        card_layout.addSpacing(5)
        card_layout.addWidget(self.backup_checkbox)
        card_layout.addSpacing(15)
        card_layout.addWidget(self.progress_bar)
        card_layout.addWidget(self.status_label)
        
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("✖  ANNULLA")
        self.cancel_btn.setObjectName("CancelButton")
        self.cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            
        self.install_btn = QPushButton("⚡  AVVIA INSTALLAZIONE")
        self.install_btn.setObjectName("InstallButton")
        self.install_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.install_btn.setDefault(True)
            
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.install_btn)
        
        self.layout.addLayout(header_layout)
        self.layout.addSpacing(5)
        self.layout.addWidget(card_frame, 1)
        self.layout.addSpacing(8)
        self.layout.addLayout(btn_layout)
        
        self.set_default_path()
        
    def set_default_path(self):
        default_path = ""
        base = os.path.expanduser("~")
        try:
            if platform.system() == "Windows":
                potential_bases = [
                    os.path.join(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)"), "Steam/steamapps/common"),
                    os.path.join(os.environ.get("ProgramFiles", "C:/Program Files"), "Steam/steamapps/common")
                ]
                import string
                available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
                for drive in available_drives:
                    if drive.lower() != 'c:':
                         potential_bases.append(os.path.join(drive, "Program Files (x86)/Steam/steamapps/common"))
                         potential_bases.append(os.path.join(drive, "Program Files/Steam/steamapps/common"))
                         potential_bases.append(os.path.join(drive, "SteamLibrary/steamapps/common"))
            elif platform.system() == "Linux":
                potential_bases = [
                    os.path.expanduser("~/.steam/steam/steamapps/common"),
                    os.path.expanduser("~/.local/share/Steam/steamapps/common"),
                    os.path.expanduser("~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/common"),
                    "/home/deck/.local/share/Steam/steamapps/common"
                ]
            else:
                potential_bases = [os.path.expanduser("~/Library/Application Support/Steam/steamapps/common")]
                
            found_base = None
            target_game_folder = "KINGDOM HEARTS -HD 1.5+2.5 ReMIX-"
            
            for base_path in potential_bases:
                if os.path.isdir(os.path.join(base_path, target_game_folder)):
                    found_base = os.path.join(base_path, target_game_folder)
                    break
                    
            if not found_base:
                 for base_path in potential_bases:
                     if os.path.isdir(base_path):
                         found_base = base_path
                         break
                         
            base = found_base if found_base else os.path.expanduser("~")
            default_path = os.path.join(base, DEFAULT_FOLDER_NAME)
        except Exception as e:
            print(f"Error determining default path: {e}")
            default_path = os.path.join(os.path.expanduser("~"), DEFAULT_FOLDER_NAME)
            
        self.path_input.setText(os.path.normpath(default_path).replace("\\", "/"))
        
    def select_folder(self):
        current_path = self.path_input.text()
        start_dir = current_path
        if not os.path.isdir(current_path):
            start_dir = os.path.dirname(current_path)
        if not os.path.isdir(start_dir):
            start_dir = os.path.expanduser("~")
            
        folder = QFileDialog.getExistingDirectory(self, "Seleziona la cartella principale di KINGDOM HEARTS -HD 1.5+2.5 ReMIX-", start_dir)
        if folder:
            self.path_input.setText(folder.replace("\\", "/"))
            
    def update_icon_position(self, value):
        try:
            if value > 1 and value < 100:
                self.head_icon.show()
            else:
                self.head_icon.hide()
                
            if not self.progress_bar.isVisible() or self.progress_bar.width() <= 0:
                return
                
            bar_rect = self.progress_bar.geometry()
            bar_top_left_in_parent = self.progress_bar.mapToParent(self.progress_bar.rect().topLeft())
            
            bar_x = bar_top_left_in_parent.x()
            bar_y = bar_top_left_in_parent.y()
            bar_w = bar_rect.width()
            
            icon_w = self.head_icon.width()
            icon_h = self.head_icon.height()
            padding = 0
            
            effective_bar_width = bar_w - (2 * padding)
            ratio = max(0, min(1, value / 100.0))
            
            x = bar_x + padding + int(effective_bar_width * ratio) - (icon_w // 2)
            x = max(bar_x + padding, min(x, bar_x + bar_w - icon_w - padding))
            y = bar_y + (bar_rect.height() - icon_h) // 2
            
            self.head_icon.move(x, y)
            self.head_icon.raise_()
        except Exception as e:
            print(f"Err icon pos: {e}")
            self.head_icon.hide()
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_icon_position(self.progress_bar.value())

class InstallerWizard(QWidget):
    def __init__(self):
        super().__init__()
        self.install_worker = None
        self.current_aes_key = leggi_chiave(resource_path(CHIAVE))
        self.setObjectName("InstallerWizard")
        
        self.version_checker = VersionCheckWorker(VERSIONE, GH_URL)
        self.version_checker.update_found.connect(self.show_update_dialog)
        self.version_checker.start()
        
        try:
            self.setWindowIcon(QIcon(LOGO_ICO))
        except Exception as e:
            print(f"Error setting window icon: {e}")
            
        self.setWindowTitle(f"Kingdom Hearts II Vocalia's Saga - Installer Patch ({VERSIONE})")
        self.setMinimumSize(740, 620)
        
        container = QWidget(self)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(container)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stack = QStackedWidget()
        container_layout.addWidget(self.stack)
        
        self.welcome = WelcomeScreen()
        self.notice = NoticeScreen()
        self.check_pkg = PackageCheckScreen(self)
        self.license = LicenseScreen()
        self.install = InstallScreen()
        
        self.stack.addWidget(self.welcome)
        self.stack.addWidget(self.notice)
        self.stack.addWidget(self.check_pkg)
        self.stack.addWidget(self.license)
        self.stack.addWidget(self.install)
        
        self.hidden_key_button = QPushButton(self)
        self.hidden_key_button.setObjectName("HiddenKeyButton")
        self.hidden_key_button.setFixedSize(10, 10)
        self.hidden_key_button.setFlat(True)
        self.hidden_key_button.setToolTip("Inserisci chiave AES personalizzata")
        self.hidden_key_button.setStyleSheet("background-color:transparent;border:none;")
        self.hidden_key_button.clicked.connect(self.show_custom_key_dialog)
        self.hidden_key_button.raise_()
        
        self.welcome.next_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.notice))
        self.welcome.notice_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.notice))
        self.welcome.license_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.license))
        self.notice.next_btn.clicked.connect(self.go_to_check)
        self.notice.back_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.welcome))
        self.check_pkg.next_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.license))
        self.license.next_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.install))
        self.install.install_btn.clicked.connect(self.confirm_installation)
        
        self.welcome.cancel_btn.clicked.connect(self.close)
        self.notice.cancel_btn.clicked.connect(self.close)
        self.check_pkg.cancel_btn.clicked.connect(self.close)
        self.license.cancel_btn.clicked.connect(self.close)
        self.install.cancel_btn.clicked.connect(self.handle_cancel_install)
        
        self.position_hidden_button()
        
    def show_update_dialog(self, new_version, url):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Aggiornamento Disponibile")
        msg_box.setText(f"È disponibile una nuova versione della patch: <b>{new_version}</b>")
        msg_box.setInformativeText("Vuoi aprire la pagina di download per scaricarla?")
        msg_box.setIcon(QMessageBox.Icon.Information)
        
        yes_button = msg_box.addButton("Sì, apri il sito", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("No, continua", QMessageBox.ButtonRole.NoRole)
        msg_box.setDefaultButton(yes_button)
        msg_box.exec()
        
        if msg_box.clickedButton() == yes_button:
            apri_url(url)
            self.close()
            
    def position_hidden_button(self):
        margin = 5
        button_size = self.hidden_key_button.size()
        x = self.width() - button_size.width() - margin
        y = margin
        self.hidden_key_button.move(x, y)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_hidden_button()
        if self.stack.currentWidget() == self.install:
            self.install.update_icon_position(self.install.progress_bar.value())
            
    def show_custom_key_dialog(self):
        current_key_str = ""
        try:
             if self.current_aes_key:
                 current_key_str = self.current_aes_key.decode('utf-8', errors='ignore')
        except Exception:
            pass
            
        text, ok = QInputDialog.getText(self, "Chiave AES Personalizzata", "Inserisci la chiave AES (stringa):", QLineEdit.EchoMode.Password, current_key_str)
        key_changed = False
        
        if ok and text:
            try:
                new_key_bytes = text.encode('utf-8')
                if new_key_bytes != self.current_aes_key:
                    self.current_aes_key = new_key_bytes
                    print("Chiave AES aggiornata (manuale).")
                    key_changed = True
            except Exception as e:
                QMessageBox.warning(self, "Errore Chiave", f"Errore codifica chiave: {e}")
                print(f"Err key enc: {e}")
        elif ok and not text:
             chiave_default = leggi_chiave(resource_path(CHIAVE))
             if self.current_aes_key != chiave_default:
                 self.current_aes_key = chiave_default
                 print("Chiave AES reimpostata al default (manuale).")
                 key_changed = True
                 
        if key_changed and self.stack.currentWidget() == self.check_pkg:
            print("Rieseguo check dopo cambio chiave manuale.")
            self.go_to_check()
            
    def go_to_check(self):
        package_to_check = PACKAGE_FILE
        self.check_pkg.check_package(package_to_check)
        self.stack.setCurrentWidget(self.check_pkg)
        
    def confirm_installation(self):
        dest_path = self.install.path_input.text()
        
        if not dest_path:
            QMessageBox.warning(self, "Percorso Mancante", "Specifica la cartella di installazione.")
            return
            
        do_backup = self.install.backup_checkbox.isChecked()
        game_root_path = os.path.normpath(dest_path)
        # La patch va nella root del gioco, non in una sottocartella
        install_path = game_root_path 
        
        if not os.path.isdir(game_root_path):
            QMessageBox.warning(self, "Percorso Non Valido", f"La directory base '{game_root_path}' non esiste o non è valida.")
            return
        
        executable_full_path = os.path.join(game_root_path, EXE_NAME)
        found = os.path.isfile(executable_full_path)
        warn_msg = ""
        
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)
        icon_pixmap = icon.pixmap(QSize(48, 48))

        # --- CONTROLLO PIRATERIA ---
        # Lista dei file tipicamente utilizzati dalle release pirata (es. CODEX, RUNE, FLT, ecc.)
        crack_files = [
            "steam_emu.ini", "steam_api64.cdx", "codex.ini", "codex64.dll",
            "flt.ini", "RUNE.ini", "TENOKE.ini", "SmartSteamEmu.ini",
            "RUNE.cdx", "gdk.ini", "ali213.ini", "steam_api.cdx",
            "OnlineFix.ini", "ForceLanguage.txt", "steam_api64.ini", "hlt.ini"
        ]
        
        # Cartelle tipicamente create dagli emulatori (es. Goldberg Emulator)
        crack_folders = [
            "steam_settings", "OfflineStorage", "Profile"
        ]
        
        for crack_file in crack_files:
            if os.path.isfile(os.path.join(game_root_path, crack_file)):
                dialog = PirateWarningDialog(self)
                dialog.exec()
                return
                
        for crack_folder in crack_folders:
            if os.path.isdir(os.path.join(game_root_path, crack_folder)):
                dialog = PirateWarningDialog(self)
                dialog.exec()
                return
        
        if not found:
            warn_msg = (f"<b>Attenzione:</b> Non è stato possibile trovare '{EXE_NAME}' nel percorso selezionato.<br><br>Assicurati di aver scelto la cartella principale di 'KINGDOM HEARTS -HD 1.5+2.5 ReMIX-'.")
            warn_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
            icon_pixmap = warn_icon.pixmap(QSize(48, 48))
        elif not os.path.exists(install_path):
            target_folder_name = os.path.basename(install_path)
            warn_msg = f"Nota: La cartella '{target_folder_name}' verrà creata."
            
        dialog = CustomConfirmDialog(parent=self, title="Conferma Installazione", text=f"Installare la mod in:<br><br><b>{install_path}</b>", informative_text="Procedere con l'operazione?", warning_text=warn_msg, icon_pixmap=icon_pixmap)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.perform_installation(dest_path, do_backup)
            
    def perform_installation(self, dest_path, do_backup):
        if self.install_worker and self.install_worker.isRunning():
            return
            
        if not self.current_aes_key:
            QMessageBox.critical(self, "Errore Chiave AES", f"Impossibile procedere: chiave AES non valida o non trovata ({CHIAVE}).")
            return
            
        try:
            os.makedirs(dest_path, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(self, "Errore Cartella", f"Impossibile creare o accedere alla cartella di destinazione:\n{dest_path}\nErrore: {e}")
            return
            
        self.install.install_btn.setEnabled(False)
        self.install.cancel_btn.setText("Annulla")
        self.install.cancel_btn.setObjectName("CancelButton")
        self.install.path_input.setEnabled(False)
        self.install.browse_btn.setEnabled(False)
        self.install.backup_checkbox.setEnabled(False)
        self.install.status_label.setText("Avvio preparazione operazione...")
        self.install.progress_bar.setValue(0)
        self.install.head_icon.hide()
        
        package_to_install = PACKAGE_FILE
        print(f"Avvio installazione del pacchetto: {package_to_install}")
        
        self.install_worker = InstallWorker(dest_path, self.current_aes_key, do_backup, package_to_install)
        self.install_worker.progress.connect(self.update_progress)
        self.install_worker.finished.connect(self.on_finished)
        self.install_worker.backup_status.connect(self.update_backup_status)
        self.install_worker.start()
        
    def update_backup_status(self, message):
        self.install.status_label.setText(message)
        QApplication.processEvents()
        
    def update_progress(self, value):
        self.install.progress_bar.setValue(value)
        if value > 0 and value < 100:
            self.install.status_label.setText(f"Installazione in corso... {value}%")
        self.install.update_icon_position(value)
        
    def on_finished(self, success, message):
        self.install.install_btn.setEnabled(True)
        self.install.cancel_btn.setText("Chiudi")
        self.install.cancel_btn.setObjectName("CancelButton")
        self.install.cancel_btn.setEnabled(True)
        self.install.path_input.setEnabled(True)
        self.install.browse_btn.setEnabled(True)
        self.install.backup_checkbox.setEnabled(True)
        self.install.head_icon.hide()
        self.install_worker = None
        
        if success:
            self.install.progress_bar.setValue(100)
            self.install.status_label.setText(message)
            completion_dialog = CompletionDialog(parent=self, title="Installazione Completata", text="Operazione completata con successo.", url_to_open=DONAZIONI)
            completion_dialog.exec()
        else:
            print(f"DEBUG: on_finished received error message: '{message}'")
            self.install.progress_bar.setValue(0)
            
            if message == "Installazione annullata dall'utente." or message == "Backup annullato dall'utente.":
                self.install.status_label.setText("Operazione annullata.")
            elif "chiave AES usata non è valida" in message or "archivio è corrotto" in message or "file zip non valido" in message:
                 self.install.status_label.setText("Errore: Chiave AES / Archivio.")
                 QMessageBox.warning(self, "Errore Chiave AES o Archivio", f"Si è verificato un errore durante l'estrazione:\n{message}\n\nLa chiave AES fornita non è corretta o il file della patch è corrotto.\n\nPuoi provare a inserire una chiave diversa usando il piccolo pulsante trasparente in alto a destra, quindi riprova l'installazione. Se il problema persiste, verifica l'integrità del file della patch.")
            elif "Errore durante il backup" in message:
                 self.install.status_label.setText("Errore durante il backup.")
                 QMessageBox.critical(self, "Errore di Backup", message)
            else:
                self.install.status_label.setText("Errore durante l'operazione.")
                QMessageBox.critical(self, "Errore", f"Si è verificato un errore:\n{message}\n\nControlla il file '{LOG_FILE}' per maggiori dettagli tecnici.")
                
    def handle_cancel_install(self):
        if self.install_worker and self.install_worker.isRunning():
             msg_box = QMessageBox(self)
             msg_box.setWindowTitle("Annulla Operazione")
             msg_box.setText("Interrompere l'operazione in corso?")
             msg_box.setIcon(QMessageBox.Icon.Question)
             msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
             msg_box.setDefaultButton(QMessageBox.StandardButton.No)
             
             yes_b = msg_box.button(QMessageBox.StandardButton.Yes)
             yes_b.setObjectName("CancelButton")
             no_b = msg_box.button(QMessageBox.StandardButton.No)
             no_b.setObjectName("AcceptButton")
             
             if msg_box.exec() == QMessageBox.StandardButton.Yes:
                 self.install_worker.requestInterruption()
                 self.install.status_label.setText("Annullamento in corso...")
                 self.install.cancel_btn.setEnabled(False)
        else:
            self.close()
            
    def closeEvent(self, event):
        if self.install_worker and self.install_worker.isRunning():
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Operazione In Corso")
            msg_box.setText("Operazione in corso. Interrompere e uscire?")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            
            yes_b = msg_box.button(QMessageBox.StandardButton.Yes)
            yes_b.setObjectName("CancelButton")
            no_b = msg_box.button(QMessageBox.StandardButton.No)
            no_b.setObjectName("AcceptButton")
            
            if msg_box.exec() == QMessageBox.StandardButton.Yes:
                self.install_worker.requestInterruption()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_custom_fonts()
    app.setStyle("Fusion")
    app.setStyleSheet(get_dynamic_stylesheet())
    wizard = InstallerWizard()
    wizard.show()
    sys.exit(app.exec())
