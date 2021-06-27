import cv2
import os
import glob
import re
from PIL import Image
import screenshotMaker as sM

numbers = re.compile(r'(\d+)')                                                                                          #???
def numericalSort(value):                                                                                               #Funzione copiaincollata da internet e data in pasto a sorted() in framesToGif
    parts = numbers.split(value)                                                                                        #per ordinare i file nel modo giusto
    parts[1::2] = map(int, parts[1::2])
    return parts

def pathNav(path):                                                                                                      #Funzione che permette di viaggiare tra le cartelle
    Files = []                                                                                                          #contenute in "Foto" e aprirne i file da modificare.
    for Filename in os.listdir(path):                                                                                   #Mostra il contenuto della cartella, sia
        Files.append(Filename)                                                                                          #Altre directory che file.
        l = len(Files)-1
        print("[{}]".format(l), Filename+", "+("\n"*((l > 0) & (l % 10 == 0))), end="")
    print("\n[-1] Indietro ")
    inp = (int(input("\nSeleziona cartella: ")))
    print()
    if inp < 0:
        return pathNav(path.rpartition('/')[0])                                                                         #Torni alla posizione precedente se scegli di tornare indietro
    else:
        FileName = Files[inp]                                                                                           #Il nome dell'elemento selezionato
        path += "/"+FileName                                                                                            #...Aggiunto al percorso precedente
        if os.path.isdir(path):         #if path è una directory
            return pathNav(path)                                                                                        #Se scegli un'altra directory, esplorerai quella,
        else:                           #if path è un file
            return path, FileName                                                                                       #Se scegli un file, la funzione si chiude, ritornando percorso e nome.
def cleanDir(path):
    for File in glob.glob(path+"/*"):
        os.remove(File)

def colImg(img, pB, pG, pR):                                                                                            #Modifica i valori RGB data la percentuale da applicare ad ognuno
    print("B: {}%  G: {}%  R: {}%".format(pB, pG, pR))
    newImg = img.copy()                                                                                                 #Non posso ritornare img, devo per forza copiare (idk why)
    newImg[:, :, 0] = (newImg[:, :, 0]*pB/100)                                                                          #Modifica un layer alla volta, i primi due valori sono
    newImg[:, :, 1] = (newImg[:, :, 1]*pG/100)                                                                          #le dimensioni (pixel) dell'immagine (quelli con [:])
    newImg[:, :, 2] = (newImg[:, :, 2]*pR/100)
    return newImg

def resizeImg(img, n, interpolation, origS0=0, origS1=0):                                                               #n è il moltiplicatore della dimensione (n = 2 --> dimensioni raddoppiate)
    return cv2.resize(img, ((int(img.shape[1]*n) * int(not(origS0+origS1 > 0))+origS1),                                 #Merdata perchè non mi piace l'if, se orig ha un valore usa quello,
                            (int(img.shape[0]*n) * int(not(origS0+origS1 > 0))+origS0)), interpolation)                 #sennò usa la shape dell'immagine

def createSfoc(img, imgName, nFrames, Mult, dur, nFramesPausa, nFramesPausa2):
    cv2.imwrite("Foto/Temp/gifIn/0.{}".format(imgName.rpartition('.')[2]), img)                                         #Per ovviare al problema del primo frame normale con Mult > 1
    for i in range(nFrames - 1):                                                                                        #Crea frame in cui l'immagine si sfoca pian piano e li salva in Foto/Temp/gifIn
        path = "Foto/Temp/gifIn/{}.{}".format(i, imgName.rpartition('.')[2])
        cv2.imwrite(path, resizeImg(resizeImg(img, 1 / ((i + 2) * Mult), cv2.INTER_LINEAR), 1, cv2.INTER_AREA, img.shape[0], img.shape[1]))
    framesToReverseGif("Foto/Temp/gifIn", imgName, dur, nFrames, nFramesPausa, nFramesPausa2)
def framesToReverseGif(path, imgName, dur, nFrames, nFramesPausa, nFramesPausa2):                                       #Non uso array come per framesToGif perchè ci sono sempre solo 2 valori e
    files = []                                                                                                          #Per non generalizzare e complicatore troppo le cose...Anche se sarebbe forse meglio.
    print("\nFrames creati... \nCreazione della gif in corso...")
    for file in sorted(os.listdir(path), key=numericalSort):                                                            #Salvo i frame in files[] e poi li carico nella gif, assieme alle pause
        files.append(Image.open(path+"/{}".format(file)))                                                               #(i for) ed al reversed array di files, per fare la transizione al contrario.
    files[0].save("Foto/gifOut/{}.gif".format(imgName.split(".")[0]), save_all=True, append_images=[*files, *[files[len(files) - 1] for i in range(nFramesPausa)], *reversed(files[1:nFrames - 1]), *[files[0] for i in range(nFramesPausa2)]], duration=dur, loop=0)

#Per creazione frame di più transizioni simultanee, da testare per singole immagini. <-- Rimozione array reversed perchè, per generalizzare, creati frame al contrario. Aggiungere if...? Nah.
#globFrameCounter = 0                                                                                                   #Per tenere traccia dell'enumerazione dei frame quando si usano più di 2 immagini
def frameCross(actFrame, nFrames, newImg, img1, img2):
    m2 = actFrame / (nFrames - 1)  # Essenzialmente la funzione per cambiare i colori e poi
    m1 = 1 - m2  # Quella per sfocare l'immagine
    newImg[:, :, 0] = (img1[:, :, 0]) * m1 + (img2[:, :, 0]) * m2
    newImg[:, :, 1] = (img1[:, :, 1]) * m1 + (img2[:, :, 1]) * m2
    newImg[:, :, 2] = (img1[:, :, 2]) * m1 + (img2[:, :, 2]) * m2
def createCrossfading(globFrameCounter, img1, img2, imgName, nFrames):
    newImg = img1.copy()
    a = 1*(globFrameCounter > 0)
    for actFrame in range(a, nFrames):                                                                                  #Da 0 a nF -1, quindi nF volte
        frameCross(actFrame, nFrames, newImg, img1, img2)
        #m2 = actFrame / (nFrames - 1)                                                                                   #Proporzine di m1 ed m2, ovvero la proporzione del colore di img1 e img2
        #m1 = 1 - m2
        #newImg[:, :, 0] = (img1[:, :, 0])*m1 + (img2[:, :, 0])*m2                                                       #Calcolo colori dell'immagine che andrà poi salvata
        #newImg[:, :, 1] = (img1[:, :, 1])*m1 + (img2[:, :, 1])*m2
        #newImg[:, :, 2] = (img1[:, :, 2])*m1 + (img2[:, :, 2])*m2
        path = "Foto/Temp/gifIn/{}.{}".format(str(actFrame - a + globFrameCounter), imgName.rpartition('.')[2])
        cv2.imwrite(path, newImg)
    return nFrames-a                                                                                                    #Lo uso per incrementare globFrameCounter (non riesco a fare variabile globale)
def createSfocCross(globFrameCounter, img1, img2, imgName, nFrames, Mult):
    newImg = img1.copy()
    newImgShapes = [newImg.shape[0], newImg.shape[1]]                                                                   #Setto le dimensioni originali per riutilizzarle
    a = 1 * (globFrameCounter > 0)
    sfocInd = a
    for actFrame in range(a, nFrames):
        frameCross(actFrame, nFrames, newImg, img1, img2)
        #m2 = actFrame / (nFrames - 1)  # Essenzialmente la funzione per cambiare i colori e poi
        #m1 = 1 - m2  # Quella per sfocare l'immagine
        #newImg[:, :, 0] = (img1[:, :, 0]) * m1 + (img2[:, :, 0]) * m2
        #newImg[:, :, 1] = (img1[:, :, 1]) * m1 + (img2[:, :, 1]) * m2
        #newImg[:, :, 2] = (img1[:, :, 2]) * m1 + (img2[:, :, 2]) * m2
        path = "Foto/Temp/gifIn/{}.{}".format(str(actFrame - a + globFrameCounter), imgName.rpartition('.')[2])

        # Redim di newImg
        actFrame -= a
        #newImgShapes = [newImg.shape[0], newImg.shape[1]]
        MultEff = 1 if ((actFrame == a == 0) or actFrame == nFrames - 1 - a) else Mult                                  #Per ovviare al problema dei primi e ultimi frame sfocati, controllo il moltiplicatore
        cv2.imwrite(path, resizeImg(resizeImg(newImg, 1 / ((sfocInd + 1) * MultEff), cv2.INTER_LINEAR), 1, cv2.INTER_AREA, newImgShapes[0], newImgShapes[1]))
        nFramesMezz = int(nFrames / 2)                                                                                  #Blocco che regola sfocInd, salendo fino a metà transizione e poi scendendo.
        if actFrame + a < (nFramesMezz - (not (nFrames % 2))):                                                          #Fa da 0 a nF/2 a 0, partendo da 1 dal secondo ciclo per evitare frame duplicati.
            sfocInd += 1
        elif (nFrames % 2) or (actFrame + a > (nFramesMezz - (not (nFrames % 2)))):
            sfocInd -= 1
        # Redim di newImg

    return nFrames - a
def framesToGif(path, imgName, dur, Divisore, *nFramesPausaAndTransizione):#, *nFramesTransizione):  #Array unico per entrambi, variabile per differenziarli(valore lunghezza uno per prendere valori dell'altro, unirli prima di passarli)
    print("\nFrames creati... ")        #nFramesPausa --> nFramesPausaAndTransizione senza in [ind] l'uso di Divisore.
    files = []                          #nFramesTransizione --> nFramesPausaAndTransizione con [ind + Divisore].
    indP = TransPass = i = 0
    framesGif = []
    for file in sorted(os.listdir(path), key=numericalSort):                                                            #Sorta i file in ordine giusto e ci cicla
        files.append(Image.open(path+"/{}".format(file)))
        framesGif.append(files[i])
        if i+1-TransPass+indP == nFramesPausaAndTransizione[indP+Divisore]:  #nFramesTransizione                        #Se siamo al file in cui dovrebbe esserci la pausa, aumenta il TransPass,
            TransPass += nFramesPausaAndTransizione[indP+Divisore]           #nFramesTransizione                        #Che serve a fare in modo che la i ricominci da "0" (i-TransPass) al prossimo giro,
            for j in range(nFramesPausaAndTransizione[indP]):                #nFramesPausa                              #si aggiunge IndP per contare i frame duplicati scartati quando si concatenano le transizioni,   <-- Questo commento
                framesGif.append(files[i])                                                                              #si mettono i frame di pausa(uguali a quello attuale) in frameGif.                                                ^
            indP += 1;                                                                                                  #Si aumenta indP per valore successivo di nFramesPausa e nFramesTransizione e frame scartati del commento sopra   ^
        i += 1
    print("Preparazione Gif... ")
    files[0].save("Foto/gifOut/{}.gif".format(imgName.split(".")[0]), save_all=True, append_images=framesGif[:len(framesGif)-1], duration=dur, loop=0) #framesGif[:len(framesGif)-1] per levare l'ultimo frame, che è uguale al primo

def blocconeSfocOpSfocCross(SfocTrueSfocCrossFalse): #In teoria andrebbe passato imgs ma lo usa come fosse globale... Quindi ok
    globFrameCounter = 0
    nImmagini = int(input("Numero immagini (senza contare quella già scelta): "))
    print("Le immagini verranno automaticamente ridimensionate se di dimensioni differenti. ")
                                                                                                                        #Funzione che sostituisce il doppio bloccone negli if di selezione ^^
    #Creazione frame della gif, preparazione dati per la creazione della gif... Funziona
    nFramesPausa = []
    nFramesTransizione = []
    ricI = 0
    for i in range(nImmagini):                                                                                          #imgs[0] contiene già img1
        print("\nSeleziona un'altra immagine. \n")
        path, _ = pathNav("Foto")                                                                                       #Chiedo immagine successiva
        print("\nTransizione da {} a {}: \n".format(i, i + 1))                                                          #Mostro transizione che si sta per fare
        imgs.append(resizeImg(cv2.imread(path), 1, cv2.INTER_CUBIC, imgs[0].shape[0], imgs[0].shape[1]))                #imgs[i+1]=img2. Ridimens con imgs[0] che ha dimens originali. Andava bene anche imgs[i].
        nFramesTransizione.append(int(input("Durata transizione (frames): ")))                                          #Chiedo quanti frame durerà il ciclo.
        nFramesPausa.append(int(input("Pausa su {} (frames): ".format(i + 1))))                                         #Chiedo quanti frame uguali mettere alla fine del ciclo.
        if SfocTrueSfocCrossFalse:
            globFrameCounter += createCrossfading(globFrameCounter, imgs[i], imgs[i + 1], imgName, nFramesTransizione[i]) #Creo la transizione tra imgs[i] e imgs[i+1]. globFrameCounter x codice enumerativo funzione crossFading
        else:
            globFrameCounter += createSfocCross(globFrameCounter, imgs[i], imgs[i + 1], imgName, nFramesTransizione[i], int(input("Moltiplicatore: ")))
        ricI += 1                                                                                                       #Serve essenzialmente per tenresi i fuori dal ciclo e usarla nella riga sotto (imgs[ricI]). Solo qui.
    #Blocco extra brutto che serve a gestire interazione primo/ultimo frame. Per comodità messo qui e non implementato nel ciclo. Fa parte della preparazione dati per la gif.
    print("\nTransizione da {} a 0: \n".format(nImmagini))
    nFramesTransizione.append(int(input("Durata transizione (frames): ")))
    nFramesPausa.append(int(input("Pausa su 0 (frames): ")))
    if SfocTrueSfocCrossFalse:
        createCrossfading(globFrameCounter, imgs[ricI], imgs[0], imgName, nFramesTransizione[ricI])                     #Stessa roba di prima ma senza globFrameCounter, dato che dopo non serve più
    else:
        createSfocCross(globFrameCounter, imgs[ricI], imgs[0], imgName, nFramesTransizione[ricI], int(input("Moltiplicatore: ")))

    #Unione frames in gif... Funziona, ma framesToGif va ottimizzato
    Divisore = len(nFramesPausa)                                                                                        #Serve per differenziare i due array dentro la funzione dato che
    nFramesPausaAndTransizione = [*nFramesPausa, *nFramesTransizione]                                                   #A quanto pare non posso passare due array diversi come parametro...
    framesToGif("Foto/Temp/gifIn", imgName, int(input("Durata frames (ms): ")), Divisore, *nFramesPausaAndTransizione)  #Creo la gif

#DONE: Inserire frame di pausa tra "salita" e "discesa" in gif di sfocatura e crossfading
#DONE: Crossfading con n immagini
#DONE: Relativo al punto sopra, aggiungere crossfading tra l'ultima e la prima immagine, per chiudere il ciclo
#DONE: Crosffading con sfocatura
#DONE: Generalizzare funzione sfoc e cross per singoli frame da utilizzare in entrambe le orbweorbwoe robe

#TODO kinda [Non funziona bene, forse perchè i frame sono solo simili...]: Rimozione frame duplicati nelle gif di sfocatura  #TODO: Implementarla alla creazione e non all'unione dei frame
#TODO: Implementare una creazione di gif senza salvare frame su disco (senza Image.open)...
#   Forse è meglio così per non far esplodere la ram? O esplode comunque dato che poi li carica? Dipende da come viene creata la gif... -- iFunny.co/Emre
#TODO: Importare gif e modificarne risoluzione e colore
#TODO: Crossfading tra gif, crossfading tra stillImg e gif

#Main                                                                                                                   #Shape: (heigth, width, layers). Il colore è invertito. BGR, non RGB.
try:
    cleanDir("Foto/Temp/gifIn")                                                                                         #Pulisco i frame creati in precedenza.
    path, imgName = pathNav("Foto")                                                                                     #Scelgo l'immagine con cui lavorare.
    imgs = []
    imgs.append(cv2.imread(path))                                                                                       #Inserisco l'immagine al percorso scelto nell'array che userò dopo.
    print("Stai modificando: {} \nDimensioni dell'immagine: {} x {} \nShape: {} \n".format(imgName, imgs[0].shape[1], imgs[0].shape[0], imgs[0].shape))
    inp = int(input("[-1] Elimina il file \n[0] Ridimensionare l'immagine \n[1] Modifica colore \n[2] Crea gif con sfocatura \n[3] Crea gif crossfading \n[4] Crea gif crossfading con sfocatura \n\nScegliere un'opzione: "))
    if inp == -1:
        os.remove(path)
    elif inp == 0:
        if int(input("\n[0] Moltiplica dimensioni \n[1] Assegna nuove dimensioni \n\nScegli un'opzione: ")):
            cv2.imwrite("Foto/Ridimensionate/red{}".format(imgName), resizeImg(imgs[0], 1, cv2.INTER_CUBIC, int(input("\nNuova altezza: ")), int(input("Nuova larghezza: "))))
        else:
            cv2.imwrite("Foto/Ridimensionate/red{}".format(imgName), resizeImg(imgs[0], float(input("Moltiplicatore dimensioni: ")), cv2.INTER_CUBIC))
    elif inp == 1:
        cv2.imwrite("Foto/Colorate/col{}".format(imgName), colImg(imgs[0], float(input("Percentuale Blu: ")), float(input("Percentuale Verde: ")), float(input("Percentuale Rosso: ")))) #B G R
    elif inp == 2:
        #Da rivedere causa funzioni sminchiate per far funzionare il crossfading... Questa riga va bene, rivedere la funzione, in particolare framesToGif. (Alla fine fatta funzione a parte... Forse terrò così)
        createSfoc(imgs[0], imgName, int(input("\nDurata transizione (frames): ")), int(input("Moltiplicatore: ")), int(input("Durata frames (ms): ")), int(input("Pausa su immagine sfocata (frames): ")), int(input("Pausa su immagine normale (frames): ")))
    elif inp == 3:
        blocconeSfocOpSfocCross(True)
        '''
        nImmagini = int(input("Numero immagini (senza contare quella già scelta): "))
        print("Le immagini verranno automaticamente ridimensionate se di dimensioni differenti. ")

        #Creazione frame della gif, preparazione dati per la creazione della gif... Funziona
        nFramesPausa = []
        nFramesTransizione = []
        ricI = 0
        for i in range(nImmagini):          #imgs[0] contiene già img1
            print("\nSeleziona un'altra immagine. \n")
            path, _ = pathNav("Foto")                                                                                   #Chiedo immagine successiva
            print("\nTransizione da {} a {}: \n".format(i, i+1))                                                        #Mostro transizione che si sta per fare
            imgs.append(resizeImg(cv2.imread(path), 1, cv2.INTER_CUBIC, imgs[0].shape[0], imgs[0].shape[1]))            #imgs[i+1]=img2. Ridimens con imgs[0] che ha dimens originali. Andava bene anche imgs[i].
            nFramesTransizione.append(int(input("Durata transizione (frames): ")))                                      #Chiedo quanti frame durerà il ciclo.
            nFramesPausa.append(int(input("Pausa su {} (frames): ".format(i+1))))                                       #Chiedo quanti frame uguali mettere alla fine del ciclo.
            globFrameCounter += createCrossfading(globFrameCounter, imgs[i], imgs[i + 1], imgName, nFramesTransizione[i])  #Creo la transizione tra imgs[i] e imgs[i+1]. globFrameCounter x codice enumerativo funzione crossFading
            ricI += 1                                                                                                   #Serve essenzialmente per tenresi i fuori dal ciclo e usarla nella riga sotto (imgs[ricI]). Solo qui.
        #Blocco extra brutto che serve a gestire interazione primo/ultimo frame. Per comodità messo qui e non implementato nel ciclo. Fa parte della preparazione dati per la gif.
        print("\nTransizione da {} a 0: \n".format(nImmagini))
        nFramesTransizione.append(int(input("Durata transizione (frames): ")))
        nFramesPausa.append(int(input("Pausa su 0 (frames): ")))
        createCrossfading(globFrameCounter, imgs[ricI], imgs[0], imgName, nFramesTransizione[ricI])                     #Stessa roba di prima ma senza globFrameCounter, dato che dopo non serve più

        #Unione frames in gif... Funziona, ma framesToGif va ottimizzato
        Divisore = len(nFramesPausa)                                                                                    #Serve per differenziare i due array dentro la funzione dato che
        nFramesPausaAndTransizione = [*nFramesPausa, *nFramesTransizione]                                               #A quanto pare non posso passare due array diversi come parametro...
        framesToGif("Foto/Temp/gifIn", imgName, int(input("Durata frames (ms): ")), Divisore, *nFramesPausaAndTransizione) #Creo la gif
        '''
    elif inp == 4:
        blocconeSfocOpSfocCross(False)
        '''
        nImmagini = int(input("Numero immagini (senza contare quella già scelta): "))
        print("Le immagini verranno automaticamente ridimensionate se di dimensioni differenti. ")

        #Creazione frame della gif, preparazione dati per la creazione della gif... Funziona
        nFramesPausa = []
        nFramesTransizione = []
        ricI = 0
        for i in range(nImmagini):          #imgs[0] contiene già img1
            print("\nSeleziona un'altra immagine. \n")
            path, _ = pathNav("Foto")                                                                                   #Chiedo immagine successiva
            print("\nTransizione da {} a {}: \n".format(i, i+1))                                                        #Mostro transizione che si sta per fare
            imgs.append(resizeImg(cv2.imread(path), 1, cv2.INTER_CUBIC, imgs[0].shape[0], imgs[0].shape[1]))            #imgs[i+1]=img2. Ridimens con imgs[0] che ha dimens originali. Andava bene anche imgs[i].
            nFramesTransizione.append(int(input("Durata transizione (frames): ")))                                      #Chiedo quanti frame durerà il ciclo.
            nFramesPausa.append(int(input("Pausa su {} (frames): ".format(i+1))))                                       #Chiedo quanti frame uguali mettere alla fine del ciclo.
            globFrameCounter += createSfocCross(globFrameCounter, imgs[i], imgs[i + 1], imgName, nFramesTransizione[i], int(input("Moltiplicatore: ")))  #Creo la transizione tra imgs[i] e imgs[i+1]. globFrameCounter x codice enumerativo funzione crossFading
            ricI += 1                                                                                                   #Serve essenzialmente per tenresi i fuori dal ciclo e usarla nella riga sotto (imgs[ricI]). Solo qui.
        #Blocco extra brutto che serve a gestire interazione primo/ultimo frame. Per comodità messo qui e non implementato nel ciclo. Fa parte della preparazione dati per la gif.
        print("\nTransizione da {} a 0: \n".format(nImmagini))
        nFramesTransizione.append(int(input("Durata transizione (frames): ")))
        nFramesPausa.append(int(input("Pausa su 0 (frames): ")))
        createSfocCross(globFrameCounter, imgs[ricI], imgs[0], imgName, nFramesTransizione[ricI], int(input("Moltiplicatore: "))) #Stessa roba di prima ma senza globFrameCounter, dato che dopo non serve più

        #Unione frames in gif... Funziona, ma framesToGif va ottimizzato
        Divisore = len(nFramesPausa)                                                                                    #Serve per differenziare i due array dentro la funzione dato che
        nFramesPausaAndTransizione = [*nFramesPausa, *nFramesTransizione]                                               #A quanto pare non posso passare due array diversi come parametro...
        framesToGif("Foto/Temp/gifIn", imgName, int(input("Durata frames (ms): ")), Divisore, *nFramesPausaAndTransizione) #Creo la gif
        '''
    else:
        print("\nOpzione non esistente. ")
    print("\nOperazione eseguita con successo. ")
except Exception as e:
    print("\nOperazione non riuscita:", str(e))

