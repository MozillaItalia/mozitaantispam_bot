import telepot
import time
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

TOKEN="---NASCOSTO---"

#COPIARE E INCOLLARE DA QUI - IL TOKEN E' GIA' INSERITO

versione="0.0.2 preview"
ultimoAggiornamento="16-11-2018"

VUtenti=[240188083,75870906]#damiano:295348075,saverio:240188083,simone:75870906
VUtenti_name=[]
TUtenti={}
TUtenti_name={}
SUtenti=[]
#V = Verified - T = Temporary - S = Spam

def risposte(msg):
    '''localtime=datetime.now()
    localtime=localtime.strftime("%d/%m/%y %H:%M:%S")'''
    '''file=open("log.txt","a") #apre il file in scrittura "append" per inserire orario e data -> log di utilizzo del bot (ANONIMO)
    file.write(localtime+"\n") #ricordare che l'orario è in fuso orario UTC pari a 0 (Greenwich, Londra) - mentre l'Italia è a +1 (CET) o +2 (CEST - estate)
    file.close()'''
    risposta=False
    entrato=False
    uscito=False
    messaggio=msg
    #try:
    if "text" in msg:
        text=str(msg['text'])
        #print("Messaggio")
    elif "data" in msg:
        text=str(msg['data'])
        risposta=True
        #print("Callback_query")
    elif "new_chat_participant" in msg:
        entrato=True
        #print("Join event")
    elif "left_chat_participant" in msg:
        uscito=True
        #print("Left event")
    else:
        text="--Altro tipo di file--"
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
    #except:
        #print("Exception:01 - "+localtime)
        ##entra in questa eccezione se NON è avviato come comando diretto (digitato come comando e inviato)
    #try:
        #query_id, chat_id, text = telepot.glance(msg, flavor='callback_query')
    #except:
        #print("Exception:02 - "+localtime)
        ##entra in questa eccezione se NON è stato premendo su un pulsante delle inlineKeyboard
    ##I try-except precedenti servono per assegnare, in qualunque circostanza, chat_id e text corettamente (in base al caso)
    #print("Testo: "+str(text)+" - Chat: "+str(chat_id)+" - Utente: "+str(user_name)+" - Id Utente: "+str(user_id)+" - Id Messaggio: "+str(message_id))

    new = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Leggi il Regolamento', url='https://github.com/Sav22999/Guide/blob/master/Mozilla%20Italia/Telegram/regolamento.md')],
                    [InlineKeyboardButton(text='Conferma utente', callback_data='/confutente')],
                ])

    response = bot.getUpdates()
    #print(response)
    try:
        if not risposta:
            if user_id in VUtenti or str(user_name) in VUtenti_name:
                print ("Utente verificato!")
                #bot.sendMessage(chat_id, "@"+str(user_name)+" è un utente verificato !")
            elif int(user_id) in TUtenti.values():
                print ("Utente non verificato!")
                messaggio["message_id"]=message_id
                bot.deleteMessage(telepot.message_identifier(messaggio))
                #bot.sendMessage(chat_id, "@"+str(user_name)+" non è stato verificato: Messaggio eliminato.")
            elif user_id in SUtenti:
                print ("Utente spam")
                bot.kickChatMember(chat_id, user_id, until_date=None)
                bot.sendMessage(chat_id, "@"+str(user_name)+" è stato cacciato poiché risulta utente spam.")
            else:
                if entrato:
                    bot.sendMessage(chat_id, "@"+str(user_name)+", benvenuto nel gruppo ufficiale di Mozilla Italia! Per prima cosa leggi il 'Regolamento' (è molto breve ma fondamentale!). Al momento sei temporaneamente disabilitato.", reply_markup=new)
                    TUtenti[int(message_id)]=int(user_id)
                    TUtenti_name[int(user_id)]=str(user_name)
                    #utente da inserire nella lista momentanea -> nuovo utente
                else:
                    if(not entrato and not uscito):
                        print ("Utente non verificato!")
                        messaggio["message_id"]=message_id
                        bot.deleteMessage(telepot.message_identifier(messaggio))
        else:
            if text == "/confutente" and risposta:
                if user_id in VUtenti or str(user_name) in VUtenti_name:
                    if int(message_id)-1 in TUtenti:
                        #print("Utente verificato e può verificare altri utenti!")
                        #print("Utente da verificare: "+str(TUtenti[int(message_id)-1]))
                        bot.sendMessage(chat_id, "@"+str(user_name)+" ha confermato @"+str(TUtenti_name[int(TUtenti[int(message_id)-1])])+"!")
                        VUtenti.append(int(TUtenti[int(message_id)-1]))
                        del TUtenti_name[int(TUtenti[int(message_id)-1])]
                        del TUtenti[int(message_id)-1]
    except Exception as e:
        print("Excep:03 -> "+str(e))

bot=telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': risposte, 'callback_query': risposte}).run_as_thread()

while 1:
    time.sleep(10)
