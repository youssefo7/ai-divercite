% NOM_ETUDIANT_1 (MATRICULE_1)
% NOM_ETUDIANT_2 (MATRICULE_2)

include "globals.mzn";

%-----------------------------------------------------------------------------%
% Variables de décisions
%-----------------------------------------------------------------------------%

% Nombre devant satisfaire les critères
var 1000..9999: nombre;

% Décomposition du nombre en un ensemble de chiffres
array[1..4] of var 1..9: chiffres;

%-----------------------------------------------------------------------------%
% Objectif
%-----------------------------------------------------------------------------%

% Variable à minimiser
var int: p;

%-----------------------------------------------------------------------------%
% Partie étudiant
%-----------------------------------------------------------------------------%


% Contrainte liant le nombre à ses chiffres
constraint nombre = 1000 * chiffres[1] + 100 * chiffres[2] + 10 * chiffres[3] + chiffres[4];

% 1. Nombre pair
constraint chiffres[4] mod 2 = 0;

% 2. Le chiffre 0 n'est pas présent (déjà géré par la déclaration var 1..9)

% 3. Les 4 chiffres sont différents
constraint alldifferent(chiffres);

% 4. Milliers > Centaines
constraint chiffres[1] > chiffres[2];

% 5. Dizaines < Unités
constraint chiffres[3] < chiffres[4];

% 6. Centaines > Unités
constraint chiffres[2] > chiffres[4];

% 7. Somme > 15
constraint sum(chiffres) > 15;

% 8. Produit des 3 derniers chiffres à minimiser
constraint p = chiffres[2] * chiffres[3] * chiffres[4];
solve minimize p;

%-----------------------------------------------------------------------------%

output [
  show(nombre)
];

