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

        createTable(data['table_type'], data['table_data'], data['x_title'], data['y_title']);
    };
}

function updateTable(tableData) {
    //
}

function createTable(tableType, tableData, tableXTitle, tableYTitle) {
    var table = document.getElementById('interpolation-table');
    var tableBody = document.createElement('tbody');

    tableData.forEach(function(rowData, ii) {
        var row = document.createElement('tr');

        rowData.forEach(function(cellData, jj) {
            var cell = document.createElement('td');
            if (tableType == '1D' && ii == 1) {
                cell.id = "interpolation-result-cell";
            }

            if (tableType == '2D') {
                if (ii == 1 && [0, 2].includes(jj)) {
                    cell.id = "interpolation-intermediary-cell";
                } else if ([0, 2].includes(ii) && jj == 1) {
                    cell.id = "interpolation-intermediary-cell";
                } else if (ii == 1 && jj == 1) {
                    cell.id = "interpolation-result-cell";
                }
            }
            cell.appendChild(document.createTextNode(cellData));
            row.appendChild(cell);
        });

        tableBody.appendChild(row);
    });

    if (tableType == '2D') {
    } else if (tableType == '1D') {
        
    }

    table.appendChild(tableBody);
    //document.body.appendChild(table);
}
