(function ($) {

$(document).ready(function() {
    var boletoGerado = $('.field-box.field-boleto_gerado').find('img').attr('alt');
    var  djnadditem  = $(".djn-add-item");

    $(".djn-tr.form-row").each(function(index, elem) {
        val = $(elem).val();
        var currentRow = $(elem).closest('tr');
        var fieldsetTipo = currentRow.find('.field-tipo').find('select');
        var ldelete =  currentRow.find(".delete");
        var fieldvalor = currentRow.find(".djn-td.field-valor").find('input');
        var tipo = fieldsetTipo.val();
        if (boletoGerado==='True') {
            djnadditem.addClass('displayNone');
        }
        if (boletoGerado==='True' || tipo!=='o') {
            fieldsetTipo.attr("disabled", true);
            fieldvalor.attr("readonly", true);
            ldelete.addClass('displayNone')
        } else {
            fieldsetTipo.attr("disabled", true);
        }
    });
});

})(django.jQuery);
