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

versione = "1.1.0"
ultimoAggiornamento = "02-02-2019"

print("Versione: "+versione+" - Aggiornamento: "+ultimoAggiornamento)

user_id_IRCbot = "000000000"  # user_id del bot IRC mozilla italia
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
    chat_name = []
if Path(parole_vietate_path).exists():
    parole_vietate = json.loads(open(parole_vietate_path).read())
else:
    parole_vietate = []


def risposte(msg):
    localtime = datetime.now()
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
    else:
        # EVENTO NON CATTURA/GESTITO -> ELIMINARE AUTOMATICAMENTE IL MESSAGGIO.
        text = "--Testo non identificato--"
        type_msg = "NI"  # Not Identified

    # type_msg="NotAllowed"

    user_id = msg['from']['id']
    # print(user_id)
    nousername = False
    if "username" in msg['from']:
        user_name = msg['from']['username']
    else:
        user_name = "[*NessunUsername*]"
        nousername = True
    # print(user_name)
    if not "chat" in msg:
        msg = msg["message"]
    chat_id = msg['chat']['id']
    # print(chat_id)
    message_id = msg['message_id']
    # print(message_id)

    #response = bot.getUpdates()
    # print(response)

    if str(chat_id) in chat_name and msg['chat']['type'] != "private":
        # BOT NEI GRUPPI ABILITATI
        nome_gruppo = str(chat_name[str(chat_id)])

        new = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Mostra Regolamento ⏬',
                                  callback_data="/leggiregolamento")],
        ])
        regolamentoletto = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Leggi il Regolamento completo 📙',
                                  url='https://github.com/Sav22999/Guide/blob/master/Mozilla%20Italia/Telegram/regolamento.md')],
            [InlineKeyboardButton(
                text='Conferma identità utente ☑️', callback_data='/confutente')],
        ])

        status_user = "-"
        if nousername:
            username_utente_nousername = "["+str(user_id)+"](tg://user?id="+str(user_id)+")"
        else:
            username_utente_nousername = "@"+str(user_name)
        messaggio_benvenuto = username_utente_nousername+", benvenuto nel gruppo '"+str(nome_gruppo) + "'! Per prima cosa 'Mostra il Regolamento' e leggilo attentamente; è molto breve ma fondamentale!\nAl momento non puoi inviare messaggi di alcun genere (verranno automaticamente eliminati)."

        controllo_parole_vietate = False
        if any(ext in text.lower() for ext in parole_vietate):
            controllo_parole_vietate = True

        try:
            if type_msg != "BIC":
                # Se si vuole solamente eliminare un messaggio in base a una specifica condizione
                if type == "NI":
                    messaggio["message_id"] = message_id
                    bot.deleteMessage(telepot.message_identifier(messaggio))
                    # Elimina messaggio nel caso in cui risulti proprio uguale a (vedi sopra)
                    
                if int(user_id) in SpamList and type_msg != "NI" or controllo_parole_vietate:
                    #print ("Utente spam")
                    # L'utente può essere presente anche in altre liste -> ma se è presente qui viene bloccato e cacciato ugualmente
                    messaggio["message_id"] = message_id
                    bot.deleteMessage(telepot.message_identifier(messaggio))
                    if not(user_id in AdminList) and not(user_id == user_id_IRCbot):
                        SpamList.append(int(user_id))
                        bot.kickChatMember(chat_id, user_id, until_date=None)
                        if nousername:
                            username_utente_nousername = "["+str(user_id)+"](tg://user?id="+str(user_id)+")"
                        else:
                            username_utente_nousername = "@"+str(user_name)
                        bot.sendMessage(chat_id, "‼️ " + username_utente_nousername + " è stato cacciato perché identificato come utente spam.")
                    status_user = "S"  # SpamList
                    try:
                        with open(spamlist_path, "wb") as f:
                            f.write(json.dumps(SpamList).encode("utf-8"))
                    except Exception as e:
                        print("Excep:04 -> "+str(e))
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
                    status_user = "B"  # BlackList
                    #bot.sendMessage(chat_id, "@"+str(user_name)+" non è stato verificato: Messaggio eliminato.")
                elif int(user_id) in TempList.values() and type_msg != "NI" and not controllo_parole_vietate:
                    #print ("Utente non verificato!")
                    messaggio["message_id"] = message_id
                    if type_msg != "NM":
                        if type_msg != "J" and type_msg != "L":
                            bot.deleteMessage(telepot.message_identifier(messaggio))
                    status_user = "T"  # TempList
                else:
                    if type_msg == "J":
                        # Nuovo utente
                        bot.sendMessage(chat_id, messaggio_benvenuto, reply_markup=new)
                        BlackList[str(message_id)] = int(user_id)
                        BlackList_name[str(user_id)] = str(user_name)
                        status_user = "B"
                        try:
                            with open(blacklist_path, "wb") as f:
                                f.write(json.dumps(BlackList).encode("utf-8"))
                            with open(blacklist_name_path, "wb") as f:
                                f.write(json.dumps(
                                    BlackList_name).encode("utf-8"))
                        except Exception as e:
                            print("Excep:13 -> "+str(e))
                    elif type_msg != "J" and type_msg != "L":
                        # Utente già presente nel gruppo ma non presente in alcuna lista
                        bot.sendMessage(chat_id, messaggio_benvenuto, reply_markup=new, parse_mode="Markdown")
                        BlackList[str(message_id)] = int(user_id)
                        BlackList_name[str(user_id)] = str(user_name)
                        bot.deleteMessage(telepot.message_identifier(messaggio))
                        status_user = "B"
                        try:
                            with open(blacklist_path, "wb") as f:
                                f.write(json.dumps(BlackList).encode("utf-8"))
                            with open(blacklist_name_path, "wb") as f:
                                f.write(json.dumps(BlackList_name).encode("utf-8"))
                        except Exception as e:
                            print("Excep:14 -> "+str(e))
                    else:
                        #bot.sendMessage(chat_id, "Il messaggio non è stato riconosciuto e, pertanto, è stato rimosso.")
                        bot.deleteMessage(telepot.message_identifier(messaggio))
                        status_user = "-"
            else:
                if text == "/leggiregolamento" and type_msg == "BIC":
                    if user_id == int(BlackList[str(int(message_id)-1)]):

                        TempList[str(int(message_id)-1)] = BlackList[str(int(message_id)-1)]
                        print(TempList[str(int(message_id)-1)])
                        TempList_name[str(TempList[str(int(message_id)-1)])] = BlackList_name[str(BlackList[str(int(message_id)-1)])]
                        del BlackList_name[str(BlackList[str(int(message_id)-1)])]
                        del BlackList[str(int(message_id)-1)]
                        status_user = "T"
                        if nousername:
                            username_utente_nousername = "["+str(user_id)+"](tg://user?id="+str(user_id)+")"
                        else:
                            username_utente_nousername = "@"+str(user_name)
                        bot.sendMessage(chat_id, username_utente_nousername+", ecco qui alcune delle regole principali da seguire.\nTi preghiamo di leggere TUTTO il regolamento: è breve e molto semplice, ma essenziale!\n\nRegole principali:\n1. Avere rispetto di tutti.\n2. Non utilizzare un linguaggio scurrile\n\nAttualmente puoi scrivere dei messaggi di solo testo (NO LINK) finché un altro utente, già verificato, non conferma la tua identità di UTENTE REALE e non spam.", reply_markup=regolamentoletto, parse_mode="Markdown")

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
                            print("Excep:15 -> "+str(e))

                elif text == "/confutente" and type_msg == "BIC":
                    if user_id in WhiteList or user_id in AdminList:
                        user_name_temp = str(msg['text'].split(",")[0]).lstrip("@")
                        print("Username temp: "+str(user_name_temp))
                        print("Messaggio:"+msg['text'])
                        nousername_temp=False
                        if "[*NessunUsername*]"+str(user_name_temp) in TempList_name.values():
                            nousername_temp=True
                            user_name_temp="[*NessunUsername*]"+str(user_name_temp)
                        if str(user_name_temp) in TempList_name.values() or nousername_temp:
                            if nousername:
                                username_utente_nousername = "["+str(user_id)+"](tg://user?id="+str(user_id)+")"
                            else:
                                username_utente_nousername = "@"+str(user_name)
                            user_id_temp = int(next((x for x in TempList_name if TempList_name[x] == str(user_name_temp)), None))
                            message_id_temp = int(next((x for x in TempList if TempList[x] == int(user_id_temp)), None))+1
                            if nousername_temp:
                                username_utente_nousername_temp = "["+str(user_id_temp)+"](tg://user?id="+str(user_id_temp)+")"
                            else:
                                username_utente_nousername_temp = "@"+str(TempList_name[str(TempList[str(int(message_id_temp)-1)])])
                            #print("Utente da verificare: "+str(TempList[int(message_id_temp)-1]) + "Message id: "+str(message_id_temp))
                            bot.sendMessage(chat_id, "✅ "+username_utente_nousername+" ha confermato "+username_utente_nousername_temp+".", parse_mode="Markdown")
                            bot.sendMessage(chat_id, username_utente_nousername_temp+" ora puoi inviare messaggi di qualsiasi genere, nei limiti del Regolamento 📙.\nBenvenuto, ancora una volta, ufficialmente nella comunità Mozilla Italia 🇮🇹.", parse_mode="Markdown")
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
                                print("Excep:16 -> "+str(e))
        except Exception as e:
            print("Excep:01 -> "+str(e))

        try:
            #print("AdminList: "+str(AdminList))
            #print("WhiteList: "+str(WhiteList))
            #print("BlackList: "+str(BlackList))
            #print("BlackList_name: "+str(BlackList_name))
            #print("TempList: "+str(TempList))
            #print("TempList_name: "+str(TempList_name))
            #print("SpamList: "+str(SpamList))
            #print("chat_name: "+str(chat_name))
            #print("parole_vietate: "+str(parole_vietate))
            dettagli = ""
            if modificato:
                dettagli += "(modificato) "
            if risposta:
                dettagli += "(risposta) "
            stampa = "Id Msg: "+str(message_id)+"  --  "+str(localtime)+"  --  Utente: "+str(user_name)+" ("+str(user_id)+")["+str(status_user)+"]  --  Gruppo: "+str(
                nome_gruppo)+"("+str(chat_id)+")\n >> >> Tipo messaggio: "+str(type_msg)+"\n >> >> Contenuto messaggio: "+str(dettagli)+str(text)+"\n--------------------\n"
            print(stampa)
        except Exception as e:
            stampa = "Excep:02 -> "+str(e)+"\n--------------------\n"
            print(stampa)

        try:
            # apre il file in scrittura "append" per inserire orario e data -> log di utilizzo del bot (ANONIMO)
            file = open("history.txt", "a", -1, "UTF-8")
            # ricordare che l'orario è in fuso orario UTC pari a 0 (Greenwich, Londra) - mentre l'Italia è a +1 (CET) o +2 (CEST - estate)
            file.write(stampa)
            file.close()
        except Exception as e:
            print("Excep:03 -> "+str(e))
    elif msg['chat']['type'] == "private":
        # BOT IN CHAT PRIVATA

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
                    bot.sendMessage(chat_id, "Elenco azioni disponibili:\n - utente aggiungi |USERID|\n - utente blocca |USERID|\n - utente sblocca |USERID|\n - parola mostra\n - parola aggiungi |PAROLA/FRASE|\n - parola elimina |PAROLA/FRASE|\n - gruppo mostra\n - gruppo aggiungi |USERID| |NOME GRUPPO|\n - gruppo elimina |USERID|\n - invia messaggio |TESTO MESSAGGIO|\n\nMozIta Antispam Bot è stato sviluppato da Saverio Morelli @Sav2299 con il grandissimo supporto e aiuto di Damiano Gualandri @dag7dev e Simone Massaro @mone27.")
                    lk = True
                    esito = "OK"

                if "utente" in text or "parola" in text or "gruppo" in text or "invia messaggio" in text and not lk:
                    azione = list(text.split(" "))
                    if azione[0] == "utente" and len(azione) == 3 and type_msg != "LK":
                        if azione[1] == "aggiungi":
                            if azione[2].isdigit():
                                print("Utente aggiunto")
                                WhiteList.append(int(azione[2]))
                                bot.sendMessage(
                                    chat_id, "Userid inserito correttamente nella WhiteList")
                                try:
                                    with open(whitelist_path, "wb") as f:
                                        f.write(json.dumps(
                                            WhiteList).encode("utf-8"))
                                    esito = "OK"
                                except Exception as e:
                                    print("Excep:06 -> "+str(e))
                            else:
                                err2 = True
                        elif azione[1] == "blocca":
                            if azione[2].isdigit():
                                print("Utente bloccato")
                                if not int(azione[2]) in SpamList:
                                    SpamList.append(int(azione[2]))
                                    bot.sendMessage(
                                        chat_id, "Userid inserito correttamente nella SpamList")
                                    esito = "OK"
                                else:
                                    bot.sendMessage(
                                        chat_id, "Errore: l'userid digitato è già presente nella SpamList")
                                try:
                                    with open(spamlist_path, "wb") as f:
                                        f.write(json.dumps(
                                            SpamList).encode("utf-8"))
                                except Exception as e:
                                    print("Excep:07 -> "+str(e))
                            else:
                                err2 = True
                        elif azione[1] == "sblocca":
                            if azione[2].isdigit():
                                if int(azione[2]) in SpamList:
                                    print("Utente sbloccato")
                                    SpamList.remove(int(azione[2]))
                                    bot.sendMessage(
                                        chat_id, "Userid rimosso correttamente dalla SpamList")
                                    try:
                                        with open(spamlist_path, "wb") as f:
                                            f.write(json.dumps(
                                                SpamList).encode("utf-8"))
                                        esito = "OK"
                                    except Exception as e:
                                        print("Excep:08 -> "+str(e))
                                else:
                                    bot.sendMessage(
                                        chat_id, "Errore: l'userid digitato non è presente nella SpamList")
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
                                        f.write(json.dumps(
                                            parole_vietate).encode("utf-8"))
                                    esito = "OK"
                                except Exception as e:
                                    print("Excep:09 -> "+str(e))
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
                                        f.write(json.dumps(
                                            parole_vietate).encode("utf-8"))
                                    esito = "OK"
                                except Exception as e:
                                    print("Excep:10 -> "+str(e))
                            else:
                                bot.sendMessage(
                                    chat_id, "Parola non presente nelle parole vietate")
                        else:
                            err1 = True
                    elif azione[0] == "gruppo" and len(azione) >= 2:
                        if azione[1] == "mostra" and len(azione) == 2:
                            print("Gruppi mostrati")
                            bot.sendMessage(
                                chat_id, "Elenco gruppi abilitati (in array):\n"+str(chat_name))
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
                                    bot.sendMessage(
                                        chat_id, "Gruppo \""+str(gruppo)+"\" aggiunto correttamente ai gruppi abilitati")
                                    try:
                                        with open(chat_name_path, "wb") as f:
                                            f.write(json.dumps(
                                                chat_name).encode("utf-8"))
                                        esito = "OK"
                                    except Exception as e:
                                        print("Excep:11 -> "+str(e))
                                else:
                                    bot.sendMessage(chat_id, "Gruppo già presente nei gruppi abilitati")
                            except Exception as e:
                                bot.sendMessage(chat_id, "ChatId errata. Inserirne una valida")
                                print("Excep:19 -> "+str(e))
                        elif azione[1] == "elimina" and len(azione) == 3:
                            print("Gruppo rimosso")
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
                                else:
                                    bot.sendMessage(chat_id, "Gruppo non presente nei gruppi abilitati")
                            except Exception as e:
                                bot.sendMessage(chat_id, "ChatId errata. Inserirne una valida")
                                print("Excep:20 -> "+str(e))
                        else:
                            err1 = True
                    elif azione[0] == "invia" and azione[1] == "messaggio" and len(azione) >= 3:
                        del azione[0]
                        del azione[0]
                        messaggio = ' '.join(azione)
                        if len(chat_name) > 0:
                            for gruppo_x in chat_name.keys():
                                try:
                                    bot.sendMessage(gruppo_x, messaggio, parse_mode="Markdown")
                                    bot.sendMessage(chat_id, "Messaggio inviato in \""+str(chat_name[gruppo_x])+"\"")
                                except Exception as e:
                                    print("Excep:05 -> "+str(e))
                                    bot.sendMessage(chat_id, "Non è stato possibile inviare il messaggio in: "+str(chat_name[gruppo_x]))
                            bot.sendMessage(chat_id, "Messaggio inviato in tutti i gruppi abilitati.\n\nIl messaggio che è stato inviato è:\n"+messaggio, parse_mode="Markdown")
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
                    chat_id)+")\n >> >> Esito: "+str(esito)+"\n >> >> Contenuto messaggio: "+str(text)+"\n--------------------\n"
                print(stampa)
            except Exception as e:
                stampa = "Excep:17 -> "+str(e)+"\n--------------------\n"
                print(stampa)
            try:
                # apre il file in scrittura "append" per inserire orario e data -> log di utilizzo del bot (ANONIMO)
                file = open("history.txt", "a", -1, "UTF-8")
                # ricordare che l'orario è in fuso orario UTC pari a 0 (Greenwich, Londra) - mentre l'Italia è a +1 (CET) o +2 (CEST - estate)
                file.write(stampa)
                file.close()
            except Exception as e:
                print("Excep:03 -> "+str(e))
        else:
            bot.sendMessage(
                chat_id, "Non sei un amministratore, perciò non puoi interagire con il bot in privato.")
    else:
        # BOT IN GRUPPI NON ABILITATI
        bot.sendMessage(chat_id, "Questo gruppo non è un gruppo abilitato 🚫. Se è un gruppo ufficiale di Mozilla Italia contatta un moderatore per ottenere maggiori informazione e per risolvere il problema.\n\nChat id: "+str(chat_id))
        print("\n|| -- GRUPPO NON ABILITATO: "+str(chat_id)+" -- ||\n")


bot = telepot.Bot(TOKEN)
MessageLoop(
    bot, {'chat': risposte, 'callback_query': risposte}).run_as_thread()

while 1:
    time.sleep(1)
