% NOM_ETUDIANT_1 (MATRICULE_1)
% NOM_ETUDIANT_2 (MATRICULE_2)

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

% Contrainte liant le début et la fin de chaque tâche
constraint forall(i in 1..n) (
  fin_tache[i] = debut_tache[i] + duree_tache[i]
);

% Contrainte pour définir la fin du projet (makespan)
constraint fin_projet = max(fin_tache);

% Contrainte pour s'assurer que toutes les tâches finissent dans l'horizon temporel
constraint forall(i in 1..n) (
  fin_tache[i] <= m
);

% Contrainte cumulative pour s'assurer que l'utilisation d'énergie ne dépasse pas la limite
constraint cumulative(debut_tache, duree_tache, ressource_tache, limite);

% Contrainte pour limiter le nombre de tâches qui démarrent en même temps
constraint forall(t in 1..m) (
    sum(i in 1..n) (bool2int(debut_tache[i] = t)) <= 2
);

% Objectif : minimiser le makespan
solve minimize fin_projet;

%-----------------------------------------------------------------------------%

output [
  "Envergure du projet  : ", show(fin_projet), "\n",
  "Début des tâches     : ", show(debut_tache), "\n",
  "Fin des tâches       : ", show(fin_tache), "\n",
];