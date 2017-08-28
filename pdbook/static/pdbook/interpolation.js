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
var updateTable = function(result, status) {
    if (status == "success") {
        var data = $.parseJSON(result.responseText);
        if (data['table_type'] == '2D') {
            update2DTable(data);
        } else {
            update1DTable(data);
        };
    };
}

function update2DTable(tableData) {
    if (tableData['x_value_ok'] == false) {
        document.getElementById("x-input").style.border = "1px solid #ef0c34";
        // reset
    } else {
        document.getElementById("x-input").style.border = "1px solid #0099dd";
    };

    if (tableData['y_value_ok'] == false) {
        document.getElementById("y-input").style.border = "1px solid #ef0c34";
        // reset
    } else {
        document.getElementById("y-input").style.border = "1px solid #0099dd";
    };

    if (tableData['x_value_ok'] == true && tableData['y_value_ok']) {
        document.getElementById("x-a").innerHTML = tableData['x_values'][0]
        document.getElementById("x-b").innerHTML = tableData['x_values'][2]
        document.getElementById("y-a").innerHTML = tableData['y_values'][0]
        document.getElementById("y-b").innerHTML = tableData['y_values'][2]
        document.getElementById("tl").innerHTML = tableData['table_data'][0][0]
        document.getElementById("tc").innerHTML = tableData['table_data'][0][1]
        document.getElementById("tr").innerHTML = tableData['table_data'][0][2]
        document.getElementById("cl").innerHTML = tableData['table_data'][1][0]
        document.getElementById("interp-result").innerHTML = tableData['table_data'][1][1]
        document.getElementById("cr").innerHTML = tableData['table_data'][1][2]
        document.getElementById("bl").innerHTML = tableData['table_data'][2][0]
        document.getElementById("bc").innerHTML = tableData['table_data'][2][1]
        document.getElementById("br").innerHTML = tableData['table_data'][2][2]
    };
}

function update1DTable(tableData) {
    if (tableData['y_value_ok'] == false) {
        document.getElementById("y1-input").style.border = "1px solid #ef0c34";
        // reset
    } else {
        document.getElementById("y1-input").style.border = "1px solid #0099dd";
        document.getElementById("y1-a").innerHTML = tableData['y_values'][0]
        document.getElementById("y1-b").innerHTML = tableData['y_values'][2]
        document.getElementById("tl1").innerHTML = tableData['table_data'][0]
        document.getElementById("interp-result1").innerHTML = tableData['table_data'][1]
        document.getElementById("bl1").innerHTML = tableData['table_data'][2]
    };
}
