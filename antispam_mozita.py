#!/usr/bin/python3
import telepot
import time
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import json
from pathlib import Path
from configparser import ConfigParser
import os

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
    frasi = json.loads(open("frasi.json",encoding="utf8").read())
else:
    print("File frasi non presente.")
    exit()

versione = "1.2.5"
ultimoAggiornamento = "08-03-2019"

print("Versione: "+versione+" - Aggiornamento: "+ultimoAggiornamento)

data_salvataggio=""
response=""

adminlist_path = "adminlist.json"
whitelist_path = "whitelist.json"
blacklist_path = "blacklist.json"
blacklist_name_path = "blacklist_name.json"
templist_path = "templist.json"
templist_name_path = "templist_name.json"
spamlist_path = "spamlist.json"
chat_name_path = "chat_name.json"
parole_vietate_path = "parole_vietate.json"
AdminList = []
WhiteList = []
BlackList = {}
BlackList_name = {}
TempList = {}
TempList_name = {}
SpamList = []
if Path(chat_name_path).exists():
    chat_name = json.loads(open(chat_name_path).read())
else:
    chat_name = {}
if Path(parole_vietate_path).exists():
    parole_vietate = json.loads(open(parole_vietate_path).read())
else:
    parole_vietate = []

# stampa_su_file(<cosa stampare>,<{True|False} indica se è una stampa di ERRORE/ECCEZIONE o una stampa 'normale'>)
def stampa_su_file(stampa,err):
    global response, data_salvataggio
    if err:
        stampa=str(response)+"\n\n"+str(stampa)
    stampa=stampa+"\n--------------------\n"
    try:
        if(os.path.exists("./history_mozitaantispam")==False):
            os.mkdir("./history_mozitaantispam")
    except Exception as e:
        print("Excep:21 -> "+str(e))
        stampa_su_file("Except:21 ->"+str(e),True)

    try:
        # apre il file in scrittura "append" per inserire orario e data -> log di utilizzo del bot (ANONIMO)
        file = open("./history_mozitaantispam/log_"+str(data_salvataggio)+".txt", "a", -1, "UTF-8")
        # ricordare che l'orario è in fuso orario UTC pari a 0 (Greenwich, Londra) - mentre l'Italia è a +1 (CET) o +2 (CEST - estate)
        file.write(stampa)
        file.close()
    except Exception as e:
        print("Excep:03 -> "+str(e))
        stampa_su_file("Except:03 ->"+str(e),True)

def invia_messaggio_admin(msg):
    for admin_x in AdminList:
        try:
            bot.sendMessage(admin_x, msg, parse_mode="HTML")
        except Exception as e:
            print("Excep:25 -> "+str(e))
            stampa_su_file("Except:25 ->"+str(e),True)

def risposte(msg):
    localtime = datetime.now()
    global data_salvataggio
    data_salvataggio = localtime.strftime("%Y_%m_%d")
    localtime = localtime.strftime("%d/%m/%y %H:%M:%S")
    messaggio = msg
    type_msg = "NM"  # Normal Message

    modificato = False
    risposta = False

    if Path(adminlist_path).exists():
        global AdminList
        AdminList = json.loads(open(adminlist_path).read())
    else:
        # nel caso in cui non dovesse esistere alcun file "adminlist.json" imposta staticamente l'userid di Sav22999 -> così da poter confermare anche altri utenti
        AdminList = [240188083]
    if Path(whitelist_path).exists():
        global WhiteList
        WhiteList = json.loads(open(whitelist_path).read())
    if Path(blacklist_path).exists():
        global BlackList
        BlackList = json.loads(open(blacklist_path).read())
    if Path(blacklist_name_path).exists():
        global BlackList_name
        BlackList_name = json.loads(open(blacklist_name_path).read())
    if Path(templist_path).exists():
        global TempList
        TempList = json.loads(open(templist_path).read())
    if Path(templist_name_path).exists():
        global TempList_name
        TempList_name = json.loads(open(templist_name_path).read())
    if Path(spamlist_path).exists():
        global SpamList
        SpamList = json.loads(open(spamlist_path).read())

    if "text" in msg:
        # EVENTO MESSAGGIO (SOTTO-EVENTI MESSAGGIO)
        text = str(msg['text'])
        if "entities" in msg:
            # EVENTO LINK
            type_msg = "LK"  # Link
        else:
            # EVENTO MESSAGGIO PURO
            type_msg = "NM"  # Normal Message
        if "edit_date" in msg:
            # EVENTO MODIFICA
            modificato = True
        elif "reply_to_message" in msg:
            # EVENTO RISPOSTA
            risposta = True
    elif "data" in msg:
        # EVENTO PRESS BY INLINE BUTTON
        text = str(msg['data'])
        # print("Callback_query")
        type_msg = "BIC"  # Button Inline Click
    elif "new_chat_participant" in msg:
        # EVENTO JOIN
        #print("Join event")
        type_msg = "J"  # Join
        text = "|| Un utente è entrato ||"
    elif "left_chat_participant" in msg:
        # EVENTO LEFT
        #print("Left event")
        type_msg = "L"  # Left
        text = "|| Un utente è uscito ||"
    elif "document" in msg:
        # EVENTO FILE
        type_msg = "D"  # Document
        if "caption" in msg:
            text = str(msg["caption"])
        else:
            text = ""
    elif "voice" in msg:
        # EVENTO VOICE MESSAGE
        type_msg = "VM"  # Voice Message
        text = "|| Messaggio vocale ||"
    elif "video_note" in msg:
        # EVENTO VIDEO-MESSAGE
        type_msg = "VMSG"  # Video Message
        text = "|| Video messaggio ||"
    elif "photo" in msg:
        # EVENTO FOTO/IMMAGINE
        type_msg = "I"  # Photo
        if "caption" in msg:
            text = str(msg["caption"])
        else:
            text = ""
    elif "music" in msg:
        # EVENTO MUSICA
        type_msg = "M"  # Music
        if "caption" in msg:
            text = str(msg["caption"])
        else:
            text = ""
    elif "video" in msg:
        # EVENTO VIDEO
        type_msg = "V"  # Video
        if "caption" in msg:
            text = str(msg["caption"])
        else:
            text = ""
    elif "contact" in msg:
        # EVENTO CONTATTO
        type_msg = "C"  # Contact
        if "caption" in msg:
            text = str(msg["caption"])
        else:
            text = ""
    elif "location" in msg:
        # EVENTO POSIZIONE
        type_msg = "P"  # Position
        text = ""
    elif "sticker" in msg:
        # EVENTO STICKER
        type_msg = "S"  # Stiker
        text = "(sticker) "+msg["sticker"]["emoji"]
    elif "animation" in msg:
        # EVENTO GIF
        type_msg = "G"  # Gif
        text = ""
    elif "new_chat_photo" in msg:
        # EVENTO IMMAGINE CHAT AGGIORNATA
        type_msg = "NCP" # New Chat Photo
        text="|| Immagine chat aggiornata ||"
    else:
        # EVENTO NON CATTURA/GESTITO -> ELIMINARE AUTOMATICAMENTE IL MESSAGGIO.
        text = "--Testo non identificato--"
        type_msg = "NI"  # Not Identified
    try:
        if type_msg=="J" and not (msg['from']['id']==msg['new_chat_participant']['id']):
            user_id = msg['new_chat_participant']['id']
            nousername = False
            if "username" in msg['new_chat_participant']:
                user_name = msg['new_chat_participant']['username']
            else:
                user_name = "[*NessunUsername*]"+str(user_id)
                nousername = True
            text="|| Un utente è stato aggiunto ||"
        elif type_msg=="L" and not (msg['from']['id']==msg['left_chat_participant']['id']):
            user_id = msg['left_chat_participant']['id']
            nousername = False
            if "username" in msg['left_chat_participant']:
                user_name = msg['left_chat_participant']['username']
            else:
                user_name = "[*NessunUsername*]"+str(user_id)
                nousername = True
            text="|| Un utente è stato rimosso ||"
        else:
            user_id = msg['from']['id']
            nousername = False
            if "username" in msg['from']:
                user_name = msg['from']['username']
            else:
                user_name = "[*NessunUsername*]"+str(user_id)
                nousername = True
    except Exception as e:
        print("Excep:22 -> "+str(e))
        stampa_su_file("Except:22 ->"+str(e),True)

        user_id = msg['from']['id']
        user_name = "[*NessunUsername*]"+str(user_id)
        nousername = True
    # print(user_id)
    # print(user_name)
    if not "chat" in msg:
        msg = msg["message"]
    chat_id = msg['chat']['id']
    # print(chat_id)
    message_id = msg['message_id']
    # print(message_id)

    global response
    response = bot.getUpdates()
    # print(response)

    if str(chat_id) in chat_name and msg['chat']['type'] != "private":
        # BOT NEI GRUPPI ABILITATI
        nome_gruppo = str(chat_name[str(chat_id)])

        new = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=frasi["button_mostra_regolamento"],callback_data="/leggiregolamento")],
            [InlineKeyboardButton(text=frasi["button_blocca_utente"],callback_data="/bloccautente")],
        ])
        regolamentoletto = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=frasi["button_leggi_regolamento"],url='https://github.com/Sav22999/Guide/blob/master/Mozilla%20Italia/Telegram/regolamento.md')],
            [InlineKeyboardButton(text=frasi["button_conferma_utente"], callback_data='/confutente')],
            [InlineKeyboardButton(text=frasi["button_blocca_utente"],callback_data="/bloccautente")],
        ])

        status_user = "-"
        if nousername:
            username_utente_nousername = "<a href='tg://user?id="+str(user_id)+"'>"+str(user_id)+"</a>"
        else:
            username_utente_nousername = "<a href='tg://user?id="+str(user_id)+"'>@"+str(user_name)+"</a>"+" (<code>"+str(user_id)+"</code>)"
        
        messaggio_benvenuto = str((frasi["benvenuto"]).replace("{{**username**}}",str(username_utente_nousername))).replace("{{**nome_gruppo**}}",str(nome_gruppo))

        controllo_parole_vietate = False
        if any(ext in text.lower() for ext in parole_vietate):
            controllo_parole_vietate = True

        try:
            # 732117113 -> userid del bot stesso
            if type_msg != "BIC" and not str(user_id) == "732117113":
                # Se si vuole solamente eliminare un messaggio in base a una specifica condizione
                if type_msg == "NI":
                    messaggio["message_id"] = message_id
                    bot.deleteMessage(telepot.message_identifier(messaggio))
                    text=frasi["eliminato_da_bot"]+text
                    # Elimina messaggio nel caso in cui risulti proprio uguale a (vedi sopra)

                if int(user_id) in SpamList and type_msg!="L":
                    #print ("Utente spam")
                    # L'utente può essere presente anche in altre liste -> ma se è presente qui viene bloccato e cacciato ugualmente
                    messaggio["message_id"] = message_id
                    bot.deleteMessage(telepot.message_identifier(messaggio))
                    if not(user_id in AdminList):
                        try:
                            bot.kickChatMember(chat_id, user_id, until_date=None)
                            if nousername:
                                username_utente_nousername = "<a href='tg://user?id="+str(user_id)+"'>"+str(user_id)+"</a>"
                            else:
                                username_utente_nousername = "<a href='tg://user?id="+str(user_id)+"'>"+"@"+str(user_name)+"</a>"+" (<code>"+str(user_id)+"</code>)"
                            bot.sendMessage(chat_id, str(frasi["utente_cacciato"]).replace("{{**username**}}",str(username_utente_nousername)), parse_mode="HTML")
                            status_user = "S"  # SpamList
                        except Exception as e:
                            print("Excep:24 -> "+str(e))
                            stampa_su_file("Except:24 ->"+str(e),True)
                        try:
                            with open(spamlist_path, "wb") as f:
                                f.write(json.dumps(SpamList).encode("utf-8"))
                        except Exception as e:
                            print("Excep:04 -> "+str(e))
                            stampa_su_file("Except:04 ->"+str(e),True)
                    if(user_id in AdminList):
                        status_user = "A"
                    invia_messaggio_admin("📌  "+username_utente_nousername+": CACCIATO -- Gruppo: <b>"+str(nome_gruppo)+"</b>")
                    text=frasi["eliminato_da_bot"]+text
                elif controllo_parole_vietate:
                    # Parola vietata inserita
                    messaggio["message_id"] = message_id
                    bot.deleteMessage(telepot.message_identifier(messaggio))
                    if nousername:
                        username_utente_nousername = "<a href='tg://user?id="+str(user_id)+"'>"+str(user_id)+"</a>"
                    else:
                        username_utente_nousername = "<a href='tg://user?id="+str(user_id)+"'>"+"@"+str(user_name)+"</a>"+" (<code>"+str(user_id)+"</code>)"
                    bot.sendMessage(chat_id, str(frasi["parola_vietata_presente"]).replace("{{**username**}}",str(username_utente_nousername)), parse_mode="HTML")
                    invia_messaggio_admin("📌  "+username_utente_nousername+": PAROLA VIETATA -- Gruppo: <b>"+str(nome_gruppo)+"</b>")
                    text=frasi["eliminato_da_bot"]+text
                elif (int(user_id) in AdminList and int(user_id) in WhiteList) and type_msg != "NI" and not controllo_parole_vietate:
                    #print ("Utente admin!")
                    #bot.sendMessage(chat_id, "@"+str(user_name)+" è un utente admin !")
                    status_user = "A"  # AdminList
                elif int(user_id) in WhiteList and type_msg != "NI" and not controllo_parole_vietate:
                    #print ("Utente verificato!")
                    #bot.sendMessage(chat_id, "@"+str(user_name)+" è un utente verificato !")
                    status_user = "W"  # WhiteList
                elif int(user_id) in BlackList.values() and type_msg != "NI" and not controllo_parole_vietate:
                    #print ("Utente non verificato!")
                    messaggio["message_id"] = message_id
                    if type_msg != "J" and type_msg != "L":
                        bot.deleteMessage(telepot.message_identifier(messaggio))
                        text=frasi["eliminato_da_bot"]+text
                    status_user = "B"  # BlackList
                    #bot.sendMessage(chat_id, "@"+str(user_name)+" non è stato verificato: Messaggio eliminato.")
                elif int(user_id) in TempList.values() and type_msg != "NI" and not controllo_parole_vietate:
                    #print ("Utente non verificato!")
                    messaggio["message_id"] = message_id
                    if type_msg != "NM":
                        if type_msg != "J" and type_msg != "L":
                            bot.deleteMessage(telepot.message_identifier(messaggio))
                            text=frasi["eliminato_da_bot"]+text
                    status_user = "T"  # TempList
                elif type_msg=="NCP":
                    status_user = "-"
                else:
                    if type_msg == "J":
                        # Nuovo utente
                        bot.sendMessage(chat_id, messaggio_benvenuto, reply_markup=new, parse_mode="HTML")
                        BlackList[str(message_id)] = int(user_id)
                        BlackList_name[str(user_id)] = str(user_name)
                        status_user = "B"
                        try:
                            with open(blacklist_path, "wb") as f:
                                f.write(json.dumps(BlackList).encode("utf-8"))
                            with open(blacklist_name_path, "wb") as f:
                                f.write(json.dumps(BlackList_name).encode("utf-8"))
                        except Exception as e:
                            print("Excep:13 -> "+str(e))
                            stampa_su_file("Except:13 ->"+str(e),True)
                    elif type_msg != "J" and type_msg != "L":
                        # Utente già presente nel gruppo ma non presente in alcuna lista
                        bot.sendMessage(chat_id, messaggio_benvenuto, reply_markup=new, parse_mode="HTML")
                        BlackList[str(message_id)] = int(user_id)
                        BlackList_name[str(user_id)] = str(user_name)
                        bot.deleteMessage(telepot.message_identifier(messaggio))
                        text=frasi["eliminato_da_bot"]+text
                        status_user = "B"
                        try:
                            with open(blacklist_path, "wb") as f:
                                f.write(json.dumps(BlackList).encode("utf-8"))
                            with open(blacklist_name_path, "wb") as f:
                                f.write(json.dumps(BlackList_name).encode("utf-8"))
                        except Exception as e:
                            print("Excep:14 -> "+str(e))
                            stampa_su_file("Except:14 ->"+str(e),True)
                    else:
                        # Messaggio non riconosciuto
                        # bot.sendMessage(chat_id, "Il messaggio non è stato riconosciuto e, pertanto, è stato rimosso.")
                        if type_msg != "J" and type_msg != "L":
                            bot.deleteMessage(telepot.message_identifier(messaggio))
                            text=frasi["eliminato_da_bot"]+text
                            status_user = "-"
            else:
                if text == "/leggiregolamento" and type_msg == "BIC":
                    if user_id == int(BlackList[str(int(message_id)-1)]):
                        #print(response)
                        TempList[str(int(message_id)-1)] = BlackList[str(int(message_id)-1)]
                        # print(TempList[str(int(message_id)-1)]) #userid
                        TempList_name[str(TempList[str(int(message_id)-1)])] = BlackList_name[str(BlackList[str(int(message_id)-1)])]
                        del BlackList_name[str(BlackList[str(int(message_id)-1)])]
                        del BlackList[str(int(message_id)-1)]
                        status_user = "T"
                        if nousername:
                            username_utente_nousername = "<a href='tg://user?id="+str(user_id)+"'>"+str(user_id)+"</a>"
                        else:
                            username_utente_nousername = "<a href='tg://user?id="+str(user_id)+"'>@"+str(user_name)+"</a>"+" (<code>"+str(user_id)+"</code>)"
                        try:
                            # cancella messaggio di benvenuto
                            message_id_temp_deletemessage = int(message_id)
                            bot.deleteMessage((chat_id,message_id_temp_deletemessage))
                            # print(message_id_temp_deletemessage)
                        except Exception as e:
                            print("Excep:27 -> "+str(e))
                            stampa_su_file("Except:27 ->"+str(e),True)
                        bot.sendMessage(chat_id, str(frasi["regolamento_letto"]).replace("{{**username**}}",str(username_utente_nousername)), reply_markup=regolamentoletto, parse_mode="HTML")

                        try:
                            with open(blacklist_path, "wb") as f:
                                f.write(json.dumps(BlackList).encode("utf-8"))
                            with open(blacklist_name_path, "wb") as f:
                                f.write(json.dumps(BlackList_name).encode("utf-8"))
                            with open(templist_path, "wb") as f:
                                f.write(json.dumps(TempList).encode("utf-8"))
                            with open(templist_name_path, "wb") as f:
                                f.write(json.dumps(TempList_name).encode("utf-8"))
                        except Exception as e:
                            text+="\n >> >> Esito: NO"
                            print("Excep:15 -> "+str(e))
                            stampa_su_file("Except:15 ->"+str(e),True)

                elif text == "/confutente" and type_msg == "BIC":
                    if user_id in WhiteList or user_id in AdminList:
                        user_name_temp = str(msg['text'].split(" ")[0]).lstrip("@")
                        #print("Username temp: "+str(user_name_temp))
                        #print("Messaggio:"+msg['text'])
                        nousername_temp=False
                        if "[*NessunUsername*]"+str(user_name_temp) in TempList_name.values():
                            nousername_temp=True
                            user_name_temp="[*NessunUsername*]"+str(user_name_temp)
                        if str(user_name_temp) in TempList_name.values() or nousername_temp:
                            if nousername:
                                username_utente_nousername = "<a href='tg://user?id="+str(user_id)+"'>"+str(user_id)+"</a>"
                            else:
                                username_utente_nousername = "<a href='tg://user?id="+str(user_id)+"'>@"+str(user_name)+"</a>"+" (<code>"+str(user_id)+"</code>)"
                            user_id_temp = int(next((x for x in TempList_name if TempList_name[x] == str(user_name_temp)), None))
                            message_id_temp = int(next((x for x in TempList if TempList[x] == int(user_id_temp)), None))+1
                            if nousername_temp:
                                username_utente_nousername_temp = "<a href='tg://user?id="+str(user_id_temp)+"'>"+str(user_id_temp)+"</a>"
                            else:
                                username_utente_nousername_temp = "<a href='tg://user?id="+str(user_id)+"'>@"+str(TempList_name[str(TempList[str(int(message_id_temp)-1)])])+"</a>"+" (<code>"+str(user_id_temp)+"</code>)"
                            #print("Utente da verificare: "+str(TempList[int(message_id_temp)-1]) + "Message id: "+str(message_id_temp))
                            try:
                                # cancella messaggio di 'regolamento letto'
                                message_id_temp_deletemessage = int(message_id)
                                bot.deleteMessage((chat_id,message_id_temp_deletemessage))
                                # print(message_id_temp_deletemessage)
                            except Exception as e:
                                print("Excep:28 -> "+str(e))
                                stampa_su_file("Except:28 ->"+str(e),True)
                            bot.sendMessage(chat_id, str((frasi["utente_confermato"]).replace("{{**utenteCheConferma**}}",str(username_utente_nousername))).replace("{{**utenteConfermato**}}",str(username_utente_nousername_temp)), parse_mode="HTML")
                            bot.sendMessage(chat_id, str(frasi["utente_confermato2"]).replace("{{**username**}}",str(username_utente_nousername_temp)), parse_mode="HTML")
                            WhiteList.append(int(TempList[str(int(message_id_temp)-1)]))
                            del TempList_name[str(TempList[str(int(message_id_temp)-1)])]
                            del TempList[str(int(message_id_temp)-1)]
                            status_user = "W"

                            try:
                                with open(whitelist_path, "wb") as f:
                                    f.write(json.dumps(WhiteList).encode("utf-8"))
                                with open(templist_path, "wb") as f:
                                    f.write(json.dumps(TempList).encode("utf-8"))
                                with open(templist_name_path, "wb") as f:
                                    f.write(json.dumps(TempList_name).encode("utf-8"))
                            except Exception as e:
                                text+="\n >> >> Esito: NO"
                                print("Excep:16 -> "+str(e))
                                stampa_su_file("Except:16 ->"+str(e),True)
                elif text == "/bloccautente" and type_msg == "BIC":
                    if user_id in AdminList:
                        user_name_temp = str(msg['text'].split(" ")[0]).lstrip("@")
                        user_id_temp=0 #imposto l'user_id a "0"
                        if user_name_temp in BlackList_name.values():
                            user_id_temp = int(list(BlackList_name.keys())[list(BlackList_name.values()).index(str(user_name_temp))])
                        elif user_name_temp in TempList_name.values():
                            user_id_temp = int(list(TempList_name.keys())[list(TempList_name.values()).index(str(user_name_temp))])
                        #print(str(user_id_temp) + " " + str(user_name_temp))
                        if not(user_id_temp in AdminList) and not user_id_temp==0:
                            try:
                                SpamList.append(int(user_id_temp))
                                bot.kickChatMember(chat_id, user_id_temp, until_date=None)
                                if nousername:
                                    username_utente_nousername = "<a href='tg://user?id="+str(user_id_temp)+"'>"+str(user_id_temp)+"</a>"
                                else:
                                    username_utente_nousername = "<a href='tg://user?id="+str(user_id_temp)+"'>@"+str(user_name_temp)+"</a>"+" (<code>"+str(user_id_temp)+"</code>)"
                                try:
                                    # cancella messaggio
                                    message_id_temp_deletemessage = int(message_id)
                                    bot.deleteMessage((chat_id,message_id_temp_deletemessage))
                                    # print(message_id_temp_deletemessage)
                                except Exception as e:
                                    print("Excep:29 -> "+str(e))
                                    stampa_su_file("Except:29 ->"+str(e),True)
                                bot.sendMessage(chat_id, str(frasi["utente_cacciato"]).replace("{{**username**}}",str(username_utente_nousername)), parse_mode="HTML")
                                status_user = "S"  # SpamList
                                if(user_id in AdminList):
                                    status_user = "A"
                                invia_messaggio_admin("📌  "+username_utente_nousername+": BLOCCATO E CACCIATO -- Gruppo: <b>"+str(nome_gruppo)+"</b>")
                                text="|| Un utente è stato cacciato ||"
                            except Exception as e:
                                text+="\n >> >> Esito: NO"
                                print("Excep:23 -> "+str(e))
                                stampa_su_file("Except:23 ->"+str(e),True)
                            try:
                                with open(spamlist_path, "wb") as f:
                                    f.write(json.dumps(SpamList).encode("utf-8"))
                            except Exception as e:
                                print("Excep:18 -> "+str(e))
                                stampa_su_file("Except:18 ->"+str(e),True)
        except Exception as e:
            print("Excep:01 -> "+str(e))
            stampa_su_file("Except:01 ->"+str(e),True)

        try:
            dettagli = ""
            if modificato:
                dettagli += "(modificato) "
            if risposta:
                dettagli += "(risposta) "
            stampa = "Id Msg: "+str(message_id)+"  --  "+str(localtime)+"  --  Utente: "+str(user_name)+" ("+str(user_id)+")["+str(status_user)+"]  --  Gruppo: "+str(nome_gruppo)+"("+str(chat_id)+")\n >> >> Tipo messaggio: "+str(type_msg)+"\n >> >> Contenuto messaggio: "+str(dettagli)+str(text)
            print(stampa+"\n--------------------\n")
        except Exception as e:
            stampa = "Excep:02 -> "+str(e)
            print(stampa+"\n--------------------\n")

        stampa_su_file(stampa,False)

    elif msg['chat']['type'] == "private":
        # BOT IN CHAT PRIVATA

        messaggio_sviluppatore_versione_aggiornamento="MozIta Antispam Bot è stato sviluppato, per la comunità italiana di Mozilla Italia, da Saverio Morelli (@Sav22999) con il supporto e aiuto di Damiano Gualandri (@dag7dev), Simone Massaro (@mone27) e molti altri.\n\n"+"Versione: "+versione+" - Aggiornamento: "+ultimoAggiornamento

        if user_id in AdminList:
            status_user = "A"
            err1 = False
            err2 = False
            esito = "NO"
            if type_msg == "NM" or type_msg == "LK":
                lk = False
                if text == "/start" and type_msg == "LK":
                    bot.sendMessage(chat_id, "Benvenuto nella chat privata del bot.\nPuoi interagire con il bot, in chat privata, perché sei un amministratore.\nDigita /help per ottenere la lista di tutte le azioni che puoi fare nel bot IN PRIVATO (i comandi NON funzionano nei gruppi abilitati).")
                    lk = True
                    esito = "OK"
                elif text == "/help" and type_msg == "LK":
                    bot.sendMessage(chat_id, "Elenco azioni disponibili:\n - utente aggiungi |USERID|\n - utente blocca |USERID|\n - utente sblocca |USERID|\n - parola mostra\n - parola aggiungi |PAROLA/FRASE|\n - parola elimina |PAROLA/FRASE|\n - gruppo mostra\n - gruppo aggiungi |USERID| |NOME GRUPPO|\n - gruppo elimina |USERID|\n - invia messaggio |TESTO MESSAGGIO|\n - lista white mostra\n - lista spam mostra\n - lista black mostra\n - lista black elimina\n - lista temp mostra\n - lista temp elimina")
                    bot.sendMessage(chat_id, messaggio_sviluppatore_versione_aggiornamento)
                    lk = True
                    esito = "OK"

                if ("utente" in text or "parola" in text or "gruppo" in text or "invia messaggio" in text or "lista" in text) and not lk:
                    azione = list(text.split(" "))
                    if(azione[0] == "lista" and len(azione) == 3 and type_msg != "LK"):
                        # SOLO A SCOPO DI TEST -> DA ELIMINARE SUCCESSIVAMENTE (o inserire sottoforma di commento)
                        if(azione[1] == "white"):
                            if(azione[2] == "mostra"):
                                # mostra la WhiteList
                                bot.sendMessage(chat_id, "WhiteList:\n"+str(WhiteList))
                            else:
                                err1=True
                        elif(azione[1] == "black"):
                            if(azione[2]=="elimina"):
                                # elimina il contenuto delle BlackList
                                BlackList = {}
                                BlackList_name = {}
                                bot.sendMessage(chat_id, "Le seguenti liste sono state azzerate:\n- BlackList\n- BlackList_name")
                            elif(azione[2]=="mostra"):
                                # mostra le BlackList
                                bot.sendMessage(chat_id, "BlackList:\n"+str(BlackList)+"\n\nBlackList_name:\n"+str(BlackList_name))
                            else:
                                err1=True
                        elif(azione[1] == "temp"):
                            if(azione[2]=="elimina"):
                                # elimina il contenuto delle TempList
                                TempList = {}
                                TempList_name = {}
                                bot.sendMessage(chat_id, "Le seguenti liste sono state azzerate:\n- TempList\n- TempList_name")
                            elif(azione[2]=="mostra"):
                                # mostra le TempList
                                bot.sendMessage(chat_id, "TempList:\n"+str(TempList)+"\n\nTempList_name:\n"+str(TempList_name))
                            else:
                                err1=True
                        elif(azione[1] == "spam"):
                            if(azione[2]=="mostra"):
                                # mostra la SpamList
                                bot.sendMessage(chat_id, "SpamList:\n"+str(SpamList))
                            else:
                                err1=True
                        try:
                            with open(blacklist_path, "wb") as f:
                                f.write(json.dumps(BlackList).encode("utf-8"))
                            with open(blacklist_name_path, "wb") as f:
                                f.write(json.dumps(BlackList_name).encode("utf-8"))
                            with open(templist_path, "wb") as f:
                                f.write(json.dumps(TempList).encode("utf-8"))
                            with open(templist_name_path, "wb") as f:
                                f.write(json.dumps(TempList_name).encode("utf-8"))
                            esito = "OK"
                        except Exception as e:
                            print("Excep:26 -> "+str(e))
                        else:
                            err1=True
                    elif azione[0] == "utente" and len(azione) == 3 and type_msg != "LK":
                        if azione[1] == "aggiungi":
                            if azione[2].isdigit():
                                print("Utente aggiunto")
                                WhiteList.append(int(azione[2]))
                                bot.sendMessage(chat_id, "Userid inserito correttamente nella WhiteList")
                                try:
                                    with open(whitelist_path, "wb") as f:
                                        f.write(json.dumps(WhiteList).encode("utf-8"))
                                    esito = "OK"
                                except Exception as e:
                                    print("Excep:06 -> "+str(e))
                                    stampa_su_file("Except:06 ->"+str(e),True)
                            else:
                                err2 = True
                        elif azione[1] == "blocca":
                            if azione[2].isdigit():
                                print("Utente bloccato")
                                if not int(azione[2]) in SpamList:
                                    SpamList.append(int(azione[2]))
                                    bot.sendMessage(chat_id, "Userid inserito correttamente nella SpamList")
                                    esito = "OK"
                                else:
                                    bot.sendMessage(
                                        chat_id, "Errore: l'userid digitato è già presente nella SpamList")
                                try:
                                    with open(spamlist_path, "wb") as f:
                                        f.write(json.dumps(SpamList).encode("utf-8"))
                                except Exception as e:
                                    print("Excep:07 -> "+str(e))
                                    stampa_su_file("Except:07 ->"+str(e),True)
                            else:
                                err2 = True
                        elif azione[1] == "sblocca":
                            if azione[2].isdigit():
                                if int(azione[2]) in SpamList:
                                    print("Utente sbloccato")
                                    SpamList.remove(int(azione[2]))
                                    bot.sendMessage(chat_id, "Userid rimosso correttamente dalla SpamList")
                                    try:
                                        with open(spamlist_path, "wb") as f:
                                            f.write(json.dumps(
                                                SpamList).encode("utf-8"))
                                        esito = "OK"
                                    except Exception as e:
                                        print("Excep:08 -> "+str(e))
                                        stampa_su_file("Except:08 ->"+str(e),True)
                                else:
                                    bot.sendMessage(chat_id, "Errore: l'userid digitato non è presente nella SpamList")
                            else:
                                err2 = True
                        else:
                            err1 = True
                    elif azione[0] == "parola" and len(azione) >= 2:
                        if azione[1] == "mostra" and len(azione) == 2:
                            print("Parole mostrate")
                            bot.sendMessage(
                                chat_id, "Elenco parole vietate (in array):\n"+str(parole_vietate))
                            esito = "OK"
                        elif azione[1] == "aggiungi" and len(azione) > 2:
                            print("Parola aggiunta")
                            del azione[0]
                            del azione[0]
                            parola = (' '.join(azione)).lower()
                            if not parola in parole_vietate:
                                parole_vietate.append(parola)
                                bot.sendMessage(
                                    chat_id, "Parola \""+str(parola)+"\" aggiunta correttamente alle parole vietate")
                                try:
                                    with open(parole_vietate_path, "wb") as f:
                                        f.write(json.dumps(parole_vietate).encode("utf-8"))
                                    esito = "OK"
                                except Exception as e:
                                    print("Excep:09 -> "+str(e))
                                    stampa_su_file("Except:09 ->"+str(e),True)
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
                                    chat_id, "Parola \""+str(parola)+"\" rimossa correttamente dalle parole vietate")
                                try:
                                    with open(parole_vietate_path, "wb") as f:
                                        f.write(json.dumps(parole_vietate).encode("utf-8"))
                                    esito = "OK"
                                except Exception as e:
                                    print("Excep:10 -> "+str(e))
                                    stampa_su_file("Except:10 ->"+str(e),True)
                            else:
                                bot.sendMessage(chat_id, "Parola non presente nelle parole vietate")
                        else:
                            err1 = True
                    elif azione[0] == "gruppo" and len(azione) >= 2:
                        if azione[1] == "mostra" and len(azione) == 2:
                            print("Gruppi mostrati")
                            bot.sendMessage(chat_id, "Elenco gruppi abilitati (in array):\n"+str(chat_name))
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
                                if not id_gruppo in chat_name:
                                    chat_name[str(id_gruppo)] = str(gruppo)
                                    bot.sendMessage(chat_id, "Gruppo \""+str(gruppo)+"\" aggiunto correttamente ai gruppi abilitati")
                                    try:
                                        with open(chat_name_path, "wb") as f:
                                            f.write(json.dumps(chat_name).encode("utf-8"))
                                        esito = "OK"
                                    except Exception as e:
                                        print("Excep:11 -> "+str(e))
                                        stampa_su_file("Except:11 ->"+str(e),True)
                                else:
                                    bot.sendMessage(chat_id, "Gruppo già presente nei gruppi abilitati")
                            except Exception as e:
                                bot.sendMessage(chat_id, "ChatId errata. Inserirne una valida")
                                print("Excep:19 -> "+str(e))
                                stampa_su_file("Except:19 ->"+str(e),True)
                        elif azione[1] == "elimina" and len(azione) == 3:
                            print("Gruppo rimosso")
                            id_gruppo = azione[2]
                            try:
                                int(id_gruppo)
                                if azione[2] in chat_name:
                                    del chat_name[azione[2]]
                                    bot.sendMessage(chat_id, "Gruppo rimosso correttamente dai gruppi abilitati")
                                    try:
                                        with open(chat_name_path, "wb") as f:
                                            f.write(json.dumps(chat_name).encode("utf-8"))
                                        esito = "OK"
                                    except Exception as e:
                                        print("Excep:12 -> "+str(e))
                                        stampa_su_file("Except:12 ->"+str(e),True)
                                else:
                                    bot.sendMessage(chat_id, "Gruppo non presente nei gruppi abilitati")
                            except Exception as e:
                                bot.sendMessage(chat_id, "ChatId errata. Inserirne una valida")
                                print("Excep:20 -> "+str(e))
                                stampa_su_file("Except:20 ->"+str(e),True)
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
                                    bot.sendMessage(chat_id, "Messaggio inviato in \""+str(chat_name[gruppo_x])+"\"")
                                except Exception as e:
                                    print("Excep:05 -> "+str(e))
                                    stampa_su_file("Except:05 ->"+str(e),True)
                                    bot.sendMessage(chat_id, "Non è stato possibile inviare il messaggio in: "+str(chat_name[gruppo_x]))
                            bot.sendMessage(chat_id, "Messaggio inviato in tutti i gruppi abilitati.\n\nIl messaggio che è stato inviato è:\n"+messaggio, parse_mode="HTML")
                            esito = "OK"
                        else:
                            bot.sendMessage(
                                chat_id, "Non c'è alcun gruppo abilitato")
                    else:
                        err1 = True
                else:
                    if not lk:
                        err1 = True
            else:
                err1 = True

            if err1:
                bot.sendMessage(
                    chat_id, "Azione non riconosciuta. Digita /help per ottenere l'elenco di tutte le operazione che puoi fare.")
            if err2:
                bot.sendMessage(
                    chat_id, "Errore: l'userid deve essere un valore numerico.")

            try:
                stampa = "Utente: "+str(user_name)+" ("+str(user_id)+")["+str(status_user)+"]  --  Gruppo: ChatPrivataBot ("+str(
                    chat_id)+")\n >> >> Esito: "+str(esito)+"\n >> >> Contenuto messaggio: "+str(text)
                print(stampa+"\n--------------------\n")
            except Exception as e:
                stampa = "Excep:17 -> "+str(e)
                print(stampa+"\n--------------------\n")

            stampa_su_file(stampa,False)
        else:
            bot.sendMessage(chat_id, "Non sei un amministratore, perciò non puoi interagire con il bot in privato.")
            bot.sendMessage(chat_id, messaggio_sviluppatore_versione_aggiornamento)
    else:
        # BOT IN GRUPPI NON ABILITATI
        bot.sendMessage(chat_id, "Questo gruppo non è un gruppo abilitato 🚫. Se è un gruppo ufficiale di Mozilla Italia contatta un moderatore per ottenere maggiori informazione e per risolvere il problema.\n\nChat id: "+str(chat_id))
        print("\n|| -- GRUPPO NON ABILITATO: "+str(chat_id)+" -- ||\n")


bot = telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': risposte, 'callback_query': risposte}).run_as_thread()

while 1:
    time.sleep(1)
