% OUARAD (2117136)
% FARHAT (X)

include "globals.mzn"; 

%-----------------------------------------------------------------------------%
% Données
%-----------------------------------------------------------------------------%

% Nombre de villes à visiter + point de départ de la tournée
int: n;
 % Distance entre chaque villes (symmétrique)
array[1..n,1..n] of int: distance;
 % Distance minimale possible entre deux villes différentes
int: min_val = min([distance[i,j] | i,j in 1..n where distance[i,j] > 0]);
% Distance maximale possible entre deux villes différentes
int: max_val = max([distance[i,j] | i,j in 1..n]);

% Fenêtre de temps (1 = début, 2 = fin) durant laquelle il est possible de jouer pour chaque ville
array[1..n,1..2] of int: fenetre_arrivee;
% Temps maximum pour tout le trajet
int: max_trajet = max([fenetre_arrivee[i,2] | i in 1..n]);
% Fenêtre de temps la plus grande du trajet
int: max_fenetre = max([fenetre_arrivee[i,2] - fenetre_arrivee[i,1]| i in 2..n]);

%-----------------------------------------------------------------------------%
% Variables de décisions
%-----------------------------------------------------------------------------%

% Ordre des villes visitées par la tournée
array[1..n] of var 1..n: chemin_tournee;
% Circuit de la tournée, circuit_tournee[i] = j => j est le successeur de i
array[1..n] of var 1..n: circuit_tournee;
% Temps cumulé lors de l'arrivé au point i de la tournée
array[1..n] of var 0..max_trajet: cumul_temps;
% Temps d'attente avant le spectacle en ville i
array[1..n] of var 0..max_fenetre: temps_attente;
% Temps d'attente total 
var 0..max_trajet: total_temps_attentes = sum(temps_attente);

%-----------------------------------------------------------------------------%
% Objectif
%-----------------------------------------------------------------------------%

% Temps de trajet à minimiser
var int: temps_trajet;

%-----------------------------------------------------------------------------%
% Partie étudiant
%-----------------------------------------------------------------------------%
% 1. Visiter chaque ville une fois sans répétition
constraint all_different(chemin_tournee);
constraint all_different(circuit_tournee);
constraint temps_trajet >= n * min_val;
constraint forall(i in 1..n-1)(cumul_temps[i] < cumul_temps[i+1]);


% 2. Trouver le circuit de la tournée
constraint forall(i in 1..n-1)(
  circuit_tournee[chemin_tournee[i]] = chemin_tournee[i+1]
);

% 3. Commencer par la ville de départ et y terminer
constraint chemin_tournee[n] = 1;
constraint circuit_tournee[1] = chemin_tournee[1]; 

% 3. Respect des fenetres de temps
constraint forall(i in 1..n) (
    cumul_temps[i] >= fenetre_arrivee[chemin_tournee[i], 1] /\
    cumul_temps[i] <= fenetre_arrivee[chemin_tournee[i], 2]
);

% 4. Calcul de temps 
% Le temps d’arrivée à la première ville inclut la distance depuis la dernière ville visitée pour fermer la tournée (c’est-à-dire le retour à la première ville dans un circuit fermé) et on ajoute le temps d'attente dans la première ville
constraint cumul_temps[1] = distance[chemin_tournee[n], chemin_tournee[1]] + temps_attente[chemin_tournee[1]];
% Pour les autres villes, le temps d'arrivée cumulé à la ville précédente + le temps d'attente dans la ville + la distance entre la ville i-1 (ville précédente) et la ville i (ville actuelle)
constraint forall(i in 2..n)(
  cumul_temps[i] = cumul_temps[i-1] + temps_attente[chemin_tournee[i]] + distance[chemin_tournee[i-1], chemin_tournee[i]] 
);



constraint temps_trajet = cumul_temps[n] ;

% Heuristique de recherche sur l'ordre des villes choisies dans chemin_tournee. First_fail permet de prioriser les choix maximisant la contrainte (reduits les conflits), indomain_min attribue la valeur minimale a chaque var, complete execute une recherche entiere pour optimiser
solve :: int_search(chemin_tournee, smallest, indomain_min, complete) minimize temps_trajet;


%-----------------------------------------------------------------------------%

output [
  "Chemin de la tournée                   : \(chemin_tournee)\n",
  "Circuit de la tournée                  : \(circuit_tournee)\n",
  "Temps cumulés avant d'entrer en ville  : \(cumul_temps)\n",
  "Temps d'attente avant l'entrée en ville: \(temps_attente)\n",
  "Temps d'attente total                  : \(total_temps_attentes)\n",
  "Temps de trajet total                  : \(temps_trajet)\n",
];