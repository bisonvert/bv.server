/* gettext library */

var catalog = new Array();

function pluralidx(count) { return (count == 1) ? 0 : 1; }
catalog['%s seat still available'] = ['',''];
catalog['%s seat still available'][0] = '%s place encore disponible';
catalog['%s seat still available'][1] = '%s places encore disponibles';
catalog['A directions request could not be successfully parsed.\\nError code: %s'] = 'La requ\u00eate n\'a pas \u00e9t\u00e9 enti\u00e8rement interpr\u00eat\u00e9e.\\nCode erreur: %s';
catalog['An error occurs.'] = 'Une erreur s\'est produite.';
catalog['An error occurs.\\nError code: %s'] = 'Une erreur s\'est produite.\\nCode erreur: %s';
catalog['Arrival'] = 'Arriv\u00e9e';
catalog['Calendar'] = 'Calendrier';
catalog['Cancel'] = 'Annuler';
catalog['Check point n&deg;%s'] = 'Point de passage n&deg;%s';
catalog['Delete'] = 'Supprimer';
catalog['Departure at about %s'] = 'D\u00e9part aux alentours de %s';
catalog['Departure on'] = 'D\u00e9part le';
catalog['Departure time not specified'] = 'Heure de d\u00e9part non pr\u00e9cis\u00e9e';
catalog['Departure'] = 'D\u00e9part';
catalog['Directions request could not be successfully processed.\\nError code: %s'] = 'La requ\u00eate a \u00e9chou\u00e9.\\nCode erreur: %s';
catalog['Disable'] = 'D\u00e9sactiver';
catalog['ERROR : Address not found.'] = 'ERREUR : l\'adresse n\'a pas \u00e9t\u00e9 trouv\u00e9e.';
catalog['ERROR : Arrival address not found.'] = 'ERREUR : l\'adresse d\'arriv\u00e9e n\'a pas \u00e9t\u00e9 trouv\u00e9e.';
catalog['ERROR : Departure address not found.'] = 'ERREUR : l\'adresse de d\u00e9part n\'a pas \u00e9t\u00e9 trouv\u00e9e.';
catalog['Enable'] = 'Activer';
catalog['Error : Address not found.'] = 'Erreur : Adresse non trouv\u00e9e.';
catalog['Invalid key.\\nError code: %s'] = 'Clef invalide.\\nCode erreur: %s';
catalog['January February March April May June July August September October November December'] = 'Janvier F\u00e9vrier Mars Avril Mai Juin Juillet Ao\u00fbt Septembre Octobre Novembre D\u00e9cembre';
catalog['No corresponding trip for the moment.'] = 'Aucun trajet ne correspond \u00e0 votre recherche pour le moment.';
catalog['No more seat available'] = 'Plus de place disponible';
catalog['No'] = 'Non';
catalog['Offer by'] = 'Propos\u00e9 par';
catalog['Please choose a date.'] = 'Veuillez choisir une date.';
catalog['Please choose a frequency.'] = 'Veuillez choisir une fr\u00e9quence.';
catalog['Please fill Address field.'] = 'Veuillez renseigner l\'adresse dans le champ de saisie.';
catalog['Please fill Departure and Arrival fields.'] = 'Veuillez renseigner les champs D\u00e9part et Arriv\u00e9e.';
catalog['Please give a name to your trip.'] = 'Veuillez renseigner le nom de ce trajet';
catalog['Route %s - %s not found.'] = 'Itin\u00e9taire %s - %s non trouv\u00e9.';
catalog['S M T W T F S'] = 'D L M M J V S';
catalog['Seats available not specified'] = 'Nombre de places disponibles non pr\u00e9cis\u00e9';
catalog['Show trip details'] = 'Voir les d\u00e9tails de l\'annonce';
catalog['The route is not correctly defined.'] = 'L\'itin\u00e9raire n\'est pas correctement d\u00e9fini.';
catalog['Today'] = 'Aujourd\'hui';
catalog['Tomorrow'] = 'Demain';
catalog['Trip author'] = 'Auteur de l\'annonce';
catalog['Yes'] = 'Oui';
catalog['Yesterday'] = 'Hier';
catalog['You can create a trip %s, perhaps another carpool user will contact you about it.'] = 'En cr\u00e9ant une annonce %s, vous pouvez b\u00e9n\u00e9ficier des alertes email et des flux RSS vous informant des derniers trajets qui correspondent \u00e0 votre annonce, et indiquer aux autres utilisateurs que vous \u00eates disponible.';
catalog['You can create a trip by clicking on the button &laquo;Save this search&raquo;, perhaps another carpool user will contact you about it.'] = 'Cr\u00e9ez rapidement une annonce en cliquant sur le bouton &laquo;Enregistrer cette recherche&raquo;. B\u00e9n\u00e9ficiez ainsi des alertes email et des flux RSS vous informant des derniers trajets qui correspondent \u00e0 votre annonce, et indiquez aux autres utilisateurs que vous \u00eates disponible.';
catalog['Your email is not validated, you can not receiv alert emails.'] = 'Votre adresse email est en attente de validation, vous ne pouvez pas recevoir d\'alerte par email.';
catalog['after login'] = 'apr\u00e8s connexion';
catalog['show details'] = 'voir les d\u00e9tails';

/************************************** CALENDAR FROM ADMIN ***************************************/
catalog['6 a.m.'] = '6:00';
catalog['Add'] = 'Ajouter';
catalog['Available %s'] = '%s disponible(s)';
catalog['Choose a time'] = 'Choisir une heure';
catalog['Choose all'] = 'Tout choisir';
catalog['Chosen %s'] = '%s choisi(es)';
catalog['Clear all'] = 'Tout enlever';
catalog['Clock'] = 'Horloge';
catalog['January February March April May June July August September October November December'] = 'Janvier F\u00e9vrier Mars Avril Mai Juin Juillet Ao\u00fbt Septembre Octobre Novembre D\u00e9cembre';
catalog['Midnight'] = 'Minuit';
catalog['Noon'] = 'Midi';
catalog['Now'] = 'Maintenant';
catalog['Remove'] = 'Enlever';
catalog['S M T W T F S'] = 'D L M M J V S';
catalog['Select your choice(s) and click '] = 'S\u00e9lectionnez un ou plusieurs choix et cliquez ';
catalog['Sunday Monday Tuesday Wednesday Thursday Friday Saturday'] = 'Dimanche Lundi Mardi Mercredi Jeudi Vendredi Samedi';


function gettext(msgid) {
  var value = catalog[msgid];
  if (typeof(value) == 'undefined') {
    return msgid;
  } else {
    return (typeof(value) == 'string') ? value : value[0];
  }
}

function ngettext(singular, plural, count) {
  value = catalog[singular];
  if (typeof(value) == 'undefined') {
    return (count == 1) ? singular : plural;
  } else {
    return value[pluralidx(count)];
  }
}

function gettext_noop(msgid) { return msgid; }

function interpolate(fmt, obj, named) {
  if (named) {
    return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
  } else {
    return fmt.replace(/%s/g, function(match){return String(obj.shift())});
  }
}
