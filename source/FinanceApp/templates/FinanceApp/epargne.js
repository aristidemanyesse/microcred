$(function() {

    $("form#formDepot").submit(function(event) {
            Loader.start();
            var url = "{% url 'FinanceApp:new_depot' %}";
            var formData = new FormData($(this)[0]);
            $.post({
                url: url,
                data: formData,
                processData: false,
                contentType: false
            }, function(data) {
                if (data.status) {
                    Swal.fire({
                        title: "Le dépot a été effectué avec succès !",
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
                Loader.stop();
            });
            return false;
        });



         $("form#formRetrait").submit(function(event) {
            Loader.start();
            var url = "{% url 'FinanceApp:new_retrait' %}";
            var formData = new FormData($(this)[0]);
            $.post({
                url: url,
                data: formData,
                processData: false,
                contentType: false
            }, function(data) {
                if (data.status) {
                    Swal.fire({
                        title: "Le retrait a été effectué avec succès !",
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
                Loader.stop();
            });
            return false;
        });


    })