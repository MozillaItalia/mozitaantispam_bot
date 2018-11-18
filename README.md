# MozIta Antispam Bot
Questo è il repository della beta del nuovo bot antispam dei gruppi ufficiali della comunità di Mozilla Italia su Telegram.


# Informazioni utili
Questo progetto è una beta del nuovo bot antispam per i gruppi di Mozilla Italia (su Telegram).
È sviluppato in Python e per funzionare necessita di essere avviato su un server (o su un computer).
Per segnalare errori aprire un nuovo ticket (si prega di aprire un ticket per ogni errore/idee/bug/ecc, poiché raggrupparli tutti in un unico issue è dispersivo).
`Il token per accedere al bot diretto è nascosto (per ragioni ovvie).`

Grazie a tutti.

# Funzionamento del bot
Il bot si compone di 5 liste:
 - **AdminList** -> gli utenti "amministratori" del bot: hanno gli stessi privilegi degli utenti presenti nella WhiteList ma, inoltre, possono segnalare **manualmente** (o sbloccare, eventualmente) utenti attraverso la chat con il bot in maniera privata.
 - **WhiteList** -> tutti gli utenti *verificati*: essi possono inviare qualunque cosa (testo, file, ecc.) nei gruppi Mozilla Italia (**NEL RISPETTO DEL REGOLAMENTO**)
 - **BlackList** -> tutti gli utenti *nuovi*, ovvero coloro che non hanno neppure letto il [Regolamento](https://github.com/Sav22999/Guide/blob/master/Mozilla%20Italia/Telegram/regolamento.md): essi NON possono inviare nulla nei gruppi Mozilla Italia (verranno automaticamente eliminati)
 - **TempList** -> tutti gli utenti *non verificati* ma che hanno letto già il Regolamento: possono inviare solamente del testo
 - **SpamList** -> tutti gli utenti *spam* vengono raccolti in questa lista: essi vengono automaticamente cacciati e bannati dai gruppi Mozilla Italia non appena inviano qualcosa
 
> Le liste valgono per tutti i gruppi Mozilla Italia (da qui MozIta) e sono unificate, quindi un utente presente nella lista *spam* e già cacciato e bannato in un gruppo MozIta, appena invia qualcosa in un altro gruppo MozIta viene *automaticamente* bannato e cacciato anche da quel gruppo. Così come se un utente è già *verificato* in un gruppo lo è anche in tutti gli altri.

### Primi passi
Non appena si entra in un gruppo MozIta il bot ti inserirà nella lista **BlackList**, quindi non potrai inviare nulla (se lo farai verrà automaticamente eliminata dal bot). Dovrai leggere il Regolamento, dopo fatto ciò passerai automaticamente alla **TempList** in attesa che un qualunque altro utente già verificato confermi la tua identità. Nell'attesa, finché rimarrai nella TempList, potrai inviare messaggi di solo testo (pena il passaggio nella **SpamList**, quindi ban ed eliminazione dai gruppi MozIta).
Non appena, comunque, un utente confermerà la tua identità sarai libero di inviare messaggi di qualsiasi genere nel rispetto del Regolamento.
Il bot, ugualmente, filtrerà i messaggi inviati per verificare che rispettino il Regolamento. In caso non lo fosserò, il bot **automaticamente** prenderà provvedimenti o, in caso il bot non identifichi il messaggio come spam (ma lo è), un nostro amministratore (membro della **AdminList**) provvederà al ban manuale.

`Non vogliamo negare la libertà di espressione, ma bisogna avere rispetto di tutti e seguire delle regole prestabilite, che sono state pensate, scritte e approvate da molti altri precedentemente. Per il bene comune (**Fast for Good**).`

### Lettura regolamento
Quando si preme su "Leggi Regolamento" in automatico viene inviato un messaggio (nella chat del gruppo) con delle regole basi che NON sostituiscono in alcun modo il Regolamento (che, comunque, è breve! Perciò è bene perdere 5 minuti nel leggerlo).
Il bot, in automatico, inserisce il nominativo (user_id) nella **TempList** in attesa che un utente verificato confermi la tua identità. Puoi, comunque, scrivere messaggi di testo per farci capire che, effettivamente, se una persona in carne e ossa :).

### Conferma identità
Tutti gli utenti presenti nella **WhiteList** possono confermare l'indentità degli utenti.
Si noti che prima di confermare l'identità è necessario accertarsi che l'utente non sia uno spam:
 - Vedere l'immagine del profilo: è una foto "normale"? O contiene contenuti non accettati?
 - Vedere il nome utente: è un nome utente "normale"? O sono solo alcune lettere messe insieme?

> **Se non si è sicuri dell'identità dell'utente *non* bisogna confermare ma, piuttosto, scrivere un messaggio taggando un amministratore e spiegando la situazione. Egli procederà alle verifiche più accurate**.
