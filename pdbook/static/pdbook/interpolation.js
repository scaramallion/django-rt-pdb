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
        if (data['x_value_ok'] == false) {
            document.getElementById("x_value_2d").style.border = "1px solid #ef0c34";
            // reset
        } else {
            document.getElementById("x_value_2d").style.border = "1px solid #0099dd";
        };

        if (data['y_value_ok'] == false) {
            document.getElementById("y_value_2d").style.border = "1px solid #ef0c34";
            // reset
        } else {
            document.getElementById("y_value_2d").style.border = "1px solid #0099dd";
        };

        createTable(data['table_data']);
    };
}

function createTable(tableData) {
    var table = document.createElement('table');
    var tableBody = document.createElement('tbody');

    tableData.forEach(function(rowData) {
        var row = document.createElement('tr');

        rowData.forEach(function(cellData) {
            var cell = document.createElement('td');
            cell.appendChild(document.createTextNode(cellData));
            row.appendChild(cell);
        });

        tableBody.appendChild(row);
    });

    table.appendChild(tableBody);
    document.body.appendChild(table);
}


