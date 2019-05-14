#!/usr/bin/python3
import os
import time
from datetime import datetime
import json
from pathlib import Path
from configparser import ConfigParser
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

import telegram_events

if not os.path.isfile("config.ini"):
    print("Il file di configurazione non è presente. Rinomina il file 'config-sample.ini' in 'config.ini' e inserisci il token.")
    exit()

script_path = os.path.dirname(os.path.realpath(__file__))
config_parser = ConfigParser()
config_parser.read(os.path.join(script_path, "config.ini"))

TOKEN = config_parser.get("access", "token")

if TOKEN == "":
    print("Token non presente.")
    exit()

if Path("frasi.json").exists():
    frasi = json.loads(open("frasi.json", encoding="utf8").read())
else:
    print("File frasi non presente.")
    exit()

versione = "1.4.8"  # Cambiare manualmente
ultimo_aggiornamento = "14-05-2019"  # Cambiare manualmentente

# Per poter sapere quale versione è in esecuzione (da terminale)
print("(Antispam) Versione: " + versione + " - Aggiornamento: " + ultimo_aggiornamento)

BLOCCO_PAROLE_VIETATE = 2  # 0 -> Attivato: Elimina messaggi e invia messaggio agli admin in privato
# 1 -> Disattivato: Non effettua alcun controllo
# 2 -> "Semi"-Attivo: NON elimina messaggi, ma invia messaggio agli admin in privato

USER_ID_BOT = "732117113"

data_salvataggio = ""
response = ""

adminlist_path = "adminlist.json"
whitelist_path = "whitelist.json"
blacklist_path = "blacklist.json"
blacklist_name_path = "blacklist_name.json"
templist_path = "templist.json"
templist_name_path = "templist_name.json"
spamlist_path = "spamlist.json"
chat_name_path = "chat_name.json"
parole_vietate_path = "parole_vietate.json"
adminlist = []
whitelist = []
blacklist = {}
blacklist_name = {}
templist = {}
templist_name = {}
spamlist = []
if Path(chat_name_path).exists():
    chat_name = json.loads(open(chat_name_path).read())
else:
    chat_name = {}
if Path(parole_vietate_path).exists():
    parole_vietate = json.loads(open(parole_vietate_path).read())
else:
    parole_vietate = []

# elimina il messaggio - Passare chat_id e message_id

def elimina_msg(chat_id, message_id, messaggio_eliminato=False):
    if not messaggio_eliminato:
        bot.deleteMessage((chat_id, message_id))
        return True
    return False

# assegna un unsername alternativo se l'userid non ha alcun username valido

def nousername_assegnazione(nousername, user_id, user_name):
    if nousername:
        return "<a href='tg://user?id=" + str(user_id) + "'>" + str(user_id) + "</a>"
    else:
        return "<a href='tg://user?id=" + \
            str(user_id) + "'>@" + str(user_name) + "</a>" + " (<code>" + str(user_id) + "</code>)"


# determina lo status dell'utente: user_id -> intero e type_msg -> stringa
# - Restituisce {"A"|"W"|"B"|"T"|"S"|"-"}
def identifica_utente(user_id):
    global adminlist
    global whitelist
    global blacklist
    global templist
    global spamlist
    user_id = int(user_id)

    if user_id in adminlist and user_id in whitelist:
        status_user = "A"  # adminlist
    elif user_id in spamlist:
        status_user = "S"  # spamlist
    elif user_id in whitelist:
        status_user = "W"  # whitelist
    elif user_id in blacklist.values():
        status_user = "B"  # blacklist
    elif user_id in templist.values():
        status_user = "T"  # templist
    else:
        status_user = "-"  # Other
    return status_user

# controlla se il messaggio inviato contiene una o più parole vietate - Restituisce {True|False}

def check_parole_vietate(text, attivato):
    global parole_vietate
    if attivato == 0 or attivato == 2:
        if any(ext in text.lower() for ext in parole_vietate):
            return True
    return False

# stampa_su_file(<cosa stampare>,<{True|False} indica se è una stampa di
# ERRORE/ECCEZIONE o una stampa 'normale'>)

def stampa_su_file(stampa, err):
    global response, data_salvataggio
    if err:
        stampa = str(response) + "\n\n" + str(stampa)
    stampa = stampa + "\n--------------------\n"
    try:
        if os.path.exists("./history_mozitaantispam") == False:
            os.mkdir("./history_mozitaantispam")
    except Exception as exception_value:
        print("Excep:21 -> " + str(exception_value))
        stampa_su_file("Except:21 ->" + str(exception_value), True)

    try:
        # apre il file in scrittura "append" per inserire orario e data -> log di
        # utilizzo del bot (ANONIMO)
        file = open("./history_mozitaantispam/log_" +
                    str(data_salvataggio) + ".txt", "a", -1, "UTF-8")
        # ricordare che l'orario è in fuso orario UTC pari a 0 (Greenwich, Londra)
        # - mentre l'Italia è a +1 (CET) o +2 (CEST - estate)
        file.write(stampa)
        file.close()
    except Exception as exception_value:
        print("Excep:03 -> " + str(exception_value))
        stampa_su_file("Except:03 ->" + str(exception_value), True)


def invia_messaggio_admin(msg):
    for admin_x in adminlist:
        try:
            bot.sendMessage(admin_x, "📌  " + msg, parse_mode="HTML")
        except Exception as exception_value:
            print("Excep:25 -> " + str(exception_value))
            stampa_su_file("Except:25 ->" + str(exception_value), True)


def risposte(msg):
    localtime = datetime.now()
    global data_salvataggio
    data_salvataggio = localtime.strftime("%Y_%m_%d")
    localtime = localtime.strftime("%d/%m/%y %H:%M:%S")
    messaggio = msg
    type_msg = ""

    modificato = False
    risposta = False

    global response
    response = bot.getUpdates()
    # print(response) # da mettere come commento nella stabile

    global adminlist
    global whitelist
    global blacklist
    global blacklist_name
    global templist
    global templist_name
    global spamlist
    if Path(adminlist_path).exists():
        adminlist = json.loads(open(adminlist_path).read())
    else:
        # nel caso in cui non dovesse esistere alcun file "adminlist.json" imposta
        # staticamente l'userid di Sav22999 -> così da poter confermare anche
        # altri utenti
        adminlist = [240188083]
    if Path(whitelist_path).exists():
        whitelist = json.loads(open(whitelist_path).read())
    if Path(blacklist_path).exists():
        blacklist = json.loads(open(blacklist_path).read())
    if Path(blacklist_name_path).exists():
        blacklist_name = json.loads(open(blacklist_name_path).read())
    if Path(templist_path).exists():
        templist = json.loads(open(templist_path).read())
    if Path(templist_name_path).exists():
        templist_name = json.loads(open(templist_name_path).read())
    if Path(spamlist_path).exists():
        spamlist = json.loads(open(spamlist_path).read())

    # caricamento degli eventi gestiti
    EventiList = {}
    EventiList = telegram_events.events(msg, ["[[ALL]]"], response)
    text = EventiList["text"]
    type_msg = EventiList["type_msg"]
    modificato = EventiList["modificato"]
    risposta = EventiList["risposta"]

    # verifica se (1) è stato AGGIUNTO (2) è stato RIMOSSO (3) si è UNITO (4) è USCITO
    try:
        if type_msg == "JA":
            user_id = msg['new_chat_participant']['id']
            nousername = False
            if "username" in msg['new_chat_participant']:
                user_name = msg['new_chat_participant']['username']
            else:
                user_name = "[*NessunUsername*]" + str(user_id)
                nousername = True
        elif type_msg == "LR":
            user_id = msg['left_chat_participant']['id']
            nousername = False
            if "username" in msg['left_chat_participant']:
                user_name = msg['left_chat_participant']['username']
            else:
                user_name = "[*NessunUsername*]" + str(user_id)
                nousername = True
        else:
            user_id = msg['from']['id']
            nousername = False
            if "username" in msg['from']:
                user_name = msg['from']['username']
            else:
                user_name = "[*NessunUsername*]" + str(user_id)
                nousername = True
    except Exception as exception_value:
        print("Excep:22 -> " + str(exception_value))
        stampa_su_file("Except:22 ->" + str(exception_value), True)

        user_id = msg['from']['id']
        user_name = "[*NessunUsername*]" + str(user_id)
        nousername = True
    # print(user_id)
    # print(user_name)
    if "chat" not in msg:
        msg = msg["message"]
    chat_id = msg['chat']['id']
    # print(chat_id)
    message_id = msg['message_id']
    # print(message_id)

    username_utente_nousername = nousername_assegnazione(nousername, user_id, user_name)

    if str(chat_id) in chat_name and msg['chat']['type'] != "private":
        # BOT NEI GRUPPI ABILITATI

        messaggio_eliminato = False

        # ricava dalla chat_name list il nome della chat
        nome_gruppo = str(chat_name[str(chat_id)])

        # inline button message -> possono verificarsi SOLO se si è nei gruppi abilitati
        new = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=frasi["button_mostra_regolamento"], callback_data="/leggiregolamento")],
            [InlineKeyboardButton(text=frasi["button_blocca_utente"], callback_data="/bloccautente")],
        ])
        regolamentoletto = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=frasi["button_leggi_regolamento"], url='https://github.com/Sav22999/Guide/blob/master/Mozilla%20Italia/Telegram/regolamento.md')],
            [InlineKeyboardButton(text=frasi["button_conferma_utente"], callback_data='/confutente')],
            [InlineKeyboardButton(text=frasi["button_blocca_utente"], callback_data="/bloccautente")],
        ])

        messaggio_benvenuto = str(
            (frasi["benvenuto"]).replace(
                "{{**username**}}",
                str(username_utente_nousername))).replace(
            "{{**nome_gruppo**}}",
            str(nome_gruppo))

        global BLOCCO_PAROLE_VIETATE
        controllo_parole_vietate = check_parole_vietate(text, BLOCCO_PAROLE_VIETATE)
        if controllo_parole_vietate:
            # Parola vietata inserita
            if BLOCCO_PAROLE_VIETATE == 0:
                if not messaggio_eliminato:
                    messaggio_eliminato = elimina_msg(chat_id, message_id, messaggio_eliminato)
                    text = frasi["eliminato_da_bot"] + text
                username_utente_nousername = nousername_assegnazione(nousername, user_id, user_name)
                bot.sendMessage(chat_id, str(frasi["parola_vietata_presente"]).replace(
                    "{{**username**}}", str(username_utente_nousername)), parse_mode="HTML")
            invia_messaggio_admin(
                username_utente_nousername +
                ": PAROLA VIETATA -- Gruppo: <b>" +
                str(nome_gruppo) +
                "</b>\n\nTesto messaggio:\n<i>" +
                str(text) +
                "</i>")

        status_user = identifica_utente(user_id)

        try:
            if status_user == "-":
                if not messaggio_eliminato and not type_msg == "BIC":
                    messaggio_eliminato = elimina_msg(chat_id, message_id, messaggio_eliminato)
                    text = frasi["eliminato_da_bot"] + text
                elif type_msg == "BIC":
                    messaggio_eliminato = True
            elif status_user == "S" and not (text == "/bloccautente" and type_msg == "BIC"):
                if not messaggio_eliminato:
                    messaggio_eliminato = elimina_msg(chat_id, message_id, messaggio_eliminato)
                    text = frasi["eliminato_da_bot"] + text
                try:
                    bot.kickChatMember(chat_id, user_id, until_date=None)
                    username_utente_nousername = nousername_assegnazione(
                        nousername, user_id, user_name)
                    bot.sendMessage(
                        chat_id, str(
                            frasi["utente_cacciato"]).replace(
                            "{{**username**}}", str(username_utente_nousername)), parse_mode="HTML")
                except Exception as exception_value:
                    print("Excep:24 -> " + str(exception_value))
                    stampa_su_file("Except:24 ->" + str(exception_value), True)
                invia_messaggio_admin(
                    username_utente_nousername +
                    ": CACCIATO -- Gruppo: <b>" +
                    str(nome_gruppo) +
                    "</b>")
            elif status_user == "B" and type_msg != "BIC":
                if type_msg != "J" and type_msg != "L":
                    if not messaggio_eliminato:
                        messaggio_eliminato = elimina_msg(chat_id, message_id, messaggio_eliminato)
                        text = frasi["eliminato_da_bot"] + text
            elif status_user == "T" and type_msg != "BIC":
                # Accettati solamente messaggi di TESTO, STICKER e GIF
                if type_msg != "NM" and type_msg != "S" and type_msg != "G" and (
                        type_msg != "J" and type_msg != "L"):
                    if not messaggio_eliminato:
                        messaggio_eliminato = elimina_msg(chat_id, message_id, messaggio_eliminato)
                        text = frasi["eliminato_da_bot"] + text

            if type_msg == "NI":
                # Tipo di messaggio NonIdentificato -> viene eliminato
                if not messaggio_eliminato:
                    messaggio_eliminato = elimina_msg(chat_id, message_id, messaggio_eliminato)
                    text = frasi["eliminato_da_bot"] + text
            if text == frasi["eliminato_da_bot"] + "/confutente":
                messaggio_eliminato = True # 

            global USER_ID_BOT
            # 732117113 -> userid del bot
            if type_msg == "J" and not str(user_id) == USER_ID_BOT:
                # Nuovo utente
                bot.sendMessage(chat_id, messaggio_benvenuto, reply_markup=new, parse_mode="HTML")
                blacklist[str(message_id)] = int(user_id)
                blacklist_name[str(user_id)] = str(user_name)
                try:
                    with open(blacklist_path, "wb") as file_with:
                        file_with.write(json.dumps(blacklist).encode("utf-8"))
                    with open(blacklist_name_path, "wb") as file_with:
                        file_with.write(json.dumps(blacklist_name).encode("utf-8"))
                except Exception as exception_value:
                    print("Excep:13 -> " + str(exception_value))
                    stampa_su_file("Except:13 ->" + str(exception_value), True)
            elif (type_msg != "J" and type_msg != "L" and not str(user_id) == USER_ID_BOT and status_user == "-") or (text == frasi["eliminato_da_bot"] + "/benvenuto" and type_msg == "LK" and not (user_id in templist.values()) and not (user_id in whitelist)):
                # Utente già presente nel gruppo ma non presente in alcuna lista
                bot.sendMessage(chat_id, messaggio_benvenuto, reply_markup=new, parse_mode="HTML")
                blacklist[str(message_id)] = int(user_id)
                blacklist_name[str(user_id)] = str(user_name)
                if not messaggio_eliminato:
                    messaggio_eliminato = elimina_msg(chat_id, message_id, messaggio_eliminato)
                    text = frasi["eliminato_da_bot"] + text
                try:
                    with open(blacklist_path, "wb") as file_with:
                        file_with.write(json.dumps(blacklist).encode("utf-8"))
                    with open(blacklist_name_path, "wb") as file_with:
                        file_with.write(json.dumps(blacklist_name).encode("utf-8"))
                except Exception as exception_value:
                    print("Excep:14 -> " + str(exception_value))
                    stampa_su_file("Except:14 ->" + str(exception_value), True)
            else:
                if text == "/leggiregolamento" and type_msg == "BIC":
                    user_id_presente = True
                    try:
                        user_id_to_use = int(blacklist[str(int(message_id) - 1)])
                    except Exception as exception_value:
                        print("Excep:31 -> " + str(exception_value))
                        stampa_su_file("Except:31 ->" + str(exception_value), True)
                        user_id_presente = False
                    if user_id_presente and user_id == user_id_to_use:
                        try:
                            # cancella messaggio di benvenuto
                            elimina_msg(chat_id, message_id)
                        except Exception as exception_value:
                            print("Excep:27 -> " + str(exception_value))
                            stampa_su_file("Except:27 ->" + str(exception_value), True)
                        if not user_id_to_use in whitelist:
                            templist[str(int(message_id) - 1)] = blacklist[str(int(message_id) - 1)]
                            # print(templist[str(int(message_id)-1)]) #userid
                            templist_name[str(templist[str(int(message_id) - 1)])
                                        ] = blacklist_name[str(blacklist[str(int(message_id) - 1)])]
                            del blacklist[str(int(message_id) - 1)] # cancello l'utente SOLO dalla BlackList (quando viene confermato, poi, viene rimosso anche dalla BlackList_name e viene rimosso ogni voce correlata residua anche da BlackList)
                            '''
                            Spiegazione: Un utente può entrare in vari gruppi (o comunque mostrare il messaggio di benvenuto tramite /benvenuto),
                            quindi può essere presente più di una ricorrenza nella BlackList -> le altre ricorrenze vengono automaticamente rimosse quando l'utente viene confermato
                            '''
                            status_user = "T"
                            username_utente_nousername = nousername_assegnazione(
                                nousername, user_id, user_name)

                            bot.sendMessage(
                            chat_id, str(
                                frasi["regolamento_letto"]).replace(
                                "{{**username**}}", str(username_utente_nousername)), reply_markup=regolamentoletto, parse_mode="HTML")

                        try:
                            with open(blacklist_path, "wb") as file_with:
                                file_with.write(json.dumps(blacklist).encode("utf-8"))
                            with open(templist_path, "wb") as file_with:
                                file_with.write(json.dumps(templist).encode("utf-8"))
                            with open(templist_name_path, "wb") as file_with:
                                file_with.write(json.dumps(templist_name).encode("utf-8"))
                        except Exception as exception_value:
                            text += "\n >> >> Esito: NO"
                            print("Excep:15 -> " + str(exception_value))
                            stampa_su_file("Except:15 ->" + str(exception_value), True)
                        text = "|| Lettura regolamento ||\n >> >> Esito: OK"
                    else:
                        text = "|| Lettura regolamento ||\n >> >> Esito: NO"
                    
                    if not user_id_presente:
                        try:
                            # cancella messaggio di benvenuto
                            elimina_msg(chat_id, message_id)
                        except Exception as exception_value:
                            print("Excep:27 -> " + str(exception_value))
                            stampa_su_file("Except:27 ->" + str(exception_value), True)

                elif text == "/confutente" and type_msg == "BIC":
                    if user_id in whitelist or user_id in adminlist:
                        user_name_temp = str(msg['text'].split(" ")[0])
                        user_id_temp = 0
                        # print("Username temp: "+str(user_name_temp))
                        # print("Messaggio:"+msg['text'])
                        if "@" in user_name_temp:
                            user_name_temp = user_name_temp.lstrip("@")
                        else:
                            user_name_temp = "[*NessunUsername*]" + str(user_name_temp)
                        if str(user_name_temp) in templist_name.values():
                            username_utente_nousername = nousername_assegnazione(
                                nousername, user_id, user_name)
                            user_id_temp = int(
                                next(
                                    (x for x in templist_name if templist_name[x] == str(user_name_temp)),
                                    None))
                            message_id_temp = int(
                                next(
                                    (x for x in templist if templist[x] == int(user_id_temp)),
                                    None)) + 1
                            username_utente_nousername_temp = nousername_assegnazione(
                                nousername, user_id_temp, str(templist_name[str(templist[str(int(message_id_temp) - 1)])]))
                            #print("Utente da verificare: "+str(templist[int(message_id_temp)-1]) + "Message id: "+str(message_id_temp))
                            if not user_id_temp in whitelist:
                                bot.sendMessage(
                                    chat_id,
                                    str(
                                        (frasi["utente_confermato"]).replace(
                                            "{{**utente_che_conferma**}}",
                                            str(username_utente_nousername))).replace(
                                        "{{**utente_confermato**}}",
                                        str(username_utente_nousername_temp)),
                                    parse_mode="HTML")
                                bot.sendMessage(chat_id, str( frasi["utente_confermato2"]).replace(
                                    "{{**username**}}", str(username_utente_nousername_temp)), parse_mode="HTML")
                                if not int(templist[str(int(message_id_temp) - 1)]) in whitelist:
                                    whitelist.append(int(templist[str(int(message_id_temp) - 1)]))
                                user_id_to_delete = str(templist[str(int(message_id_temp) - 1)])
                                del blacklist_name[user_id_to_delete] # cancello l'utente anche dalla BlackList_Name
                                del templist_name[user_id_to_delete] # cancello l'utente dalla TempList_Name
                                list_black_msg_id_to_delete = []
                                list_temp_msg_id_to_delete = []
                                for x in blacklist:
                                    if str(blacklist[x]) == user_id_to_delete:
                                        list_black_msg_id_to_delete.append(x)
                                for x in templist:
                                    if str(templist[x]) == user_id_to_delete:
                                        list_temp_msg_id_to_delete.append(x)
                                for x in list_black_msg_id_to_delete:
                                    del blacklist[x] # cancello ogni traccia rimanente (se presente) dalla BlackList
                                for x in list_temp_msg_id_to_delete:
                                    del templist[x] # cancello l'utente dalla TempList
                                status_user = "W"

                            try:
                                with open(blacklist_path, "wb") as file_with:
                                    file_with.write(json.dumps(blacklist).encode("utf-8"))
                                with open(blacklist_name_path, "wb") as file_with:
                                    file_with.write(json.dumps(blacklist_name).encode("utf-8"))
                                with open(whitelist_path, "wb") as file_with:
                                    file_with.write(json.dumps(whitelist).encode("utf-8"))
                                with open(templist_path, "wb") as file_with:
                                    file_with.write(json.dumps(templist).encode("utf-8"))
                                with open(templist_name_path, "wb") as file_with:
                                    file_with.write(json.dumps(templist_name).encode("utf-8"))
                            except Exception as exception_value:
                                text += "\n >> >> Esito: NO"
                                print("Excep:16 -> " + str(exception_value))
                                stampa_su_file("Except:16 ->" + str(exception_value), True)
                        try:
                            # cancella messaggio di 'regolamento letto'
                            elimina_msg(chat_id, message_id)
                            # print(message_id_temp_deletemessage)
                        except Exception as exception_value:
                            print("Excep:28 -> " + str(exception_value))
                            stampa_su_file("Except:28 ->" + str(exception_value), True)
                        text = "|| Conferma utente ||\n >> >> Esito: OK"
                    else:
                        text = "|| Conferma utente ||\n >> >> Esito: NO"
                elif text == "/bloccautente" and type_msg == "BIC":
                    if user_id in adminlist:
                        user_name_temp = str(msg['text'].split(" ")[0])
                        if "@" in user_name_temp:
                            user_name_temp = user_name_temp.lstrip("@")
                        else:
                            user_name_temp = "[*NessunUsername*]" + str(user_name_temp)
                        user_id_temp = 0  # imposto l'user_id a "0"

                        if user_name_temp in templist_name.values():
                            user_id_temp = int(
                                list(
                                    templist_name.keys())[
                                    list(
                                        templist_name.values()).index(
                                        str(user_name_temp))])
                            msg_id_temp = int(
                                list(
                                    templist.keys())[
                                    list(
                                        templist.values()).index(
                                        int(user_id_temp))])
                            del blacklist_name[str(user_id_temp)] # cancello l'utente da BlackList_name
                            del templist_name[str(user_id_temp)] # cancello l'utente da TempList_name

                            list_temp_msg_id_to_delete = []
                            for x in templist:
                                if str(templist[x]) == str(user_id_temp):
                                    list_temp_msg_id_to_delete.append(x)
                            for x in list_temp_msg_id_to_delete:
                                del templist[x] # cancello ogni traccia dell'utente spam dalla TempList
                            # print("Utente templist eliminato\n")
                        elif user_name_temp in blacklist_name.values():
                            user_id_temp = int(
                                list(
                                    blacklist_name.keys())[
                                    list(
                                        blacklist_name.values()).index(
                                        str(user_name_temp))])
                            msg_id_temp = int(
                                list(
                                    blacklist.keys())[
                                    list(
                                        blacklist.values()).index(
                                        int(user_id_temp))])
                            del blacklist_name[str(user_id_temp)]

                            list_black_msg_id_to_delete = []
                            for x in blacklist:
                                if str(blacklist[x]) == str(user_id_temp):
                                    list_black_msg_id_to_delete.append(x)
                            for x in list_black_msg_id_to_delete:
                                del blacklist[x] # cancello ogni traccia dell'utente spam dalla BlackList
                            # print("Utente blacklist eliminato\n")
                        # print(str(user_id_temp) + " " + str(user_name_temp) + " " + str(msg_id_temp))
                        if not(user_id_temp in adminlist) and not user_id_temp == 0:
                            try:
                                if not int(user_id_temp) in spamlist:
                                    spamlist.append(int(user_id_temp))
                                    bot.kickChatMember(chat_id, user_id_temp, until_date=None)
                                    username_utente_nousername = nousername_assegnazione(
                                        nousername, user_id_temp, user_name_temp)
                                    # bot.sendMessage(chat_id, str(frasi["utente_cacciato"]).replace("{{**username**}}", str(username_utente_nousername)), parse_mode="HTML")
                                    status_user = "S"  # spamlist
                                    if user_id in adminlist:
                                        status_user = "A"
                                    invia_messaggio_admin(
                                        username_utente_nousername +
                                        ": BLOCCATO E CACCIATO -- Gruppo: <b>" +
                                        str(nome_gruppo) +
                                        "</b>")
                                text = "|| Un utente è stato bloccato e cacciato ||"
                            except Exception as exception_value:
                                text += "\n >> >> Esito: NO"
                                print("Excep:23 -> " + str(exception_value))
                                stampa_su_file("Except:23 ->" + str(exception_value), True)
                        try:
                            with open(spamlist_path, "wb") as file_with:
                                file_with.write(json.dumps(spamlist).encode("utf-8"))
                            with open(blacklist_path, "wb") as file_with:
                                file_with.write(json.dumps(blacklist).encode("utf-8"))
                            with open(blacklist_name_path, "wb") as file_with:
                                file_with.write(json.dumps(blacklist_name).encode("utf-8"))
                            with open(templist_path, "wb") as file_with:
                                file_with.write(json.dumps(templist).encode("utf-8"))
                            with open(templist_name_path, "wb") as file_with:
                                file_with.write(json.dumps(templist_name).encode("utf-8"))
                        except Exception as exception_value:
                            print("Excep:18 -> " + str(exception_value))
                            stampa_su_file("Except:18 ->" + str(exception_value), True)
                        text = "|| Blocca utente ||\n >> >> Esito: OK"
                        try:
                            # cancella messaggio
                            elimina_msg(chat_id, message_id)
                        except Exception as exception_value:
                            print("Excep:29 -> " + str(exception_value))
                            stampa_su_file("Except:29 ->" + str(exception_value), True)
                    else:
                        text = "|| Blocca utente ||\n >> >> Esito: NO"
        except Exception as exception_value:
            print("Excep:01 -> " + str(exception_value))
            stampa_su_file("Except:01 ->" + str(exception_value), True)

        try:
            dettagli = ""
            if modificato:
                dettagli += "(modificato) "
            if risposta:
                dettagli += "(risposta) "
            stampa = "Id Msg: " + str(message_id) + "  --  " + str(localtime) + "  --  Utente: " + str(user_name) + " (" + str(user_id) + ")[" + str(status_user) + "]  --  Gruppo: " + str(
                nome_gruppo) + "(" + str(chat_id) + ")\n >> >> Tipo messaggio: " + str(type_msg) + "\n >> >> Contenuto messaggio: " + str(dettagli) + str(text)
            print(stampa + "\n--------------------\n")
        except Exception as exception_value:
            stampa = "Excep:02 -> " + str(exception_value)
            print(stampa + "\n--------------------\n")

        stampa_su_file(stampa, False)

    elif msg['chat']['type'] == "private":
        # BOT IN CHAT PRIVATA

        segnalazione_da_utente_bloccato = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=frasi["messaggio_chat_privata_utente_bloccato_button"], callback_data="/segnalapossibileerrore")],
        ])

        messaggio_sviluppatore_versione_aggiornamento = "MozIta Antispam Bot è stato sviluppato, per la comunità italiana di Mozilla Italia, da Saverio Morelli (@Sav22999) con il supporto e aiuto di Damiano Gualandri (@dag7dev), Simone Massaro (@mone27) e molti altri.\n\n" + \
            "Versione: " + versione + " - Aggiornamento: " + ultimo_aggiornamento
        status_user = identifica_utente(user_id)
        if status_user == "A":
            err1 = False
            err2 = False
            esito = "NO"
            # print(type_msg)
            if type_msg == "NM" or type_msg == "LK":
                type_link = False
                if type_msg == "LK":
                    type_link = True
                if text == "/start" and type_link:
                    bot.sendMessage(
                        chat_id,
                        "Benvenuto nella chat privata del bot.\nPuoi interagire con il bot, in chat privata, perché sei un amministratore.\nDigita /help per ottenere la lista di tutte le azioni che puoi fare nel bot IN PRIVATO (i comandi NON funzionano nei gruppi abilitati).")
                    esito = "OK"
                elif text == "/help" and type_link:
                    bot.sendMessage(chat_id, "Elenco azioni disponibili:\n - utente aggiungi |USERID|\n - utente blocca |USERID|\n - utente sblocca |USERID|\n - parola mostra\n - parola aggiungi |PAROLA/FRASE|\n - parola elimina |PAROLA/FRASE|\n - gruppo mostra\n - gruppo aggiungi |USERID| |NOME GRUPPO|\n - gruppo elimina |USERID|\n - invia messaggio |TESTO MESSAGGIO|\n - lista white mostra\n - lista spam mostra\n - lista black mostra\n - lista black elimina\n - lista temp mostra\n - lista temp elimina")
                    bot.sendMessage(chat_id, messaggio_sviluppatore_versione_aggiornamento)
                    esito = "OK"

                if (("utente" in text or "parola" in text or "gruppo" in text or "lista" in text) and not type_link) or "invia messaggio" in text:
                    azione = list(text.split(" "))
                    if azione[0] == "lista" and len(azione) == 3 and not type_link:
                        if azione[1] == "admin":
                            if azione[2] == "mostra":
                                # mostra la adminlist
                                bot.sendMessage(chat_id, "adminlist:\n" + str(adminlist))
                            else:
                                err1 = True
                        elif azione[1] == "white":
                            if azione[2] == "mostra":
                                # mostra la whitelist
                                bot.sendMessage(chat_id, "whitelist:\n" + str(whitelist))
                            else:
                                err1 = True
                        elif azione[1] == "black":
                            if azione[2] == "elimina":
                                # elimina il contenuto delle blacklist
                                blacklist = {}
                                blacklist_name = {}
                                bot.sendMessage(
                                    chat_id, "Le seguenti liste sono state azzerate:\n- blacklist\n- blacklist_name")
                            elif azione[2] == "mostra":
                                # mostra le blacklist
                                bot.sendMessage(
                                    chat_id,
                                    "blacklist:\n" +
                                    str(blacklist) +
                                    "\n\nblacklist_name:\n" +
                                    str(blacklist_name))
                            else:
                                err1 = True
                        elif azione[1] == "temp":
                            if azione[2] == "elimina":
                                # elimina il contenuto delle templist
                                templist = {}
                                templist_name = {}
                                bot.sendMessage(
                                    chat_id, "Le seguenti liste sono state azzerate:\n- templist\n- templist_name")
                            elif azione[2] == "mostra":
                                # mostra le templist
                                bot.sendMessage(
                                    chat_id,
                                    "templist:\n" +
                                    str(templist) +
                                    "\n\ntemplist_name:\n" +
                                    str(templist_name))
                            else:
                                err1 = True
                        elif azione[1] == "spam":
                            if azione[2] == "mostra":
                                # mostra la spamlist
                                bot.sendMessage(chat_id, "spamlist:\n" + str(spamlist))
                            else:
                                err1 = True
                        else:
                            err1 = True
                        try:
                            with open(blacklist_path, "wb") as file_with:
                                file_with.write(json.dumps(blacklist).encode("utf-8"))
                            with open(blacklist_name_path, "wb") as file_with:
                                file_with.write(json.dumps(blacklist_name).encode("utf-8"))
                            with open(templist_path, "wb") as file_with:
                                file_with.write(json.dumps(templist).encode("utf-8"))
                            with open(templist_name_path, "wb") as file_with:
                                file_with.write(json.dumps(templist_name).encode("utf-8"))
                            esito = "OK"
                        except Exception as exception_value:
                            print("Excep:26 -> " + str(exception_value))
                    elif azione[0] == "utente" and len(azione) == 3 and not type_link:
                        if azione[1] == "aggiungi":
                            if azione[2].isdigit():
                                if not int(azione[2]) in whitelist:
                                    print("Utente aggiunto")
                                    whitelist.append(int(azione[2]))
                                    bot.sendMessage(
                                        chat_id, "Userid inserito correttamente nella whitelist")
                                    try:
                                        with open(whitelist_path, "wb") as file_with:
                                            file_with.write(json.dumps(whitelist).encode("utf-8"))
                                        esito = "OK"
                                    except Exception as exception_value:
                                        print("Excep:06 -> " + str(exception_value))
                                        stampa_su_file("Except:06 ->" + str(exception_value), True)
                                else:
                                    print("Utente già presente nella whitelist")
                                    bot.sendMessage(
                                        chat_id, "Errore: l'userid digitato è già presente nella whitelist")
                            else:
                                err2 = True
                        elif azione[1] == "rimuovi":
                            if azione[2].isdigit():
                                if int(azione[2]) in whitelist:
                                    print("Utente rimosso")
                                    whitelist.remove(int(azione[2]))
                                    bot.sendMessage(
                                        chat_id, "Userid rimosso correttamente dalla whitelist")
                                    try:
                                        with open(whitelist_path, "wb") as file_with:
                                            file_with.write(json.dumps(whitelist).encode("utf-8"))
                                        esito = "OK"
                                    except Exception as exception_value:
                                        print("Excep:06 -> " + str(exception_value))
                                        stampa_su_file("Except:06 ->" + str(exception_value), True)
                                else:
                                    print("Utente non presente nella whitelist")
                                    bot.sendMessage(
                                        chat_id, "Errore: l'userid digitato non è presente nella whitelist")
                            else:
                                err2 = True
                        elif azione[1] == "blocca":
                            if azione[2].isdigit():
                                print("Utente bloccato")
                                if not int(azione[2]) in spamlist:
                                    spamlist.append(int(azione[2]))
                                    bot.sendMessage(
                                        chat_id, "Userid inserito correttamente nella spamlist")
                                    esito = "OK"
                                else:
                                    bot.sendMessage(
                                        chat_id, "Errore: l'userid digitato è già presente nella spamlist")
                                try:
                                    with open(spamlist_path, "wb") as file_with:
                                        file_with.write(json.dumps(spamlist).encode("utf-8"))
                                except Exception as exception_value:
                                    print("Excep:07 -> " + str(exception_value))
                                    stampa_su_file("Except:07 ->" + str(exception_value), True)
                            else:
                                err2 = True
                        elif azione[1] == "sblocca":
                            if azione[2].isdigit():
                                if int(azione[2]) in spamlist:
                                    print("Utente sbloccato")
                                    spamlist.remove(int(azione[2]))
                                    bot.sendMessage(
                                        chat_id, "Userid rimosso correttamente dalla spamlist")
                                    try:
                                        with open(spamlist_path, "wb") as file_with:
                                            file_with.write(json.dumps(
                                                spamlist).encode("utf-8"))
                                        esito = "OK"
                                    except Exception as exception_value:
                                        print("Excep:08 -> " + str(exception_value))
                                        stampa_su_file("Except:08 ->" + str(exception_value), True)
                                else:
                                    bot.sendMessage(
                                        chat_id, "Errore: l'userid digitato non è presente nella spamlist")
                            else:
                                err2 = True
                        else:
                            err1 = True
                    elif azione[0] == "parola" and len(azione) >= 2:
                        if azione[1] == "mostra" and len(azione) == 2:
                            print("Parole mostrate")
                            bot.sendMessage(
                                chat_id,
                                "Elenco parole vietate (in array):\n" +
                                str(parole_vietate))
                            esito = "OK"
                        elif azione[1] == "aggiungi" and len(azione) > 2:
                            print("Parola aggiunta")
                            del azione[0]
                            del azione[0]
                            parola = (' '.join(azione)).lower()
                            if parola not in parole_vietate:
                                parole_vietate.append(parola)
                                bot.sendMessage(
                                    chat_id,
                                    "Parola \"" +
                                    str(parola) +
                                    "\" aggiunta correttamente alle parole vietate")
                                try:
                                    with open(parole_vietate_path, "wb") as file_with:
                                        file_with.write(json.dumps(parole_vietate).encode("utf-8"))
                                    esito = "OK"
                                except Exception as exception_value:
                                    print("Excep:09 -> " + str(exception_value))
                                    stampa_su_file("Except:09 ->" + str(exception_value), True)
                            else:
                                bot.sendMessage(
                                    chat_id, "Parola già presente nelle parole vietate")
                        elif azione[1] == "elimina" and len(azione) > 2:
                            print("Parola rimossa")
                            del azione[0]
                            del azione[0]
                            parola = (' '.join(azione)).lower()
                            if parola in parole_vietate:
                                parole_vietate.remove(parola)
                                bot.sendMessage(
                                    chat_id,
                                    "Parola \"" +
                                    str(parola) +
                                    "\" rimossa correttamente dalle parole vietate")
                                try:
                                    with open(parole_vietate_path, "wb") as file_with:
                                        file_with.write(json.dumps(parole_vietate).encode("utf-8"))
                                    esito = "OK"
                                except Exception as exception_value:
                                    print("Excep:10 -> " + str(exception_value))
                                    stampa_su_file("Except:10 ->" + str(exception_value), True)
                            else:
                                bot.sendMessage(chat_id, "Parola non presente nelle parole vietate")
                        else:
                            err1 = True
                    elif azione[0] == "gruppo" and len(azione) >= 2:
                        if azione[1] == "mostra" and len(azione) == 2:
                            print("Gruppi mostrati")
                            bot.sendMessage(
                                chat_id, "Elenco gruppi abilitati (in array):\n" + str(chat_name))
                            esito = "OK"
                        elif azione[1] == "aggiungi" and len(azione) >= 4:
                            print("Gruppo aggiunto")
                            id_gruppo = azione[2]
                            del azione[0]
                            del azione[0]
                            del azione[0]
                            gruppo = ' '.join(azione)
                            try:
                                int(id_gruppo)
                                if id_gruppo not in chat_name:
                                    chat_name[str(id_gruppo)] = str(gruppo)
                                    bot.sendMessage(
                                        chat_id, "Gruppo \"" + str(gruppo) + "\" aggiunto correttamente ai gruppi abilitati")
                                    try:
                                        with open(chat_name_path, "wb") as file_with:
                                            file_with.write(json.dumps(chat_name).encode("utf-8"))
                                        esito = "OK"
                                    except Exception as exception_value:
                                        print("Excep:11 -> " + str(exception_value))
                                        stampa_su_file("Except:11 ->" + str(exception_value), True)
                                else:
                                    bot.sendMessage(
                                        chat_id, "Gruppo già presente nei gruppi abilitati")
                            except Exception as exception_value:
                                bot.sendMessage(chat_id, "ChatId errata. Inserirne una valida")
                                print("Excep:19 -> " + str(exception_value))
                                stampa_su_file("Except:19 ->" + str(exception_value), True)
                        elif azione[1] == "elimina" and len(azione) == 3:
                            print("Gruppo rimosso")
                            id_gruppo = azione[2]
                            try:
                                int(id_gruppo)
                                if azione[2] in chat_name:
                                    del chat_name[azione[2]]
                                    bot.sendMessage(
                                        chat_id, "Gruppo rimosso correttamente dai gruppi abilitati")
                                    try:
                                        with open(chat_name_path, "wb") as file_with:
                                            file_with.write(json.dumps(chat_name).encode("utf-8"))
                                        esito = "OK"
                                    except Exception as exception_value:
                                        print("Excep:12 -> " + str(exception_value))
                                        stampa_su_file("Except:12 ->" + str(exception_value), True)
                                else:
                                    bot.sendMessage(
                                        chat_id, "Gruppo non presente nei gruppi abilitati")
                            except Exception as exception_value:
                                bot.sendMessage(chat_id, "ChatId errata. Inserirne una valida")
                                print("Excep:20 -> " + str(exception_value))
                                stampa_su_file("Except:20 ->" + str(exception_value), True)
                        else:
                            err1 = True
                    elif azione[0] == "invia" and azione[1] == "messaggio" and len(azione) >= 3:
                        del azione[0]
                        del azione[0]
                        messaggio = ' '.join(azione)
                        if len(chat_name) > 0:
                            for gruppo_x in chat_name.keys():
                                try:
                                    bot.sendMessage(gruppo_x, messaggio, parse_mode="HTML")
                                    bot.sendMessage(chat_id, "Messaggio inviato in \"" +
                                                    str(chat_name[gruppo_x]) + "\"")
                                except Exception as exception_value:
                                    print("Excep:05 -> " + str(exception_value))
                                    stampa_su_file("Except:05 ->" + str(exception_value), True)
                                    bot.sendMessage(
                                        chat_id, "Non è stato possibile inviare il messaggio in: " + str(chat_name[gruppo_x]))
                            bot.sendMessage(
                                chat_id,
                                "Messaggio inviato in tutti i gruppi abilitati.\n\nIl messaggio che è stato inviato è:\n" +
                                messaggio,
                                parse_mode="HTML")
                            esito = "OK"
                        else:
                            bot.sendMessage(
                                chat_id, "Non c'è alcun gruppo abilitato")
                    else:
                        err1 = True
                else:
                    if not type_link:
                        err1 = True
            else:
                err1 = True

            if err1:
                bot.sendMessage(
                    chat_id,
                    "Azione non riconosciuta. Digita /help per ottenere l'elenco di tutte le operazione che puoi fare.")
            if err2:
                bot.sendMessage(chat_id, "Errore: l'userid deve essere un valore numerico.")

            try:
                stampa = "Utente: " + str(user_name) + " (" + str(user_id) + ")[" + str(status_user) + "]  --  Gruppo: ChatPrivataBot (" + str(
                    chat_id) + ")\n >> >> Esito: " + str(esito) + "\n >> >> Contenuto messaggio: " + str(text)
                print(stampa + "\n--------------------\n")
            except Exception as exception_value:
                stampa = "Excep:17 -> " + str(exception_value)
                print(stampa + "\n--------------------\n")

            stampa_su_file(stampa, False)
        elif status_user == "S":
            segnalazione_errore_path = "segnalazione_errore.json"
            if Path(segnalazione_errore_path).exists():
                segnalazione_errore = json.loads(open(segnalazione_errore_path).read())
            else:
                segnalazione_errore = {}
            esito = "NO"
            if (text == "/segnalapossibileerrore"):
                if str(user_id) not in segnalazione_errore:
                    segnalazione_errore[str(user_id)] = str(localtime)
                    invia_messaggio_admin(
                        frasi["messaggio_utente_blocca_per_admin"].replace("{{**utente_bloccato**}}",
                            username_utente_nousername))
                    try:
                        with open(segnalazione_errore_path, "wb") as file_with:
                            file_with.write(json.dumps(segnalazione_errore).encode("utf-8"))
                        esito = "OK"
                    except Exception as exception_value:
                        print("Excep:30 -> " + str(exception_value))
                        stampa_su_file("Except:30 ->" + str(exception_value), True)
                else:
                    bot.sendMessage(
                        chat_id,
                        frasi["messaggio_utente_bloccato_segnalazione_gia_inviata"].replace("{{**data_invio_segnalazione**}}", str(segnalazione_errore[str(user_id)])),
                        parse_mode="HTML")

                stampa = "Id Msg: " + str(message_id) + "  --  " + str(localtime) + "  --  Utente: " + str(user_name) + " (" + str(user_id) + ")[" + str(status_user) + "]\n >> >> Esito: " + str(esito) + "\n >> >> Contenuto messaggio: " + str(text)
                print(stampa + "\n--------------------\n")
                stampa_su_file(stampa, False)
            else:
                bot.sendMessage(
                    chat_id,
                    frasi["messaggio_chat_privata_utente_bloccato"],
                    reply_markup=segnalazione_da_utente_bloccato,
                    parse_mode="HTML"
                )
        else:
            bot.sendMessage(
                chat_id,
                "Non sei un amministratore, perciò non puoi interagire con il bot in privato.")
            bot.sendMessage(chat_id, messaggio_sviluppatore_versione_aggiornamento)
    else:
        # BOT IN GRUPPI NON ABILITATI
        bot.sendMessage(
            chat_id,
            "Questo gruppo non è un gruppo abilitato 🚫. Se è un gruppo ufficiale di Mozilla Italia contatta un moderatore per ottenere maggiori informazione e per risolvere il problema.\n\nChat id: " +
            str(chat_id))
        print("\n|| -- GRUPPO NON ABILITATO: " + str(chat_id) + " -- ||\n")


bot = telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': risposte, 'callback_query': risposte}).run_as_thread()

while True:
    time.sleep(1)
