include "globals.mzn";

% Données
int: n; % Nombre d'acteurs et de rôles
enum costumes; % Couleurs des costumes
array[1..n, 1..n] of costumes: choix_costume; % Préférences de costume

% Variables de décision
array [1..n] of var 1..n: assignation_role;
array [1..n] of var costumes: costume_assignation;

% Contraintes
% 1. Rôles uniques
constraint all_different(assignation_role);
constraint all_different(costume_assignation);


% 2. Conflit de voisinage
constraint forall(i in 1..n-1) (
    abs(assignation_role[i] - assignation_role[i+1]) > 1
);

% 4. Link assigned roles to their chosen costumes
constraint forall(i in 1..n) (
    costume_assignation[i] = choix_costume[assignation_role[i], i]
);

% Sortie
output [
    "L'acteur " ++ show(i) ++ 
    " prendra le rôle " ++ show(fix(assignation_role[i])) ++ 
    " (costume " ++ show(fix(costume_assignation[i])) ++ ")\n" 
    | i in 1..n
];
