import tkinter as tk # bibliothèque pour créer des interfaces graphiques
from tkinter import ttk, messagebox # crée des widjets
from PIL import Image, ImageTk # bibliothèque pour image
import matplotlib.pyplot as plt # bibliothèque pour les graphiques
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # bibliothèque pour les graphiques
import datetime # bibliothèque pour la date

class ApplicationBancaire:
    def __init__(self, root): # Initialisation de la class
        self.root = root
        self.root.title("BDS BANK") # titre de la première fenêtre donc = Titre du projet

        # Création du canvas et de la barre de défilement
        self.canvas = tk.Canvas(self.root, borderwidth=0)
        self.frame = tk.Frame(self.canvas)
        self.vsb = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)  # Permet de scroller en vertical
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y") # la scroll bar est placé à droite
        self.canvas.pack(side="left", fill="both", expand=True) # Place le canvas à gauche, l'étend pour remplir tout l'espace disponible
        self.canvas.create_window((4,4), window=self.frame, anchor="nw", tags="self.frame") # Permet de créer une fenêtre dans le canva/ "nw" = coin supérieur gauche

        self.frame.bind("<Configure>", self.on_frame_configure)

        # Dictionnaire pour stocker les comptes
        self.comptes = {}
        self.compte_courant = None

        # Affichage de l'image en haut
        self.afficher_image()

        # Création de l'interface utilisateur
        self.creer_widgets()

    def afficher_image(self):
        image_path = "BDSbank.png"
        image = Image.open(image_path) # Ouvre l'image grâce à PIL
        image = image.resize((image.width // 2, image.height // 2), Image.LANCZOS) # Redimension de l'image à la moitié de sa taille initiale, car beaucoup trop grande
        photo = ImageTk.PhotoImage(image)

        self.label_image = tk.Label(self.frame, image=photo)
        self.label_image.image = photo
        self.label_image.grid(row=0, column=0, columnspan=2, pady=10) # Placement du LOGO

    def creer_widgets(self): # Section pour créer un compte
        self.cadre_creation_compte = ttk.LabelFrame(self.frame, text="Créer un Compte")
        self.cadre_creation_compte.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(self.cadre_creation_compte, text="Nom du Compte:").grid(row=0, column=0, padx=5, pady=5)
        self.entree_nom_compte = ttk.Entry(self.cadre_creation_compte)
        self.entree_nom_compte.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.cadre_creation_compte, text="Solde Initial:").grid(row=1, column=0, padx=5, pady=5)
        self.entree_solde_initial = ttk.Entry(self.cadre_creation_compte)
        self.entree_solde_initial.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.cadre_creation_compte, text="Créer", command=self.creer_compte).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Section pour sélectionner un compte
        self.cadre_selection_compte = ttk.LabelFrame(self.frame, text="Sélectionner un Compte")
        self.cadre_selection_compte.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.combo_comptes = ttk.Combobox(self.cadre_selection_compte)
        self.combo_comptes.grid(row=0, column=0, padx=5, pady=5)
        self.combo_comptes.bind("<<ComboboxSelected>>", self.selectionner_compte)

        # Section pour ajouter des transactions
        self.cadre_transactions = ttk.LabelFrame(self.frame, text="Transactions")
        self.cadre_transactions.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        ttk.Label(self.cadre_transactions, text="Type:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_type = ttk.Combobox(self.cadre_transactions, values=["Revenu", "Dépense"])
        self.combo_type.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.cadre_transactions, text="Montant:").grid(row=1, column=0, padx=5, pady=5)
        self.entree_montant = ttk.Entry(self.cadre_transactions)
        self.entree_montant.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.cadre_transactions, text="Ajouter", command=self.ajouter_transaction).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.cadre_transactions, text="Modifier", command=self.modifier_transaction).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.cadre_transactions, text="Supprimer", command=self.supprimer_transaction).grid(row=2, column=2, padx=5, pady=5)

        # Liste des transactions
        self.liste_transactions = ttk.Treeview(self.cadre_transactions, columns=("Date", "Type", "Montant"), show='headings')
        self.liste_transactions.heading("Date", text="Date")
        self.liste_transactions.heading("Type", text="Type")
        self.liste_transactions.heading("Montant", text="Montant")
        self.liste_transactions.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
        self.liste_transactions.bind("<<TreeviewSelect>>", self.selectionner_transaction)

        # Section pour afficher le solde
        self.cadre_solde = ttk.LabelFrame(self.frame, text="Solde")
        self.cadre_solde.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.label_solde_mensuel = ttk.Label(self.cadre_solde, text="Solde Mensuel: 0")
        self.label_solde_mensuel.grid(row=0, column=0, padx=5, pady=5)

        self.label_solde_annuel = ttk.Label(self.cadre_solde, text="Solde Annuel: 0")
        self.label_solde_annuel.grid(row=0, column=1, padx=5, pady=5)

        # Section pour afficher les graphiques
        self.cadre_graphiques = ttk.LabelFrame(self.frame, text="Graphiques")
        self.cadre_graphiques.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        ttk.Button(self.cadre_graphiques, text="Graphique Mensuel", command=self.afficher_graphiques_mensuels).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(self.cadre_graphiques, text="Graphique Annuel", command=self.afficher_graphiques_annuels).grid(row=0, column=1, padx=5, pady=5)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def creer_compte(self):
        nom_compte = self.entree_nom_compte.get()
        solde_initial = self.entree_solde_initial.get()

        if not nom_compte or not solde_initial:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs") # Envoie un message si l'utilisateur a oubliié d'indiquer le solde ou/et son nom
            return

        try:
            solde_initial = float(solde_initial)
        except ValueError:
            messagebox.showerror("Erreur", "Le solde initial doit être un nombre") # Envoie un message d'erreur si l'utilisateur à rempli autre chose qu'un nbs dans le solde initiale
            return

        self.comptes[nom_compte] = {"solde": solde_initial, "transactions": []}
        self.compte_courant = nom_compte
        self.mettre_a_jour_comptes()
        self.mettre_a_jour_solde()
        messagebox.showinfo("Succès", f"Compte {nom_compte} créé avec succès") # Envoie un message pop-up de la réussite de l'ouvertur du compte

    def mettre_a_jour_comptes(self):
        self.combo_comptes['values'] = list(self.comptes.keys())
        if self.compte_courant:
            self.combo_comptes.set(self.compte_courant)

    def selectionner_compte(self, event):
        self.compte_courant = self.combo_comptes.get()
        self.mettre_a_jour_solde()
        self.afficher_transactions()

    def ajouter_transaction(self):
        if self.compte_courant is None:
            messagebox.showerror("Erreur", "Veuillez sélectionner un compte d'abord") # Envoie un message d'erreur si l'utilisateur n'a pas selectionner un compte
            return

        type_transaction = self.combo_type.get()
        montant = self.entree_montant.get()

        if not type_transaction or not montant:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs") # Envoie un message d'erreur si l'utilisateur à oublié un champ
            return

        try:
            montant = float(montant)
        except ValueError:
            messagebox.showerror("Erreur", "Le montant doit être un nombre") # Envoie un message d'erreur si l'utilisateur à rempli autre chose qu'un nbs dans le montant
            return

        if type_transaction == "Dépense":
            montant = -montant

        self.comptes[self.compte_courant]["transactions"].append((datetime.date.today(), type_transaction, montant))
        self.mettre_a_jour_solde()
        self.afficher_transactions()

    def selectionner_transaction(self, event):
        selected_item = self.liste_transactions.selection()
        if not selected_item:
            return

        transaction = self.liste_transactions.item(selected_item)["values"]
        self.combo_type.set(transaction[1])
        self.entree_montant.delete(0, tk.END)
        self.entree_montant.insert(0, transaction[2])

    def modifier_transaction(self):
        selected_item = self.liste_transactions.selection()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner une transaction à modifier") # Envoie un message d'erreur si l'utilisateur n'a pas selectionner une transaction
            return

        type_transaction = self.combo_type.get()
        montant = self.entree_montant.get()

        if not type_transaction or not montant:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs") # Envoie un message d'erreur si l'utilisateur à oublié un champ
            return

        try:
            montant = float(montant)
        except ValueError:
            messagebox.showerror("Erreur", "Le montant doit être un nombre") # Envoie un message d'erreur si l'utilisateur à rempli autre chose qu'un nbs dans le montant
            return

        if type_transaction == "Dépense":
            montant = -montant

        index = self.liste_transactions.index(selected_item[0])
        self.comptes[self.compte_courant]["transactions"][index] = (datetime.date.today(), type_transaction, montant)
        self.mettre_a_jour_solde()
        self.afficher_transactions()

    def supprimer_transaction(self):
        selected_item = self.liste_transactions.selection()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner une transaction à supprimer")
            return

        index = self.liste_transactions.index(selected_item[0])  # index = nom de la variable pour évité de réecrire la liste des transactions entièrement
        del self.comptes[self.compte_courant]["transactions"][index]
        self.mettre_a_jour_solde()
        self.afficher_transactions()

    def mettre_a_jour_solde(self):
        solde_mensuel = self.calculer_solde("mensuel")
        solde_annuel = self.calculer_solde("annuel")
        self.label_solde_mensuel.config(text=f"Solde Mensuel: {solde_mensuel:.2f}") # affichage continuel du solde mensuel
        self.label_solde_annuel.config(text=f"Solde Annuel: {solde_annuel:.2f}") # afichage continuel du solde annuel

    def calculer_solde(self, periode):
        solde = self.comptes[self.compte_courant]["solde"]  # Solde initial
        maintenant = datetime.date.today()
        for date, _, montant in self.comptes[self.compte_courant]["transactions"]:
            if periode == "mensuel" and date.month == maintenant.month and date.year == maintenant.year:
                solde += montant
            elif periode == "annuel" and date.year == maintenant.year:
                solde += montant
        return solde

    def afficher_transactions(self):
        for item in self.liste_transactions.get_children():
            self.liste_transactions.delete(item)

        for transaction in self.comptes[self.compte_courant]["transactions"]:
            self.liste_transactions.insert("", "end", values=transaction) # permet de sauté des lignes pour que se soit plus visuel

    def afficher_graphiques_mensuels(self):
        self.afficher_graphiques("mensuel")

    def afficher_graphiques_annuels(self):
        self.afficher_graphiques("annuel")

    def afficher_graphiques(self, periode):
        revenus = 0
        depenses = 0
        maintenant = datetime.date.today()

        for date, type_transaction, montant in self.comptes[self.compte_courant]["transactions"]:
            if periode == "mensuel" and date.month == maintenant.month and date.year == maintenant.year:
                if montant > 0:
                    revenus += montant
                else:
                    depenses += -montant
            elif periode == "annuel" and date.year == maintenant.year:
                if montant > 0:
                    revenus += montant
                else:
                    depenses += -montant

        if periode == "mensuel":
            labels = ['Revenus', 'Dépenses']
            sizes = [revenus, depenses]
            explode = (0, 0.1)  # Sépare la part des dépenses

            fig, ax = plt.subplots()
            ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                   shadow=True, startangle=90)
            ax.axis('equal')  # Assure que le graphique est un camembert
            plt.title("Répartition Mensuelle")

        else:
            months = ["Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
            revenus_par_mois = [0] * 12
            depenses_par_mois = [0] * 12

            for date, type_transaction, montant in self.comptes[self.compte_courant]["transactions"]:
                if date.year == maintenant.year:
                    if montant > 0:
                        revenus_par_mois[date.month - 1] += montant
                    else:
                        depenses_par_mois[date.month - 1] += -montant

            fig, ax = plt.subplots()
            ax.plot(months, revenus_par_mois, label="Revenus")
            ax.plot(months, depenses_par_mois, label="Dépenses")
            ax.set_xlabel("Mois")
            ax.set_ylabel("Montant")
            ax.set_title("Revenus et Dépenses Annuel")
            ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.cadre_graphiques)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationBancaire(root)
    root.mainloop()
