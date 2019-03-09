## it permits you to catch every events in telegram (telepot)
## version 1.0 - 2019-03-09

'''
parameters have to be the message (msg) and a list (allowed_events), and inside event(s) you want to catch
(possibile) parameters:
"NM" -> Normal Message (Only Text)
"LK" -> Link
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
"[[ALL]]" -> All events || If you want to use "all events" you have to put JUST "[[ALL]]" in the list
'''

def events(msg,allowed_events):
    all_events=False # to check if [[ALL]]
    if(len(allowed_events)==1 and allowed_events[0]=="[[ALL]]"):
        all_events=True
    modificato=False
    risposta=False
    if "text" in msg:
        # EVENTO MESSAGGIO 'TESTO' (SOTTO-EVENTI 'TESTO')
        text = str(msg['text'])
        if ("entities" in msg) and (("LK" in allowed_events) or all_events):
            # EVENTO LINK
            type_msg = "LK"  # Link
        else:
            if ("NM" in allowed_events) or all_events:
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
    elif ("document" in msg) and (("D" in allowed_events) or all_events):
        # EVENTO FILE
        type_msg = "D"  # Document
        if "caption" in msg:
            text = str(msg["caption"])
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
            text = str(msg["caption"])
        else:
            text = "|| Immagine/Foto ||"
    elif ("music" in msg) and (("M" in allowed_events) or all_events):
        # EVENTO MUSICA
        type_msg = "M"  # Music
        if "caption" in msg:
            text = str(msg["caption"])
        else:
            text = "|| Musica/Audio ||"
    elif ("video" in msg) and (("V" in allowed_events) or all_events):
        # EVENTO VIDEO
        type_msg = "V"  # Video
        if "caption" in msg:
            text = str(msg["caption"])
        else:
            text = "|| Video ||"
    elif ("contact" in msg) and (("C" in allowed_events) or all_events):
        # EVENTO CONTATTO
        type_msg = "C"  # Contact
        if "caption" in msg:
            text = str(msg["caption"])
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
    else:
        # EVENTO NON CATTURA/GESTITO -> ELIMINARE AUTOMATICAMENTE IL MESSAGGIO.
        text = "|| Testo non identificato ||"
        type_msg = "NI"  # Not Identified

    return {"text":text,"type_msg":type_msg,"modificato":modificato,"risposta":risposta}