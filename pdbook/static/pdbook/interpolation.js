// Get cookie using jQuery, as per docs.djangoproject.com/en/1.11/ref/csrf
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken')

function csrfSafeMethod(method) {
    return(/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false,
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// Interpolation functions
var updateTable2D = function(result, status) {
    if (status == "success") {
        var data = $.parseJSON(result.responseText);
        console.log(data);
        if (data['x_value_ok'] == false) {
            console.log('Requested X value is not OK')
        } else {
            console.log('Requested X value is OK')
        };

        if (data['y_value_ok'] == false) {
            console.log('Requested Y value is not OK')
        } else {
            console.log('Requested Y value is OK')
        };
    };
}
        
