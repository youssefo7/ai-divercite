% OUARAD (2117136)
% FARHAT (2153946)

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

% 0. Contrainte globale de circuit pour notre variable
constraint subcircuit(circuit_tournee);

% 1. Visiter chaque ville seulement une fois : 
constraint all_different(chemin_tournee);
constraint all_different(circuit_tournee);

% 2. Durée minimale de la tournée : 
% Le temps total de trajet doit être supérieur ou égal à la durée minimale calculée.
constraint temps_trajet >= n * min_val;

% 3. Ordre des visites : 
% Le temps de cumul doit être croissant entre les villes successives.
constraint increasing(cumul_temps);

% 4. Définir le circuit de la tournée : 
% Chaque ville dans le chemin doit être reliée à la ville suivante dans le circuit.
constraint forall(i in 1..n-1)( 
  circuit_tournee[chemin_tournee[i]] = chemin_tournee[i+1]
);

% 5. La ville de départ et de fin sont les mêmes : 
constraint chemin_tournee[n] = 1;
constraint circuit_tournee[1] = chemin_tournee[1]; 

% 6. Respect des fenêtres de temps lors des visites des villes : 
constraint forall(i in 1..n) (
    cumul_temps[i] >= fenetre_arrivee[chemin_tournee[i], 1] /\ 
    cumul_temps[i] <= fenetre_arrivee[chemin_tournee[i], 2]
);

% 7. Calcul du temps de trajet, d'abord la ville 1: 
% Le temps de cumul pour la première ville est la distance de retour plus le temps d'attente à la première ville.
constraint cumul_temps[1] = distance[chemin_tournee[n], chemin_tournee[1]] + temps_attente[chemin_tournee[1]];

% 8. Pour chaque ville suivante, calculer le temps de cumul : 
% Le temps de cumul pour chaque ville est le temps précédent plus le temps d'attente et la distance parcourue.
constraint forall(i in 2..n)(
  cumul_temps[i] = cumul_temps[i-1] + temps_attente[chemin_tournee[i]] + distance[chemin_tournee[i-1], chemin_tournee[i]]
);

% 9. Calcul du temps total de trajet : 
% Le temps total est le dernier temps de cumul.
constraint temps_trajet = cumul_temps[n];

% 10. Heuristique pour la recherche : 
% Utilisation de la méthode de recherche pour minimiser le temps de trajet en utilisant un algorithme de recherche par échec (first_fail).
solve :: int_search(chemin_tournee, first_fail, indomain_split, complete) minimize temps_trajet;



%-----------------------------------------------------------------------------%

output [
  "Chemin de la tournée                   : \(chemin_tournee)\n",
  "Circuit de la tournée                  : \(circuit_tournee)\n",
  "Temps cumulés avant d'entrer en ville  : \(cumul_temps)\n",
  "Temps d'attente avant l'entrée en ville: \(temps_attente)\n",
  "Temps d'attente total                  : \(total_temps_attentes)\n",
  "Temps de trajet total                  : \(temps_trajet)\n",
];