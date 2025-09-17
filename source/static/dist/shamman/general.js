
$(function () {

    //bouton principal de deconnexion
    $("a#btn-deconnexion").click(function (event) {
        alerty.confirm("Voulez-vous vraiment vous deconnecter ???", {
            title: "Deconnexion",
            cancelLabel: "Non",
            okLabel: "Oui, me deconnecter !",
        }, function () {
            window.location.href = "/auth/logout/";
        })
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



    //superposition de modals
    $(document).on('show.bs.modal', '.modal', function () {
        var zIndex = 1040 + (10 * $('.modal:visible').length);
        $(this).css('z-index', zIndex);
        setTimeout(function () {
            $('.modal-backdrop').not('.modal-stack').css('z-index', zIndex - 1).addClass('modal-stack');
        }, 0);
    });
    $(document).on('hidden.bs.modal', '.modal', function () {
        $('.modal:visible').length && $(document.body).addClass('modal-open');
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




    //boutons de changement des langues
    $(".div-langues a").fadeOut()
    $(".div-langues a.active").fadeIn()
    $(".div-langues a.active span").fadeOut()

    $(".div-langues").hover(() => {
        $(".div-langues a").fadeIn()
        $(".div-langues a span").fadeIn()
    }, () => {
        $(".div-langues a").fadeOut()
        $(".div-langues a.active").fadeIn()
        $(".div-langues a.active span").fadeOut()
    })


    $(".div-langues a").click(function(){
        if($(this).hasClass("active")){
            return false
        }else{
            var lang = $(this).attr("set")
            $(".div-langues a").removeClass("active")
            $(this).addClass("active")
            Alerter.success('Langue changée avec succès !');

            url = "../../../core/ajax/change_language/";
            $.post(url, {lang:lang}, (data)=>{
                console.log(data)
                window.location.reload()
            },"json");
        }
    })

});