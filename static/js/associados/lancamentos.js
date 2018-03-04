(function ($) {

$(document).ready(function() {
    if ($('#id_turma').val() > 0) {
        $.getJSON("/getvaloraula/", {turma: $('#id_turma').val() },
                                function(json, textStatus) {
            var valorAula =json.valor_aula;
            valorAula = parseFloat(valorAula).toFixed(2);
            $('#id_valor_aula').val(valorAula);
        });
    }

    $('#id_turma').change(function(event) {
        $.getJSON("/getvaloraula/", {turma: $('#id_turma').val() },
                                function(json, textStatus) {
            var valorAula =json.valor_aula;
            valorAula = parseFloat(valorAula).toFixed(2);
            $('#id_valor_aula').val(valorAula);
        });
    });

    $('#id_qt_hora').change(function(event) {
        $('#id_valor').val($('#id_valor_aula').val() * $('#id_qt_hora').val());
    });

    $( "input[type='text']" ).change(function(event) {
        //console.log($('#id_valor_aula').val(), 'teste input')
    });

    //evento chamdo ao trocr a qtd hora
    $( ".qtdHora" ).change(function(event) {
       var currentRow = $(event.target).closest('tr');
       var qty =  currentRow.find(".qtdHora").val();
       var valorHora =  $('#id_valor_aula').val();
       var valorTotal = qty *valorHora;
       valorTotal = parseFloat(valorTotal).toFixed(2).replace(".",",");
       var valor =  currentRow.find(".field-valor p").text(valorTotal);
       var valorAula =  currentRow.find('.field-vl_hora_aula p').text($('#id_valor_aula').val())
    });

    // Loop ao carregar tela para ajustar cor e disable e
    $(".qtdHora").each(function(index, elem) {
        val = $(elem).val();
        var currentRow = $(elem).closest('tr');
        var recebido = currentRow.find('img').attr('alt');
        var qty =  currentRow.find(".qtdHora");
        var ldelete =  currentRow.find(".delete");
        var data_vencimento = currentRow.find(".field-data_de_vencimento input");
        var data_recebido = currentRow.find(".field-data_de_recebimento input");

        if (recebido==="True") {
            qty.attr("readonly", true);
            data_vencimento.removeClass("vDateField");
            data_vencimento.attr("readonly", true);
            data_recebido.removeClass("vDateField");
            data_recebido.attr("readonly", true);
            ldelete.addClass('displayNone')
        } else {
            qty.prop("disabled", false);
            data_vencimento.attr("readonly",  false);
            ldelete.attr("readonly", false);
        }
    });
});

})(django.jQuery);
