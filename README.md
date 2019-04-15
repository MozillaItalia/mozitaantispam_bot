# MozIta Antispam Bot
Questo è il repository della beta del nuovo bot antispam dei gruppi ufficiali della comunità di Mozilla Italia su Telegram.


# Informazioni utili
Questo progetto è una beta del nuovo bot antispam per i gruppi di Mozilla Italia (su Telegram).
È sviluppato in Python e per funzionare necessita di essere avviato su un server (o su un computer).
Per segnalare errori aprire un nuovo ticket (si prega di aprire un ticket per ogni errore/idee/bug/ecc, poiché raggrupparli tutti in un unico issue è dispersivo).
`Il token per accedere al bot diretto è nascosto (per ragioni ovvie).`

> **Per poter funzionare in chat di gruppo, il bot deve essere necessariamente amministratore del gruppo**

Grazie a tutti.

### Installazione ed esecuzione bot
Per poter eseguire il codice, quindi far girare il bot, è necessario seguire i seguenti passaggi (in ordine):
 - Clonare questa repository, quindi premere su *Fork* in alto a destra
 - Installare Python 3 (o verificare di averlo già installato) **sviluppato e testato con Python 3.6.6**, ma dovrebbe funzionare anche con altre versioni
 - Installare la libreria **telepot**, tramite *pip* (o verificare di averla già installata)

   > pip3 install telepot

### Frasi visualizzate e contenuto bottoni

Le frasi e il testo contenuto nei bottoni che vengono visualizzati dall'utente quando viene utilizzato il bot sono contenuti nel file **frasi.json**. È possibile perfino utilizzare l'HTML (vedi sotto "_Tag HTML supportati_")

Può essere sempre modificato, ma è necessario seguire le seguenti regole:

- Le variabili non vanno modificate.
  Le variabili sono identificabili facilmente perché sono del tipo: `{{**nome_variabile**}}`
- La variabile `{{**username**}}` in '_benvenuto_', '_regolamento_letto_' e '_utente_confermato_' deve essere **obbligatoriamente** all'inizio del messaggio/frase

##### Tag HTML Supportati

I tag HTML supportati da Telegram sono:

- `<b></b>`: testo in grassetto
- `<i></i>`: testo in corsivo
- `<a href="https://..."></a>`: inserire link
- `<a href="tg://user?id="></a>`: menzionare un utente sapendo il suo *user_id*
- `<code></code>`: codice/monospazio
- `<pre></pre>`: codice "preformattato"

**Altri tag potrebbero mandare il bot in crash**

# Funzionamento del bot
_Per poter entrare nel gruppo è consigliato impostare un username_
Il bot si compone di 5 liste:
 - **AdminList** -> gli utenti "amministratori" del bot: hanno gli stessi privilegi degli utenti presenti nella WhiteList ma, inoltre, possono segnalare **manualmente** (o sbloccare, eventualmente) utenti attraverso la chat con il bot in maniera privata.
(Inoltre ricevono avvisi quando gli utenti vengono **bannati** o quando utilizzano **parole vietate**)
 - **WhiteList** -> tutti gli utenti *verificati*: essi possono inviare qualunque cosa (testo, file, ecc.) nei gruppi Mozilla Italia (**NEL RISPETTO DEL REGOLAMENTO**)
 - **BlackList** -> tutti gli utenti *nuovi*, ovvero coloro che non hanno neppure letto il [Regolamento](https://github.com/Sav22999/Guide/blob/master/Mozilla%20Italia/Telegram/regolamento.md): essi NON possono inviare nulla nei gruppi Mozilla Italia (verranno automaticamente eliminati)
 - **TempList** -> tutti gli utenti *non verificati* ma che hanno letto già il Regolamento: possono inviare solamente del testo
 - **SpamList** -> tutti gli utenti *spam* vengono raccolti in questa lista: essi vengono automaticamente cacciati e bannati dai gruppi Mozilla Italia non appena inviano qualcosa

Inoltre sono presenti altre tre liste:
 - **chat_name** -> dove sono racchiusi tutti i gruppi abilitati con il relativo nominativo
 - **parole_vietate** -> dove sono racchiuse tutte le parole/frasi vietate
 - **segnalazione_errori** -> dove vengono raccolte le segnalazioni degli eventuali errori (utilizzata principalmente per gli utenti presenti nella SpamList)

> Le liste valgono per tutti i gruppi Mozilla Italia (da qui MozIta) e sono unificate, quindi un utente presente nella lista *spam* e già cacciato e bannato in un gruppo MozIta, appena invia qualcosa in un altro gruppo MozIta viene *automaticamente* bannato e cacciato anche da quel gruppo. Così come se un utente è già *verificato* in un gruppo lo è anche in tutti gli altri.

Le liste vengono salvate in file *.json*. I file generati sono i seguenti:
 - adminlist.json
 - whitelist.json
 - blacklist.json
 - blacklist_name.json
 - templist.json
 - templist_name.json
 - spamlist.json
 - chat_name.json
 - parole_vietate.json
 - segnalazione_errori.json

Inoltre ogni singolo messaggio viene salvato in un file *.txt* per soli scopi di debug in caso di malfunzionamenti del bot:
 - log_YYYY_MM_DD.txt
Dopo 2 settimana il file viene automaticamente distrutto.

Il bot funziona in maniera differente in base a se si trova in un *gruppo abilitato* o in una *chat privata*.
Infatti solo chi è nella AdminList può interagire, in chat privata, con il bot.

### Primi passi
Non appena si entra in un gruppo MozIta il bot ti inserirà nella lista **BlackList**, quindi non potrai inviare nulla (se lo farai verrà automaticamente eliminata dal bot). Dovrai leggere il Regolamento, dopo fatto ciò passerai automaticamente alla **TempList** in attesa che un qualunque altro utente già verificato confermi la tua identità. Nell'attesa, finché rimarrai nella TempList, potrai inviare messaggi di solo testo (pena il passaggio nella **SpamList**, quindi ban ed eliminazione dai gruppi MozIta).
Non appena, comunque, un utente confermerà la tua identità sarai libero di inviare messaggi di qualsiasi genere nel rispetto del Regolamento.
Il bot, ugualmente, filtrerà i messaggi inviati per verificare che rispettino il Regolamento. In caso non lo fosserò, il bot **automaticamente** prenderà provvedimenti o, in caso il bot non identifichi il messaggio come spam (ma lo è), un nostro amministratore (membro della **AdminList**) provvederà al ban manuale.

`Non vogliamo negare la libertà di espressione, ma bisogna avere rispetto di tutti e seguire delle regole prestabilite, che sono state pensate, scritte e approvate da molti altri precedentemente. Per il bene comune (**Fast for Good**).`

### Lettura regolamento
Quando si preme su "Mostra Regolamento" in automatico viene inviato un messaggio (nella chat del gruppo) con delle regole basi che NON sostituiscono in alcun modo il Regolamento (che, comunque, è breve! Perciò è bene perdere 5 minuti nel leggerlo).
Il bot, in automatico, inserisce il nominativo (user_id) nella **TempList** in attesa che un utente verificato confermi la tua identità. Puoi, comunque, scrivere messaggi di testo per farci capire che, effettivamente, se una persona in carne e ossa :).
Inoltre il messaggio di benvenuto relativo all'utente viene automaticamente eliminato.
Gli Admin possono anche premere su "Blocca utente" che bannerà l'utente in un singolo clic.

Il messaggio viene visualizzato **solo** nel primo gruppo in cui si ci unisce. È possibile (ri)mostrare il messaggio di benvenuto (anche negli altri gruppi) digitando il comando <code>/benvenuto</code>.

### Conferma identità
Tutti gli utenti presenti nella **WhiteList** possono confermare l'identità degli utenti.
Si noti che prima di confermare l'identità è necessario accertarsi che l'utente non sia uno spam:

 - Vedere l'immagine del profilo: è una foto "normale"? O contiene contenuti non accettati?
 - Vedere il nome utente: è un nome utente "normale"? O sono solo alcune lettere messe insieme?
Una volta premuto su "Conferma utente" il messaggio di "Regolamento letto" viene automaticamente eliminato.
Gli Admin possono anche premere su "Blocca utente" che bannerà l'utente in un singolo clic.

> **Se non si è sicuri dell'identità dell'utente *non* bisogna confermare ma, piuttosto, scrivere un messaggio taggando un amministratore e spiegando la situazione. Egli procederà alle verifiche più accurate**.

### Privilegi amministratori (AdminList)
Ecco ciò che si può fare in chat (**solo in chat: i comandi non funzionano nei gruppi**).
 - Gestire utenti:
    - Inserire (manualmente) un utente nella WhiteList: `utente aggiungi *USERID*`

      > utente aggiungi *123456789*
    - Inserire un utente nella SpamList: `utente blocca *USERID*`

      > utente blocca *123456789*
    - Rimuovere un utente dalla SpamList -> bisognerà procedere, poi, manualmente a "sbloccarli" nei singoli gruppi (da "Gestione gruppo"): `utente sblocca *USERID*`

      > utente sblocca *12345678*
- Gestire parole vietate:
    - Mostrare tutte le parole vietate: `parola mostra`

      > parola mostra
    - Aggiungere nuove parole (**tutto in minuscolo**): `parola aggiungi *PAROLA/FRASE*`

      > parola aggiungi *parola/frase di esempio*
    - Rimuovere delle parole (**tutto in minuscolo**): `parola elimina *PAROLA/FRASE*`

      > parola elimina *parola/frase di esempio*
- Gestire gruppi abilitati:
    - Mostrare tutti i gruppi abilitati: `gruppo mostra`

      > gruppo mostra
    - Aggiungere un gruppo: `gruppo aggiungi *USERID GRUPPO* *NOME GRUPPO*`

      > gruppo aggiungi *123456789* *Nome Gruppo di esempio*
    - Rimuove un gruppo `gruppo elimina *USERID*`
    > gruppo elimina *123456789*
- Inviare un messaggio in tutti i gruppo abilitati: `invia messaggio *TESTO MESSAGGIO*`

  > invia messaggio *Testo messaggio di esempio*
- Gestire liste:
    - Mostrare utenti in WhiteList: `lista white mostra`
    - Mostrare utenti in SpamList: `lista spam mostra`
    - Mostrare utenti in BlackList: `lista black mostra`
    - Eliminare utenti in BlackList: `lista black elimina`
    - Mostrare utenti in TempList: `lista temp mostra`
    - Eliminare utenti in TempList: `lista temp elimina`

### Per gli utenti bloccati

Gli utenti *bloccati*, se credono di esserlo stati (bloccati) per errore, possono inviare una segnalazione tramite chat privata dal bot (<code>@mozita_antispam_bot</code>):

1. Digitare <code>/start</code> 
1. Premere sul bottone <code>Segnala il possibile errore</code> del messaggio visualizzato

Gli amministratori effettueranno tutte le dovute verifiche.
**Il messaggio di segnalazione può essere inviato una singola volta.**

In caso ci fosse stato un errore, l’utente interessato verrà sbloccato e potrà unirsi nuovamente ai gruppi di Mozilla Italia. In caso contrario, invece, rimarrà nello stato di *Bloccato/Utente spam* e, quindi, non potrà entrare più nei gruppi comunitari.

# Librerie utilizzate
Elenco delle librerie utilizzate nel codice (Python):
 - Telepot
 - Time
 - Datetime
 - Json
 - Pathlib
