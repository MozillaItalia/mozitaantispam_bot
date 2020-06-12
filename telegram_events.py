## it permits you to catch every events in telegram (telepot)

'''
parameters have to be the message (msg) and a list (allowed_events), and inside event(s) you want to catch
(possibile) parameters:
"NM" -> Normal Message (Only Text)
"LK" -> Link (or Bot Command)
"T" -> Tag/Mention
"D" -> Document
"VM" -> Voice Message
"VMSG" -> Video Message
"I" -> Image/Photo
"M" -> Music
"V" -> Video
"C" -> Contact
"P" -> Position
"S" -> Sticket
"G" -> Gif
"POLL" -> Poll
"[[ALL]]" -> All events || If you want to use "all events" you have to put JUST "[[ALL]]" in the list

These are other possible return value (in addition to elements above):
"BIC" -> Button Inline Click
"J" -> Join
"JA" -> Join (Added)
"L" -> Left
"LR" -> Left (Removed)
"NI" -> Not Identified (or Not Allowed)
'''
versione = "1.2.2" # Cambiare manualmente
ultimoAggiornamento = "12-06-2020" # Cambiare manualmentente

print("(Telegram events) Versione: "+versione+" - Aggiornamento: "+ultimoAggiornamento) # Per poter sapere quale versione è in esecuzione (da terminale)

def events(msg,allowed_events,response):
    all_events=False # to check if [[ALL]]
    if(len(allowed_events)==1 and allowed_events[0]=="[[ALL]]"):
        all_events=True
    modificato=False
    risposta=False
    ni=False
    if "text" in msg:
        # EVENTO MESSAGGIO 'TESTO' (SOTTO-EVENTI 'TESTO')
        text = str(msg['text'])
        if ("entities" in msg and "type" in msg["entities"][0]) and (("NM" in allowed_events or "LK" in allowed_events or "T" in allowed_events) or all_events):
            # EVENTO LINK
            if (msg["entities"][0]["type"] == "mention") and ("T" in allowed_events or all_events):
                type_msg = "T" # Tag/Mention
            elif (msg["entities"][0]["type"] == "url" or msg["entities"][0]["type"] == "bot_command") and ("LK" in allowed_events or all_events):
                type_msg = "LK"  # Link (or Bot Command)
            else:
                type_msg = "NM" # Normal Message
        else:
            if ("NM" in allowed_events) or all_events:
                # EVENTO MESSAGGIO PURO
                type_msg = "NM"  # Normal Message
            else:
                ni=True
        if "edit_date" in msg:
            # EVENTO MODIFICA
            modificato = True
        elif "reply_to_message" in msg:
            # EVENTO RISPOSTA
            risposta = True
    elif "data" in msg:
        # EVENTO PRESS BY INLINE BUTTON
        text = str(msg['data'])
        type_msg = "BIC"  # Button Inline Click
    elif "new_chat_participant" in msg:
        # EVENTO JOIN
        if(not (msg['from']['id']==msg['new_chat_participant']['id'])):
            type_msg = "JA" # Join (Added)
            text = "|| Un utente è stato aggiunto ||"
        else:
            type_msg = "J"  # Join
            text = "|| Un utente è entrato ||"
    elif "left_chat_participant" in msg:
        # EVENTO LEFT
        if(not (msg['from']['id']==msg['left_chat_participant']['id'])):
            type_msg = "LR"  # Left (Removed)
            text = "|| Un utente è stato rimosso ||"
        else:
            type_msg = "L"  # Left
            text = "|| Un utente è uscito ||"
    elif ("document" in msg) and not ("animation" in msg) and (("D" in allowed_events) or all_events):
        # EVENTO FILE
        type_msg = "D"  # Document
        if "caption" in msg:
            text = "|| Documento ||\n >> >> Didascalia documento: " + str(msg["caption"])
        else:
            text = "|| Documento ||"
    elif ("voice" in msg) and (("VM" in allowed_events) or all_events):
        # EVENTO VOICE MESSAGE
        type_msg = "VM"  # Voice Message
        text = "|| Messaggio vocale ||"
    elif ("video_note" in msg) and (("VMSG" in allowed_events) or all_events):
        # EVENTO VIDEO-MESSAGE
        type_msg = "VMSG"  # Video Message
        text = "|| Video messaggio ||"
    elif ("photo" in msg) and (("I" in allowed_events) or all_events):
        # EVENTO FOTO/IMMAGINE
        type_msg = "I"  # Photo
        if "caption" in msg:
            text = "|| Immagine/Foto ||\n >> >> Didascalia immagine/foto: " + str(msg["caption"])
        else:
            text = "|| Immagine/Foto ||"
    elif ("music" in msg) and (("M" in allowed_events) or all_events):
        # EVENTO MUSICA
        type_msg = "M"  # Music
        if "caption" in msg:
            text = "|| Musica/Audio ||\n >> >> Didascalia musica/audio: " + str(msg["caption"])
        else:
            text = "|| Musica/Audio ||"
    elif ("video" in msg) and (("V" in allowed_events) or all_events):
        # EVENTO VIDEO
        type_msg = "V"  # Video
        if "caption" in msg:
            text = "|| Video ||\n >> >> Didascalia video: " + str(msg["caption"])
        else:
            text = "|| Video ||"
    elif ("contact" in msg) and (("C" in allowed_events) or all_events):
        # EVENTO CONTATTO
        type_msg = "C"  # Contact
        if "caption" in msg:
            text = "|| Contatto ||\n >> >> Didascalia contatto: " + str(msg["caption"])
        else:
            text = "|| Contatto ||"
    elif ("location" in msg) and (("P" in allowed_events) or all_events):
        # EVENTO POSIZIONE
        type_msg = "P"  # Position
        text = "|| Posizione ||"
    elif ("sticker" in msg) and (("S" in allowed_events) or all_events):
        # EVENTO STICKER
        type_msg = "S"  # Sticker
        text = "(sticker) "+msg["sticker"]["emoji"]
    elif ("animation" in msg) and (("G" in allowed_events) or all_events):
        # EVENTO GIF
        type_msg = "G"  # Gif
        text = "|| Immagine GIF ||"
    elif "new_chat_photo" in msg:
        # EVENTO IMMAGINE CHAT AGGIORNATA
        type_msg = "NCP" # New Chat Photo
        text="|| Immagine chat aggiornata ||"
    elif ("poll" in msg) and (("POLL" in allowed_events) or all_events):
        # EVENTO SONDAGGIO
        type_msg = "POLL" # New Poll created
        text="|| Nuovo sondaggio creato ||"
    else:
        ni=True
    
    if ni:
        # EVENTO NON CATTURA/GESTITO -> ELIMINARE AUTOMATICAMENTE IL MESSAGGIO.
        text = "|| Messaggio non identificato o non consentito ||\n >> >> Response: "+str(response)
        type_msg = "NI"  # Not Identified (or Not Allowed)

    return {"text":text,"type_msg":type_msg,"modificato":modificato,"risposta":risposta}
