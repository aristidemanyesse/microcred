
$(function () {

     $('input[type="text"].number').each(function() {
    // si tu veux éviter de ré-initialiser un masque déjà présent :
    if ($(this).data('imask')) return;
    const mask = IMask(this, {
      mask: Number,
      min: 0,
      max: 999999999,
      thousandsSeparator: ' ',
      radix: ',',
      scale: 2,
      normalizeZeros: true,
      padFractionalZeros: false
    });
    $(this).data('imask', mask);
  });

  // Taux %
  $('input[type="text"].taux').each(function() {
    if ($(this).data('imask')) return;
    const mask = IMask(this, {
      mask: Number,
      min: 0,
      max: 100,
      thousandsSeparator: ' ',
      radix: ',',
      scale: 2,
      normalizeZeros: true,
      padFractionalZeros: false,
      suffix: ' %'
    });
    $(this).data('imask', mask);
  });


    //filtre de la barre generale de recherche
    $("#top-search").on("keyup", function () {
        var value = $(this).val().toLowerCase();
        $("table.table-mise tr:not(.no), .item").filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });


    //selection des images
    $('body').on("click", "button.btn_image", function (event) {
        $(this).prev("input[type=file]").trigger('click');
    });
    $('body').on("change", ".modal input[type=file]", function (e) {
        var src = URL.createObjectURL(e.target.files[0])
        $(this).prev("img.logo").attr('src', src);
    });



    //Watchdog de deconnexion
    $(document).idleTimer(10 * 60 * 1000);
    $(document).on("idle.idleTimer", function (event, elem, obj) {
        window.location.href = "/auth/locked/";
    });



    function beforePrint() {
        $("i#print").click()
    }

    function afterPrint() {
        $("i#print").click()
    }




});