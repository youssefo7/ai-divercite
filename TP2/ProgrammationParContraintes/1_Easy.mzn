% OUARAD (2117136)
% FARHAT (2153946)

include "globals.mzn";

%-----------------------------------------------------------------------------%
% Données
%-----------------------------------------------------------------------------%
% Nombre d'acteurs et de rôles
int: n;
% Couleurs des costumes
enum costumes; 
% Costume démandé pour un rôle i (première dimension) par un acteur j (seconde dimension)
array[1..n,1..n] of costumes: choix_costume;


%-----------------------------------------------------------------------------%
% Variables de décisions
%-----------------------------------------------------------------------------%
% Variables de décision pour assigner un acteur à un rôle
array [1..n] of var 1..n: assignation_role;
array [1..n] of var costumes: costume_assignation;


%-----------------------------------------------------------------------------%
% Partie étudiant
%-----------------------------------------------------------------------------%

% Contraintes
% 1. Rôles  et costumes uniques
constraint all_different(assignation_role);
constraint all_different(costume_assignation);


% 2. Deux acteurs voisins, selon l’ordre lexicographique, ne jouent pas un rôle adjacent
constraint forall(i in 1..n-1) (
    abs(assignation_role[i] - assignation_role[i+1]) > 1
);

% 4. Associé les costumes aux acteurs
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
