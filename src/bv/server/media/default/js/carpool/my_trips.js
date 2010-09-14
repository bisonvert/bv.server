onAlertClick = function(event) {
    if (!email_validated && confirm(gettext("Your email is not validated, you can not receiv alert emails.")) || email_validated) {
        var trip_id = event.element().id;
        new Ajax.Request('/ajax/switch_alert/'+trip_id+'/', { method:'get',
            onSuccess: function(transport){
                var json = transport.responseText.evalJSON();
                if (json.alert) {
                    $('a_'+trip_id).innerHTML = gettext("Yes");
                    $(''+trip_id).innerHTML = gettext("Disable");
                } else {
                    $('a_'+trip_id).innerHTML = gettext("No");
                    $(''+trip_id).innerHTML = gettext("Enable");
                }
            },
            onFailure: function(transport){
                alert(gettext("An error occurs."));
            }
        });
    }
}

for (index = 0, len = trip_ids.length; index < len; index++) {
    $(''+trip_ids[index]).observe('click', onAlertClick)
}
