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
            url = "/core/ajax/change_active/";
            var token = $("div.footer").find("input[name=csrfmiddlewaretoken]").val()
            $.post(url, {model:model, id:id, csrfmiddlewaretoken:token}, (data)=>{
                if (data.status) {
                    Alerter.success('Mise à jour !', "Modification effectuée avec succès !");
                }else{
                    Alerter.error('Erreur !', data.message);
                }
            },"json");
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
            var token = $("div.footer").find("input[name=csrfmiddlewaretoken]").val()
            alerty.confirm("Voulez-vous vraiment supprimer cet element ?", {
                title: "Suppression",
                cancelLabel : "Non",
                okLabel : "OUI, supprimer",
            }, function(){
                alerty.prompt("Entrer votre mot de passe pour confirmer l'opération !", {
                    title: 'Récupération du mot de passe !',
                    inputType : "password",
                    cancelLabel : "Annuler",
                    okLabel : "Valider"
                }, function(password){
                    Loader.start();
                    $.post(url, {model:model, id:id, password:password, csrfmiddlewaretoken:token}, (data)=>{
                        if (data.status) {
                            window.location.reload()
                        }else{
                            Alerter.error('Erreur !', data.message);
                        }
                    },"json");
                })
            })
        }
        
    })