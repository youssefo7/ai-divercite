% OUARAD (2117136)
% FARHAT (2153946)

include "globals.mzn"; 

%-----------------------------------------------------------------------------%
% Données
%-----------------------------------------------------------------------------%

% Nombre de tâches
int: n;
% Durée maximal du projet
int: m;
% Limite de ressources pouvant être partagées entre les tâches en cours
int: limite;

% Durée des tâches
array[1..n] of 1..m: duree_tache;
% Ressources requises par les tâches
array[1..n] of 1..m: ressource_tache;

%-----------------------------------------------------------------------------%
% Variables de décisions
%-----------------------------------------------------------------------------%

array[1..n] of var 1..m: debut_tache; % Début des tâches
array[1..n] of var 1..m: fin_tache; % Fin des tâches

%-----------------------------------------------------------------------------%
% Objectif
%-----------------------------------------------------------------------------%

% Fin du projet
var int: fin_projet;

%-----------------------------------------------------------------------------%
% Partie étudiant
%-----------------------------------------------------------------------------%

% 1. Définir les temps t de fin de tâches, pour chaque tâche
constraint forall(i in 1..n) (
  fin_tache[i] = debut_tache[i] + duree_tache[i]
);

% 2. Limiter la consommation d'énergie à chaque instant (Contrainte globale)
constraint cumulative(debut_tache, duree_tache, ressource_tache, limite);

% 3. Limiter le nombre de tâche conccurentes à 2 à chaque instant
constraint forall(t in 1..m) (
  sum(i in 1..n) (bool2int(debut_tache[i] = t)) <= 2
);

% 4. Respecter la limite de temps que peut prendre le projet
constraint forall(i in 1..n) (
  fin_tache[i] <= m
);

% 5. Contrainte globale pour minimiser le makespan
constraint maximum(fin_projet, fin_tache);

% 6. Minimiser fin_projet
solve minimize fin_projet;

%-----------------------------------------------------------------------------%

output [
  "Envergure du projet  : ", show(fin_projet), "\n",
  "Début des tâches     : ", show(debut_tache), "\n",
  "Fin des tâches       : ", show(fin_tache), "\n",
];