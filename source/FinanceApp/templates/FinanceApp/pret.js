$(function() {

    $("form#formNewRemboursement").submit(function(event) {
            Loader.start();
            var url = "{% url 'FinanceApp:new_remboursement' %}";
            var formData = new FormData($(this)[0]);
            $.post({
                url: url,
                data: formData,
                processData: false,
                contentType: false
            }, function(data) {
                if (data.status) {
                    Loader.stop()
                    Swal.fire({
                        title: "Le remboursement a été effectué avec succès !",
                        icon: "success",
                        showConfirmButton: true,
                        showDenyButton: false,
                        confirmButtonText: "Ok, c'est compris !",
                        }).then((result) => {
                            /* Read more about isConfirmed, isDenied below */
                            if (result.isConfirmed) {
                                window.location.reload()
                            } 
                    });
                } else {
                    Loader.stop();
                    Alerter.error('Erreur !', data.message);
                }
            });
            return false;
        });


        confirmPret = function(pretId) {
            Swal.fire({
                title: "Êtes-vous sûr de vouloir valider ce prêt ?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: "Oui, valider le prêt",
                cancelButtonText: "Non, annuler",
                }).then((result) => {
                    /* Read more about isConfirmed, isDenied below */
                    if (result.isConfirmed) {
                        Loader.start()
                        var token = $(".footer").find("input[name=csrfmiddlewaretoken]").val()
                        $.ajax({
                            url: "{% url 'FinanceApp:confirm_pret' %}",     
                            type: "POST",
                            data: {
                                pret_id: pretId,
                                csrfmiddlewaretoken:token
                            },
                            success: function(data) {
                                if (data.status) {
                                    Loader.stop()
                                    Swal.fire({
                                        title: "Le prêt a été validé avec succès !",
                                        icon: "success",
                                        showConfirmButton: true,
                                        showDenyButton: false,
                                        confirmButtonText: "Ok, c'est compris !",
                                        }).then((result) => {
                                            /* Read more about isConfirmed, isDenied below */
                                            if (result.isConfirmed) {
                                                window.location.reload()
                                            } 
                                    });
                                } else {
                                    Alerter.error('Erreur !', data.message);
                                }
                            }
                        })
                    } else if (result.isDenied) {
                        Swal.fire("Annulation", "Vous avez annulé la validation du prêt", "error");
                    }
                });
        }   




        decaissement = function(pretId) {
            Swal.fire({
                title: "Êtes-vous sûr de vouloir faire le décaissement du prêt ?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: "Oui, décaisser le prêt",
                cancelButtonText: "Non, annuler",
                }).then((result) => {
                    /* Read more about isConfirmed, isDenied below */
                    if (result.isConfirmed) {
                        Loader.start()
                        var token = $(".footer").find("input[name=csrfmiddlewaretoken]").val()
                        $.ajax({
                            url: "{% url 'FinanceApp:decaissement' %}",
                            type: "POST",
                            data: {
                                pret_id: pretId,
                                csrfmiddlewaretoken:token
                            },
                            success: function(data) {
                                if (data.status) {
                                    Loader.stop()
                                    Swal.fire({
                                        title: "Le décaissement du prêt a été effectué avec succès !",
                                        icon: "success",
                                        showConfirmButton: true,
                                        showDenyButton: false,
                                        confirmButtonText: "Ok, c'est compris !",
                                        }).then((result) => {
                                            /* Read more about isConfirmed, isDenied below */
                                            if (result.isConfirmed) {
                                                window.location.reload()
                                            } 
                                    });
                                } else {
                                    Alerter.error('Erreur !', data.message);
                                }
                            }
                        })
                    } else if (result.isDenied) {
                        Swal.fire("Annulation", "Vous avez annulé le décaissement du prêt", "error");
                    }
                });
        }   

    })