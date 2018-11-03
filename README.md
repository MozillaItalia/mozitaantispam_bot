# mozitahub_bot
Questo è il repository della beta del nuovo bot antispam dei gruppi ufficiali della comunità di Mozilla Italia su Telegram.


# informazioni utili
Questo progetto è una beta del nuovo bot antispam per i gruppi di Mozilla Italia (su Telegram).
È sviluppato in Python e per funzionare necessita di essere avviato su un server (o su un computer).
Per segnalare errori aprire un nuovo ticket (si prega di aprire un ticket per ogni errore/idee/bug/ecc, poiché raggrupparli tutti in un unico issue è dispersivo).
Il token per accedere al bot diretto è nascosto.

Grazie a tutti.

# funzionamento del bot (idea iniziale)
L'idea di questo bot è realizzare una **whitelist** di tutti gli utenti **verificati** (=utenti NON spam) che possono inviare nel gruppo file di qualsiasi tipo (sempre nel rispetto del regolamente, altrimenti si viene ugualmente bannati manualmente).
Consiste anche in una blacklist, nella quale vengono inseriti tutti gli utenti non ancora verificati (=utenti ancora non verificati). Questi utenti non possono, infatti, inviare nessun file e neppure testo finché non vengono verificati correttamente.
E, infine, consiste in una templist, nella quale vengono inseriti tutti gli utente non ancora verificati ma che hanno letto il regolamente. Pertanto questi utenti possono scrivere SOLO del testo (no link!).
### Come si passa da utente non verificato a verificato?
Molto semplicemente, quando si entra nel gruppo di Mozilla Italia, si riceve un messaggio dal bot che avvisa di "**Leggere il regolamento**"<sup>#1</sup> per essere abilitato a scrivere del testo. Una volta letto il regolamento si passa (dalla blacklist) alla "templist".
Tutti gli altri utenti "verificati" possono abilitare gli utenti presenti nella **templist**.
In questo modo si genera una specie di algortimo di fiducia, ovvero tutti gli utenti verificati possono verificare altri utenti, per non pesare solo sulle spalle dei moderatori.
Ovviamente, prima di verificare un utente, bisogna prestare attenzione che, effettivamente, sia un utente non-spam.

<sup>#1</sup> probabilmente presente separatamente, in una pagina web, così da non mostrare ogni volta il regolamento sul gruppo e non riempirlo di messaggi inutili/superflui
