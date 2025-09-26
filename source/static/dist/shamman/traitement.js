    $(function(){

        $("body").on("submit", "form.formShamman", function(event) {
            Loader.start()
            form = $(this).attr('classname');
            reload = $(this).attr('reload');
            url = "/core/ajax/save/";
            var formdata = new FormData($(this)[0]);
            formdata.append('modelform', form);
            $.post({url:url, data:formdata, contentType:false, processData:false}, function(data){
                if (data.status) {
                    if (reload == "false") {
                        Loader.stop();
                        Alerter.success('Réussite', data.message);
                        $(".modal").modal('hide');
                    }else if (!!data.url) {
                        window.location.href = data.url;
                    }else{
                        window.location.reload();
                    }
                }else{
                    Alerter.error('Erreur !', data.message);
                }
            }, 'json')
            return false;
        });



        $("input.maj, select.maj").change(function(){
            url = "/core/ajax/mise_a_jour/";
            var token = $("div.footer").find("input[name=csrfmiddlewaretoken]").val()
            var id = $(this).attr("id")
            var model = $(this).attr("model")
            var name = $(this).attr("name")
            var val = $(this).val()
            $.post(url, {model:model, name:name, id:id, val:val, csrfmiddlewaretoken:token}, (data)=>{
                if (data.status) {
                    Alerter.success('Reussite !', "Modification prise en compte avec succès !");
                }else{
                    Alerter.error('Erreur !', data.message);
                }
            },"json");
        })
        

        filtrer = function(){
            Loader.start()
            session("date1", $("#formFiltrer input[name=date1]").val())
            window.location.reload();
        }


        filter_date = function(debut, fin){
            url = "/core/ajax/filter_date/";
            Loader.start()
            $.post(url, {debut:debut, fin:fin}, (data)=>{
                window.location.reload();
            },"json");
        }



        change_active = function(model, id){
            Swal.fire({
                title: "Voulez-vous vraiment changer le statut de cet element ?",
                icon: "warning",
                showConfirmButton: true,
                showDenyButton: true,
                denyButtonText: "Non",
                confirmButtonText: "Oui, changer !",
            }).then((result) => {
                if (result.isConfirmed) {
                    Swal.fire({
                        title: "Entrez votre mot de passe pour confirmer l'opération !",
                        input: "password",
                        inputAttributes: {
                            autocapitalize: "off"
                        },
                        showCancelButton: true,
                        confirmButtonText: "Valider",
                        showLoaderOnConfirm: true,
                        preConfirm: async (password) => {
                            url = "/core/ajax/change_active/";
                            var token = $(".footer").find("input[name=csrfmiddlewaretoken]").val()
                            $.post(url, {model:model, id:id, password:password, csrfmiddlewaretoken:token}, (data)=>{
                                if (data.status) {
                                    window.location.reload()
                                }else{
                                    Alerter.error('Erreur !', data.message);
                                }
                            },"json");
                        },
                        allowOutsideClick: () => !Swal.isLoading()
                    })
                }
            });
        }



        supprimer = function(model, id){
            url = "/core/ajax/supprimer/";
            var token = $("div.footer").find("input[name=csrfmiddlewaretoken]").val()
            alerty.confirm("Voulez-vous vraiment supprimer cet element ?", {
                title: "Suppression",
                cancelLabel : "Non",
                okLabel : "OUI, supprimer",
            }, function(){
                Loader.start()
                $.post(url, {action:"delete_suppression", model:model, id:id, csrfmiddlewaretoken:token}, (data)=>{
                    if (data.status) {
                        window.location.reload()
                    }else{
                        Alerter.error('Erreur !', data.message);
                    }
                },"json");
            })
        }


        delete_password = function(model, id){
            url = "/core/ajax/supprimer/";
            Swal.fire({
                title: "Vous êtes sur le point de faire une suppression. Voulez-vous continuer ?",
                icon: "warning",
                showConfirmButton: true,
                showDenyButton: true,
                denyButtonText: "Non",
                confirmButtonText: "Oui, supprimer !",
            }).then((result) => {
                if (result.isConfirmed) {
                    Swal.fire({
                        title: "Entrez votre mot de passe pour confirmer l'opération !",
                        input: "password",
                        inputAttributes: {
                            autocapitalize: "off"
                        },
                        showCancelButton: true,
                        confirmButtonText: "Valider",
                        showLoaderOnConfirm: true,
                        preConfirm: async (password) => {
                            url = "/core/ajax/supprimer/";
                            var token = $(".footer").find("input[name=csrfmiddlewaretoken]").val()
                            $.post(url, {model:model, id:id, password:password, csrfmiddlewaretoken:token}, (data)=>{
                                if (data.status) {
                                    window.location.reload()
                                }else{
                                    Alerter.error('Erreur !', data.message);
                                }
                            },"json");
                        },
                        allowOutsideClick: () => !Swal.isLoading()
                    })
                }
            });
        }


        refresh_password = function(id) {
            Swal.fire({
                title: "Voulez-vous vraiment reinitialiser les accès de cet utilisateur ?",
                icon: "warning",
                showConfirmButton: true,
                showDenyButton: true,
                denyButtonText: "Non",
                confirmButtonText: "Oui, changer !",
                }).then((result) => {
                    /* Read more about isConfirmed, isDenied below */
                    if (result.isConfirmed) {
                        Swal.fire({
                            title: "Entrez votre mot de passe pour confirmer l'opération !",
                            input: "password",
                            inputAttributes: {
                                autocapitalize: "off"
                            },
                            showCancelButton: true,
                            confirmButtonText: "Valider",
                            showLoaderOnConfirm: true,
                            preConfirm: async (password) => {
                                url = "/core/ajax/refresh_password/";
                                var token = $(".footer").find("input[name=csrfmiddlewaretoken]").val()
                                $.post(url, {id:id, password:password, csrfmiddlewaretoken:token}, (data)=>{
                                    if (data.status) {
                                        window.location.reload()
                                    }else{
                                        Alerter.error('Erreur !', data.message);
                                    }
                                },"json");
                            },
                            allowOutsideClick: () => !Swal.isLoading()
                        })
                    } 
            });
        }


        
    })