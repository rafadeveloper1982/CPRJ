(function ($) {

$(document).ready(function() {

    console.log("testetetetet")

    $('#id_titulo').change(function(event) {
        console.log($('#id_titulo').val())

        $.getJSON("/getvaloraula/", {titulo: $('#id_titulo').val() },
                                function(json, textStatus) {
             $('#id_valor_aula').val(json.valor_aula);
        });



    });

    $('#id_qt_hora').change(function(event) {
        $('#id_valor').val($('#id_valor_aula').val() * $('#id_qt_hora').val());
    });
});

})(django.jQuery);
