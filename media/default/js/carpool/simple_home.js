var geocoder;
var address_request, address_found;

Event.observe(window, 'load', function() {
    $('id_address').focus();
    geocoder = new GClientGeocoder();
});

get_point = function(point) {
    address_request = true;
    if (!point) {
        alert(gettext("ERROR : Address not found."));
        address_found = false;
    } else {
        address_found = true;
        $('id_point').setValue('POINT(' + point.lng() + ' ' + point.lat() + ')');
    }
};

function checkFields(btn_element_id, type_value, event) {
    if ($('id_address').getValue()) {
        address_request = false;
        geocoder.getLatLng(
            $('id_address').getValue(),
            get_point
        );
        submitForm(btn_element_id, type_value);
    } else {
        alert(gettext("Please fill Address field."));
    }
    if (undefined !== event) {
        Event.stop(event);
    }
}

function submitForm(btn_element_id, type_value) {
    if (address_request) {
        if (address_found) {
            $('id_type').setValue(type_value);
            $('quick_search_form').submit();
        }
    } else {
        setTimeout("submitForm('"+btn_element_id+"',"+type_value+");", 100);
    }
}

$('btn_search_demand').observe('click', function(event) {
    checkFields('btn_search_demand', 1);
})

$('quick_search_form').observe('submit', function(event) {
    checkFields('btn_search_offer', 0, event);
})
