import telepot
import time
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

TOKEN="---NASCOSTO---"

#COPIARE E INCOLLARE DA QUI - IL TOKEN E' GIA' INSERITO

versione="0.1.1 preview"
ultimoAggiornamento="22-11-2018"

AdminList=[240188083]
WhiteList=[240188083,295348075,75870906,69903837]#damiano:295348075,saverio:240188083,simone:75870906,daniele:69903837
BlackList={}#2381:75870906
BlackList_name={}#75870906:"mone27"
TempList={}
TempList_name={}
SpamList=[]
chat_name={"-1001225861773": "Super-Gruppo di prova","ID CHAT (GRUPPO)": "Nome da assegnare al gruppo","ID CHAT (Gruppo) (2)": "Nome da assegnare al gruppo (2)"}

def risposte(msg):
    localtime=datetime.now()
    localtime=localtime.strftime("%d/%m/%y %H:%M:%S")
    messaggio=msg
    type_msg="NM" #Normal Message

    modificato=False
    risposta=False
    #try:

    if "text" in msg:
        #EVENTO MESSAGGIO (SOTTO-EVENTI MESSAGGIO)
        text=str(msg['text'])
        if "entities" in msg:
            #EVENTO LINK
            type_msg="LK" #Link
        else:
            #EVENTO MESSAGGIO PURO
            type_msg="NM" #Normal Message
        if "edit_date" in msg:
            #EVENTO MODIFICA
            modificato=True
        elif "reply_to_message" in msg:
            #EVENTO RISPOSTA
            risposta=True
    elif "data" in msg:
        #EVENTO PRESS BY INLINE BUTTON
        text=str(msg['data'])
        #print("Callback_query")
        type_msg="BIC" #Button Inline Click
    elif "new_chat_participant" in msg:
        #EVENTO JOIN
        #print("Join event")
        type_msg="J" #Join
        text="|| Un utente è entrato ||"
    elif "left_chat_participant" in msg:
        #EVENTO LEFT
        #print("Left event")
        type_msg="L" #Left
        text="|| Un utente è uscito ||"
    elif "document" in msg:
        #EVENTO FILE
        type_msg="D" #Document
        if "caption" in msg:
            text=str(msg["caption"])
        else:
            text=""
    elif "voice" in msg:
        #EVENTO VOICE MESSAGE
        type_msg="VM" #Voice Message
        text="|| Messaggio vocale ||"
    elif "video_note" in msg:
        #EVENTO VIDEO-MESSAGE
        type_msg="VMSG" #Video Message
        text="|| Video messaggio ||"
    elif "photo" in msg:
        #EVENTO FOTO/IMMAGINE
        type_msg="I" #Photo
        if "caption" in msg:
            text=str(msg["caption"])
        else:
            text=""
    elif "music" in msg:
        #EVENTO MUSICA
        type_msg="M" #Music
        if "caption" in msg:
            text=str(msg["caption"])
        else:
            text=""
    elif "video" in msg:
        #EVENTO VIDEO
        type_msg="V" #Video
        if "caption" in msg:
            text=str(msg["caption"])
        else:
            text=""
    elif "contact" in msg:
        #EVENTO CONTATTO
        type_msg="C" #Contact
        if "caption" in msg:
            text=str(msg["caption"])
        else:
            text=""
    elif "location" in msg:
        #EVENTO POSIZIONE
        type_msg="P" #Position
        text=""
    elif "sticker" in msg:
        #EVENTO STICKER
        type_msg="S" #Stiker
        text=""
    elif "animation" in msg:
        #EVENTO GIF
        type_msg="G" #Gif
        text=""
    else:
        #EVENTO NON CATTURA/GESTITO -> ELIMINARE AUTOMATICAMENTE IL MESSAGGIO
        text="--Testo non identificato--"
        type_msg="NI" #Not Identified

    user_id=msg['from']['id']
    #print(user_id)
    user_name=msg['from']['username']
    #print(user_name)
    if not "chat" in msg:
        msg=msg["message"]
    chat_id=msg['chat']['id']
    #print(chat_id)
    message_id=msg['message_id']
    #print(message_id)

    if str(chat_id) in chat_name:
        #BOT NEI GRUPPI ABILITATI
        nome_gruppo=str(chat_name[str(chat_id)])

        new = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Mostra Regolamento', callback_data="/leggiregolamento")],
                    ])
        regolamentoletto = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Leggi il Regolamento completo', url='https://github.com/Sav22999/Guide/blob/master/Mozilla%20Italia/Telegram/regolamento.md')],
                        [InlineKeyboardButton(text='Conferma identità utente', callback_data='/confutente')],
                    ])

        response = bot.getUpdates()
        #print(response)

        status_user="-"

        parole_vietate=["vaffanculo","fuck off","fuck you","fanculo","puttana","stronza","troia","cazzo","cretino","bartardo","coglione","imbecille"]

        controllo_parole_vietate=False
        if any(ext in text.lower() for ext in parole_vietate):
            controllo_parole_vietate=True

        #if text=="J":
            #type_msg="J"

        try:
            if type_msg!="BIC":
                if (user_id in WhiteList or user_id in AdminList) and type_msg!="NI" and not controllo_parole_vietate:
                    #print ("Utente verificato!")
                    #bot.sendMessage(chat_id, "@"+str(user_name)+" è un utente verificato !")
                    status_user="W" #WhiteList
                elif int(user_id) in BlackList.values() and type_msg!="NI" and not controllo_parole_vietate:
                    #print ("Utente non verificato!")
                    messaggio["message_id"]=message_id
                    bot.deleteMessage(telepot.message_identifier(messaggio))
                    status_user="B" #BlackList
                    #bot.sendMessage(chat_id, "@"+str(user_name)+" non è stato verificato: Messaggio eliminato.")
                elif int(user_id) in TempList.values() and type_msg!="NI" and not controllo_parole_vietate:
                    #print ("Utente non verificato!")
                    messaggio["message_id"]=message_id
                    if type_msg!="NM":
                        bot.deleteMessage(telepot.message_identifier(messaggio))
                    status_user="T" #TempList
                elif (user_id in SpamList and type_msg!="NI") or controllo_parole_vietate:
                    #print ("Utente spam")
                    messaggio["message_id"]=message_id
                    bot.deleteMessage(telepot.message_identifier(messaggio))
                    if not(user_id in AdminList):
                        SpamList.append(int(user_id))
                        bot.kickChatMember(chat_id, user_id, until_date=None)
                    bot.sendMessage(chat_id, "@"+str(user_name)+" è stato cacciato poiché risulta utente spam.")
                    status_user="S" #SpamList
                else:
                    if type_msg=="J":
                        bot.sendMessage(chat_id, "@"+str(user_name)+", benvenuto nel gruppo '"+str(nome_gruppo)+"'! Per prima cosa leggi il 'Regolamento' (è molto breve ma fondamentale!). Al momento sei temporaneamente disabilitato.", reply_markup=new)
                        BlackList[int(message_id)]=int(user_id)
                        BlackList_name[int(user_id)]=str(user_name)
                        status_user="B"
                        #utente da inserire nella lista momentanea -> nuovo utente
                    ##else:
                        ##if (type_msg!="J" and type_msg!="L") or type_msg=="NI":
                            ###print ("Utente non verificato o Messaggio di tipo non identificato!")
                            ##messaggio["message_id"]=message_id
                            ##bot.deleteMessage(telepot.message_identifier(messaggio))
                            ##status_user="S"
                            ##SpamList.append(int(user_id))
                            #del BlackList_name[int(BlackList[int(message_id)-1])]
                            #'''if user_id in WhiteList:
                            #    del WhiteList[int(user_id)]'''
                            #'''elif user_id in BlackList:
                            #    del BlackList''' #DA COMPLETARE -> elimina l'id dalla lista nella quale è presente (contrallare)
            else:
                if text=="/leggiregolamento" and type_msg=="BIC":
                    if user_id == int(BlackList[int(message_id)-1]):
                        TempList[int(message_id)-1]=BlackList[int(message_id)-1]
                        TempList_name[int(TempList[int(message_id)-1])]=BlackList_name[int(BlackList[int(message_id)-1])]
                        del BlackList_name[int(BlackList[int(message_id)-1])]
                        del BlackList[int(message_id)-1]
                        status_user="T"
                        bot.sendMessage(chat_id, "@"+str(user_name)+", ecco qui alcune delle regole principali da seguire.\nTi preghiamo di leggere TUTTO il regolamento: è breve e molto semplice, ma essenziale!\n\nRegole principali:\n1. Avere rispetto di tutti.\n2. Non utilizzare un linguaggio scurrile\n\nOra puoi scrivere dei messaggi di solo testo (NO LINK) finché un altro utente già verificato non conferma la tua identità di UTENTE REALE e non spam.", reply_markup=regolamentoletto)
                    
                elif text == "/confutente" and type_msg=="BIC":
                    if user_id in WhiteList or user_id in AdminList:
                        user_name_temp=str(msg['text'].split(",")[0]).lstrip("@")
                        if str(user_name_temp) in TempList_name.values():
                            user_id_temp=int(next((x for x in TempList_name if TempList_name[x] == str(user_name_temp)), None))
                            message_id_temp=next((x for x in TempList if TempList[x] == int(user_id_temp)), None)+1
                            #print("Utente da verificare: "+str(TempList[int(message_id_temp)-1]) + "Message id: "+str(message_id_temp))
                            bot.sendMessage(chat_id, "@"+str(user_name)+" ha confermato @"+str(TempList_name[int(TempList[int(message_id_temp)-1])])+"!")
                            WhiteList.append(int(TempList[int(message_id_temp)-1]))
                            del TempList_name[int(TempList[int(message_id_temp)-1])]
                            del TempList[int(message_id_temp)-1]
                            status_user="W"
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
            dettagli=""
            if modificato:
                dettagli+="(modificato) "
            if risposta:
                dettagli+="(risposta) "
            stampa="Id Msg: "+str(message_id)+"  --  "+str(localtime)+"  --  Utente: "+str(user_name)+" ("+str(user_id)+")["+str(status_user)+"]  --  Gruppo: "+str(nome_gruppo)+"\n >> >> Tipo messaggio: "+str(type_msg)+"\n >> >> Contenuto messaggio: "+str(dettagli)+str(text)+"\n--------------------\n"
            print(stampa)
        except Exception as e:
            stampa="Excep:02 -> "+str(e)
            print(stampa)

        #try:
            #file=open("history.txt","a",-1,"UTF-8") #apre il file in scrittura "append" per inserire orario e data -> log di utilizzo del bot (ANONIMO)
            #file.write(stampa) #ricordare che l'orario è in fuso orario UTC pari a 0 (Greenwich, Londra) - mentre l'Italia è a +1 (CET) o +2 (CEST - estate)
            #file.close()
        #except Exception as e:
            #print("Excep:03 -> "+str(e))
    else:
        #BOT IN CHAT PRIVATA
        print("BOT IN CHAT PRIVATA")

        conf_user_id=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Username', callback_data="/confusername"),
                         InlineKeyboardButton(text='Id', callback_data="/confid")],
                    ])

        if user_id in AdminList:
            err1=False
            if type_msg=="NM":
                if ("conferma" or "ban" or "sblocca") in text:
                    azione=list(text.split(" "))
                    if azione[0]=="conferma" and len(azione)==2:
                        #CONFERMA MANUALE
                        if azione[1].isdigit():
                            #CONFERMA MANUALE PER USER_ID
                            print("")
                        else:
                            #CONFERMA MANUALE PER USERNAME
                            print("")
                    elif azione[0]=="ban" and len(azione)==2:
                        #BAN MANUALE
                        if azione[1].isdigit():
                            #BAN MANUALE PER USER_ID
                            print("")
                        else:
                            err1=True
                    elif azione[0]=="sblocca" and len(azione)==2:
                        #SBLOCCO MANUALE
                        if azione[1].isdigit():
                            #SBLOCCO MANUALE PER USER_ID
                            print("")
                        else:
                            err1=True
                    else:
                        err1=True
                else:
                    err1=True
            elif type_msg=="LK":
                if text=="/start":
                    bot.sendMessage(chat_id, "Benvenuto nella chat privata del bot.\nPuoi interagire con il bot, in chat privata, perché sei un amministratore.\nDigita /help per ottenere la lista di tutte le azioni che puoi fare nel bot IN PRIVATO (i comandi NON funzionano nei gruppi abilitati).")
                elif text=="/help":
                    bot.sendMessage(chat_id, "Ecco la lista delle azioni disponibili:\n 1 - 'conferma USER_ID': per confermare un utente attraverso il suo user_id (intero) -> sostituire USER_ID con l'id dell'utente\n 2 - 'conferma USERNAME': per confermare un utente attraverso il suo username (@username) -> sostituire USERNAME con l'username dell'utente, non inserire la '@' nel comando\n 3 - 'ban USER_ID': inserire un utente, partendo dal suo user id intero, nella SpamList -> nota che l'utente verrà cacciato dai gruppi solo quando scriverà qualcosa in essi\n 4 - 'sblocca USER_ID': per sbloccare un utente precedentemente bloccato -> viene rimosso dalla SpamList MA NON VIENE SBLOCCATO dai gruppi: procedere manualmente\n")
                else:
                    err1=True
            else:
                err1=True

            if err1:
                bot.sendMessage(chat_id, "Messaggio non riconosciuto. Digita /help per ottenere la lista di ciò che puoi fare.")
        else:
            bot.sendMessage(chat_id, "Non sei un amministratore, perciò non puoi interagire con il bot in privato.")
            

bot=telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': risposte, 'callback_query': risposte}).run_as_thread()

while 1:
    time.sleep(1)
