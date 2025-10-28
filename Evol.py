import pygame               #initialisation
import time
import pandas as pd         #imports excels
import openpyxl
import tkinter as tk
from tkinter import ttk
import random
from random import randint

# Configuration initiale du fichier Excel
file_path = r"D:\PRIVE\programmation\EVOL\graphique.xlsx"
wb = openpyxl.load_workbook(file_path)
feuille = wb["Sheet1"]

"""----------------------------------------------------paramètres----------------------------------------------------------------""" 
#TAILLE ET DIMENSIONS
fenetre_X = 1550     #largeur de la fenêtre (900)   1550,800 pour le plein écran
fenetre_Y = 880     #hauteur de la fenêtre (780)
bordure_X = 1300     #largeur de la bordure (800)
bordure_Y = 800     #hauteur de la bordure (700)
objets_petits = True  #taille des objets (divisé par 2 si True)

#CONDITIONS DE DÉPART
pions_au_depart = True          #la simulation démarre dès le départ ? (si non, appuyer sur espace pour lancer la simulation)

#MUTATIONS
mutations = True               #mutations activées ?
mutations_de_type = True       #mutations de type activées ?
rareté_des_mutations = 5        # une chance sur le nombre de muter les caractères
rareté_des_mutations_type = 20  # une chance sur le nombre de changer de type

#PREDATEURS
nb_predateurs = 10               #nombre de prédateurs au départ
ressources_predateurs = 6000     #ressources de base des prédateurs
delai_attaque_predateurs = 20    #délai entre deux attaques des prédateurs
delai_predateurs = 50            #délai entre deux apparitions de prédateurs
malus_de_rencontre = True        #malus de rencontre des prédateurs (si True, les prédateurs ont un malus s'ils se rencontrent sans qu'un des deux ne soit prêt pour nouvelle reproduction de prédateur)
taux_mortalité = 6               #taux de mortalité des predateurs (1/... du tuer le pion)
portee_predateurs = 100          #portée de base des prédateurs
vitesse_predateurs = 2           #vitesse de base des prédateurs

#PIONS
nb_pions = 100                    #nombre de pions au départ
vitesse_pions = 1                #vitesse de base des pions
portee_pions = 80                #portée de base des pions
ressources_pions = 6000          #ressources de base (6000 est pas mal)
recherche_de_nourriture = 80     #pourcentage de ressources nécessaires pour partir à la recherche de nourriture
fuite = True                     #fuit-il les prédateurs ? (si True les deux types fuient)
fuite_bob = True                 #les pions verts fuient-ils les prédateurs ?
fuite_bod = True                 #les pions oranges fuient-ils les prédateurs ?
pions_apparaissent = 0           #pions qui apparaissent "magiquement" (1/...) (0 = Aucun)
ressources_replication = "70%"   #nombre de ressources nécessaires pour se repliquer, format : "20%" ou "20" pour la valeur brute
delai_pions = 1000                #délai entre deux apparitions de pions

#AVANTAGES pions
vitesse_orange = 0               #bonus de vitesse des pions oranges (en %)
vitesse_vert = 50                 #bonus de vitesse des pions verts (en %)
ressources_vert = 0              #bonus de ressources des pions verts
ressources_orange = 400            #bonus de ressources des pions oranges
portee_vert = 20                  #bonus de portée des pions verts
portee_orange = 0                #bonus de portée des pions oranges
proportion_vert = 50             #proportion de pions verts
proportion_orange = 50           #proportion de pions oranges

#EVENEMENTS ET APPARITIONS
potions = False                   #potions activées ? (augmente les statistiques des pions)
maisons = 0                       #nombre de maisons
fond_multicolore = True           #fond multicolore ?
ressources_apparaissent = 6       #ressources qui apparaissent magiquement (.../100)
disponibilite_ressources = 20     #temps avant que les ressources ne disparaissent (en secondes)
max_ressources = 30               #nombre maximum de ressources sur la carte
croissance_log = False            #pions se multiplient quand ils sont seuls (effectif seulement sur l'apparition "magique des pions")

#DIVERS
FPS = 20                         #nombre de frames par seconde

"""----------------------------------------------------------------------------------------------------------------------------------------------------------------""" 
dimensions_changées = False             #PARAMETRES AUTOMATIQUES

if fuite_bob == True or fuite_bod == True:
    fuite = True

#disponibilite des ressources mise en secondes (mltiplié par le FPS)
disponibilite_ressources *= FPS

#ressources de replication
if ressources_replication[-1] == "%":
    ressources_replication = ressources_pions * int(ressources_replication[:-1])/100
else:
    try:
        ressources_replication = int(ressources_replication[:-1])
    except:
        ressources_replication = ressources_pions * 0.5
        print("Erreur : ressources_replication doit être un nombre entier ou un pourcentage (ex : 20% ou 20)")

#dimmensions modifiées ?
if bordure_X > 800 or bordure_Y > 700:
    dimensions_changées = True

#recherche de nourriture en % éventuellement corrigé
if recherche_de_nourriture > 100:
    recherche_de_nourriture = 100
elif recherche_de_nourriture < 0:
    recherche_de_nourriture = 0

#ajustement des proportions
if proportion_vert != 50 and proportion_orange == 50:
    proportion_orange = 100 - proportion_vert
elif proportion_orange != 50 and proportion_vert == 50:
    proportion_vert = 100 - proportion_orange

if proportion_vert + proportion_orange != 100:
    proportion_vert = 50
    proportion_orange = 50

if objets_petits == True:                       #traitement des paramètres manuels (taille)
    taille_objets = 2
else:
    taille_objets = 1

# Initialisation de Pygame après la fermeture de la fenêtre Tkinter
pygame.init()
#dimensions de l'écran : 1550,800 pour le plein écran
borderup = (0,0)                                        #coin supérieur gauche de la bordure
borderdown = (bordure_X,bordure_Y)                      #coin inférieur droit de la bordure
Épaisseur = bordure_X / 200                             #épaisseur de la bordure

#listes pour l'apparition aléatoire de ressources
list_apparition_ressources = []
for i in range (0,ressources_apparaissent):
    list_apparition_ressources.append(i)

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        if dimensions_changées:
            self.speed = 20
        else:
            self.speed = 10
    
    def move_left(self):
        self.x -= self.speed
    
    def move_right(self):
        self.x += self.speed
    
    def move_up(self):
        self.y -= self.speed
    
    def move_down(self):
        self.y += self.speed

# Création d'une instance globale de la caméra
camera = Camera()
screen = pygame.display.set_mode((fenetre_X,fenetre_Y))


class pion :
    def __init__ (self,x,y,nom=None):
        if nom == None:
            nom = "Bob" if randint(0,1) == 1 else "Bod"
        if (nom == "Bod"):                     #choix entre 2 pions
            self.image = pygame.image.load(r"D:\PRIVE\programmation\EVOL\Bod.png")#.convert()    #C:\PRIVE\programmation\Evol\
            self.image = pygame.transform.scale(self.image,(int(self.image.get_width()/int(taille_objets*2)), int(self.image.get_height()/int(taille_objets*2))))     #réduction de taille
            self.nom = "Bod"                #orange  
        else:
            self.image = pygame.image.load(r"D:\PRIVE\programmation\EVOL\Bob.png")#.convert()     #C:\PRIVE\programmation\Evol\
            self.image = pygame.transform.scale(self.image,(int(self.image.get_width()/int(taille_objets*2)), int(self.image.get_height()/int(taille_objets*2))))
            self.nom = "Bob"                #vert

        self.rect = self.image.get_rect()       #propriétés du pion
        self.moving = False                     #bouge t-il
        self.cache = True                       #est-il caché                          
        self.target_x = 0                       #coordonées x visées actuellement
        self.target_y = 0                       #coordonées y visées actuellement
        self.move_time = 0                      #temps nécéssaire au mouvement
        self.stepsx = 0                         #distance x jusqu'au point
        self.stepsy = 0                         #distance y jusqu'au point
        self.rect.x = x                         #coordonnées x du haut-gaiche du pion
        self.rect.y = y                         #coordonnées y du haut-gaiche du pion
        
        # Coordonnées flottantes pour mouvement précis
        self.pos_x = float(x)                   #position flottante x
        self.pos_y = float(y)                   #position flottante y

        # Calcul des centres des pions
        self.centre_x = self.rect.x + self.image.get_width()/2
        self.centre_y = self.rect.y + self.image.get_height()/2

        self.ressource = ressources_pions
        self.ressource_base = ressources_pions
        self.portee = 70 if not objets_petits else 35
        self.vitesse = 1
        if self.nom == "Bob":
            self.portee += portee_vert
            self.vitesse += vitesse_vert/100 * self.vitesse
            self.ressource += ressources_vert
        else:
            self.portee += portee_orange
            self.vitesse += vitesse_orange/100 * self.vitesse
            self.ressource += ressources_orange

        pion.R_proche = [0,100000000]                       #ressource la plus proche et distance
        self.recherche_nourriture = False
        self.fuite = False
        self.delai = 0

    def TP(self,x,y):                           #TP à une position
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

    def Goto(self, x, y):
        self.moving = True
        self.target_x = x       #coordonnées visées
        self.target_y = y
        # Calculer le vecteur de direction
        dx = self.target_x - self.pos_x
        dy = self.target_y - self.pos_y
        distance_totale = (dx**2 + dy**2)**0.5
        
        # Normalisation du vecteur
        if distance_totale > 0:
            # Vecteur normalisé, on a un ratio des déplacements x et y sur le total de la distance
            dx_norm = dx / distance_totale
            dy_norm = dy / distance_totale
            
            # Appliquer la vitesse
            self.stepsx = dx_norm * self.vitesse
            self.stepsy = dy_norm * self.vitesse
        else:
            self.stepsx = 0
            self.stepsy = 0

        # Vitesse minimale globale au lieu de forcer chaque axe individuellement
        vitesse_actuelle = (self.stepsx**2 + self.stepsy**2)**0.5       #vitesse (distance) de laquelle le pion bouge actuellement
        min_vitesse = 0.6 if objets_petits else 0.3
        
        if vitesse_actuelle > 0 and vitesse_actuelle < min_vitesse:
            # Augmenter proportionnellement les deux composantes pour atteindre la vitesse minimale (si la vitesse actuelle est inférieure à la vitesse minimale)
            facteur = min_vitesse / vitesse_actuelle
            self.stepsx *= facteur
            self.stepsy *= facteur

    def update(self):
        if self.moving:
            distance_avant = ((self.target_x - self.pos_x)**2 + (self.target_y - self.pos_y)**2)**0.5
            self.pos_x += self.stepsx               #mise à jour des coordonnées flottantes
            self.pos_y += self.stepsy
            self.rect.x = int(self.pos_x)           #conversion en entiers pour l'affichage
            self.rect.y = int(self.pos_y)
            self.centre_x = self.rect.x + self.image.get_width()/2          # Mise à jour du centre
            self.centre_y = self.rect.y + self.image.get_height()/2
            distance_apres = ((self.target_x - self.pos_x)**2 + (self.target_y - self.pos_y)**2)**0.5
            

            # Arrêt du mouvement si on est assez proche de la cible ou si on s'en éloigne
            if distance_apres < 5:          #si on est proche c'est bon
                self.moving = False
                self.TP(self.target_x,self.target_y)
            if distance_apres > distance_avant and distance_apres > 5:       #si on s'éloigne on y retourne avec un autre Goto
                self.Goto(self.target_x,self.target_y)

class predateur :
    def __init__ (self,x,y):
        self.image = pygame.image.load(r"D:\PRIVE\programmation\EVOL\predateur.png")#.convert()    #C:\PRIVE\programmation\Evol\
        self.image = pygame.transform.scale(self.image,(int(self.image.get_width()/int(taille_objets*4)), int(self.image.get_height()/int(taille_objets*4))))

        self.rect = self.image.get_rect()       #propriétés du pion
        self.moving = False                     #bouge t-il
        self.target_x = 0                       #coordonées x visées actuellement
        self.target_y = 0                       #coordonées y visées actuellement
        self.move_time = 0                      #temps nécéssaire au mouvement
        self.stepsx = 0                         #distance x jusqu'au point
        self.stepsy = 0                         #distance y jusqu'au point
        self.rect.x = x                         #coordonnées x du haut-gauche du predateur
        self.rect.y = y                         #coordonnées y du haut-gauche du predateur

        # Coordonnées flottantes pour mouvement précis du predateur
        self.pos_x = float(x)                   #position flottante x
        self.pos_y = float(y)                   #position flottante y

        # Calcul des centres des predateurs
        self.centre_x = self.rect.x + self.image.get_width()/2
        self.centre_y = self.rect.y + self.image.get_height()/2

        self.ressource = ressources_predateurs
        self.ressource_base = ressources_predateurs
        self.portee = portee_predateurs
        self.vitesse = vitesse_predateurs
        self.delai_attaque = delai_attaque_predateurs
        self.delai = 0
        self.proie = 0               # = Rproche pour les pions, pions a proximité
        self.chasse = False          #chasse t-il ?

        # DEPLACEMENT DES PREDATEURS

    def TP(self,x,y):                           #TP à une position
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

    def Goto(self, x, y):
        self.moving = True
        self.target_x = x       #coordonnées visées
        self.target_y = y
        # Calculer le vecteur de direction
        dx = self.target_x - self.pos_x
        dy = self.target_y - self.pos_y
        distance_totale = (dx**2 + dy**2)**0.5
        
        # Normalisation du vecteur
        if distance_totale > 0:
            # Vecteur normalisé (direction unitaire)
            dx_norm = dx / distance_totale
            dy_norm = dy / distance_totale
            
            # Appliquer la vitesse constante
            self.stepsx = dx_norm * self.vitesse
            self.stepsy = dy_norm * self.vitesse
        else:
            self.stepsx = 0
            self.stepsy = 0
        
        # Vitesse minimale globale au lieu de forcer chaque axe individuellement
        vitesse_actuelle = (self.stepsx**2 + self.stepsy**2)**0.5
        min_vitesse = 0.6 if objets_petits else 0.3
        
        if vitesse_actuelle > 0 and vitesse_actuelle < min_vitesse:
            # Augmenter proportionnellement les deux composantes pour atteindre la vitesse minimale
            facteur = min_vitesse / vitesse_actuelle
            self.stepsx *= facteur
            self.stepsy *= facteur

    def update(self):
        if self.moving:
            distance_avant = ((self.target_x - self.pos_x)**2 + (self.target_y - self.pos_y)**2)**0.5
            self.pos_x += self.stepsx               #mise à jour des coordonnées flottantes
            self.pos_y += self.stepsy
            self.rect.x = int(self.pos_x)           #conversion en entiers pour l'affichage
            self.rect.y = int(self.pos_y)
            self.centre_x = self.rect.x + self.image.get_width()/2          # Mise à jour du centre
            self.centre_y = self.rect.y + self.image.get_height()/2
            distance_apres = ((self.target_x - self.pos_x)**2 + (self.target_y - self.pos_y)**2)**0.5
            # Arrêt du mouvement si on est assez proche de la cible ou si on s'en éloigne
            if distance_apres < 5:          #si on est proche c'est bon
                self.moving = False
                self.TP(self.target_x,self.target_y)
            if distance_apres > distance_avant and distance_apres > 5:       #si on s'éloigne on y retourne avec un autre Goto
                self.Goto(self.target_x,self.target_y)

class text :
    def __init__ (self, texte, police, couleur, taille,Posx,Posy):
        self.ecrit = texte          #texte réel
        self.police = police        #police
        self.taille = taille        #taille
        self.font = pygame.font.Font(self.police,self.taille)
        self.x = Posx
        self.y = Posy
        self.texte = self.font.render(self.ecrit, True, couleur)

class decor :
    def __init__ (self,x,y,type):
        if type == "maison":
            self.image = pygame.image.load(r"D:\PRIVE\programmation\EVOL\decor.png")#.convert()          #image    #C:\PRIVE\programmation\Evol\
            self.image = pygame.transform.scale(self.image,(int(self.image.get_width()/int(taille_objets*2)), int(self.image.get_height()/int(taille_objets*2))))     #réduite par 2
            self.type = "maison"
        elif type == "ressource":
            self.image = pygame.image.load(r"D:\PRIVE\programmation\EVOL\Ressource.png")#.convert()          #image    #C:\PRIVE\programmation\Evol\
            self.image = pygame.transform.scale(self.image,(int(self.image.get_width()/int(taille_objets*2)), int(self.image.get_height()/int(taille_objets*2))))
            self.type = "ressource"
            self.disponibilite = disponibilite_ressources
        elif type == "potions":
            self.image = pygame.image.load(r"D:\PRIVE\programmation\EVOL\potion.png")#.convert()          #image    #C:\PRIVE\programmation\Evol\
            self.image = pygame.transform.scale(self.image,(int(self.image.get_width()/int(taille_objets*2)), int(self.image.get_height()/int(taille_objets*2))))
            self.type = "potions"
        else:
            pass
        self.rect = self.image.get_rect()
        if x > borderdown[0]-self.image.get_width():                #fait en sorte que le décor ne sorte pas de la bordure
            x = borderdown[0]-self.image.get_width()
        if y > borderdown[1]-self.image.get_height():
            y = borderdown[1]-self.image.get_height()
        self.rect.x = x             #Pos x
        self.rect.y = y             #Pos y
        # Calcul des centres des décors
        self.centre_x = self.rect.x + self.image.get_width()/2
        self.centre_y = self.rect.y + self.image.get_height()/2

class dessin:
    def __init__ (self,posX,posY, x,y,couleur = (255,255,255)):
        self.rect = pygame.Rect(posX,posY,x,y)          #rectangle de x sur y avec le coin haut gauche à Posx,Posy
        self.couleur = couleur                          #couleur

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True                 #sinon fin de jeu
        self.clock = pygame.time.Clock()    #fps
        self.list_text = []                 #liste de tous les textes
        self.list_pion = []                 #liste de tous les pions
        self.list_decor = []                #liste de tous les décors
        self.list_dessin = []               #liste de tous les dessins (rects)
        self.list_predateur = []            #liste de tous les prédateurs
        self.tpsGame= 0                     #temps général
        self.lancé = False                  #la simulation est-elle lancée ?
        self.pions_a_creer = []             #Liste des pions à créer avec leur tic d'apparition
        self.compteur = 2                   #compteur de lignes pour excel
        self.bob = 0                        #nombre de bob en vie (vert)
        self.bod = 0                        #nombre de bod en vie (orange)
        self.ressources_bob = 0             #caractéristiques de bob
        self.portee_bob = 0
        self.vitesse_bob = 0
        self.ressources_bod = 0             #caractéristiques de bod
        self.portee_bod = 0
        self.vitesse_bod = 0
        self.predateur = 0
        self.predateur_vie = 0

        self.R = 227                        #couleurs RGB du fond changeant
        self.G = 148
        self.B = 255
        self.couleur_visée = (randint(0,255),randint(0,255),randint(0,255))
        self.compteur_couleur = 0

        if pions_au_depart:
            self.lancer_simulation()
        
    def lancer_simulation(self):
        self.ajouter_text("Jeu de Paul",100,100,"Blue")
        self.ajouter_dessin(borderup[0],borderup[1],borderdown[0]-borderup[0],Épaisseur,(200,69,230))           #apparition des bordures
        self.ajouter_dessin(borderup[0],borderup[1],Épaisseur,borderdown[1],(200,69,230))
        self.ajouter_dessin(borderdown[0],borderup[1],Épaisseur,Épaisseur+borderdown[1],(200,69,230))  #Ici on rajoute une épaissaur car sinon on a pas le coin en bas à droite, qui n'est couvert par rien
        self.ajouter_dessin(borderup[0],borderdown[1],borderdown[0],Épaisseur,(200,69,230))
        self.lancé = True
        for i in range (nb_pions):
            if randint(0,100) < proportion_orange:
                self.ajouter_pion(randint(borderup[0],borderdown[0]), randint(borderup[1],borderdown[1]),"Bod")   #orange
            else:
                self.ajouter_pion(randint(borderup[0],borderdown[0]), randint(borderup[1],borderdown[1]),"Bob")   #vert

        for i in range (nb_predateurs):
            self.ajouter_predateur(randint(borderup[0],borderdown[0]), randint(borderup[1],borderdown[1]))       

        for i in range (maisons):
            self.ajouter_decor(randint(borderup[0],borderdown[0]), randint(borderup[1],borderdown[1]))

    def ajouter_pion(self, x, y,nom = None):
        if nom == None:
            nom = "Bob" if randint(0,1) == 1 else "Bod"
        nouveau_pion = pion(x,y,nom)            #ajoute un pion à x,y
        self.list_pion.append(nouveau_pion)
        return nouveau_pion                     #retourne le pion pour pouvoir le modifier (grace à variable = self.ajouter_pion(x,y,nom)) puis on modifie la variable

        #déplacement pion : for pion in self.list_pion:
        #                       pion.Goto(200-camera.x,200-camera.y)
    def ajouter_predateur(self, x, y):
        nouveau_predateur = predateur(x,y)            #ajoute un pion à x,y
        self.list_predateur.append(nouveau_predateur)
        return nouveau_predateur
    def ajouter_text(self, texte,x,y,couleur = (255,255,255),taille = 45,police= None):
        nouveau_text = text(texte,police,couleur,taille,x,y)
        self.list_text.append(nouveau_text)
        #ajouter texte : self.ajouter_text("Bonjour",100,100,None, (255,0,100),46)
    def ajouter_decor(self, x, y,type = "maison"):
        nouveau_decor = decor(x,y,type)
        self.list_decor.append(nouveau_decor)
        #ajouter decor : self.ajouter_decor(400,400)
    def ajouter_dessin(self,posX,posY,x,y,couleur = (255,255,255)):
        nouveau_dessin = dessin(posX,posY,x,y,couleur)
        self.list_dessin.append(nouveau_dessin)

    def events (self):
        for event in pygame.event.get():        #quitte le jeu
            if event.type == pygame.QUIT:
                self.running = False

        touche = pygame.key.get_pressed()           #déplacements caméra
        if touche[pygame.K_LEFT]:               
            camera.move_left()
        if touche[pygame.K_RIGHT]:
            camera.move_right()
        if touche[pygame.K_UP]:    
            camera.move_up()
        if touche[pygame.K_DOWN]:
            camera.move_down()
        if touche[pygame.K_ESCAPE]:
            self.lancer_simulation()

        if touche[pygame.K_a]:      #tue les bobs
            for pion in self.list_pion[:]:
                if pion.nom == "Bob":
                    self.list_pion.remove(pion)
        if touche[pygame.K_z]:      #tue les bods
            for pion in self.list_pion[:]:
                if pion.nom == "Bod":
                    self.list_pion.remove(pion)
        
        if touche[pygame.K_y]:              #controle utilisateur
            pass
               
    def update(self):
        self.tpsGame += 1           # temps général
        for pion in self.list_pion[:]:

        # Vérification de la mort des pions
            if pion.ressource < 0:  # mort du pion
                self.list_pion.remove(pion)
        #colisions de pions avec les décors
            for decor in self.list_decor:
                if decor.type == "maison":
                    if pion.rect.colliderect(decor.rect):
                        pion.cache += 1                 #compte si il y a des maisons qui le touchent
                    else:
                        pass
                elif decor.type =="ressource": 
                    # Calcul de la distance entre les centres
                    distance = ((pion.centre_x - decor.centre_x)**2 + (pion.centre_y - decor.centre_y)**2)**0.5
                    # Le pion peut collecter la ressource s'il est suffisamment proche 
                    if distance < pion.portee:  # Utilisation de la portée du pion pour vérifier s'il est suffisament proche
                        pion.ressource += 30
                        self.list_decor.remove(decor)
                        pion.recherche_nourriture = False  # Reset l'état de recherche
                        pion.R_proche = [0,100000000]
                    distance = 0
                    
                elif decor.type =="potions":
                    distance = ((pion.centre_x - decor.centre_x)**2 + (pion.centre_y - decor.centre_y)**2)**0.5
                    # Le pion peut collecter la ressource s'il est suffisamment proche 
                    if distance < pion.portee:
                        if randint (1,3)== 1:
                            pion.vitesse = min(5.0, pion.vitesse + 0.04)  # Limite la vitesse à 5.0
                        elif randint(1,2) == 2:
                            pion.portee += 5
                        else:
                            pion.ressource +=pion.ressource_base/2
                            pion.ressource_base += 3
                        self.list_decor.remove(decor)
        #collisions de pions avec les prédateurs
            for predateur in self.list_predateur:
                if ((pion.centre_x - predateur.centre_x)**2 + (pion.centre_y - predateur.centre_y)**2)**0.5 < pion.portee:
                    if  predateur.delai_attaque == 0:
                        if randint(1,taux_mortalité) == 1:
                            predateur.ressource += pion.ressource/2
                            pion.ressource -= pion.ressource
                            predateur.delai_attaque = 1
                            predateur.Goto(randint(borderup[0],borderdown[0]), randint(borderup[1],borderdown[1]))
                        else:
                            predateur.ressource += pion.ressource/20
                            pion.ressource -= pion.ressource/20
                            predateur.delai_attaque = 1
                            predateur.Goto(randint(borderup[0],borderdown[0]), randint(borderup[1],borderdown[1]))

        #collisions de pions avec les autres pions
            #for autre_pion in self.list_pion[:]:
        #colisions de pion avec les bordures
            if pion.rect.x < borderup[0]:
                pion.rect.x = borderup[0]+3
                pion.pos_x = float(pion.rect.x)
                pion.centre_x = pion.rect.x + pion.image.get_width()/2
                pion.target_x = borderup[0]+3
                pion.target_y = pion.rect.y
            if (pion.rect.x+int(pion.image.get_width())) > borderdown[0]:
                pion.rect.x = borderdown[0]- int(pion.image.get_width())-3
                pion.pos_x = float(pion.rect.x)
                pion.centre_x = pion.rect.x + pion.image.get_width()/2
                pion.target_x = borderdown[0] - int(pion.image.get_width())-3
                pion.target_y = pion.rect.y
            if pion.rect.y < borderup[1]:
                pion.rect.y = borderup[1]+3
                pion.pos_y = float(pion.rect.y)
                pion.centre_y = pion.rect.y + pion.image.get_height()/2
                pion.target_y = borderup[1]+3
                pion.target_x = pion.rect.x
            if pion.rect.y+int(pion.image.get_height()) > borderdown[1]:
                pion.rect.y = borderdown[1]-int(pion.image.get_height())-3
                pion.pos_y = float(pion.rect.y)
                pion.centre_y = pion.rect.y + pion.image.get_height()/2
                pion.target_y = borderdown[1]-int(pion.image.get_height())-3
                pion.target_x = pion.rect.x

        # Mise à jour pions
            pion.update()               # update du mouvement

            if pion.delai > 0:    #update délai d'apparition
                pion.delai -= 1
            else:
                pion.delai = 0

            if not pion.cache:
                pion.ressource = pion.ressource - 1  # update de la vie
            if pion.ressource/pion.ressource_base < recherche_de_nourriture/100 and pion.recherche_nourriture == False and pion.fuite == False:          #arrete le mouvement si il a faim pour immédiatement chercher de la nourriture
                pion.moving = False
                pion.recherche_nourriture = True
                pion.R_proche = [0,1000000000000]  # Reset la cible actuelle pour chercher une nouvelle ressource
            if fuite:       #update trajectoire pour fuir les prédateurs
                if fuite_bob == True and pion.nom == "Bob" or fuite_bod == True and pion.nom == "Bod":
                    for predateur in self.list_predateur:
                        if ((pion.rect.x-predateur.rect.x)**2 + (pion.rect.y-predateur.rect.y)**2)**0.5 < pion.portee*4 :
                            if pion.rect.x > predateur.rect.x:
                                x = pion.rect.x + randint(10,30)
                            elif pion.rect.x <= predateur.rect.x:
                                x = pion.rect.x - randint(10,30)
                            if pion.rect.y > predateur.rect.y:
                                y = pion.rect.y + randint(10,30)
                            elif pion.rect.y <= predateur.rect.y:
                                y = pion.rect.y - randint(10,30)
                            if x < borderup[0]+10:                # si il est trop près du bord et qu'il est en dessus de la moitié de la fenêtre, il fuit vers le haut
                                if y > borderdown[1]/2:
                                    y += 40
                                    x = pion.rect.x+3
                            elif x+int(pion.image.get_width()) > borderdown[0]+10:            # si il est trop près du bord et qu'il est en dessous de la moitié de la fenêtre, il fuit vers le bas
                                if y < borderdown[1]/2:
                                    y -= 40
                                    x = pion.rect.x-3
                            if y < borderup[1]+10:                # si il est trop près du bord et qu'il est en dessus de la moitié de la fenêtre, il fuit vers le haut
                                if x > borderdown[0]/2:
                                    x += 40
                                    y = pion.rect.y+3
                            elif y+int(pion.image.get_height()) > borderdown[1]+10:            # si il est trop près du bord et qu'il est en dessous de la moitié de la fenêtre, il fuit vers le bas
                                if x < borderdown[0]/2:
                                    x -= 40
                                    y = pion.rect.y-3
                            pion.Goto(x,y)
                            pion.fuite = True
                
        #déplacement continu des pions aléatoire ou vers une ressource
            if pion.moving == False:
                if pion.recherche_nourriture:               #première recherche de nourriture
                    for decor in self.list_decor:   
                        if decor.type == "ressource":                                       #tente de trouver des ressources à proximité
                            if ((pion.centre_x - decor.centre_x)**2 + (pion.centre_y - decor.centre_y)**2)**0.5 < pion.portee *4 and ((pion.centre_x - decor.centre_x)**2 + (pion.centre_y - decor.centre_y)**2)**0.5 < pion.R_proche[1]:
                                pion.R_proche = [decor,(((pion.rect.x - decor.centre_x)**2 + (pion.rect.y - decor.centre_y)**2)**0.5)]    #sauvegarde le plus proche
                            if pion.R_proche[0] != 0 and pion.R_proche[0] != 1:
                                pion.Goto(pion.R_proche[0].rect.x, pion.R_proche[0].rect.y)
                                break  # Sortir de la boucle une fois une ressource trouvée

                if pion.R_proche[0] == 1:                   #recherche de nourriture une fois en mouvement
                    for decor in self.list_decor:
                        if decor.type == "ressource":                                       #tente de trouver des ressources à proximité
                            if ((pion.centre_x - decor.centre_x)**2 + (pion.centre_y - decor.centre_y)**2)**0.5 < pion.portee *4 and ((pion.centre_x - decor.centre_x)**2 + (pion.centre_y - decor.centre_y)**2)**0.5 < pion.R_proche[1]:
                                pion.R_proche = [decor,(((pion.centre_x - decor.centre_x)**2 + (pion.centre_y - decor.centre_y)**2)**0.5)]    #sauvegarde le plus proche
                            if pion.R_proche[0] != 0 and pion.R_proche[0] != 1:
                                pion.Goto(pion.R_proche[0].centre_x, pion.R_proche[0].centre_y)
                                break  # Sortir de la boucle une fois une ressource trouvée

                if pion.R_proche[0] == 0 or pion.R_proche[0] == 1 or pion.recherche_nourriture == False:             #Sinon, il continue sa route aléatoire s'il n'a pas faim ou n'a pas trouvé de ressources
                    if randint(0,1) == 1:
                        if randint(0,1) == 1:
                            pion.Goto(pion.rect.x + randint(int(borderdown[0]/28), int(borderdown[0]/8)), 
                            pion.rect.y + randint(int(borderdown[1]/28), int(borderdown[1]/8)))
                            pion.R_proche[0] = 1  # Indique que le pion se déplace aléatoirement
                        else:
                            pion.Goto(pion.rect.x + randint(int(borderdown[0]/28), int(borderdown[0]/8)), 
                            pion.rect.y - randint(int(borderdown[1]/28), int(borderdown[1]/8)))
                            pion.R_proche[0] = 1  # Indique que le pion se déplace aléatoirement
                    else:
                        if randint(0,1) == 1:
                            pion.Goto(pion.rect.x - randint(int(borderdown[0]/28), int(borderdown[0]/8)), 
                            pion.rect.y + randint(int(borderdown[1]/28), int(borderdown[1]/8)))
                            pion.R_proche[0] = 1  # Indique que le pion se déplace aléatoirement
                        else:
                            pion.Goto(pion.rect.x - randint(int(borderdown[0]/28), int(borderdown[0]/8)), 
                            pion.rect.y - randint(int(borderdown[1]/28), int(borderdown[1]/8)))
                            pion.R_proche[0] = 1  # Indique que le pion se déplace aléatoirement

        #apparition des pions "naturelle"
            for pion2 in self.list_pion:
                if pion2 != pion:
                        if pion2.rect.colliderect(pion.rect):
                            if pion.ressource > ressources_replication and pion2.ressource > ressources_replication and pion.delai == 0 and pion2.delai == 0:
                                pion.delai = delai_pions
                                pion2.delai = delai_pions
                                if pion.nom == "Bob":
                                    type = "Bob"
                                    if mutations_de_type and randint(1,rareté_des_mutations_type) == 1:           #mutation une fois sur la rareté définie
                                        type = "Bod"
                                elif pion.nom == "Bod":
                                    type = "Bod"
                                    if mutations_de_type and randint(1,rareté_des_mutations_type) == 1:           #mutation une fois sur la rareté définie
                                        type = "Bob"

                                # Appeler une seule fois `ajouter_pion` avec les nouvelles coordonnées
                                nouveau_pion = self.ajouter_pion(pion.rect.x, pion.rect.y,type)

                                nouveau_pion.ressource_base = pion.ressource_base    #ressources de base
                                nouveau_pion.ressource = pion.ressource_base
                                nouveau_pion.portee = pion.portee            # Portée de base
                                nouveau_pion.vitesse = pion.vitesse            #vitesse de base

                                if mutations and randint(1,rareté_des_mutations) == 1:               #modification des caractéristiques du pion en fonction du parent si les mutations sont activées
                                    #cas :                                            coeff sur 16 : (décroissance simple en fonction du nombre de mutations)
                                    # vitesse mutée (1/2 aumenté)                     coeff : 3
                                    # portée mutée (1/2 augmentée)                    coeff : 3
                                    # ressources mutées (1/2 augmentées)              coeff : 3
                                    # vitesse et portée (1/2 augmentées)              coeff : 2
                                    # ressources et vitesse (1/2 augmentées)          coeff : 2
                                    # ressources et portée (1/2 augmentées)           coeff : 2
                                    # vitesse et portée et ressources (1/2 augmentées) coeff : 1
                                    coeff = randint(1,16)
                                    if coeff == 1:   # cas 3 mutations (vitesse, portée, ressources)
                                        if randint(0,1) == 1:
                                            nouveau_pion.vitesse = min(5.0, pion.vitesse + randint(1,100)/200)
                                        else:
                                            nouveau_pion.vitesse = max(0.1, pion.vitesse - randint(1,100)/200)
                                        if randint(0,1) == 1:
                                            nouveau_pion.portee -= randint(1,20)/10
                                        else:
                                            nouveau_pion.portee += randint(1,20)/10
                                        if randint(0,1) == 1:
                                            nouveau_pion.ressource_base += randint(1,25)
                                        else:
                                            nouveau_pion.ressource_base -= randint(1,25)

                                    elif coeff in (2,3):   # cas 2,3 mutations (ressources, portée)
                                        if randint(0,1) == 1:
                                            nouveau_pion.ressource_base = min(5.0, pion.ressource_base + randint(1,25))
                                        else:
                                            nouveau_pion.ressource_base = max(0.1, pion.ressource_base - randint(1,25))
                                        if randint(0,1) == 1:
                                            nouveau_pion.portee -= randint(1,20)/10
                                        else:
                                            nouveau_pion.portee += randint(1,20)/10
                                    
                                    elif coeff in (4,5):   # cas 4,5 mutations (ressources, vitesse)
                                        if randint(0,1) == 1:
                                            nouveau_pion.ressource_base = min(5.0, pion.ressource_base + randint(1,25))
                                        else:
                                            nouveau_pion.ressource_base = max(0.1, pion.ressource_base - randint(1,25))
                                        if randint(0,1) == 1:
                                            nouveau_pion.vitesse = min(5.0, pion.vitesse + randint(1,100)/200)
                                        else:
                                            nouveau_pion.vitesse = max(0.1, pion.vitesse - randint(1,100)/200)
                                    
                                    elif coeff in (6,7):   # cas 6,7 mutations (portée, vitesse)
                                        if randint(0,1) == 1:
                                            nouveau_pion.portee -= randint(1,20)/10
                                        else:
                                            nouveau_pion.portee += randint(1,20)/10
                                        if randint(0,1) == 1:
                                            nouveau_pion.vitesse = min(5.0, pion.vitesse + randint(1,100)/200)
                                        else:
                                            nouveau_pion.vitesse = max(0.1, pion.vitesse - randint(1,100)/200)
                                    
                                    elif coeff in (8,9,10):     # cas 8,9,10 mutations ressources
                                        if randint(0,1) == 1:
                                            nouveau_pion.ressource_base = min(5.0, pion.ressource_base + randint(1,25))
                                        else:
                                            nouveau_pion.ressource_base = max(0.1, pion.ressource_base - randint(1,25))

                                    elif coeff in (11,12,13):     # cas 11,12,13 mutations portée
                                        if randint(0,1) == 1:
                                            nouveau_pion.portee -= randint(1,20)/10
                                        else:
                                            nouveau_pion.portee += randint(1,20)/10
                                    
                                    elif coeff in (14,15,16):     # cas 14,15,16 mutations ressources
                                        if randint(0,1) == 1:
                                            nouveau_pion.vitesse = min(5.0, pion.vitesse + randint(1,100)/200)
                                        else:
                                            nouveau_pion.vitesse = max(0.1, pion.vitesse - randint(1,100)/200)

        #apparition de pions "magique"
        if self.lancé:
            if randint(0, pions_apparaissent) == 1 and pions_apparaissent > 0:     #un pion apparait-il ("magiquement") ?
                if len(self.list_pion) > 0:                 # est-ce qu'il y a encore des pions en vie
                    # Générer une valeur aléatoire pour choisir un pion et une position une seule fois
                    num = randint(0, len(self.list_pion)-1)
                    pos = randint(1, 4)
                    #si la croissance logarithmique est activée
                    if croissance_log == True:
                        pion = self.list_pion[num]              #récupère le pion à l'index choisi aléatoirement  
                        
                        # Calcul de la densité locale (nombre de pions dans un rayon de 20 pixels)
                        densite = 0
                        for autre_pion in self.list_pion:
                            if autre_pion != pion:  # Ne pas compter le pion lui-même
                                if ((pion.rect.x - autre_pion.rect.x)**2 + (pion.rect.y - autre_pion.rect.y)**2)**0.5 < 20:     #compte le nombre de pions dans un rayon de 20 pixels
                                    densite += 1

                        # Probabilité de création inversement proportionnelle à la densité
                        proba_creation = 1.0 / (1.0 + densite * 0.75)

                        if random.random() < proba_creation and densite < 3:
                            dx, dy = 0, 0
                            changPosX = randint(0, 60)
                            changPosY = randint(0, 60)
                            if pos == 1:
                                dx, dy = changPosX,changPosY 
                            elif pos == 2:
                                dx, dy = -changPosX,changPosY
                            elif pos == 3:
                                dx, dy = changPosX,-changPosY
                            elif pos == 4:
                                dx, dy = -changPosX,-changPosY
                        
                            if pion.nom == "Bob":
                                type = "Bob"
                                if mutations_de_type and randint(1,rareté_des_mutations_type) == 1:           #mutation une fois sur la rareté définie
                                    type = "Bod"
                            elif pion.nom == "Bod":
                                type = "Bod"
                                if mutations_de_type and randint(1,rareté_des_mutations_type) == 1:           #mutation une fois sur la rareté définie
                                    type = "Bob"

                            if pion.rect.x + dx > borderdown[0]:
                                dx = borderdown[0] - pion.rect.x
                            if pion.rect.x + dx < borderup[0]:
                                dx = borderup[0] - pion.rect.x
                            if pion.rect.y + dy > borderdown[1]:
                                dy = borderdown[1] - pion.rect.y
                            if pion.rect.y + dy < borderup[1]:
                                dy = borderup[1] - pion.rect.y
                            
                            nouveau_pion = self.ajouter_pion(pion.rect.x + dx, pion.rect.y + dy,type)

                            nouveau_pion.ressource_base = pion.ressource_base    #ressources de base
                            nouveau_pion.ressource = pion.ressource_base
                            nouveau_pion.portee = pion.portee            # Portée de base
                            nouveau_pion.vitesse = pion.vitesse            #vitesse de base

                            if mutations and randint(1,rareté_des_mutations) == 1:               #modification des caractéristiques du pion en fonction du parent si les mutations sont activées
                                #cas :                                            coeff sur 16 : (décroissance simple en fonction du nombre de mutations)
                                # vitesse mutée (1/2 aumenté)                     coeff : 3
                                # portée mutée (1/2 augmentée)                    coeff : 3
                                # ressources mutées (1/2 augmentées)              coeff : 3
                                # vitesse et portée (1/2 augmentées)              coeff : 2
                                # ressources et vitesse (1/2 augmentées)          coeff : 2
                                # ressources et portée (1/2 augmentées)           coeff : 2
                                # vitesse et portée et ressources (1/2 augmentées) coeff : 1
                                coeff = randint(1,16)
                                if coeff == 1:   # cas 3 mutations (vitesse, portée, ressources)
                                    if randint(0,1) == 1:
                                        nouveau_pion.vitesse = min(5.0, pion.vitesse + randint(1,100)/200)
                                    else:
                                        nouveau_pion.vitesse = max(0.1, pion.vitesse - randint(1,100)/200)
                                    if randint(0,1) == 1:
                                        nouveau_pion.portee -= randint(1,20)/10
                                    else:
                                        nouveau_pion.portee += randint(1,20)/10
                                    if randint(0,1) == 1:
                                        nouveau_pion.ressource_base += randint(1,25)
                                    else:
                                        nouveau_pion.ressource_base -= randint(1,25)

                                elif coeff in (2,3):   # cas 2,3 mutations (ressources, portée)
                                    if randint(0,1) == 1:
                                        nouveau_pion.ressource_base = min(5.0, pion.ressource_base + randint(1,25))
                                    else:
                                        nouveau_pion.ressource_base = max(0.1, pion.ressource_base - randint(1,25))
                                    if randint(0,1) == 1:
                                        nouveau_pion.portee -= randint(1,20)/10
                                    else:
                                        nouveau_pion.portee += randint(1,20)/10
                                
                                elif coeff in (4,5):   # cas 4,5 mutations (ressources, vitesse)
                                    if randint(0,1) == 1:
                                        nouveau_pion.ressource_base = min(5.0, pion.ressource_base + randint(1,25))
                                    else:
                                        nouveau_pion.ressource_base = max(0.1, pion.ressource_base - randint(1,25))
                                    if randint(0,1) == 1:
                                        nouveau_pion.vitesse = min(5.0, pion.vitesse + randint(1,100)/200)
                                    else:
                                        nouveau_pion.vitesse = max(0.1, pion.vitesse - randint(1,100)/200)
                                
                                elif coeff in (6,7):   # cas 6,7 mutations (portée, vitesse)
                                    if randint(0,1) == 1:
                                        nouveau_pion.portee -= randint(1,20)/10
                                    else:
                                        nouveau_pion.portee += randint(1,20)/10
                                    if randint(0,1) == 1:
                                        nouveau_pion.vitesse = min(5.0, pion.vitesse + randint(1,100)/200)
                                    else:
                                        nouveau_pion.vitesse = max(0.1, pion.vitesse - randint(1,100)/200)
                                
                                elif coeff in (8,9,10):     # cas 8,9,10 mutations ressources
                                    if randint(0,1) == 1:
                                        nouveau_pion.ressource_base = min(5.0, pion.ressource_base + randint(1,25))
                                    else:
                                        nouveau_pion.ressource_base = max(0.1, pion.ressource_base - randint(1,25))

                                elif coeff in (11,12,13):     # cas 11,12,13 mutations portée
                                    if randint(0,1) == 1:
                                        nouveau_pion.portee -= randint(1,20)/10
                                    else:
                                        nouveau_pion.portee += randint(1,20)/10
                                
                                elif coeff in (14,15,16):     # cas 14,15,16 mutations ressources
                                    if randint(0,1) == 1:
                                        nouveau_pion.vitesse = min(5.0, pion.vitesse + randint(1,100)/200)
                                    else:
                                        nouveau_pion.vitesse = max(0.1, pion.vitesse - randint(1,100)/200)
                            else:
                                pass
                    #si la croissance logarithmique n'est pas activée, apparition
                    else:
                        pion = self.list_pion[num] # Sélectionne le pion
                        dx, dy = 0, 0       # Calculer les nouvelles positions une seule fois
                        changPosX = randint(0, 60)
                        changPosY = randint(0, 60)
                        if pos == 1:
                            dx, dy = changPosX,changPosY 
                        elif pos == 2:
                            dx, dy = -changPosX,changPosY
                        elif pos == 3:
                            dx, dy = changPosX,-changPosY
                        elif pos == 4:
                            dx, dy = -changPosX,-changPosY

                        # modification du type en fonction des mutations
                        if pion.nom == "Bob":
                            type = "Bob"
                            if mutations_de_type and randint(1,rareté_des_mutations_type) == 1:           #mutation de type selon la rareté définie
                                type = "Bod"
                        elif pion.nom == "Bod":
                            type = "Bod"
                            if mutations_de_type and randint(1,rareté_des_mutations_type) == 1:           #mutation de type selon la rareté définie
                                type = "Bob"

                        if pion.rect.x + dx > borderdown[0]:
                            dx = borderdown[0] - pion.rect.x
                        if pion.rect.x + dx < borderup[0]:
                            dx = borderup[0] - pion.rect.x
                        if pion.rect.y + dy > borderdown[1]:
                            dy = borderdown[1] - pion.rect.y
                        if pion.rect.y + dy < borderup[1]:
                            dy = borderup[1] - pion.rect.y

                        nouveau_pion = self.ajouter_pion(pion.rect.x + dx, pion.rect.y + dy,type)

                        #modification des caractéristiques
                        nouveau_pion.ressource_base = pion.ressource_base    #ressources de base
                        nouveau_pion.ressource = pion.ressource_base
                        nouveau_pion.portee = pion.portee            # Portée de base
                        nouveau_pion.vitesse = pion.vitesse            #vitesse de base

                        if mutations and randint(1,rareté_des_mutations) == 1:               #modification des caractéristiques du pion en fonction du parent si les mutations sont activées
                            #cas :                                            coeff sur 16 : (décroissance simple en fonction du nombre de mutations)
                            # vitesse mutée (1/2 aumenté)                     coeff : 3
                            # portée mutée (1/2 augmentée)                    coeff : 3
                            # ressources mutées (1/2 augmentées)              coeff : 3
                            # vitesse et portée (1/2 augmentées)              coeff : 2
                            # ressources et vitesse (1/2 augmentées)          coeff : 2
                            # ressources et portée (1/2 augmentées)           coeff : 2
                            # vitesse et portée et ressources (1/2 augmentées) coeff : 1
                            coeff = randint(1,16)
                            if coeff == 1:   # cas 3 mutations (vitesse, portée, ressources)
                                if randint(0,1) == 1:
                                    nouveau_pion.vitesse = min(5.0, pion.vitesse + randint(1,100)/200)
                                else:
                                    nouveau_pion.vitesse = max(0.1, pion.vitesse - randint(1,100)/200)
                                if randint(0,1) == 1:
                                    nouveau_pion.portee -= randint(1,20)/10
                                else:
                                    nouveau_pion.portee += randint(1,20)/10
                                if randint(0,1) == 1:
                                    nouveau_pion.ressource_base += randint(1,25)
                                else:
                                    nouveau_pion.ressource_base -= randint(1,25)

                            elif coeff in (2,3):   # cas 2,3 mutations (ressources, portée)
                                if randint(0,1) == 1:
                                    nouveau_pion.ressource_base = min(5.0, pion.ressource_base + randint(1,25))
                                else:
                                    nouveau_pion.ressource_base = max(0.1, pion.ressource_base - randint(1,25))
                                if randint(0,1) == 1:
                                    nouveau_pion.portee -= randint(1,20)/10
                                else:
                                    nouveau_pion.portee += randint(1,20)/10
                                
                            elif coeff in (4,5):   # cas 4,5 mutations (ressources, vitesse)
                                if randint(0,1) == 1:
                                    nouveau_pion.ressource_base = min(5.0, pion.ressource_base + randint(1,25))
                                else:
                                    nouveau_pion.ressource_base = max(0.1, pion.ressource_base - randint(1,25))
                                if randint(0,1) == 1:
                                    nouveau_pion.vitesse = min(5.0, pion.vitesse + randint(1,100)/200)
                                else:
                                    nouveau_pion.vitesse = max(0.1, pion.vitesse - randint(1,100)/200)
                                
                            elif coeff in (6,7):   # cas 6,7 mutations (portée, vitesse)
                                if randint(0,1) == 1:
                                    nouveau_pion.portee -= randint(1,20)/10
                                else:
                                    nouveau_pion.portee += randint(1,20)/10
                                if randint(0,1) == 1:
                                    nouveau_pion.vitesse = min(5.0, pion.vitesse + randint(1,100)/200)
                                else:
                                    nouveau_pion.vitesse = max(0.1, pion.vitesse - randint(1,100)/200)
                                
                            elif coeff in (8,9,10):     # cas 8,9,10 mutations ressources
                                if randint(0,1) == 1:
                                    nouveau_pion.ressource_base = min(5.0, pion.ressource_base + randint(1,25))
                                else:
                                    nouveau_pion.ressource_base = max(0.1, pion.ressource_base - randint(1,25))

                            elif coeff in (11,12,13):     # cas 11,12,13 mutations portée
                                if randint(0,1) == 1:
                                    nouveau_pion.portee -= randint(1,20)/10
                                else:
                                    nouveau_pion.portee += randint(1,20)/10
                                
                            elif coeff in (14,15,16):     # cas 14,15,16 mutations ressources
                                if randint(0,1) == 1:
                                    nouveau_pion.vitesse = min(5.0, pion.vitesse + randint(1,100)/200)
                                else:
                                    nouveau_pion.vitesse = max(0.1, pion.vitesse - randint(1,100)/200)
                        else:
                            pass      

        #affichage excel
        if self.lancé and len(self.list_pion) > 0:  # Enregistre uniquement si la simulation est lancée et qu'il y a des pions
            feuille[f"B{self.compteur}"] = len(self.list_pion)             #mise à jour graphique du nombre de pions
            self.ressources_bob = 0
            self.portee_bob = 0
            self.vitesse_bob = 0
            self.ressources_bod = 0
            self.portee_bod = 0
            self.vitesse_bod = 0
            self.bob = 0
            self.bod = 0
            self.predateur = 0
            self.predateur_vie = 0

            #addition des caractéristiques
            for pion in self.list_pion[:]:
                if pion.nom == "Bob":
                    self.bob +=1
                    self.ressources_bob += pion.ressource_base
                    self.portee_bob += pion.portee
                    self.vitesse_bob += pion.vitesse

                elif pion.nom == "Bod":
                    self.bod +=1
                    self.ressources_bod += pion.ressource_base
                    self.portee_bod += pion.portee
                    self.vitesse_bod += pion.vitesse
            
            for predateur in self.list_predateur:
                self.predateur += 1
                self.predateur_vie += predateur.ressource
            
            if self.predateur > 0:
                self.predateur_vie = self.predateur_vie/self.predateur
            else:
                self.predateur_vie = 0

            if self.bob > 0:                #compte seulement si des pions sont en vie
                self.vitesse_bob = self.vitesse_bob/self.bob            #moyenne des caractéristiques en divisant par le nombre de pions
                self.ressources_bob = self.ressources_bob/self.bob
                self.portee_bob = self.portee_bob/self.bob

            if self.bod > 0:                #compte seulement si des pions sont en vie
                self.vitesse_bod = self.vitesse_bod/self.bod            #moyenne des caractéristiques en divisant par le nombre de pions
                self.ressources_bod = self.ressources_bod/self.bod
                self.portee_bod = self.portee_bod/self.bod
            
                
            feuille[f"C{self.compteur}"] = self.bob
            feuille[f"D{self.compteur}"] = self.bod

            feuille[f"E{self.compteur}"] = self.vitesse_bob
            feuille[f"F{self.compteur}"] = self.vitesse_bod
            feuille[f"H{self.compteur}"] = self.portee_bob
            feuille[f"I{self.compteur}"] = self.portee_bod
            feuille[f"K{self.compteur}"] = self.ressources_bob
            feuille[f"L{self.compteur}"] = self.ressources_bod
            feuille[f"N{self.compteur}"] = self.predateur
            feuille[f"O{self.compteur}"] = self.predateur_vie

            self.compteur +=1                                           #incrémente pour la ligne d'après

        #apparition de ressources
        if self.lancé:
            nb_ressources = 0
            for ressource in self.list_decor:
                if ressource.type == "ressource":
                    nb_ressources += 1
            if nb_ressources < max_ressources:
                if randint(0,100) in list_apparition_ressources:
                    self.ajouter_decor(randint(borderup[0],borderdown[0]), randint(borderup[1],borderdown[1]),"ressource")

        #disparition des ressources
        for ressource in self.list_decor:
            if ressource.type == "ressource":
                ressource.disponibilite -= 1
                if ressource.disponibilite == 0:
                    self.list_decor.remove(ressource)
                else:
                    pass

        #apparition de potions
        if potions:
            if self.lancé:
                if randint (0,80)==1:
                    self.ajouter_decor(randint(borderup[0],borderdown[0]), randint(borderup[1],borderdown[1]),"potions")

        #prédateurs
        for predateur in self.list_predateur:
            predateur.update()
        #délai de naissance des prédateurs
            if predateur.delai > 0:
                predateur.delai -= 1
            else:
                predateur.delai = 0
        #cooldown attaque des prédateurs
            if predateur.delai_attaque != 0 and predateur.delai_attaque < delai_attaque_predateurs:
                predateur.delai_attaque += 1
            else:
                predateur.delai_attaque = 0      
        #déplacement des prédateurs
            if predateur.moving == False:
                if predateur.ressource/predateur.ressource_base < recherche_de_nourriture/100 and predateur.chasse == False:
                    predateur.chasse = True
                    for pion in self.list_pion:
                        if ((predateur.centre_x - pion.centre_x)**2 + (predateur.centre_y - pion.centre_y)**2)**0.5 < predateur.portee *4:
                            predateur.proie = pion
                else:
                    predateur.proie = 0
                    predateur.chasse = False
                if predateur.proie != 0:                                                          #s'il a trouvé un pion à proximité, il se déplace vers elle, sinon aléatoirement
                    predateur.Goto(predateur.proie.centre_x, predateur.proie.centre_y)
                else:                                                                           #déplacement aléatoire si le pion n'a pas faim
                    if randint(0,1) == 1:
                        if randint(0,1) == 1:
                            predateur.Goto(predateur.rect.x + randint(int(borderdown[0]/28), int(borderdown[0]/8)), 
                                    predateur.rect.y + randint(int(borderdown[1]/28), int(borderdown[1]/8)))
                        else:
                            predateur.Goto(predateur.rect.x + randint(int(borderdown[0]/28), int(borderdown[0]/8)), 
                                    predateur.rect.y - randint(int(borderdown[1]/28), int(borderdown[1]/8)))
                    else:
                        if randint(0,1) == 1:
                            predateur.Goto(predateur.rect.x - randint(int(borderdown[0]/28), int(borderdown[0]/8)),predateur.rect.y + randint(int(borderdown[1]/28), int(borderdown[1]/8)))
                        else:
                            predateur.Goto(predateur.rect.x - randint(int(borderdown[0]/28), int(borderdown[0]/8)),predateur.rect.y - randint(int(borderdown[1]/28), int(borderdown[1]/8)))
        #mort du predateur
            if predateur.ressource > 0:
                predateur.ressource = predateur.ressource - 1
            else:
                self.list_predateur.remove(predateur)
        #collisions bordures
            if predateur.rect.x < borderup[0]:
                predateur.rect.x = borderup[0]+3
                predateur.pos_x = float(predateur.rect.x)
                predateur.centre_x = predateur.rect.x + predateur.image.get_width()/2
                predateur.target_x = borderup[0]+3
                predateur.target_y = predateur.rect.y
            if (predateur.rect.x+int(predateur.image.get_width())) > borderdown[0]:
                predateur.rect.x = borderdown[0]- int(predateur.image.get_width())-3
                predateur.pos_x = float(predateur.rect.x)
                predateur.centre_x = predateur.rect.x + predateur.image.get_width()/2
                predateur.target_x = borderdown[0] - int(predateur.image.get_width())-3
                predateur.target_y = predateur.rect.y
            if predateur.rect.y < borderup[1]:
                predateur.rect.y = borderup[1]+3
                predateur.pos_y = float(predateur.rect.y)
                predateur.centre_y = predateur.rect.y + predateur.image.get_height()/2
                predateur.target_y = borderup[1]+3
                predateur.target_x = predateur.rect.x
            if predateur.rect.y+int(predateur.image.get_height()) > borderdown[1]:
                predateur.rect.y = borderdown[1]-int(predateur.image.get_height())-3
                predateur.pos_y = float(predateur.rect.y)
                predateur.centre_y = predateur.rect.y + predateur.image.get_height()/2
                predateur.target_y = borderdown[1]-int(predateur.image.get_height())-3
                predateur.target_x = predateur.rect.x
        #apparition prédateurs
            for predateur2 in self.list_predateur:
                if predateur2 != predateur:
                    if predateur.rect.colliderect(predateur2.rect):
                        if predateur.delai == 0 and predateur2.delai == 0:
                            if predateur.ressource > predateur.ressource_base/3 and predateur2.ressource > predateur2.ressource_base/3:
                                nouveau_predateur = self.ajouter_predateur(predateur.rect.x,predateur.rect.y)
                                predateur.delai = delai_predateurs
                                predateur2.delai = delai_predateurs
                        else:
                            if malus_de_rencontre:
                                predateur.ressource = predateur.ressource - predateur.ressource/60
                                predateur2.ressource = predateur2.ressource - predateur2.ressource/60   
                            else:
                                pass

        if fond_multicolore:            # mise à jour couleur fond dégradé
            if self.compteur_couleur != 50:
                self.R += (self.couleur_visée[0]-self.R)/50
                self.G += (self.couleur_visée[1]-self.G)/50
                self.B += (self.couleur_visée[2]-self.B)/50
                self.compteur_couleur += 1
            else:
                self.couleur_visée = ((randint(0,255),randint(0,255),randint(0,255)))
                self.compteur_couleur = 0
            
            self.R = max(0, min(255, self.R))
            self.G = max(0, min(255, self.G))
            self.B = max(0, min(255, self.B))           

    def display(self):
        screen.fill((self.R,self.G,self.B))
        for texte in self.list_text:
            screen.blit(texte.texte, (texte.x - camera.x, texte.y - camera.y))              #affichage texte
        for decor in self.list_decor:
            screen.blit(decor.image, (decor.rect.x - camera.x,decor.rect.y - camera.y))     #affichage des décors
        for dessin in self.list_dessin:
            rect_ajuste = pygame.Rect(dessin.rect.x - camera.x, dessin.rect.y - camera.y, dessin.rect.width, dessin.rect.height)        #affichage des dessins
            pygame.draw.rect(screen,dessin.couleur,rect_ajuste)
        for predateur in self.list_predateur:
            screen.blit(predateur.image, (predateur.rect.x - camera.x, predateur.rect.y - camera.y))
        for pion in self.list_pion:         #affichage des pions
            if pion.cache > 0:              
                pass                        #si dans un décor
                pion.cache = 0
            else:
                screen.blit(pion.image, (pion.rect.x - camera.x, pion.rect.y - camera.y))   #affichage
        pygame.display.flip()
        
    def run (self):
        while self.running:
            self.events()
            self.update()
            self.display()
            self.clock.tick(FPS)

game = Game(screen)
game.run()
pygame.quit()
wb.save(file_path)



#bordures pas vraiment respectées ?